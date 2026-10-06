<!-- Часть 915 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ themes.apply_theme(QApplication.instance(), "dark")](914_themes_apply_themeQApplication_instance_dark.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](916_part.md)

---

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

