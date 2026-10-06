<!-- Часть 387 из 1409 -->
# client/registration_dialog.py
*Хлебные крошки:* client/registration_dialog.py

[◀ Обновляем sync.py — сохраняем last_sync_ts после успешной синхронизации](386_Obnovlyaem_sync_py_sohranyaem_last_sync_ts_posle_uspeshnoy_sinhronizatsii.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](388_part.md)

---

# client/registration_dialog.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QHBoxLayout)
import logging
from . import registration

log = logging.getLogger("tracker.reg_dialog")


class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация Tracker")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        title = QLabel("?? Регистрация компьютера в системе Трекер")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        
        info = QLabel(
            "Для регистрации компьютера введите одноразовый токен, "
            "полученный у администратора.\n\n"
            "После регистрации токен станет недействительным, а данные "
            "начнут отправляться на сервер автоматически."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #555; margin-bottom: 10px;")
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Вставьте bootstrap-токен сюда")
        self.token_input.setMinimumHeight(36)
        self.token_input.setStyleSheet("font-size: 14px; padding: 4px;")
        self.token_input.returnPressed.connect(self._register)
        
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #dc3545; margin-top: 6px;")
        
        self.btn_register = QPushButton("Зарегистрировать")
        self.btn_register.setMinimumHeight(40)
        self.btn_register.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "border: none; border-radius: 6px; font-size: 14px;"
        )
        self.btn_register.clicked.connect(self._register)
        
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(self.reject)
        
        btns = QHBoxLayout()
        btns.addWidget(self.btn_register)
        btns.addWidget(btn_cancel)
        
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(self.token_input)
        layout.addWidget(self.status_label)
        layout.addLayout(btns)
        self.setLayout(layout)
    
    def _register(self):
        token = self.token_input.text().strip()
        if not token:
            self.status_label.setText("Введите токен")
            return
        
        self.btn_register.setEnabled(False)
        self.btn_register.setText("Регистрация…")
        self.status_label.setText("")
        
        try:
            registration.register_with_token(token)
            QMessageBox.information(self, "Успех", 
                "Компьютер успешно зарегистрирован!\n\n"
                "Нажмите «Начать работу», чтобы приступить.")
            self.accept()
        except Exception as e:
            log.exception("Registration failed")
            self.status_label.setText(f"Ошибка: {e}")
            self.btn_register.setEnabled(True)
            self.btn_register.setText("Зарегистрировать")
Now I need registration.register_with_token(token) function. Let me modify registration.py:
python
def register_with_token(token: str) -> str:
    """Регистрирует ПК с явно переданным токеном. Возвращает computer_uid."""
    # Проверяем, не зарегистрирован ли уже
    uid = _safe_keyring_get("computer_uid")
    secret = _safe_keyring_get("client_secret")
    if uid and secret:
        return uid
    
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
    log.info("Registered as %s (secret_version=%s)", uid, data.get("secret_version"))
    return uid
And I need to update ensure_registered() to be stricter - it should NOT silently work if not registered, but instead raise a specific exception that tells us to show the dialog.
Actually, let me make it cleaner:
python
def is_registered() -> bool:
    uid = _safe_keyring_get("computer_uid")
    secret = _safe_keyring_get("client_secret")
    return bool(uid and secret)


def ensure_registered():
    """Старая функция - для обратной совместимости. 
    Проверяет регистрацию; если нет - падает с RuntimeError."""
    if is_registered():
        return _safe_keyring_get("computer_uid")
    raise RuntimeError("Not registered")
Then in main.py:
python
def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Проверяем регистрацию
    if not registration.is_registered():
        dlg = RegistrationDialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return  # пользователь отказался
        if not registration.is_registered():
            return
    
    win = MainWindow()
    win.install_signal_handlers()
    win.show()
    sys.exit(app.exec())
And in MainWindow._start() we remove the ensure_registered() call because we've done it already.
Also remove the "Active window" row from panel.
This is good. Let me now write the full PowerShell scripts.
Also, I should think about the user experience: when the EXE is distributed, it should have TRACKER_SERVER_URL configured. Currently it reads from .env. For a distributed EXE, we need the URL baked in. Two options:
Hardcode in config.py (compile-time)
Allow user to enter in dialog
For simplicity, I'll:
Bake the URL in as default in config.py
Keep .env override for dev
In the dialog, don't ask for URL (it's admin's job to set it in the build)
That's cleaner. Let me not overcomplicate.
Now let me write the response. I'll:
Explain the plan briefly
Provide registration.py changes
Provide registration_dialog.py (new file)
Provide main.py changes
Explain how to test
I'll also mention what comes next (admin filters etc.).
Let me not do everything in this response - focus on the client registration wizard since that's what the user emphasized with "Давай начнём настраивать клиентский интерфейс". I'll outline the rest.
Actually re-reading the user's message, they say "Давай начнём настраивать" = "Let's START setting up". So they want to focus on this first. Good. I'll do the client wizard first and end with "next we'll do X".
Let me write this now.
One more thing - when distributing EXE, the bootstrap token needs to be typed. So the wizard must be user-friendly. Let me make it nice.
Actually, I could also let the user paste a token, or upload a bootstrap.txt file. Let me add a "Загрузить из файла" button as a convenience.
Hmm, keep it simple for now. Just text field.
Let me also think about the initial screen: it would be nicer to have a welcome window on first run that says "Регистрация Tracker" with clear instructions. Then after registration, the main window appears.
Let me write:
client/registration_dialog.py - full QDialog with nice styling
Then update client/main.py to check on startup.
Let me also add a settings dialog for changing the token if needed. Nah, keep it simple.
Let me also make sure the IP/URL is configurable in the build. For EXE distribution, the admin would set TRACKER_SERVER_URL in client/.env or hardcode in config.py before building.
Now writing the response. I'll keep it focused and clean.
Actually, I need to be careful: the registration function currently is in registration.py. Let me structure:
registration.py gets:
is_registered() -> bool (new)
register_with_token(token: str) -> str (new)
ensure_registered() (kept for compatibility, but stricter)
_safe_keyring_get/set (existing)
Let me write clean full versions of each file.
Given length constraints, let me write the files cleanly. I'll produce:
Full client/registration.py
New client/registration_dialog.py
Full client/main.py (with Active window removed, dialog integration)
Then in the message text, list what we'll do next.
Let me actually do a good job on main.py since I'm rewriting the whole thing anyway. Let me remove "Active window" and integrate the registration flow cleanly.
OK writing now.
Actually, I realize I should be pragmatic. The user has a lot of pending requests. Let me:
Focus this response on CLIENT registration + remove Active window (as user said "Давай начнём")
Include at the bottom a clear plan for what I'll do in the next few responses
Let me not do the admin stuff in this response to keep it manageable.
Writing now.
Клиентский интерфейс с регистрацией
Отличный план. Разберём по приоритетам — сначала клиент, потому что это критично для распространения .exe. Админские фильтры, XLSX-формат, календарь, heartbeat, PDF и массовая привязка — сделаем в следующих сообщениях.
________________________________________
Что делаем сейчас
Убираем «Активное окно» из панели клиента — не работает, нечего место занимать.
Создаём диалог регистрации — при первом запуске клиент покажет окно с полем для ввода bootstrap-токена. После успешной регистрации — обычное окно.
Меняем main.py — при старте проверяем регистрацию, если нет — показываем диалог.
Меняем registration.py — добавляем is_registered() и register_with_token(token).
Как это будет работать после сборки .exe:
Пользователь получает TrackerSetup.exe + отдельно токен (или админ вставляет его в инсталлятор).
Запускает ? видит диалог «Введите bootstrap-токен» ? вводит ? регистрируется ? работает.
Токен после этого сгорает, повторно не нужен.
________________________________________
Скрипт 1 — client/registration.py (полная замена)
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

$registration_py = @'
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


