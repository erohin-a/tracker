<!-- Часть 883 из 1409 -->
# Registration tab
*Хлебные крошки:* Registration tab

[◀ General tab](882_General_tab.md) | [Оглавление](00_BCE_INDEX.md) | [Settings dialog with 3 tabs: reminder, general, registration ▶](884_Settings_dialog_with_3_tabs_reminder_general_registration.md)

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
