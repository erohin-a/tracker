# ============================================================

*Часть 60 из 100. Источник: `BCE.md`.*

[◀ Registration tab](059_Registration_tab.md) | [Оглавление](00_BCE_INDEX.md) | [...docstring... ▶](061_docstring.md)

---

# ============================================================
TRANSLATIONS = {
    # ---------- Общие ----------
    "btn.save": {"ru": "Сохранить", "en": "Save"},
    "btn.close": {"ru": "Закрыть", "en": "Close"},
    "btn.cancel": {"ru": "Отмена", "en": "Cancel"},
    "btn.yes": {"ru": "Да", "en": "Yes"},
    "btn.no": {"ru": "Нет", "en": "No"},

    # ---------- Окно настроек ----------
    "settings.title": {"ru": "Настройки Tracker", "en": "Tracker Settings"},
    "settings.tab.reminder": {"ru": "Напоминание", "en": "Reminders"},
    "settings.tab.general": {"ru": "Общие", "en": "General"},
    "settings.tab.registration": {"ru": "Регистрация", "en": "Registration"},

    # ---------- Напоминание ----------
    "reminder.source.personal": {
        "ru": "Источник: персональные настройки (заданы администратором)",
        "en": "Source: personal settings (set by administrator)",
    },
    "reminder.source.global": {
        "ru": "Источник: глобальные настройки (значения по умолчанию)",
        "en": "Source: global settings (default values)",
    },
    "reminder.group.start": {
        "ru": "Напоминание о старте работы",
        "en": "Start-of-work reminder",
    },
    "reminder.enabled": {"ru": "Включить напоминание", "en": "Enable reminder"},
    "reminder.threshold": {"ru": "Порог срабатывания:", "en": "Trigger threshold:"},
    "reminder.threshold.hint": {
        "ru": "Сколько минут активности без запущенной сессии должно пройти до первого напоминания",
        "en": "How many minutes of activity without an active session before the first reminder",
    },
    "reminder.repeat": {"ru": "Интервал повторов:", "en": "Repeat interval:"},
    "reminder.repeat.hint": {
        "ru": "Если проигнорировали напоминание — через сколько минут напомнить снова",
        "en": "If ignored — after how many minutes to remind again",
    },
    "reminder.max_per_day": {
        "ru": "Максимум напоминаний за день:",
        "en": "Max reminders per day:",
    },
    "reminder.max_per_day.hint": {
        "ru": "Защита от спама. При превышении — больше не напоминаем до следующего дня",
        "en": "Anti-spam. Above this limit — no reminders until next day",
    },
    "reminder.group.eod": {
        "ru": "Уведомление о конце рабочего дня",
        "en": "End-of-day notification",
    },
    "reminder.eod_hour": {"ru": "Час срабатывания:", "en": "Hour:"},
    "reminder.eod_minute": {"ru": "Минуты:", "en": "Minute:"},
    "reminder.eod.hint": {
        "ru": "В это время, если сессия ещё идёт, покажем уведомление «Не забыли завершить день?»",
        "en": "At this time, if a session is still running, show a «Did you forget to finish?» notification",
    },
    "reminder.eod_hour.zero": {"ru": "0 = выключено", "en": "0 = disabled"},
    "reminder.btn.reset_to_global": {
        "ru": "Сбросить к общим",
        "en": "Reset to global",
    },
    "reminder.btn.reset_to_global.tooltip": {
        "ru": "Удалить персональные настройки. Будут применены глобальные значения.",
        "en": "Delete personal settings. Global values will be applied.",
    },
    "reminder.reset.confirm_title": {"ru": "Сбросить к общим", "en": "Reset to global"},
    "reminder.reset.confirm_text": {
        "ru": "Будут удалены персональные настройки, заданные администратором.\n\nПосле этого применятся глобальные значения. Продолжить?",
        "en": "Personal settings set by administrator will be deleted.\n\nGlobal values will be applied. Continue?",
    },
    "reminder.status.local_only": {
        "ru": "Сохранено локально. ПК не зарегистрирован — на сервер не отправлено.",
        "en": "Saved locally. PC not registered — not sent to server.",
    },
    "reminder.status.synced": {
        "ru": "OK: Сохранено и синхронизировано с сервером.",
        "en": "OK: Saved and synced with server.",
    },
    "reminder.status.server_refused": {
        "ru": "Сохранено локально. Сервер отказал: {detail}",
        "en": "Saved locally. Server refused: {detail}",
    },
    "reminder.status.not_authorized": {
        "ru": "Сохранено локально. ПК не авторизован — обратитесь к администратору.",
        "en": "Saved locally. PC not authorized — contact administrator.",
    },
    "reminder.status.server_error": {
        "ru": "Сохранено локально. Сервер ответил {code}.",
        "en": "Saved locally. Server replied {code}.",
    },
    "reminder.status.net_error": {
        "ru": "Сохранено локально. Ошибка сети: {err}",
        "en": "Saved locally. Network error: {err}",
    },
    "reminder.reset.not_registered": {
        "ru": "ПК не зарегистрирован",
        "en": "PC not registered",
    },
    "reminder.reset.not_linked": {
        "ru": "ПК не привязан к сотруднику — обратитесь к администратору.",
        "en": "PC not linked to employee — contact administrator.",
    },
    "reminder.reset.unauth": {
        "ru": "ПК не авторизован — обратитесь к администратору.",
        "en": "PC not authorized — contact administrator.",
    },
    "reminder.reset.server_error": {
        "ru": "Сервер вернул {code}. Сброс не выполнен.",
        "en": "Server replied {code}. Reset failed.",
    },
    "reminder.reset.success": {
        "ru": "OK: Персональные настройки удалены. Применены глобальные.",
        "en": "OK: Personal settings deleted. Global applied.",
    },
    "reminder.reset.partial": {
        "ru": "Удалено, но не удалось загрузить настройки ({code})",
        "en": "Deleted, but failed to reload ({code})",
    },

    # ---------- Общие ----------
    "general.group.autostart": {"ru": "Автозапуск", "en": "Autostart"},
    "general.autostart": {
        "ru": "Запускать Tracker при входе в систему",
        "en": "Run Tracker on system startup",
    },
    "general.autostart.hint": {
        "ru": "Клиент запустится автоматически после входа пользователя в Windows",
        "en": "Client will launch automatically after user logs into Windows",
    },
    "general.autostart.error": {
        "ru": "Не удалось изменить автозапуск. Проверьте права доступа.",
        "en": "Failed to change autostart. Check permissions.",
    },
    "general.group.appearance": {"ru": "Внешний вид", "en": "Appearance"},
    "general.theme": {"ru": "Тема:", "en": "Theme:"},
    "general.theme.hint": {
        "ru": "Цветовая схема интерфейса клиента. Применяется мгновенно.",
        "en": "Client UI color scheme. Applied instantly.",
    },
    "general.theme.light": {"ru": "Светлая", "en": "Light"},
    "general.theme.dark": {"ru": "Тёмная", "en": "Dark"},
    "general.theme.system": {"ru": "Системная", "en": "System"},
    "general.group.language": {"ru": "Язык интерфейса", "en": "UI language"},
    "general.lang": {"ru": "Язык:", "en": "Language:"},
    "general.lang.hint": {
        "ru": "Язык надписей в клиенте. Для применения требуется перезапуск.",
        "en": "Language of client labels. Restart required to apply.",
    },
    "general.lang.restart_title": {
        "ru": "Перезапуск клиента",
        "en": "Restart client",
    },
    "general.lang.restart_text": {
        "ru": "Язык изменён на «{lang}».\n\nДля применения требуется перезапуск клиента. Перезапустить сейчас?",
        "en": "Language changed to «{lang}».\n\nRestart is required. Restart now?",
    },
    "general.group.connectivity": {"ru": "Подключение", "en": "Connection"},
    "general.server_url": {"ru": "Адрес сервера:", "en": "Server URL:"},
    "general.server_url.hint": {
        "ru": "Полный адрес сервера, включая https://. Например: https://tracker.company.ru",
        "en": "Full server URL including https://. For example: https://tracker.company.ru",
    },
    "general.cert_fingerprint": {
        "ru": "Отпечаток сертификата:",
        "en": "Certificate fingerprint:",
    },
    "general.cert_fingerprint.hint": {
        "ru": "SHA-256 отпечаток сертификата сервера (64 hex-символа). Оставьте пустым, если не требуется pinning. Администратор подскажет значение.",
        "en": "SHA-256 fingerprint of server certificate (64 hex chars). Leave empty if pinning is not required. Administrator will provide the value.",
    },
    "general.btn.check_connection": {
        "ru": "Проверить соединение",
        "en": "Check connection",
    },
    "general.btn.save_server": {
        "ru": "Сохранить адрес",
        "en": "Save server URL",
    },
    "general.conn.checking": {"ru": "Проверяем...", "en": "Checking..."},
    "general.conn.ok": {
        "ru": "OK: сервер отвечает, версия {version}",
        "en": "OK: server responds, version {version}",
    },
    "general.conn.fail": {
        "ru": "Ошибка: сервер недоступен ({err})",
        "en": "Error: server unavailable ({err})",
    },
    "general.conn.no_server": {
        "ru": "Укажите адрес сервера",
        "en": "Enter server URL",
    },
    "general.conn.saved": {
        "ru": "Адрес сохранён. Перезапустите клиент для применения.",
        "en": "URL saved. Restart client to apply.",
    },
    "general.group.notifications": {
        "ru": "Уведомления",
        "en": "Notifications",
    },
    "general.notif.offline": {
        "ru": "Показывать тост при потере связи с сервером",
        "en": "Show toast when connection lost",
    },
    "general.notif.offline.hint": {
        "ru": "Появится системное уведомление, если клиент не может связаться с сервером больше 2 циклов синхронизации",
        "en": "System notification appears if client cannot reach server for more than 2 sync cycles",
    },
    "general.notif.eod": {
        "ru": "Показывать напоминание о конце дня",
        "en": "Show end-of-day reminder",
    },
    "general.notif.eod.hint": {
        "ru": "В указанное время, если сессия ещё идёт, появится напоминание завершить рабочий день",
        "en": "At specified time, if session is still running, show end-of-day reminder",
    },

    # ---------- Регистрация ----------
    "reg.group.info": {
        "ru": "Информация о регистрации",
        "en": "Registration info",
    },
    "reg.uid": {"ru": "Computer UID:", "en": "Computer UID:"},
    "reg.hostname": {"ru": "Hostname:", "en": "Hostname:"},
    "reg.server": {"ru": "Сервер:", "en": "Server:"},
    "reg.group.server": {
        "ru": "Адрес сервера",
        "en": "Server address",
    },
    "reg.server_url": {"ru": "URL сервера:", "en": "Server URL:"},
    "reg.server_url.hint": {
        "ru": "Адрес сервера Tracker. Формат: https://host или https://IP. Если не указан — используется значение из файла .env",
        "en": "Tracker server address. Format: https://host or https://IP. If not set — value from .env is used",
    },
    "reg.cert_fingerprint": {
        "ru": "Отпечаток сертификата (опционально):",
        "en": "Certificate fingerprint (optional):",
    },
    "reg.cert_fingerprint.hint": {
        "ru": "SHA-256 отпечаток TLS-сертификата сервера (64 hex-символа). Оставьте пустым, если не нужен pinning. Админ выдаст значение командой на сервере.",
        "en": "SHA-256 fingerprint of the server TLS certificate (64 hex chars). Leave empty if pinning is not required. Admin will provide it.",
    },
    "reg.bootstrap_token": {
        "ru": "Bootstrap-токен:",
        "en": "Bootstrap token:",
    },
    "reg.bootstrap_token.hint": {
        "ru": "Одноразовый токен от администратора для регистрации ПК. Используется только при первой регистрации. Если ПК уже зарегистрирован — можно оставить пустым.",
        "en": "One-time token from administrator to register PC. Used only at first registration. If PC is already registered — leave empty.",
    },
    "reg.btn.save_server": {
        "ru": "Сохранить адрес",
        "en": "Save server URL",
    },
    "reg.btn.check_connection": {
        "ru": "Проверить соединение",
        "en": "Check connection",
    },
    "reg.server.saved": {
        "ru": "Адрес сохранён. Перезапустите клиент для применения.",
        "en": "URL saved. Restart client to apply.",
    },
    "reg.server.checking": {"ru": "Проверяем...", "en": "Checking..."},
    "reg.server.ok": {
        "ru": "OK: сервер отвечает, версия {version}",
        "en": "OK: server responds, version {version}",
    },
    "reg.server.fail": {
        "ru": "Ошибка: {err}",
        "en": "Error: {err}",
    },
    "reg.reregister": {
        "ru": "Перерегистрировать компьютер",
        "en": "Re-register computer",
    },
    "reg.reregister.warn": {
        "ru": "Перерегистрация удалит текущий ключ клиента. Понадобится новый bootstrap-токен от администратора.",
        "en": "Re-registration will delete the current client key. A new bootstrap token from administrator will be required.",
    },
    "reg.reregister.confirm_title": {
        "ru": "Перерегистрация",
        "en": "Re-registration",
    },
    "reg.reregister.confirm_text": {
        "ru": "Компьютер: {uid}...\n\nКлюч доступа будет удалён. UID компьютера сохранится, чтобы администратор мог разрешить перерегистрацию именно для этого ПК.\n\nПродолжить?",
        "en": "Computer: {uid}...\n\nAccess key will be deleted. Computer UID will be kept so administrator can allow re-registration for this specific PC.\n\nContinue?",
    },
    "reg.reregister.done_title": {"ru": "Готово", "en": "Done"},
    "reg.reregister.done_text": {
        "ru": "Ключ доступа удалён. UID компьютера сохранён.\n\nШаги для завершения перерегистрации:\n1. Попросите администратора в админке нажать «Разрешить перерегистрацию» для этого ПК.\n2. Закройте это окно и запустите Tracker заново.\n3. В появившемся окне введите новый токен от администратора.",
        "en": "Access key deleted. Computer UID kept.\n\nSteps to complete re-registration:\n1. Ask administrator to click «Allow re-registration» for this PC.\n2. Close this window and restart Tracker.\n3. In the appeared dialog, enter the new token from administrator.",
    },
    "reg.reregister.no_uid": {
        "ru": "Computer UID неизвестен. Обратитесь к администратору — требуется полная перерегистрация с нуля.",
        "en": "Computer UID unknown. Contact administrator — full re-registration required.",
    },
    "reg.reregister.error": {
        "ru": "Не удалось выполнить перерегистрацию: {err}",
        "en": "Failed to re-register: {err}",
    },
}


def set_language(code: str) -> bool:
    """Устанавливает текущий язык. Возвращает True при успехе."""
    global _current_lang
    if code in [l["code"] for l in SUPPORTED_LANGS]:
        _current_lang = code
        log.info("Language set to %s", code)
        return True
    return False


def get_language() -> str:
    """Возвращает текущий язык."""
    return _current_lang


def is_valid_lang(code: str) -> bool:
    """Проверяет поддержку языка."""
    return code in [l["code"] for l in SUPPORTED_LANGS]


def t(key: str, **kwargs) -> str:
    """
    Возвращает перевод по ключу.
    Если в строке есть {name} — подставит из kwargs.
    """
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(_current_lang) or entry.get("ru") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
'@

[System.IO.File]::WriteAllText("D:\tracker\client\i18n.py", $content, [System.Text.UTF8Encoding]::new($false))

Write-Host "OK: client/i18n.py создан" -ForegroundColor Green

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'D:\tracker\client\i18n.py', encoding='utf-8').read()); print('SYNTAX OK')"
Что ожидаем:
text
OK: client/i18n.py создан
SYNTAX OK
________________________________________
Скрипт 2 — client/themes.py
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$content = @'
# ============================================================
# Темы оформления клиента Tracker
# ============================================================
# Light  — стандартная светлая (пустой stylesheet)
# Dark   — тёмная (QSS ниже)
# System — по умолчанию системная, сейчас = светлая
#
# Применение:
#   from . import themes
#   themes.apply_theme(QApplication.instance(), "dark")
# ============================================================

import logging

log = logging.getLogger("tracker.themes")

SUPPORTED_THEMES = [
    {"code": "light"},
    {"code": "dark"},
    {"code": "system"},
]

DARK_QSS = """
QWidget { background-color: #2b2b2b; color: #e0e0e0; }
QDialog { background-color: #2b2b2b; }
QLabel { color: #e0e0e0; background: transparent; }
QPushButton {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555; border-radius: 4px;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #4a4a4a; }
QPushButton:pressed { background-color: #555; }
QPushButton:disabled { color: #777; background-color: #333; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555; border-radius: 4px;
    padding: 4px 6px;
}
QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {
    background-color: #333; color: #777;
}
QComboBox QAbstractItemView {
    background-color: #2b2b2b; color: #e0e0e0;
    selection-background-color: #4a4a4a;
    border: 1px solid #555;
}
QCheckBox { color: #e0e0e0; background: transparent; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #666; border-radius: 3px;
    background-color: #3c3c3c;
}
QCheckBox::indicator:checked {
    background-color: #4a90e2;
    border-color: #4a90e2;
}
QGroupBox {
    color: #e0e0e0;
    border: 1px solid #555; border-radius: 4px;
    margin-top: 12px; padding-top: 10px;
}
QGroupBox::title {
    left: 10px; padding: 0 4px;
    background-color: #2b2b2b; color: #e0e0e0;
}
QTabWidget::pane {
    border: 1px solid #555; background-color: #2b2b2b;
}
QTabBar::tab {
    background-color: #3c3c3c; color: #e0e0e0;
    padding: 6px 14px; border: 1px solid #555;
    border-bottom: none;
    border-top-left-radius: 4px; border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #2b2b2b; color: #ffffff;
    border-bottom: 1px solid #2b2b2b;
}
QTabBar::tab:hover:!selected { background-color: #4a4a4a; }
QMenu {
    background-color: #2b2b2b; color: #e0e0e0;
    border: 1px solid #555;
}
QMenu::item { padding: 6px 20px; }
QMenu::item:selected { background-color: #4a4a4a; }
QToolTip {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555; padding: 4px 6px;
}
QMessageBox { background-color: #2b2b2b; }
QScrollBar:vertical {
    background-color: #2b2b2b; width: 12px;
    border: none; margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #555; border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #666; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0; background: none;
}
QScrollBar:horizontal {
    background-color: #2b2b2b; height: 12px;
    border: none; margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: #555; border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background-color: #666; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0; background: none;
}
"""


def apply_theme(app, code: str) -> bool:
    """
    Применяет тему к приложению.
    code: "light" | "dark" | "system"
    """
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(DARK_QSS)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet("")
        log.info("Applied %s theme", code or "light")
        return True
    else:
        log.warning("Unknown theme: %s, using light", code)
        app.setStyleSheet("")
        return False


def is_valid_theme(code: str) -> bool:
    return code in [t["code"] for t in SUPPORTED_THEMES]
'@

[System.IO.File]::WriteAllText("D:\tracker\client\themes.py", $content, [System.Text.UTF8Encoding]::new($false))

Write-Host "OK: client/themes.py создан" -ForegroundColor Green

python -c "import ast; ast.parse(open(r'D:\tracker\client\themes.py', encoding='utf-8').read()); print('SYNTAX OK')"
Что ожидаем:
text
OK: client/themes.py создан
SYNTAX OK
________________________________________
Скрипт 3 — Патч config.py
Добавляем функции для работы с config.json (где будут храниться язык, тема, кастомный URL сервера, отпечаток и т.п.).
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\config.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "def load_config" in content:
    print("SKIP: config helpers уже есть")
    raise SystemExit(0)

addition = '''

# ============================================================
# Работа с локальным config.json (настройки клиента)
# ============================================================
# Здесь хранятся:
#   - language         — "ru" | "en"
#   - theme            — "light" | "dark" | "system"
#   - autostart_enabled
#   - server_url       — переопределение TRACKER_SERVER_URL из .env
#   - cert_fingerprint — переопределение TRACKER_PIN
#   - notifications    — {offline: bool, eod: bool}
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

# Проверяем наличие ключевых функций
for name in ["load_config", "save_config", "get_setting", "set_setting",
             "get_server_url", "get_cert_fingerprint",
             "get_language_code", "get_theme_code"]:
    ok = f"def {name}" in content
    print(f" {'OK' if ok else 'MISS'}: {name}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_config.py", $patcher, [System.Text.UTF8Encoding]::new($false))

Write-Host "=== Запуск патчера ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_config.py
Что ожидаем:
text
OK: config.py дополнен функциями load/save/get/set
SYNTAX OK
 OK: load_config
 OK: save_config
 OK: get_setting
 OK: set_setting
 OK: get_server_url
 OK: get_cert_fingerprint
 OK: get_language_code
 OK: get_theme_code
________________________________________
Проверка, что всё связалось
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
from client import i18n, themes, config

print('=== i18n ===')
print('Язык сейчас:', i18n.get_language())
print('RU:', i18n.t('settings.title'))
i18n.set_language('en')
print('EN:', i18n.t('settings.title'))
i18n.set_language('ru')

print()
print('=== themes ===')
print('Темы:', [t['code'] for t in themes.SUPPORTED_THEMES])
print('Тёмная QSS:', len(themes.DARK_QSS), 'символов')

print()
print('=== config ===')
print('Текущий язык (из config):', config.get_language_code())
print('Текущая тема (из config):', config.get_theme_code())
print('URL сервера:', config.get_server_url())
print('Отпечаток:', config.get_cert_fingerprint() or '(не задан)')
"@
Что ожидаем:
text
=== i18n ===
Язык сейчас: ru
RU: Настройки Tracker
EN: Tracker Settings

=== themes ===
Темы: ['light', 'dark', 'system']
Тёмная QSS: 2847 символов

=== config ===
Текущий язык (из config): ru
Текущая тема (из config): light
URL сервера: https://127.0.0.1
Отпечаток: (не задан)
________________________________________
Что делаем дальше
Проверь эти 4 скрипта. Если всё чисто — пришли подтверждение, и в следующем сообщении я:
Полностью перепишу settings_dialog.py — новая вкладка «Общие» + расширенная «Регистрация» + i18n + тултипы на всех элементах
Патчну main.py — применение темы и языка при старте
Дам settings_dialog.py через Python-патчер (для обхода проблем с большими here-string'ами)
Если где-то SYNTAX ERROR или MISS — не иди дальше, пришли вывод, поправим точечно.
По твоему замечанию про подсказки: я везде добавляю ключи .hint для тултипов. В settings_dialog.py на каждой группе будет иконка ? или <span class="hint"> с title — чтобы новый пользователь сразу понимал, что за настройка.
OK: client/i18n.py создан SYNTAX OK OK: client/themes.py создан SYNTAX OK >> & client\.venv\Scripts\python.exe _patch_config.py === Запуск патчера === OK: config.py дополнен функциями load/save/get/set SYNTAX OK OK: load_config OK: save_config OK: get_setting OK: set_setting OK: get_server_url OK: get_cert_fingerprint OK: get_language_code OK: get_theme_code === i18n === Язык сейчас: ru RU: Настройки Tracker EN: Tracker Settings === themes === Темы: ['light', 'dark', 'system'] Тёмная QSS: 2907 символов === config === Текущий язык (из config): ru Текущая тема (из config): light URL сервера: https://127.0.0.1 Отпечаток: (не задан)
Отлично, все 4 скрипта прошли чисто. Теперь переходим к большому блоку — переписыванию settings_dialog.py и патчу main.py.
Ключевые задачи:
settings_dialog.py — полностью переписать:
Вкладка «Напоминание» — оставить логику, добавить i18n + тултипы
Вкладка «Общие» — тема (light/dark/system), язык (ru/en) с перезапуском, автозапуск, уведомления, адрес сервера + отпечаток + кнопка «Проверить соединение»
Вкладка «Регистрация» — расширить: URL сервера, отпечаток, bootstrap-токен, кнопка «Проверить соединение», оставить перерегистрацию
main.py патч — при старте применяем тему и язык из config.json.
Важно: файл settings_dialog.py получится большой (~600+ строк). По опыту пользователя с here-string'ами — надо использовать Python-патчер или разбить на несколько блоков.
Стратегия: используем Python-патчер, который пишет файл целиком через io.open с UTF-8. Это надёжнее всего. Патчер будет содержать полный текст нового settings_dialog.py в виде Python-строки.
Но это тоже большая Python-строка... Другой вариант — писать файл построчно через массив строк. Но проще всего — дать пользователю скрипт, который строит файл через массив строк в Python, затем записывает.
Или ещё проще: использовать подход @() массив строк в PowerShell + Out-File. Как они делали в конце — это работало.
Хм, но проблема в том, что в строках будут и " и ' и \ — экранирование сложное.
Самое надёжное — использовать Python-патчер, где строки кодируются через тройные кавычки. Но тогда внутри Python-строки не должно быть """.
Другой вариант — использовать base64. Это вообще надёжно, но громоздко.
Или — как раньше делал пользователь — здесь-строки в PowerShell с одинарными кавычками. Внутри — Python-код с двойными кавычками. Это работало.
Решу так: разобью на 3 скрипта по вкладкам + главный диалог. Каждый скрипт — небольшой here-string в PowerShell.
Скрипт A1: сначала создаём новый файл settings_dialog.py с частью 1 (импорты + ReminderTab)
Скрипт A2: добавляем GeneralTab через Python-патчер (append к файлу)
Скрипт A3: добавляем RegistrationTab + SettingsDialog через Python-патчер
Скрипт A4: патч main.py — применяем тему/язык при старте
Хм, но тогда получится несколько промежуточных состояний с неработающим файлом. Лучше сначала собрать полностью в памяти, потом записать.
Наилучший подход: используем Python-патчер, который строит файл из нескольких блоков (конкатенация строк). Каждый блок — тройные кавычки '''...''' в Python. Внутри Python-кода — не должно быть '''. А двойные кавычки — ок.
Проверю свой будущий settings_dialog.py — там будут docstring'и через """. Не '''. Значит тройные одинарные кавычки подойдут.
Но ещё проблема — PowerShell here-string для самого Python-патчера. Внутри Python-кода с '''...''' могут быть одинарные кавычки — они не поломают PowerShell here-string @'...'@, потому что там всё literal, но надо чтобы не было строки, начинающейся с '@.
ОК, попробую так. Пишу Python-патчер, содержащий в себе все три вкладки как тройные строки.
Другой подход — вообще не использовать Python-патчер, а использовать base64. Пользователь даёт команду:
powershell
$b64 = "....."  # длинная base64-строка
[System.IO.File]::WriteAllBytes("D:\tracker\client\settings_dialog.py", [Convert]::FromBase64String($b64))
Но мне нужно сгенерировать base64 из контента, а я не могу это сделать, потому что это текст на русском с разными кавычками.
Ладно, не буду изобретать. Давайте так:
Подход: разбить на 3 части через here-string, каждая часть пишется в отдельный .tmp файл, потом склеиваем.
powershell
$part1 = @'
...imports + ReminderTab...
'@
[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part1.tmp", $part1, [System.Text.UTF8Encoding]::new($false))

$part2 = @'
...GeneralTab...
'@
[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part2.tmp", $part2, [System.Text.UTF8Encoding]::new($false))

$part3 = @'
...RegistrationTab + SettingsDialog...
'@
[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part3.tmp", $part3, [System.Text.UTF8Encoding]::new($false))

# Склейка
Get-Content "D:\tracker\client\_sd_part1.tmp" -Raw -Encoding UTF8 | Set-Content ...
Хм, проще через .NET:
powershell
$full = [System.IO.File]::ReadAllText("...part1.tmp") + [System.IO.File]::ReadAllText("...part2.tmp") + [System.IO.File]::ReadAllText("...part3.tmp")
[System.IO.File]::WriteAllText("D:\tracker\client\settings_dialog.py", $full, [System.Text.UTF8Encoding]::new($false))
Remove-Item ...part*.tmp
Это надёжно. Каждая часть — до 200 строк here-string, что должно пройти.
Действуем. Разобью новую settings_dialog.py на 3 части:
Часть 1: заголовок + импорты + ReminderTab (с i18n и тултипами)
Часть 2: GeneralTab (тема, язык, автозапуск, уведомления, адрес сервера)
Часть 3: RegistrationTab (переписан: адрес, отпечаток, токен, проверка) + SettingsDialog
Затем main.py патч.
По main.py — надо применить тему и язык при старте. Это делается в main() перед созданием QApplication или сразу после. Также нужно подписаться на сохранение настроек — сейчас SettingsDialog закрывается, надо чтобы изменения применились. Вариант: после закрытия диалога перечитать config.json и применить тему/язык. Если язык изменился — предложить перезапуск.
Начнём.
Пишу код для всех трёх частей.
Часть 1 — заголовок + ReminderTab:
python
