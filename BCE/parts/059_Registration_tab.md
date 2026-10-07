# Registration tab

*Часть 59 из 100. Источник: `BCE.md`.*

[◀ ---- 6.6: user_edit_submit — сохраняем department_id ----](058_6_6_user_edit_submit_sohranyaem_department_id.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](060_part.md)

---

# Registration tab
reg.group.info
reg.uid
reg.hostname
reg.server_current
reg.group.server
reg.server_url
reg.server_url.hint
reg.cert_fingerprint
reg.cert_fingerprint.hint
reg.bootstrap_token
reg.bootstrap_token.hint
reg.check_connection
reg.save_server
reg.reregister
reg.reregister.confirm_title
reg.reregister.confirm_text
reg.reregister.done_title
reg.reregister.done_text
reg.reregister.no_uid
reg.reregister.error
Plus status messages.
OK. Let me finalize. I'll write i18n.py with all these keys.
Let me count: ~70 keys. That's manageable.
Now, structure of files:
client/i18n.py
python
"""Translations for client."""
import logging
log = logging.getLogger("tracker.i18n")

DEFAULT_LANG = "ru"
_current_lang = DEFAULT_LANG

SUPPORTED_LANGS = [
    {"code": "ru", "label": "Русский"},
    {"code": "en", "label": "English"},
]

TRANSLATIONS = {
    ... ~70 keys
}

def set_language(code):
    global _current_lang
    if code in [l["code"] for l in SUPPORTED_LANGS]:
        _current_lang = code
        log.info("Language set to %s", code)
        return True
    return False

def get_language():
    return _current_lang

def t(key):
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(_current_lang) or entry.get("ru") or key

def is_valid_lang(code):
    return code in [l["code"] for l in SUPPORTED_LANGS]
client/themes.py
python
"""Themes for client."""
import logging
log = logging.getLogger("tracker.themes")

SUPPORTED_THEMES = [
    {"code": "light", "label_key": "theme.light"},
    {"code": "dark", "label_key": "theme.dark"},
    {"code": "system", "label_key": "theme.system"},
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
QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555; border-radius: 4px;
    padding: 4px 6px;
}
QComboBox QAbstractItemView {
    background-color: #2b2b2b; color: #e0e0e0;
    selection-background-color: #4a4a4a;
}
QCheckBox { color: #e0e0e0; background: transparent; }
QGroupBox {
    color: #e0e0e0; border: 1px solid #555;
    border-radius: 4px; margin-top: 10px;
    padding-top: 8px;
}
QGroupBox::title { left: 10px; padding: 0 4px; background-color: #2b2b2b; }
QTabWidget::pane { border: 1px solid #555; background-color: #2b2b2b; }
QTabBar::tab {
    background-color: #3c3c3c; color: #e0e0e0;
    padding: 6px 14px; border: 1px solid #555;
    border-bottom: none; border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected { background-color: #2b2b2b; color: #ffffff; }
QMenu { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #555; }
QMenu::item:selected { background-color: #4a4a4a; }
QToolTip {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555; padding: 4px;
}
QMessageBox { background-color: #2b2b2b; }
QScrollBar:vertical {
    background-color: #2b2b2b; width: 12px;
}
QScrollBar::handle:vertical {
    background-color: #555; border-radius: 5px; min-height: 20px;
}
"""

def apply_theme(app, code):
    """Apply theme to QApplication. Returns True if applied."""
    if code == "dark":
        app.setStyleSheet(DARK_QSS)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", ""):
        app.setStyleSheet("")
        log.info("Applied %s theme", code or "light")
        return True
    return False
config.py additions
python
import json

CONFIG_FILE = BASE_DIR / "config.json"

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            _log.warning("Failed to read config.json: %s", e)
    return {}

def save_config(data: dict) -> None:
    try:
        CONFIG_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        _log.error("Failed to save config.json: %s", e)

def get_setting(key: str, default=None):
    return load_config().get(key, default)

def set_setting(key: str, value) -> None:
    data = load_config()
    data[key] = value
    save_config(data)
OK. Let me write the response now.
For i18n keys, let me be thorough. Also need keys for the reminder tab that we're keeping.
Let me finalize the i18n dictionary. I need:
Common:
btn.save, btn.close, btn.cancel, btn.yes, btn.no
common.error
Settings dialog:
settings.title
settings.tab.reminder, settings.tab.general, settings.tab.registration
Reminder tab:
reminder.source.personal
reminder.source.global
reminder.group.start
reminder.enabled
reminder.threshold
reminder.repeat
reminder.max_per_day
reminder.group.eod
reminder.eod_hour
reminder.eod_minute
reminder.eod_hour_hint (0 = выкл)
reminder.btn.save
reminder.btn.reset_to_global
reminder.btn.reset_to_global.tooltip
reminder.status.local_only
reminder.status.synced
reminder.status.server_refused
reminder.status.not_authorized
reminder.status.server_error
reminder.status.net_error
reminder.reset.confirm_title
reminder.reset.confirm_text
reminder.reset.not_registered
reminder.reset.not_linked
reminder.reset.unauth
reminder.reset.server_error
reminder.reset.success
reminder.reset.partial
General tab:
general.group.autostart
general.autostart
general.autostart.error
general.group.appearance
general.theme
general.theme.light
general.theme.dark
general.theme.system
general.theme.hint
general.group.language
general.lang
general.lang.ru
general.lang.en
general.lang.hint
general.lang.restart_title
general.lang.restart_text
general.group.connectivity
general.server_url
general.cert_fingerprint
general.cert_fingerprint.hint
general.btn.check_connection
general.conn.checking
general.conn.ok
general.conn.fail
general.conn.no_server
general.conn.saved
general.btn.save_server
Registration tab:
reg.group.info
reg.uid
reg.hostname
reg.server
reg.group.server
reg.server_url
reg.server_url.hint
reg.cert_fingerprint
reg.cert_fingerprint.hint
reg.bootstrap_token
reg.bootstrap_token.hint
reg.btn.save_server
reg.btn.check_connection
reg.reregister
reg.reregister.warn
reg.reregister.confirm_title
reg.reregister.confirm_text
reg.reregister.done_title
reg.reregister.done_text
reg.reregister.no_uid
reg.reregister.error
Tooltips (many)
OK that's about 90 keys. Let me write.
Actually, let me simplify and reduce. Not every status message needs a key - we can format them. But for i18n consistency, all UI strings should be keys.
Let me just write. I'll be pragmatic.
Actually, at this point I need to decide: is it better to give a complete dict in one script, or split?
Let me estimate: 90 keys ? 3 lines = ~280 lines just for TRANSLATIONS. Plus functions. Total ~330 lines. That's a lot for one here-string.
Let me split i18n.py into sections. Actually, since I need to give one file, let me do the here-string and hope it works. If not, we'll handle it.
Alternatively, use the "array of lines" approach:
powershell
$lines = [System.Collections.ArrayList]::new()
$lines.Add("line1") | Out-Null
$lines.Add("line2") | Out-Null
...
$content = $lines -join "`n"
[System.IO.File]::WriteAllText($path, $content, ...)
But escaping ' as '' is painful for so many lines.
Actually, here-string @'...'@ is the way. Let me just do it.
Let me also be smart about this: since we're going to have English translations too, I can make the file shorter by using a compact format.
Format 1:
python
TRANSLATIONS = {
    "key1": {"ru": "...", "en": "..."},
}
Format 2 (compact, one line per key):
python
_RU = {
    "key1": "...",
}
_EN = {
    "key1": "...",
}
Format 2 might be shorter in total. Let me use it.
Actually, Format 2 is more error prone (need to keep both dicts in sync). Let me stick with Format 1 but compact.
OK final decision: use Format 1, be compact.
Let me write.
Actually, I realize I should just try the here-string and if it fails we deal. Let me be optimistic.
Let me now write the full i18n.py file. I'll keep it under 150 lines by being economical.
Wait, I want to be pragmatic here. Let me give three scripts:
Script 1: i18n.py (here-string, ~150 lines)
Script 2: themes.py (here-string, ~70 lines)
Script 3: config.py patch (Python patcher, ~30 lines)
Then a fourth script to test.
Then next message: settings_dialog.py + main.py patch.
OK let me write.
Actually for the config.py patch, adding at the end is fine. Let me use a simple appender.
Let me write the response.
I need to be careful with Cyrillic in PowerShell. Single-quoted here-string should preserve it if saved as UTF-8. Let me use [System.Text.UTF8Encoding]::new($false) which is UTF-8 without BOM.
OK here we go.
One more consideration - the i18n.py keys might have some overlap with what we need. Let me also add tooltips i18n keys.
Let me actually structure i18n.py by section for readability:
python
TRANSLATIONS = {
    # ---------- Common ----------
    "btn.save": {"ru": "Сохранить", "en": "Save"},
    "btn.close": {"ru": "Закрыть", "en": "Close"},
    "btn.cancel": {"ru": "Отмена", "en": "Cancel"},
    "btn.yes": {"ru": "Да", "en": "Yes"},
    "btn.no": {"ru": "Нет", "en": "No"},
    
    # ---------- Settings dialog ----------
    "settings.title": {"ru": "Настройки Tracker", "en": "Tracker Settings"},
    ...
}
OK let me write it out. I'll aim for completeness but keep it tight.
Also I realize I should add tooltips for various elements. Let me add hint keys.
Final list (let me be quick):
Common (5):
btn.save, btn.close, btn.cancel, btn.yes, btn.no
Settings (5):
settings.title, settings.tab.reminder, settings.tab.general, settings.tab.registration, settings.close
Reminder (20):
reminder.source.personal, reminder.source.global
reminder.group.start, reminder.enabled
reminder.threshold, reminder.threshold.hint
reminder.repeat, reminder.repeat.hint
reminder.max_per_day, reminder.max_per_day.hint
reminder.group.eod
reminder.eod_hour, reminder.eod_minute, reminder.eod_hour.hint
reminder.btn.save, reminder.btn.reset_to_global, reminder.btn.reset_to_global.tooltip
reminder.reset.confirm_title, reminder.reset.confirm_text
reminder.status.local_only, reminder.status.synced
reminder.status.server_refused, reminder.status.not_authorized
reminder.status.server_error, reminder.status.net_error
reminder.reset.not_registered, reminder.reset.not_linked
reminder.reset.unauth, reminder.reset.server_error
reminder.reset.success, reminder.reset.partial
General (25):
general.group.autostart, general.autostart, general.autostart.hint
general.autostart.error
general.group.appearance, general.theme, general.theme.hint
general.theme.light, general.theme.dark, general.theme.system
general.group.language, general.lang, general.lang.hint
general.lang.ru, general.lang.en
general.lang.restart_title, general.lang.restart_text
general.group.connectivity
general.server_url, general.server_url.hint
general.cert_fingerprint, general.cert_fingerprint.hint
general.btn.check_connection, general.btn.save_server
general.conn.checking, general.conn.ok, general.conn.fail
general.conn.no_server, general.conn.saved
general.group.notifications
general.notif.offline, general.notif.offline.hint
general.notif.eod, general.notif.eod.hint
Registration (20):
reg.group.info, reg.uid, reg.hostname, reg.server
reg.group.server
reg.server_url, reg.server_url.hint
reg.cert_fingerprint, reg.cert_fingerprint.hint
reg.bootstrap_token, reg.bootstrap_token.hint
reg.btn.save_server, reg.btn.check_connection
reg.server.saved, reg.server.checking, reg.server.ok, reg.server.fail
reg.reregister
reg.reregister.warn
reg.reregister.confirm_title, reg.reregister.confirm_text
reg.reregister.done_title, reg.reregister.done_text
reg.reregister.no_uid, reg.reregister.error
Total: ~75 keys. OK.
Let me write.
Hmm, I realize settings_dialog.py is really the big rewrite. Let me think about whether to give it now or later.
Given that the user provided both files and wants to start Sprint A now, let me give a comprehensive response:
Intro
Script 1: i18n.py
Script 2: themes.py
Script 3: config.py additions
Script 4: settings_dialog.py rewrite (big)
Script 5: main.py patch
Test
But that's a LOT. Let me split: this message will do i18n.py, themes.py, config.py. Next message will do settings_dialog.py and main.py.
Actually, let me combine. The user is eager. I'll give everything and warn about the big here-strings.
OK let me write the response now.
Let me finalize the settings_dialog.py structure:
python
# Settings dialog with 3 tabs: reminder, general, registration

from . import db, http_client, reminder_settings, i18n, themes
from .i18n import t
from .config import BASE_DIR, SERVER_URL, SSL_CA_BUNDLE, PINNED_CERT_SHA256, get_setting, set_setting

class ReminderTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build()
        self._load()
    
    def _build(self):
        # Use t() for all labels
        ...
    
    def _load(self):
        ...
    
    def _on_save(self):
        ...

class GeneralTab(QWidget):
    def __init__(self):
        ...
    
    def _build(self):
        # theme combobox
        # lang combobox  
        # autostart checkbox
        # notifications checkboxes
        # server_url field + check button
    
    def _load(self):
        # Load from config.json
    
    def _on_theme_changed(self, idx):
        code = "light"/"dark"/"system"
        themes.apply_theme(QApplication.instance(), code)
        set_setting("theme", code)
    
    def _on_lang_changed(self, idx):
        code = "ru"/"en"
        i18n.set_language(code)
        set_setting("language", code)
        # Prompt restart
        reply = QMessageBox.question(...)
        if reply: restart app
    
    def _on_autostart_changed(self, state):
        # Same as before
    
    def _on_save_server(self):
        # Save new server_url
        set_setting("server_url", self.edit_server_url.text().strip())
        ...

class RegistrationTab(QWidget):
    def __init__(self):
        ...
    
    def _build(self):
        # Info section
        # New: URL + fingerprint + token + check button
        # Reregister
    
    def _on_check_connection(self):
        # ping /api/v1/version
OK. There's a lot.
Let me finalize and write. I'll try to keep settings_dialog.py under 500 lines. If it's too big for one here-string, I'll split.
Actually, I just realized - if there's a problem with big here-strings, I should minimize the risk by using a Python script to write the file. Like:
powershell
$python_writer = @'
import sys
with open(r"D:\target.py", "w", encoding="utf-8") as f:
    f.write(r"""FILE CONTENT""")
'@
But then the content can't have """ inside. That's OK if we use Python properly.
Actually there's a cleaner way: use base64.
powershell
$base64_content = "base64 string here"
$bytes = [System.Convert]::FromBase64String($base64_content)
[System.IO.File]::WriteAllBytes("D:\target.py", $bytes)
But I'd have to base64-encode the content myself. Can I? Yes, but it's error prone.
OK, simplest approach: use here-string, split if > 100 lines.
Let me just do i18n.py (which is ~120 lines) with a here-string. If it works, great.
Actually let me structure i18n.py to be compact - use list of tuples:
python
_KEYS = [
    ("btn.save", "Сохранить", "Save"),
    ("btn.close", "Закрыть", "Close"),
    ...
]
TRANSLATIONS = {k: {"ru": ru, "en": en} for k, ru, en in _KEYS}
This is more compact! ~75 keys ? 1 line = 75 lines instead of 225.
But I like the explicit dict format for readability. Hmm. Let me use the compact tuple format - it's pragmatic.
Actually, let me use the explicit dict format. Readability matters for maintenance. If here-string is a problem, we'll deal.
Let me write it. I'll be economical with keys.
Actually, I realize I'm overthinking. Let me just write the file and stop optimizing.
Final i18n.py structure:
python
"""i18n for Tracker client."""

import logging
log = logging.getLogger("tracker.i18n")

DEFAULT_LANG = "ru"
_current_lang = DEFAULT_LANG

SUPPORTED_LANGS = [
    {"code": "ru", "label": "Русский"},
    {"code": "en", "label": "English"},
]

TRANSLATIONS = {
    # --- Common ---
    "btn.save": {"ru": "Сохранить", "en": "Save"},
    ...
}

def set_language(code): ...
def get_language(): ...
def t(key): ...
def is_valid_lang(code): ...
OK let me write.
For the config.py patch, I'll add at the very end:
python
import json as _json

CONFIG_FILE = BASE_DIR / "config.json"

def load_config() -> dict:
    ...

def save_config(data: dict) -> None:
    ...

def get_setting(key, default=None):
    return load_config().get(key, default)

def set_setting(key, value):
    data = load_config()
    data[key] = value
    save_config(data)

# Текущие значения (читаются при старте)
LANGUAGE = get_setting("language", "ru")
THEME = get_setting("theme", "light")
Actually, LANGUAGE/THEME at module level won't update. Let me just expose the functions.
OK writing now.
Let me be practical about the response length. The chat is getting long. Let me focus and deliver.
Response structure:
Привет! Вижу контекст. Начинаем Спринт A.
Что делаем сейчас (3 файла):
client/i18n.py — новая инфраструктура переводов
client/themes.py — QSS-темы
client/config.py — добавим функции для работы с config.json
Потом (следующее сообщение):
settings_dialog.py — переписываем с новыми полями
main.py — применяем тему/язык при старте
Script 1: client/i18n.py
Script 2: client/themes.py
Script 3: config.py patch
Test
Let me write.
Also, user emphasized tooltips. Let me add tooltips to key elements.
For i18n keys with hints, add .hint suffix.
OK, writing now. Let me be decisive.
Final decision: I'll write with here-strings, no longer than ~120 lines each. Should work.
For i18n.py, let me use compact format with comments. ~110 lines.
For themes.py, ~60 lines.
For config.py, use Python patcher (small).
Let me write.
Отлично, файлы получил. Разбираю.
Что вижу в settings_dialog.py:
Вкладка «Напоминание» — полностью функциональная, останется как есть + i18n
Вкладка «Общие» — есть автозапуск, но тема/язык — заглушки («скоро»). Надо реализовать.
Вкладка «Регистрация» — показывает UID/hostname/server + перерегистрация. Надо расширить полями URL, отпечатка сертификата, bootstrap-токена и кнопкой «Проверить соединение».
Что вижу в config.py:
Читает .env, дефолты хорошие, но нет сохранения настроек (язык/тема сохранятся только в config.json вручную).
План на этот чат (Спринт A):
client/i18n.py — инфраструктура переводов RU/EN
client/themes.py — QSS-темы (light/dark/system)
Патч config.py — функции get_setting/set_setting
Переписать settings_dialog.py — новая вкладка «Общие» + расширенная «Регистрация» + i18n + тултипы
Патч main.py — применяем тему/язык при старте
Тест
Учитывая твой опыт с большими here-string'ами в PowerShell, я разбиваю работу на две порции. В этой порции — три файла (i18n, themes, config), они небольшие. В следующей — settings_dialog.py (большой) и патч main.py.
________________________________________
Скрипт 1 — client/i18n.py
Помещаем в папку client/. Файл ~100 строк.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$content = @'
# ============================================================
# Интернационализация клиента Tracker (RU/EN)
# ============================================================
# Без внешних библиотек. Простой словарь + функция t(key).
#
# Как пользоваться в коде:
#   from .i18n import t
#   label = QLabel(t("settings.title"))
#
# Как добавить перевод:
#   1. Придумать ключ по схеме "раздел.элемент" (например "settings.title")
#   2. Добавить строку в TRANSLATIONS с обоими языками
#   3. Использовать через t("settings.title")
#
# Что НЕ переводится:
#   - ФИО, hostname, UID, IP, названия отделов
#   - Имена приложений в отчётах (PyCharm, Chrome)
#   - Пути к файлам
# ============================================================

import logging

log = logging.getLogger("tracker.i18n")

DEFAULT_LANG = "ru"
_current_lang = DEFAULT_LANG

SUPPORTED_LANGS = [
    {"code": "ru", "label": "Русский"},
    {"code": "en", "label": "English"},
]


# ============================================================
# Словарь переводов
