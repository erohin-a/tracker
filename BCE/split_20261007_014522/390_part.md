<!-- Часть 390 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Fallback-хранилище (когда keyring не работает)](389_Fallback_hranilische_kogda_keyring_ne_rabotaet.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](391_part.md)

---

# ============================================================

def _local_key() -> bytes:
    seed = (socket.gethostname() + platform.node()).encode()
    return base64.urlsafe_b64encode(hashlib.sha256(seed).digest())


def _protect(data: bytes) -> bytes:
    if sys.platform.startswith("win"):
        try:
            import win32crypt
            return win32crypt.CryptProtectData(data, None, None, None, None, 0)
        except ImportError:
            log.warning("win32crypt недоступен, fallback на Fernet")
            from cryptography.fernet import Fernet
            return Fernet(_local_key()).encrypt(data)
    from cryptography.fernet import Fernet
    return Fernet(_local_key()).encrypt(data)


def _unprotect(data: bytes) -> bytes:
    if sys.platform.startswith("win"):
        try:
            import win32crypt
            return win32crypt.CryptUnprotectData(data, None, None, None, 0)[1]
        except ImportError:
            pass
    from cryptography.fernet import Fernet
    return Fernet(_local_key()).decrypt(data)


def _load_fallback() -> dict:
    if not _FALLBACK_FILE.exists():
        return {}
    try:
        return json.loads(_unprotect(_FALLBACK_FILE.read_bytes()))
    except Exception as e:
        log.warning("Fallback read failed: %s", e)
        return {}


def _save_fallback(data: dict) -> None:
    _FALLBACK_FILE.write_bytes(_protect(json.dumps(data).encode()))
    if os.name != "nt":
        _FALLBACK_FILE.chmod(0o600)


def _safe_keyring_set(key: str, value: str) -> None:
    try:
        keyring.set_password(SERVICE, key, value)
        return
    except Exception as e:
        log.warning("keyring.set(%s) failed: %s ? fallback", key, e)
    data = _load_fallback()
    data[key] = value
    try:
        _save_fallback(data)
    except Exception as e2:
        log.error("Fallback write failed: %s", e2)
        raise RuntimeError(f"Cannot persist credentials: {e2}") from e2


def _safe_keyring_get(key: str):
    v = None
    try:
        v = keyring.get_password(SERVICE, key)
    except Exception as e:
        log.warning("keyring.get(%s): %s", key, e)
    fv = _load_fallback().get(key)
    if v and fv and v != fv:
        log.warning("keyring/fallback mismatch for %s (используем keyring)", key)
    return v or fv


