<!-- Часть 884 из 1409 -->
# Settings dialog with 3 tabs: reminder, general, registration
*Хлебные крошки:* Settings dialog with 3 tabs: reminder, general, registration

[◀ Registration tab](883_Registration_tab.md) | [Оглавление](00_BCE_INDEX.md) | [Текущие значения (читаются при старте) ▶](885_Tekuschie_znacheniya_chitayutsya_pri_starte.md)

---

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

