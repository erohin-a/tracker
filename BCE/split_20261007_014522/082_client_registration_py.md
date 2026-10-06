<!-- Часть 82 из 1409 -->
# `client/registration.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/registration.py`

[◀ `client/http_client.py`](081_client_http_client_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/collector.py` ▶](083_client_collector_py.md)

---

### `client/registration.py`

```python
import base64
import hashlib
import json
import logging
import os
import platform
import socket
import sys
import uuid
from pathlib import Path

import keyring

from . import http_client
from .config import BASE_DIR, CLIENT_VERSION, SERVER_URL

log = logging.getLogger("tracker.register")
SERVICE = "tracker"
_FALLBACK_FILE = BASE_DIR / "credentials.enc"


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


def _safe_keyring_get(key: str) -> str | None:
    v = None
    try:
        v = keyring.get_password(SERVICE, key)
    except Exception as e:
        log.warning("keyring.get(%s): %s", key, e)
    fv = _load_fallback().get(key)
    if v and fv and v != fv:
        log.warning("keyring/fallback mismatch for %s (используем keyring)", key)
    return v or fv


def ensure_registered(bootstrap_token: str | None = None) -> str:
    uid = _safe_keyring_get("computer_uid")
    secret = _safe_keyring_get("client_secret")
    if uid and secret:
        return uid

    token = bootstrap_token or os.environ.get("TRACKER_BOOTSTRAP_TOKEN")
    if not token:
        tf = BASE_DIR / "bootstrap.txt"
        if tf.exists():
            token = tf.read_text(encoding="utf-8").strip()
    if not token:
        raise RuntimeError(
            "Bootstrap token required. Получите у администратора и положите "
            f"в {BASE_DIR / 'bootstrap.txt'}")

    uid = uid or str(uuid.uuid4())
    payload = {
        "computer_uid": uid,
        "hostname": socket.gethostname(),
        "os_info": f"{platform.system()} {platform.release()}",
        "client_version": CLIENT_VERSION,
        "bootstrap_token": token,
    }
    resp = http_client.post(f"{SERVER_URL}/api/v1/computers/register", json=payload)
    resp.raise_for_status()
    data = resp.json()
    _safe_keyring_set("computer_uid", uid)
    _safe_keyring_set("client_secret", data["client_secret"])
    try:
        (BASE_DIR / "bootstrap.txt").unlink(missing_ok=True)
    except OSError:
        pass
    log.info("Registered as %s (secret_version=%s)", uid, data.get("secret_version"))
    return uid


def get_computer_uid() -> str | None:
    return _safe_keyring_get("computer_uid")
```

