<!-- Часть 878 из 1409 -->
# После всех настроек:
*Хлебные крошки:* После всех настроек:

[◀ Registration tab](877_Registration_tab.md) | [Оглавление](00_BCE_INDEX.md) | [PowerShell script that uses Python itself to write the file ▶](879_PowerShell_script_that_uses_Python_itself_to_write_the_file.md)

---

# После всех настроек:
LANGUAGE = get_setting("language", "ru")
THEME = get_setting("theme", "light")
Wait, but config.py is imported at module load. If language is read at import time, we can't change it dynamically.
Better: read language at import, but have a way to reload. Or read language dynamically via function.
Approach:
i18n.py has set_language(lang) and t(key) that reads current global
main.py on startup: from .config import get_setting; i18n.set_language(get_setting("language", "ru"))
On change: i18n.set_language(new_lang) + emit signal
OK let me write.
For theme similar:
themes.py has apply_theme(app, theme_name)
main.py on startup applies
For language change without restart: emit signal. SettingsDialog rebuild itself. MainWindow rebuild - complex. Let me use the "restart prompt" approach for main window, but settings dialog retranslates itself.
Actually let me be brave and just do the retranslateUi approach for settings dialog, and for MainWindow do a rebuild of the window (close + new).
Hmm, that's risky. Let me do this:
Option A (simple): Language change ? "Для применения требуется перезапуск. Перезапустить сейчас?" ? restart via subprocess.
Option B (complex): Retranslate everything live.
Let me go with hybrid:
SettingsDialog retranslates itself immediately
MainWindow: shows prompt. If yes ? restart app.
This is honest and works.
For theme: instant switch, no restart needed.
OK let me write.
Actually, I realize I should focus on making it clean and working first. Let me start:
Script 1: client/i18n.py
python
TRANSLATIONS = {
    "app.title": {"ru": "Tracker", "en": "Tracker"},
    "settings.title": {"ru": "Настройки Tracker", "en": "Tracker Settings"},
    ...
}

DEFAULT_LANG = "ru"
_current = DEFAULT_LANG

def set_language(lang):
    global _current
    if lang in ("ru", "en"):
        _current = lang

def get_language():
    return _current

def t(key):
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(_current) or entry.get("ru") or key
Script 2: client/themes.py
python
LIGHT_QSS = ""
DARK_QSS = """
QWidget { background-color: #2b2b2b; color: #e0e0e0; }
QTabWidget::pane { border: 1px solid #444; }
...
"""

def apply_theme(app, name):
    from PyQt6.QtWidgets import QApplication
    if name == "dark":
        app.setStyleSheet(DARK_QSS)
    elif name == "system":
        # определить по палитре ОС? Сложно. Используем светлую.
        app.setStyleSheet("")
    else:
        app.setStyleSheet("")
OK let me write the full scripts.
Let me start writing. I'll try to keep each script self-contained.
For PowerShell and here-strings, I need to be careful. Let me use Python-patchers where feasible.
Actually let me try this approach: write a small PowerShell script that creates a .py file from a here-string. If the here-string is small (< 50 lines), it should work.
Let me break scripts:
Script 1: create client/i18n.py (~80 lines) - here-string, ok
Script 2: create client/themes.py (~60 lines) - here-string, ok
Script 3: patch config.py - small addition, easy
Script 4: rewrite settings_dialog.py (~500 lines) - HERE-STRING WILL BE BIG. Better use Python patcher approach or write in parts.
Script 5: patch main.py - small
Hmm, settings_dialog.py rewrite is the big one. Let me split:
Write i18n keys first (in i18n.py)
Write themes (themes.py)
Write a patch that modifies settings_dialog.py to add new fields/tabs
Actually rewriting is cleaner because we need to add i18n to all texts. Let me rewrite but with a helper: write the file in chunks.
Actually, I know from the previous chat that PowerShell here-strings with >30 lines had issues. Let me try writing it via base64 or chunked approach.
Or: use Set-Content with an array of lines:
powershell
$lines = @(
    "line1",
    "line2",
    ...
)
$lines | Out-File -Encoding utf8 file.py
This avoids here-string issues. But escaping is a pain.
Alternative: use a Python script that writes the file. Like:
powershell
$py_writer = @'
content = """..."""
with open(r"D:\...", "w", encoding="utf-8") as f:
    f.write(content)
'@
But then the content contains quotes...
OK, let me just use a straightforward here-string and hope it works. If user has issues, we'll split.
Actually, in the previous audit, user noted: "PowerShell here-string ломается на больших блоках. Проси ассистента: Давать скрипты через Python-патчеры (короткие, с io.open(...,encoding='utf-8')) Или через @() массивы строк + Out-File (как в последнем скрипте) Не использовать @'...'@ для блоков >30 строк"
So user explicitly asked to avoid here-strings > 30 lines. Let me use the array approach.
For a Python file, I can do:
powershell
$lines = @(
    '# comment',
    'import logging',
    '',
    'def foo():',
    '    pass',
)
$content = $lines -join "`n"
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
But then any ' inside needs escaping as ''. And $ needs escaping as `$ if in double-quoted strings, but I'm using single-quoted so no $ interpolation.
Actually in single-quoted PowerShell strings, $ is literal. Only ' needs to be escaped as ''.
For a Python file with lots of strings, that's a lot of escaping. Painful.
Alternative: use single-quoted here-string @'...'@ - it preserves everything literally. The only issue is if content contains the closing sequence '@ at line start.
Let me try here-string approach but split the file into 2-3 parts if needed.
Or: use a Python writer script:
powershell
$script = @'
import sys
content = r'''...file content here...'''
with open(r"D:\target", "w", encoding="utf-8") as f:
    f.write(content)
'@
But then the content can't contain '''. That's usually fine for Python.
OK let me try the here-string approach first. If it doesn't work, we can split.
Actually, let me look at the audit again: "PowerShell here-string ломается на больших блоках". So the issue is not the size per se, but something else. Maybe the copy-paste from chat gives line ending issues.
Let me just use here-strings and be careful about size (< 100 lines each). Split into multiple scripts if needed.
OK let me start writing.
Actually I'll take a different approach. Since settings_dialog.py needs a full rewrite, let me write it as a Python file using the JSON-based writer. Like:
powershell
