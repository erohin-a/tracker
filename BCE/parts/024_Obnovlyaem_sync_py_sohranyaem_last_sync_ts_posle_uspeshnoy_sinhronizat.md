# Обновляем sync.py — сохраняем last_sync_ts после успешной синхронизации

*Часть 24 из 100. Источник: `BCE.md`.*

[◀ employees.html — с отделами и вкладками Активные/Уволенные](023_employees_html_s_otdelami_i_vkladkami_Aktivnye_Uvolennye.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](025_part.md)

---

# Обновляем sync.py — сохраняем last_sync_ts после успешной синхронизации
$syncPath = "$clientDir\sync.py"
$syncContent = [System.IO.File]::ReadAllText($syncPath, [System.Text.UTF8Encoding]::new($false))

if (-not $syncContent.Contains("last_sync_ts")) {
    $syncContent = $syncContent.Replace(
        "        self.synced.emit(len(accepted))`n        return True",
        "        if accepted:`n            try:`n                from datetime import datetime, timezone as _tz`n                db.set_meta('last_sync_ts', datetime.now(_tz.utc).isoformat())`n            except Exception:`n                pass`n        self.synced.emit(len(accepted))`n        return True"
    )
    [System.IO.File]::WriteAllText($syncPath, $syncContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  sync.py сохраняет last_sync_ts" -ForegroundColor Green
} else {
    Write-Host "  sync.py уже пропатчен" -ForegroundColor Yellow
}
python -c "import ast; ast.parse(open(r'$syncPath', encoding='utf-8').read()); print('  sync.py SYNTAX OK')"
________________________________________
Что делать после запуска
Запустить скрипты 1 ? 2 ? 3 ? 4 ? 5 ? 6 по порядку.
Открыть https://localhost/admin/settings — увидите 8 настроек (отчёты + клиенты).
Открыть https://localhost/admin/departments — создать пару отделов.
Открыть /admin/employees — вкладки «Активные» / «Уволенные» / «Все».
Открыть /admin/reports — сотрудники выбираются мультивыбором (Ctrl+клик), есть фильтр по отделу.
Сформировать XLSX — длительности должны быть в формате [ЧЧ]:ММ:СС, дата — ДД.ММ.ГГГГ.
Перезапустить клиент: cd D:\tracker; client\.venv\Scripts\Activate.ps1; python -m client.main — на панели появится время старта в локальном поясе, счётчик, статус сервера, очередь, последняя синхронизация.
________________________________________
Что осталось для следующей сессии
Из моих предложений — самое ценное:
Heartbeat-эндпоинт — колонка «Онлайн/Оффлайн» на дашборде. 20 минут работы.
Опоздания — сравнение старта сессии с workday_start_hour.
Плановые часы на месяц — сравнение «факт vs норма» в отчёте по сотрудникам.
PDF-отчёт — reportlab, шрифт с кириллицей.
Массовая привязка ПК — загрузка CSV «hostname ? ФИО».
Telegram-уведомления — если ПК офлайн > 30 мин.
Скажите, что делаем следующим — выдам такой же готовый код.
в админке в отчётах в фильтрах Отдел добавить возможность добавить возможность выбора нескольких отделов как и в сотрудниках. когда выбираем несколько отделов, в фильтре сотрудники сразу отфильтровываются и остаются только те которые входят в отдел. В фильтре компьютер тоже добавить возможность выбрать несколько. попробуй реализовать поиск в фильтрах. В XLSX отчётах убери столбец Группа и столбец и Аварийный. Добавь отдельно столбцы с форматом дата год (пример 2026) месяц (пример Сентябрь) число (пример 17) В отчётах онлайн нужно сделать возможность сворачивать до месяца. (когда будет 50 сотрудников и в сентябре 22 сотрудника будет очень много строчек и будет не читабельно) Также необходимо подсвечивать дни недели особенно субботы воскресенья возможность считать их или не считать. А может быть в настройках создать календарь рабочие не рабочие дни и ручками прям пройти на год в перед и проставить как считаешь? Как лучше поступить? Делаем твои предложения Heartbeat-эндпоинт — колонка «Онлайн/Оффлайн» на дашборде. 20 минут работы. Массовая привязка ПК — загрузка CSV «hostname ? ФИО». PDF-отчёт — reportlab, шрифт с кириллицей. В клиентской части не заработало Активное окно. давай его уберём. Давай начнём настраивать клиентский интерфейс что бы в нём проводить регистрацию. что бы в дальнейшем отправить Exe он его запустил зарегистрировал свой компьютер без всяких лишних манипуляций
The user is asking for a lot. Let me organize this carefully. The tasks are:
Admin reports filters:
Multiple departments selection (like employees)
When multiple departments selected, filter employees in the employee filter to only those in those departments
Multiple computers selection
Search in filters
XLSX reports:
Remove "Группа" column
Remove "Аварийный" column
Add date format columns: year (2026), month (Сентябрь), day (17)
Also make date in DMY format that Excel understands
Online reports (HTML):
Ability to collapse to month level (when 50 employees x 22 days = too many rows)
Weekend highlighting:
Highlight Saturday/Sunday
Ability to count or not count them
Better: calendar in settings where admin can mark working/non-working days for the year
Do the proposals:
Heartbeat endpoint + online/offline column on dashboard
Bulk PC assignment via CSV
PDF report with reportlab + Cyrillic
Client:
Remove "Active window" from client panel (didn't work)
Add registration wizard to client interface - so we can distribute EXE and user just runs it and registers
This is a lot. Let me think about the best approach. The user has been asking me to write full PowerShell scripts to replace files. That's been working well. But this is a huge amount of code. Let me break it into chunks.
Given the complexity, I should:
First address the client-side registration interface (task 6) - most important for distributing EXE
Remove Active window from client
Then admin filters (1, 2, 3, 4)
Then heartbeat, bulk PC, PDF
Finally weekend calendar
Actually, let me think about priority. The user says "Давай начнём настраивать клиентский интерфейс что бы в нём проводить регистрацию. что бы в дальнейшем отправить Exe он его запустил зарегистрировал свой компьютер без всяких лишних манипуляций"
This is important because currently client requires bootstrap.txt file to be pre-placed. For distributing as EXE, we need a wizard.
Let me structure my response:
Part 1 (this response): Client registration wizard + remove active window
Part 2 (next response): Admin reports filters
Part 3: XLSX changes + month collapsing + weekend highlighting + calendar
Part 4: Heartbeat + bulk assign + PDF
Actually, the user asked to do everything. Let me try to do it in one big response but organized. Or maybe split into 2 responses.
Given the sheer volume, I'll do a focused response for client registration wizard first, since that's the biggest value item, and outline what comes next. Then in the next message I'll do the admin part.
Wait, but the user said "Давай начнём настраивать клиентский интерфейс" - let's START setting up the client interface. So they want to do this now.
Let me focus on:
Client registration wizard (new RegistrationDialog in client)
Remove Active window from client panel
Server endpoint check for bootstrap-token validation (to give feedback in wizard)
Then briefly outline the rest.
Actually let me think about the registration flow:
User launches EXE
Client checks if registered (keyring/credentials.enc)
If not registered ? show dialog asking for bootstrap token
User enters token ? client sends to server ? gets client_secret
Saved to keyring, dialog closes, main window appears
But currently ensure_registered() reads from bootstrap.txt or env. We need to change this to show a dialog if not registered.
Also need a way to validate the token on server side without burning it (or just try to register and show error if fails).
Let me write:
client/registration_dialog.py - new file with QDialog
client/main.py - modified to show dialog if not registered
client/registration.py - modify ensure_registered to accept token as arg
client/main.py - remove "active window" from panel (actually it's just a label that shows "—" because no data)
Wait, the user said "не заработало Активное окно. давай его уберём" - the "Active window" field in the panel didn't work. Remove it.
Let me write these scripts.
For the registration dialog, I'll need:
Big title "Регистрация Трекера"
Text explaining what to do
Input field for bootstrap token
Button "Зарегистрировать"
Status/error label
On success - save and close
Also I should add a "tray" icon option maybe? Let me keep it simple.
Let me also make sure the dialog doesn't call ensure_registered() automatically - the main flow needs to change so that main window opens first, then it checks registration.
Actually let me think about the flow again:
main() creates QApplication
main() tries to check if registered
If not - show RegistrationDialog (modal)
If user cancels - quit
If registered successfully - proceed to MainWindow
MainWindow runs as normal
This is cleaner than opening MainWindow and then dialog. Let me do this.
Let me code it:
python
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


# ============================================================
# Fallback-хранилище (когда keyring не работает)
# ============================================================

def _local_key() -> bytes:
    seed = (socket.gethostname() + platform.node()).encode()
    return base64.urlsafe_b64encode(hashlib.sha256(seed).digest())


def _protect(data: bytes) -> bytes:
    if sys.platform.startswith("win"):
        try:
            import win32crypt
            return win32crypt.CryptProtectData(data, None, None, None, None, 0)
        except ImportError:
            log.warning("win32crypt недоступен, fallback на Fernet")
            from cryptography.fernet import Fernet
            return Fernet(_local_key()).encrypt(data)
    from cryptography.fernet import Fernet
    return Fernet(_local_key()).encrypt(data)


def _unprotect(data: bytes) -> bytes:
    if sys.platform.startswith("win"):
        try:
            import win32crypt
            return win32crypt.CryptUnprotectData(data, None, None, None, 0)[1]
        except ImportError:
            pass
    from cryptography.fernet import Fernet
    return Fernet(_local_key()).decrypt(data)


def _load_fallback() -> dict:
    if not _FALLBACK_FILE.exists():
        return {}
    try:
        return json.loads(_unprotect(_FALLBACK_FILE.read_bytes()))
    except Exception as e:
        log.warning("Fallback read failed: %s", e)
        return {}


def _save_fallback(data: dict) -> None:
    _FALLBACK_FILE.write_bytes(_protect(json.dumps(data).encode()))
    if os.name != "nt":
        _FALLBACK_FILE.chmod(0o600)


def _safe_keyring_set(key: str, value: str) -> None:
    try:
        keyring.set_password(SERVICE, key, value)
        return
    except Exception as e:
        log.warning("keyring.set(%s) failed: %s ? fallback", key, e)
    data = _load_fallback()
    data[key] = value
    try:
        _save_fallback(data)
    except Exception as e2:
        log.error("Fallback write failed: %s", e2)
        raise RuntimeError(f"Cannot persist credentials: {e2}") from e2


def _safe_keyring_get(key: str):
    v = None
    try:
        v = keyring.get_password(SERVICE, key)
    except Exception as e:
        log.warning("keyring.get(%s): %s", key, e)
    fv = _load_fallback().get(key)
    if v and fv and v != fv:
        log.warning("keyring/fallback mismatch for %s (используем keyring)", key)
    return v or fv


# ============================================================
# Публичный API
