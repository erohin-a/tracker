<!-- Часть 999 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Задаются через objectName у виджета.](998_Zadayutsya_cherez_objectName_u_vidzheta.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ключевых маркеров ▶](1000_Proverka_klyuchevyh_markerov.md)

---

# ============================================================

_CUSTOM_LIGHT = """
QFrame#infoPanel {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { color: #333333; background: transparent; }
QFrame#infoPanel QLabel[role="title"] { color: #6c757d; }

QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:pressed { background-color: #218838; }
QPushButton#btnStart:disabled { background-color: #c0c0c0; color: #888888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:pressed { background-color: #c82333; }
QPushButton#btnStop:disabled { background-color: #c0c0c0; color: #888888; }
"""

_CUSTOM_DARK = """
/* ---------- Главное окно ---------- */
QMainWindow { background-color: #2b2b2b; }
QMainWindow > QWidget { background-color: #2b2b2b; }
QDialog { background-color: #2b2b2b; }

QWidget { background-color: #2b2b2b; color: #e0e0e0; }
QLabel { color: #e0e0e0; background: transparent; }
QLabel[role="title"] { color: #a0a0a0; }

QPushButton {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555555; border-radius: 4px;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #4a4a4a; }
QPushButton:pressed { background-color: #555555; }
QPushButton:disabled { color: #777777; background-color: #333333; }

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
QPlainTextEdit, QTextEdit {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555555; border-radius: 4px;
    padding: 4px 6px;
}
QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {
    background-color: #333333; color: #777777;
}
QComboBox QAbstractItemView {
    background-color: #2b2b2b; color: #e0e0e0;
    selection-background-color: #4a4a4a;
    border: 1px solid #555555;
}

QCheckBox { color: #e0e0e0; background: transparent; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #666666; border-radius: 3px;
    background-color: #3c3c3c;
}
QCheckBox::indicator:checked {
    background-color: #4a90e2; border-color: #4a90e2;
}

QGroupBox {
    color: #e0e0e0;
    border: 1px solid #555555; border-radius: 4px;
    margin-top: 12px; padding-top: 10px;
}
QGroupBox::title {
    left: 10px; padding: 0 4px;
    background-color: #2b2b2b; color: #e0e0e0;
}

QTabWidget::pane { border: 1px solid #555555; background-color: #2b2b2b; }
QTabBar::tab {
    background-color: #3c3c3c; color: #e0e0e0;
    padding: 6px 14px; border: 1px solid #555555;
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
    border: 1px solid #555555;
}
QMenu::item { padding: 6px 20px; }
QMenu::item:selected { background-color: #4a4a4a; }

QToolTip {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555555; padding: 4px 6px;
}

QMessageBox { background-color: #2b2b2b; }

QScrollBar:vertical {
    background-color: #2b2b2b; width: 12px;
    border: none; margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #555555; border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #666666; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0; background: none;
}
QScrollBar:horizontal {
    background-color: #2b2b2b; height: 12px;
    border: none; margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: #555555; border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background-color: #666666; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0; background: none;
}

/* ---------- Панель информации в главном окне ---------- */
QFrame#infoPanel {
    background-color: #3a3a3a;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { color: #e0e0e0; background: transparent; }
QFrame#infoPanel QLabel[role="title"] { color: #a0a0a0; }

/* ---------- Кнопки старт/стоп ---------- */
QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:pressed { background-color: #218838; }
QPushButton#btnStart:disabled { background-color: #404040; color: #888888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:pressed { background-color: #c82333; }
QPushButton#btnStop:disabled { background-color: #404040; color: #888888; }
"""


def apply_theme(app, code: str) -> bool:
    """
    Применяет тему к приложению.
    code: "light" | "dark" | "system"
    """
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(_CUSTOM_DARK)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet(_CUSTOM_LIGHT)
        log.info("Applied %s theme", code or "light")
        return True
    else:
        log.warning("Unknown theme: %s, using light", code)
        app.setStyleSheet(_CUSTOM_LIGHT)
        return False


def is_valid_theme(code: str) -> bool:
    return code in [t["code"] for t in SUPPORTED_THEMES]
'@

[System.IO.File]::WriteAllText("D:\tracker\client\themes.py", $content, [System.Text.UTF8Encoding]::new($false))

Write-Host "OK: themes.py переписан ($($content.Length) символов)" -ForegroundColor Green

python -c "import ast; ast.parse(open(r'D:\tracker\client\themes.py', encoding='utf-8').read()); print('SYNTAX OK')"

