<!-- Часть 926 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ - notifications    — {offline: bool, eod: bool}](925_notifications_offline_bool_eod_bool.md) | [Оглавление](00_BCE_INDEX.md) | [Проверяем наличие ключевых функций ▶](927_Proveryaem_nalichie_klyuchevyh_funktsiy.md)

---

# ============================================================

import json as _json

CONFIG_FILE = BASE_DIR / "config.json"


def load_config() -> dict:
    """Читает config.json. Возвращает {} при отсутствии или ошибке."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return _json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        _log.warning("Failed to read config.json: %s", e)
        return {}


def save_config(data: dict) -> None:
    """Записывает config.json (UTF-8, без BOM)."""
    try:
        CONFIG_FILE.write_text(
            _json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        _log.error("Failed to save config.json: %s", e)


def get_setting(key: str, default=None):
    """Возвращает значение из config.json или default."""
    return load_config().get(key, default)


def set_setting(key: str, value) -> None:
    """Устанавливает значение в config.json."""
    data = load_config()
    data[key] = value
    save_config(data)


def get_server_url() -> str:
    """
    Возвращает эффективный адрес сервера:
    config.json > .env > дефолт.
    """
    custom = get_setting("server_url")
    if custom:
        return custom
    return SERVER_URL


def get_cert_fingerprint() -> str:
    """
    Возвращает эффективный отпечаток сертификата:
    config.json > .env > пусто.
    """
    custom = get_setting("cert_fingerprint")
    if custom:
        return custom.strip().lower()
    return PINNED_CERT_SHA256


def get_language_code() -> str:
    """Язык из config.json (ru/en), по умолчанию ru."""
    return get_setting("language", "ru")


def get_theme_code() -> str:
    """Тема из config.json (light/dark/system), по умолчанию light."""
    return get_setting("theme", "light")
'''

content = content.rstrip() + addition + "\n"

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("OK: config.py дополнен функциями load/save/get/set")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

