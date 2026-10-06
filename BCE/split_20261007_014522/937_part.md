<!-- Часть 937 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 3. Регистрация  — UID, hostname, сервер, отпечаток, bootstrap-токен](936_3_Registratsiya_UID_hostname_server_otpechatok_bootstrap_token.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](938_part.md)

---

# ============================================================

import json
import logging
import socket

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget,
)

from . import db, http_client, reminder_settings, themes
from .autostart import set_autostart
from .config import (
    BASE_DIR,
    get_cert_fingerprint,
    get_language_code,
    get_server_url,
    get_setting,
    get_theme_code,
    set_setting,
)
from .i18n import SUPPORTED_LANGS, get_language, set_language, t
from .registration import get_computer_uid

log = logging.getLogger("tracker.settings_dialog")


def _hint(text_key: str) -> QLabel:
    """Возвращает маленькую метку ? с подсказкой из i18n."""
    lbl = QLabel("?")
    lbl.setToolTip(t(text_key))
    lbl.setStyleSheet("color: #8a94a6; margin-left: 3px;")
    lbl.setCursor(Qt.CursorShape.WhatsThisCursor)
    return lbl


def _label_with_hint(text_key: str, hint_key: str) -> QWidget:
    """Строка: текст + ? с тултипом. Для вставки в QFormLayout."""
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(2)
    h.addWidget(QLabel(t(text_key)))
    h.addWidget(_hint(hint_key))
    h.addStretch()
    return w


