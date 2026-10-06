<!-- Часть 393 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Публичный API](392_Publichnyy_API.md) | [Оглавление](00_BCE_INDEX.md) | [1) Заменить подключение сигналов в _start_sync_worker ▶](394_1_Zamenit_podklyuchenie_signalov_v_start_sync_worker.md)

---

# ============================================================

def is_registered() -> bool:
    """Зарегистрирован ли уже этот ПК."""
    uid = _safe_keyring_get("computer_uid")
    secret = _safe_keyring_get("client_secret")
    return bool(uid and secret)


def get_computer_uid():
    return _safe_keyring_get("computer_uid")


def get_client_secret():
    return _safe_keyring_get("client_secret")


def register_with_token(token: str) -> str:
    """
    Регистрирует ПК с явно переданным bootstrap-токеном.
    Возвращает computer_uid.
    Бросает RuntimeError с понятным текстом при ошибке.
    """
    token = (token or "").strip()
    if not token:
        raise RuntimeError("Токен не введён")

    # Уже зарегистрирован — просто возвращаем UID
    if is_registered():
        return _safe_keyring_get("computer_uid")

    uid = _safe_keyring_get("computer_uid") or str(uuid.uuid4())

    payload = {
        "computer_uid": uid,
        "hostname": socket.gethostname(),
        "os_info": f"{platform.system()} {platform.release()}",
        "client_version": CLIENT_VERSION,
        "bootstrap_token": token,
    }

    try:
        resp = http_client.post(
            f"{SERVER_URL}/api/v1/computers/register",
            json=payload,
        )
    except Exception as e:
        raise RuntimeError(
            f"Не удалось связаться с сервером {SERVER_URL}.\n{e}"
        ) from e

    if resp.status_code == 401:
        raise RuntimeError(
            "Токен неверный или уже использован.\n"
            "Попросите администратора выпустить новый."
        )
    if resp.status_code == 409:
        raise RuntimeError(
            "Этот компьютер уже зарегистрирован.\n"
            "Обратитесь к администратору для разблокировки."
        )
    if resp.status_code >= 500:
        raise RuntimeError(f"Сервер вернул ошибку {resp.status_code}")
    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", "")
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Ошибка регистрации: {resp.status_code} {detail}")

    data = resp.json()
    _safe_keyring_set("computer_uid", uid)
    _safe_keyring_set("client_secret", data["client_secret"])

    log.info("Registered as %s (secret_version=%s)", uid, data.get("secret_version"))
    return uid


def ensure_registered():
    """Обратная совместимость. Если не зарегистрирован — RuntimeError."""
    if not is_registered():
        raise RuntimeError("Компьютер не зарегистрирован")
    return _safe_keyring_get("computer_uid")
'@
[System.IO.File]::WriteAllText("$clientDir\registration.py", $registration_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/registration.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$clientDir\registration.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — новый файл client/registration_dialog.py
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

$reg_dialog_py = @'
"""
Диалог регистрации компьютера в системе «Трекер».
Показывается при первом запуске, если ПК ещё не зарегистрирован.
"""
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QVBoxLayout,
)

from . import registration
from .config import SERVER_URL

log = logging.getLogger("tracker.reg_dialog")


class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация Tracker")
        self.setMinimumWidth(540)
        self.setModal(True)

        # Заголовок
        title = QLabel("?? Регистрация компьютера")
        f = QFont()
        f.setPointSize(15)
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Пояснение
        info = QLabel(
            "Для начала работы введите одноразовый токен, полученный "
            "у администратора системы.\n\n"
            "После успешной регистрации токен станет недействительным, "
            "а данные об активности начнут отправляться на сервер "
            "автоматически."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color:#555; font-size:13px;")

        # Сервер
        server_lbl = QLabel(f"Сервер: <code>{SERVER_URL}</code>")
        server_lbl.setStyleSheet("color:#888; font-size:11px;")
        server_lbl.setTextFormat(Qt.TextFormat.RichText)

        # Поле ввода
        token_lbl = QLabel("Bootstrap-токен:")
        token_lbl.setStyleSheet("font-size:13px; margin-top:6px;")

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Вставьте токен сюда (Ctrl+V)")
        self.token_input.setMinimumHeight(38)
        self.token_input.setStyleSheet(
            "font-size:14px; padding:6px 8px; "
            "border:1px solid #ced4da; border-radius:6px;"
        )
        self.token_input.returnPressed.connect(self._on_register)

        # Статус
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color:#dc3545; font-size:12px; margin-top:4px;")

        # Кнопки
        self.btn_register = QPushButton("Зарегистрировать")
        self.btn_register.setMinimumHeight(42)
        self.btn_register.setStyleSheet(
            "background-color:#28a745; color:white; font-weight:bold; "
            "border:none; border-radius:6px; font-size:14px;"
        )
        self.btn_register.clicked.connect(self._on_register)

        btn_cancel = QPushButton("Выход")
        btn_cancel.setMinimumHeight(42)
        btn_cancel.setStyleSheet(
            "background-color:#f0f0f0; color:#333; border:none; "
            "border-radius:6px; font-size:14px;"
        )
        btn_cancel.clicked.connect(self.reject)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_register, 2)
        btns.addWidget(btn_cancel, 1)

        # Компоновка
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(server_lbl)
        layout.addWidget(token_lbl)
        layout.addWidget(self.token_input)
        layout.addWidget(self.status_label)
        layout.addLayout(btns)
        self.setLayout(layout)

    def _on_register(self):
        token = self.token_input.text().strip()
        if not token:
            self.status_label.setText("Введите токен")
            self.token_input.setFocus()
            return

        self.btn_register.setEnabled(False)
        self.btn_register.setText("Регистрация…")
        self.status_label.setText("")
        # Принудительно обновляем UI до сетевого вызова
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            registration.register_with_token(token)
        except Exception as e:
            log.exception("Registration failed")
            self.status_label.setText(str(e))
            self.btn_register.setEnabled(True)
            self.btn_register.setText("Зарегистрировать")
            return

        QMessageBox.information(
            self, "Успех",
            "Компьютер успешно зарегистрирован!\n\n"
            "Окно трекера откроется автоматически. "
            "Нажмите «Начать работу», чтобы приступить.",
        )
        self.accept()
'@
[System.IO.File]::WriteAllText("$clientDir\registration_dialog.py", $reg_dialog_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/registration_dialog.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$clientDir\registration_dialog.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 3 — client/main.py (полная замена)
Изменения:
Убрана строка «Активное окно» из панели.
Добавлена проверка регистрации до открытия главного окна.
Если не зарегистрирован — показывается RegistrationDialog.
Внутри MainWindow._start() больше нет вызова ensure_registered().
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

$main_py = @'
import json
import logging
import os
import signal
import socket
import sys
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QSocketNotifier, QThread, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenu, QMessageBox, QPushButton, QSystemTrayIcon,
    QVBoxLayout, QWidget,
)

from . import db, http_client, registration
from .autostart import set_autostart
from .collector import CollectorWorker
from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH, IDLE_CLOSE_MINUTES
from .registration_dialog import RegistrationDialog
from .sync import SyncWorker
from .updater import UpdateChecker, apply_update

handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024,
                              backupCount=3, encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[handler],
)
log = logging.getLogger("tracker.main")


def _icon_path() -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "icon.ico")


def _local_time_str(iso_str: str) -> str:
    """UTC ISO-строка ? локальное время HH:MM:SS."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%H:%M:%S")
    except Exception:
        return "—"


def _fmt_duration(seconds: int) -> str:
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Tracker {CLIENT_VERSION}")
        self.resize(540, 400)

        # --- главный статус ---
        self.status = QLabel("Инициализация...")
        self.status.setStyleSheet("font-size: 14px; padding: 4px; color:#555;")

        # --- кнопки ---
        self.btn_start = QPushButton("?  Начать работу")
        self.btn_start.setStyleSheet(
            "background-color:#28a745; color:white; font-weight:bold;"
            "padding:14px; font-size:15px; border:none; border-radius:6px;"
        )
        self.btn_start.clicked.connect(self._on_start_work)

        self.btn_stop = QPushButton("?  Конец работы")
        self.btn_stop.setStyleSheet(
            "background-color:#dc3545; color:white; font-weight:bold;"
            "padding:14px; font-size:15px; border:none; border-radius:6px;"
        )
        self.btn_stop.clicked.connect(self._on_stop_work)
        self.btn_stop.setEnabled(False)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_stop)

        # --- панель информации ---
        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background: #f8f9fa; border: 1px solid #dee2e6;"
            " border-radius: 6px; padding: 8px; }"
        )
        grid = QGridLayout(panel)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)

        def mk_label(text=""):
            l = QLabel(text)
            l.setStyleSheet("font-size: 13px;")
            return l

        def mk_title(text):
            l = QLabel(text)
            l.setStyleSheet("color:#6c757d; font-size:12px;")
            return l

        # Строка 1: сессия
        grid.addWidget(mk_title("Сессия"), 0, 0)
        self.lbl_session_start = mk_label("не запущена")
        grid.addWidget(self.lbl_session_start, 0, 1)

        grid.addWidget(mk_title("Сейчас работаем"), 0, 2)
        self.lbl_session_clock = mk_label("—")
        self.lbl_session_clock.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#28a745;"
        )
        grid.addWidget(self.lbl_session_clock, 0, 3)

        # Строка 2: сервер и последняя синхронизация
        grid.addWidget(mk_title("Сервер"), 1, 0)
        self.lbl_server = mk_label("—")
        grid.addWidget(self.lbl_server, 1, 1)

        grid.addWidget(mk_title("Последняя синхронизация"), 1, 2)
        self.lbl_last_sync = mk_label("никогда")
        grid.addWidget(self.lbl_last_sync, 1, 3)

        # Строка 3: очередь
        grid.addWidget(mk_title("Записей в очереди"), 2, 0)
        self.lbl_pending = mk_label("0")
        grid.addWidget(self.lbl_pending, 2, 1)

        # Автозапуск
        self.autostart_cb = QCheckBox("Автозапуск при входе в систему")
        self.autostart_cb.setChecked(self._load_autostart_setting())
        self.autostart_cb.stateChanged.connect(self._on_autostart_changed)

        # Собираем
        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addLayout(btns)
        layout.addWidget(panel)
        layout.addWidget(self.autostart_cb)
        layout.addStretch()

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        # --- state ---
        self.session_uid = None
        self.collector = None
        self.collector_thread = None
        self.sync = None
        self.sync_thread = None
        self._signal_notifier = None
        self._signal_socks = None

        self._build_tray()
        self._start()

        # Обновление панели каждую секунду
        self._ui_timer = QTimer(self)
        self._ui_timer.setInterval(1000)
        self._ui_timer.timeout.connect(self._update_panel)
        self._ui_timer.start()

    def _update_panel(self):
        try:
            if self.session_uid:
                start_iso = db.get_session_start(self.session_uid) or ""
                self.lbl_session_start.setText(_local_time_str(start_iso))
                try:
                    start_dt = datetime.fromisoformat(start_iso)
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=timezone.utc)
                    elapsed = int((datetime.now(timezone.utc) - start_dt).total_seconds())
                    self.lbl_session_clock.setText(_fmt_duration(elapsed))
                except Exception:
                    self.lbl_session_clock.setText("—")
            else:
                self.lbl_session_start.setText("не запущена")
                self.lbl_session_clock.setText("—")

            try:
                rows = db.get_conn().execute(
                    "SELECT COUNT(*) AS n FROM records WHERE synced=0 AND poisoned=0"
                ).fetchone()
                self.lbl_pending.setText(str(rows["n"]) if rows else "0")
            except Exception:
                self.lbl_pending.setText("?")

            last_sync = db.get_meta("last_sync_ts")
            if last_sync:
                try:
                    dt = datetime.fromisoformat(last_sync)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    self.lbl_last_sync.setText(dt.astimezone().strftime("%d.%m %H:%M:%S"))
                except Exception:
                    self.lbl_last_sync.setText("—")
        except Exception:
            log.exception("_update_panel failed")

    # --- tray ---
    def _build_tray(self):
        self.tray = QSystemTrayIcon(self)
        ip = _icon_path()
        if os.path.exists(ip):
            self.tray.setIcon(QIcon(ip))
        else:
            self.tray.setIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_ComputerIcon))

        menu = QMenu()
        a_show = QAction("Показать", self)
        a_show.triggered.connect(self._show)
        a_start = QAction("Начать работу", self)
        a_start.triggered.connect(self._on_start_work)
        a_stop = QAction("Конец работы", self)
        a_stop.triggered.connect(self._on_stop_work)
        a_quit = QAction("Выход", self)
        a_quit.triggered.connect(self._quit)

        menu.addAction(a_show)
        menu.addSeparator()
        menu.addAction(a_start)
        menu.addAction(a_stop)
        menu.addSeparator()
        menu.addAction(a_quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def _show(self):
        self.showNormal()
        self.activateWindow()

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.tray.showMessage(
            "Tracker", "Свёрнуто в трей",
            QSystemTrayIcon.MessageIcon.Information, 2000,
        )

    # --- lifecycle ---
    def _start(self):
        try:
            db.init_db()
        except Exception as e:
            log.exception("DB init failed")
            QMessageBox.critical(self, "Ошибка БД", str(e))
            self._quit()
            return

        active = db.get_active_session_uid()
        if active:
            log.warning("Найдена незакрытая сессия %s — закрываем как аварийную", active)
            try:
                db.close_session(active, abnormal=True)
            except Exception:
                log.exception("close_session on start failed")

        self.status.setText("Готов к работе")
        self._start_sync_worker()

        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(60 * 1000)
        self._idle_timer.timeout.connect(self._check_idle_session)
        self._idle_timer.start()

        self._check_updates()

    def _start_sync_worker(self):
        self.sync_thread = QThread()
        self.sync = SyncWorker()
        self.sync.moveToThread(self.sync_thread)
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.server_down.connect(
            lambda: self.lbl_server.setText("? офлайн"))
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()

    def _on_synced(self, n):
        self.lbl_server.setText("? онлайн")
        try:
            db.set_meta("last_sync_ts", datetime.now(timezone.utc).isoformat())
        except Exception:
            pass
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")

    def _on_auth_failed(self):
        QMessageBox.warning(self, "Авторизация",
                            "Сервер отклонил клиента. Требуется перерегистрация.")
        self.status.setText("Ошибка авторизации")

    # --- work session ---
    def _on_start_work(self):
        if self.session_uid is not None:
            return
        try:
            self.session_uid = str(uuid.uuid4())
            db.start_session(self.session_uid)
        except Exception as e:
            log.exception("start_session failed")
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать сессию: {e}")
            self.session_uid = None
            return

        self.collector_thread = QThread()
        self.collector = CollectorWorker(self.session_uid)
        self.collector.moveToThread(self.collector_thread)
        self.collector_thread.started.connect(self.collector.run)
        self.collector.error.connect(lambda m: self.status.setText(f"Сбор: {m}"))
        self.collector_thread.start()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status.setText("Работа начата")

        if self.sync:
            self.sync.trigger()
        log.info("Work session started uid=%s", self.session_uid)

    def _on_stop_work(self):
        if self.session_uid is None:
            return
        r = QMessageBox.question(
            self, "Конец работы",
            "Завершить рабочий день? Данные будут отправлены на сервер.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return

        uid = self.session_uid
        self._stop_collector()
        try:
            db.close_session(uid, abnormal=False)
        except Exception:
            log.exception("close_session failed")

        self.session_uid = None
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status.setText("Работа завершена, синхронизация…")

        if self.sync:
            self.sync.trigger()
        log.info("Work session stopped uid=%s", uid)

    def _stop_collector(self):
        if self.collector:
            try:
                self.collector.stop()
            except Exception:
                log.exception("collector.stop")
        if self.collector_thread:
            self.collector_thread.quit()
            if not self.collector_thread.wait(5000):
                log.warning("collector thread didn't stop")
        self.collector = None
        self.collector_thread = None

    def _check_idle_session(self):
        try:
            idle = db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)
            closed_uid = db.auto_close_idle_session(idle)
            if closed_uid:
                log.info("Auto-closed idle session %s", closed_uid)
                self.session_uid = None
                self.btn_start.setEnabled(True)
                self.btn_stop.setEnabled(False)
                self.status.setText("Сессия закрыта автоматически, отправляем на сервер…")
                if self.sync:
                    self.sync.trigger()
                self._stop_collector()
        except Exception:
            log.exception("_check_idle_session failed")

    # --- autostart ---
    def _load_autostart_setting(self) -> bool:
        cfg = BASE_DIR / "config.json"
        if cfg.exists():
            try:
                return json.loads(cfg.read_text(encoding="utf-8")).get("autostart_enabled", False)
            except Exception:
                pass
        return False

    def _on_autostart_changed(self, state):
        enabled = (state == 2)
        ok = set_autostart(enabled)
        if not ok:
            QMessageBox.warning(self, "Автозапуск",
                                "Не удалось изменить автозапуск. Проверьте права.")
            return
        cfg = BASE_DIR / "config.json"
        data = {}
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
            except Exception:
                pass
        data["autostart_enabled"] = enabled
        cfg.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- updates ---
    def _check_updates(self):
        self._upd_thread = QThread()
        self._upd = UpdateChecker(auto_download=False)
        self._upd.moveToThread(self._upd_thread)
        self._upd_thread.started.connect(self._upd.run)
        self._upd.no_update.connect(self._upd_thread.quit)
        self._upd.update_available.connect(self._on_update_available)
        self._upd.update_ready.connect(self._on_update_ready)
        self._upd.error.connect(lambda e: log.warning("upd: %s", e))
        self._upd_thread.start()

    def _on_update_available(self, info):
        if info.get("mandatory"):
            self._download_and_apply(info)
        else:
            r = QMessageBox.question(self, "Обновление",
                                     f"Обновиться до {info['latest_version']}?")
            if r == QMessageBox.StandardButton.Yes:
                self._download_and_apply(info)

    def _on_update_ready(self, info, path):
        try:
            self._stop_collector()
            self._shutdown_sync()
            http_client.close_client()
            db.close_conn()
            from pathlib import Path
            apply_update(Path(path))
        except Exception:
            log.exception("apply update failed")

    def _download_and_apply(self, info):
        self._dl_thread = QThread()
        self._dl = UpdateChecker(auto_download=True)
        self._dl.moveToThread(self._dl_thread)
        self._dl_thread.started.connect(self._dl.run)
        self._dl.update_ready.connect(self._on_update_ready)
        self._dl.error.connect(lambda e: QMessageBox.warning(self, "Ошибка", e))
        self._dl_thread.start()

    def install_signal_handlers(self):
        r, w = socket.socketpair()
        r.setblocking(False)
        w.setblocking(False)

        def _noop(*_a):
            pass

        signal.signal(signal.SIGTERM, _noop)
        signal.signal(signal.SIGINT, _noop)
        signal.set_wakeup_fd(w.fileno())

        n = QSocketNotifier(r.fileno(), QSocketNotifier.Type.Read, self)

        def _on():
            try:
                r.recv(1024)
            except BlockingIOError:
                pass
            self._quit()

        n.activated.connect(_on)
        self._signal_notifier = n
        self._signal_socks = (r, w)

    def _shutdown_sync(self):
        if self.sync:
            try:
                self.sync.stop()
            except Exception:
                log.exception("sync.stop")
        if self.sync_thread:
            self.sync_thread.quit()
            if not self.sync_thread.wait(5000):
                log.warning("sync thread didn't stop")
        self.sync = None
        self.sync_thread = None

    def _quit(self):
        log.info("Shutting down")
        self._stop_collector()
        if self.session_uid:
            try:
                db.close_session(self.session_uid, abnormal=True)
                log.info("Closed session %s on quit (abnormal=True)", self.session_uid)
            except Exception:
                log.exception("close_session on quit")
            self.session_uid = None
        self._shutdown_sync()
        http_client.close_client()
        db.close_conn()
        try:
            if self._signal_notifier:
                self._signal_notifier.setEnabled(False)
                self._signal_notifier = None
            if self._signal_socks:
                r, w = self._signal_socks
                signal.set_wakeup_fd(-1)
                r.close()
                w.close()
                self._signal_socks = None
        except Exception:
            log.exception("signal cleanup")
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Проверяем регистрацию ДО открытия главного окна
    if not registration.is_registered():
        dlg = RegistrationDialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            log.info("Пользователь отменил регистрацию — выход")
            return
        if not registration.is_registered():
            log.error("После диалога регистрация всё ещё отсутствует")
            return

    win = MainWindow()
    win.install_signal_handlers()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'@
[System.IO.File]::WriteAllText("$clientDir\main.py", $main_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/main.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$clientDir\main.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 4 — проверка и запуск
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

Write-Host "--- Проверка файлов клиента ---" -ForegroundColor Cyan
foreach ($f in @("registration.py", "registration_dialog.py", "main.py")) {
    $p = Join-Path $clientDir $f
    if (Test-Path $p) {
        $size = (Get-Item $p).Length
        Write-Host ("  OK  {0}  ({1} bytes)" -f $f, $size) -ForegroundColor Green
    } else {
        Write-Host ("  MISSING  {0}" -f $f) -ForegroundColor Red
    }
}

Write-Host "`n--- Тест: имитация «первого запуска» ---" -ForegroundColor Cyan
Write-Host "  Чтобы проверить сценарий регистрации как с чистого листа,"
Write-Host "  удалите сохранённые секреты этого ПК."
Write-Host ""
Write-Host "  ВАЖНО: если вы уже зарегистрированы и не хотите потерять связь,"
Write-Host "  НЕ выполняйте следующие команды. Они удаляют локальную регистрацию." -ForegroundColor Yellow
Write-Host ""
$answer = Read-Host "  Стереть регистрацию (y/N)?"
if ($answer -eq "y") {
    # Чистим keyring через маленький скрипт
    client\.venv\Scripts\python.exe -c @"
import keyring
try:
    keyring.delete_password('tracker', 'computer_uid')
    keyring.delete_password('tracker', 'client_secret')
    print('  keyring: удалено')
except Exception as e:
    print('  keyring:', e)
import os
p = os.path.join(os.environ.get('APPDATA', ''), 'Tracker', 'credentials.enc')
if os.path.exists(p):
    os.remove(p)
    print('  credentials.enc: удалено')
"@
    Write-Host "  Готово. Теперь запустите клиент — появится диалог регистрации." -ForegroundColor Green
}

Write-Host "`n--- Запуск клиента ---" -ForegroundColor Cyan
Write-Host "cd D:\tracker"
Write-Host "client\.venv\Scripts\Activate.ps1"
Write-Host "python -m client.main"
Write-Host ""
Write-Host "Если не зарегистрирован — откроется окно «Регистрация Tracker»." -ForegroundColor Green
________________________________________
Что должно произойти
Сценарий «чистый ПК»
Запускаете python -m client.main
Открывается диалог «?? Регистрация компьютера» с полем для токена.
Вставляете bootstrap-токен (выпущенный через /admin/tokens)
Жмёте «Зарегистрировать»:
Если токен верный — сообщение «Успех» и открывается главное окно.
Если токен неверный — красный текст с объяснением прямо в диалоге.
Если сервер недоступен — понятное сообщение с адресом.
В главном окне на панели теперь нет строки «Активное окно».
Нажимаете «Начать работу» — сессия стартует, время показывается в локальном часовом поясе (то, что мы уже исправили ранее).
Сценарий «повторный запуск»
Регистрация уже в keyring — диалог не показывается, сразу открывается главное окно.
Как это скажется на сборке .exe
Админ собирает Tracker.exe, при необходимости вшивает TRACKER_SERVER_URL в client/.env (или правит config.py до сборки).
Отдаёт пользователю EXE и отдельно bootstrap-токен (или встраивает его в инсталлятор).
Пользователь запускает ? диалог ? токен ? готово.
Никаких ручных bootstrap.txt больше не нужно — это legacy.
________________________________________
Что делаем дальше
По вашему списку осталось:
Следующее сообщение:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация (отделы ? сотрудники), поиск внутри <select>.
XLSX — убрать «Группа» и «Аварийный», добавить колонки «Год / Месяц / Число» (Месяц — по-русски: Сентябрь), дату в формате, который Excel понимает как дату.
Онлайн-отчёт — сворачивание до месяца (группировка «Месяц ? Сотрудник»).
Сообщение после:
Календарь рабочих/нерабочих дней — таблица calendar_days + страница админки + подсветка Сб/Вс + чекбокс «считать выходные».
Heartbeat — /api/v1/heartbeat + колонка Онлайн/Оффлайн на дашборде.
Массовая привязка ПК — загрузка CSV «hostname ? ФИО».
PDF-отчёт — reportlab + кириллица.
Запускайте скрипты 1–4 и проверьте диалог регистрации. Если что-то пойдёт не так (например, ModuleNotFoundError или ошибка сети) — пришлите вывод, поправим. После этого двигаемся к админским фильтрам.
регистрация прошла успешно но сервер сейчас пишет офлайн хотя сайт работает
Пользователь зарегистрировался успешно, но клиент показывает "офлайн", хотя сервер работает. Нужно разобраться.
Причины:
Sync worker не отправляет данные - возможно, ошибка в sync или http_client
Нет активной сессии - sync может не отправлять ничего, если нечего отправлять, и не обновляет статус
Проблема с _on_synced - я вызываю его только если sync успешно отправил
Возможно, sync не запускается или падает
Смотрим на логику:
server_down сигнал ? "? офлайн"
synced сигнал ? "? онлайн"
Sync в цикле: _sync_sessions ? _sync_records ? sleep
Если сессий нет и записей нет - _sync_sessions вернёт True (нечего отправлять), _sync_records вернёт True, но synced.emit не вызывается, если accepted пустой!
Смотрим _sync_records:
python
batch = db.fetch_unsynced(limit=BATCH_SIZE)
if not batch:
    return True   # ? НЕ вызывает synced.emit
...
self.synced.emit(len(accepted))
А _on_synced обновляет статус "онлайн". Если записей нет - статус не обновляется.
Также _fetch_client_config должен работать - он дергает сервер. Но он тоже не вызывает synced.
Решение:
В sync после успешной синхронизации (даже если нечего отправлять) вызывать synced.emit(0) или новый сигнал connected
Или вызывать synced.emit даже если записи не было
Ещё лучше - добавить проверку соединения как отдельный сигнал. Например, _fetch_client_config успешно - значит сервер жив. Тогда synced.emit(0).
Давайте поправим sync.py - чтобы:
При каждом успешном цикле (даже без данных) обновлять статус "онлайн"
Добавим отдельный сигнал connected в sync worker
Или проще - в _fetch_client_config после успешного запроса слать сигнал.
Смотрю sync.py который я писал ранее:
python
def run(self):
    self._running = True
    while self._running:
        try:
            ok = self._sync_sessions()
            if ok:
                ok = self._sync_records()
            if not ok:
                break
            db.enforce_size_limit()
        except Exception as e:
            log.warning("sync failed: %s", e)
            self.server_down.emit()

        # Подтягиваем client-config раз в 10 циклов
        self._cycles += 1
        if self._cycles % 10 == 1:
            self._fetch_client_config()

        self._wake.wait(timeout=SYNC_INTERVAL)
        self._wake.clear()
Здесь server_down эмитится только при исключении. Если всё ок, но нечего отправлять - вообще ничего не эмитится.
Плюс, у нас теперь есть _fetch_client_config - он делает HTTP-запрос к серверу. Если он успешен - значит сервер жив.
Решение: сделать _fetch_client_config публичным статусом. Если он успешен и вернул 200 - эмитить connected (новый сигнал) или переиспользовать synced с 0.
Давайте перепишу sync.py так, чтобы:
Раз в цикл (не раз в 10) делал лёгкую проверку связи через /api/v1/client-config (или отдельный endpoint) — но это много запросов
Лучше: каждые 10 циклов делает запрос, но при первом цикле сразу (для отображения статуса)
Более правильно: сразу при старте делаем запрос, потом периодически. И при успехе - synced.emit(0) или новый сигнал connected.emit().
Также надо проверить, что _fetch_client_config вообще работает. Он вызывается с if self._cycles % 10 == 1, а _cycles += 1 до проверки. То есть при первом проходе _cycles = 1, 1 % 10 == 1 ? True. Ок, первый вызов происходит.
Но _fetch_client_config не эмитит ничего при успехе. Только логирует.
Меняю логику: _fetch_client_config возвращает bool, и в run при успехе эмитим synced.emit(0) (или новый сигнал).
Или лучше - сразу при старте делать проверку соединения в отдельном методе, чтобы показать статус без ожидания 30 секунд.
Давайте поправлю sync.py так:
python
def run(self):
    self._running = True
    # Сразу при старте — проверяем связь, чтобы UI обновил статус
    self._check_connection()
    
    while self._running:
        try:
            ok = self._sync_sessions()
            if ok:
                ok = self._sync_records()
            if not ok:
                break
            db.enforce_size_limit()
        except Exception as e:
            log.warning("sync failed: %s", e)
            self.server_down.emit()

        self._cycles += 1
        if self._cycles % 10 == 1:
            self._fetch_client_config()

        self._wake.wait(timeout=SYNC_INTERVAL)
        self._wake.clear()


def _check_connection(self):
    """Лёгкая проверка связи при старте."""
    try:
        r = http_client.get(f"{SERVER_URL}/api/v1/version",
                            headers=self._headers(), timeout=5.0)
        if r.status_code < 500:
            self.synced.emit(0)  # ? UI показывает "онлайн"
    except Exception as e:
        log.debug("connection check failed: %s", e)


def _fetch_client_config(self):
    try:
        r = http_client.get(f"{SERVER_URL}/api/v1/client-config",
                            headers=self._headers(), timeout=5.0)
        if r.status_code == 200:
            data = r.json()
            idle = int(data.get("idle_close_minutes", 30))
            current = db.get_meta("idle_close_minutes")
            if str(idle) != current:
                db.set_meta("idle_close_minutes", str(idle))
                log.info("idle_close_minutes updated: %d", idle)
            # Обновляем статус UI
            self.synced.emit(0)
    except Exception as e:
        log.debug("client-config fetch failed: %s", e)
И в main.py _on_synced(0) не должен писать "Синхронизировано 0" — сейчас там if n > 0. Ок.
Но _on_synced также обновляет last_sync_ts - это неправильно, если n=0 (мы просто проверили связь, не синхронизировали). Нужно разделять:
synced.emit(N) - реально отправили N записей ? обновляем last_sync_ts
Просто связь есть - отдельный сигнал
Лучше сделать так: добавить сигнал connected = pyqtSignal(). В main.py его связать с lbl_server.setText("? онлайн").
Или: использовать synced.emit(-1) как маркер "просто проверка связи", а в main.py обрабатывать по-разному.
Пойду простым путём - отдельный сигнал connected.
Также стоит пересмотреть _sync_sessions и _sync_records — они не шлют никаких сигналов при успехе, если нечего отправлять. Значит, если сессий нет и записей нет, статус "онлайн" никогда не установится.
Также важно: возможно ошибка вообще в другом. Пользователь говорит "сервер пишет офлайн". Это не "работает медленно". Значит, server_down вызывается либо никогда не устанавливается "онлайн".
Проверим sync.py:
server_down.emit() вызывается только в except Exception as e: в run()
Значит, если связь есть, но записей нет - server_down не эмитится, но и "онлайн" не эмитится
А начальное состояние lbl_server = "—". Но пользователь пишет "офлайн". Значит, server_down вызвался.
Что могло упасть? Возможно:
_sync_sessions бросает исключение при попытке постить сессию
_sync_records - то же
Что-то другое
Проверим _sync_sessions:
python
def _sync_sessions(self) -> bool:
    for r in db.fetch_unsynced_sessions():
        payload = {...}
        resp = self._post(f"{SERVER_URL}/api/v1/sessions",
                          json=payload, headers=self._headers())
self._post использует tenacity с retry на 5xx. Если сервер вернёт 401/403 - вернёт resp, потом проверка.
Но обратите внимание - _post может бросить httpx.HTTPStatusError при 5xx после 3 ретраев. Это приведёт к except Exception в run() ? server_down.emit().
Также - _headers возвращает X-Computer-Uid. Если get_computer_uid() вернул None (регистрация не полностью сохранилась?) - может быть 401.
Скорее всего проблема в том, что после регистрации computer_uid сохраняется в keyring, но sync worker запущен до этого. В моей новой версии main.py:
python
if not registration.is_registered():
    dlg = RegistrationDialog()
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return
    ...

win = MainWindow()
Т.е. регистрация происходит ДО создания MainWindow. И в MainWindow._start() запускается sync worker. Значит, get_computer_uid() должен вернуть значение.
НО - возможно keyring не сохранил, а fallback в credentials.enc. Или что-то ещё.
Другой вариант - ошибка в _fetch_client_config, которая вызывается из run(), но так как это внутри try/except в вызывающем коде... нет, _fetch_client_config вызывается вне try/except. Если он бросает - падает весь цикл. Но у меня там свой try/except.
Давайте посмотрим внимательнее. В _fetch_client_config есть except Exception as e: log.debug(...). То есть ошибки ловятся. Хорошо.
Возможно, sync вообще не запускается или падает на старте. Давайте добавим диагностику и одновременно улучшим логику статуса.
План:
В sync.py добавить сигнал connected и вызывать его:
при старте после _check_connection()
в _fetch_client_config при успехе
в _sync_sessions и _sync_records при успехе (даже если нечего отправлять)
В main.py подписать connected на lbl_server.setText("? онлайн")
Также поправить логику: _on_synced(n) обновляет last_sync_ts только если n > 0
Ещё лучше: чтобы не переделывать много, можно в sync.py после успешного цикла эмитить synced.emit(0) и в main.py обновлять статус при любом n (даже 0), но last_sync_ts - только при n>0.
Хм, но _on_synced(0) в главном окне - надо не перезаписывать "Синхронизировано N" если n=0.
Так, план:
Поправить sync.py:
сразу при старте - _check_connection() (легкий запрос к /api/v1/version)
при успехе - self.synced.emit(0) (значит "связь есть")
в цикле при _sync_sessions и _sync_records успешно завершённых, если нечего отправлять - всё равно synced.emit(0)? Нет, лучше - synced.emit(-1)? Нет, запутаемся.
Лучше сделать отдельный сигнал connected = pyqtSignal():
Сразу при старте вызвать _check_connection() ? при успехе connected.emit()
В _fetch_client_config при успехе ? connected.emit()
В main.py подписать на lbl_server.setText("? онлайн")
И _on_synced(n) оставить как есть, только убрать обновление last_sync_ts при n=0.
Также добавить диагностику в лог при server_down.
Давайте так и сделаем. Полный sync.py.
Также нужно подстраховаться: если sync стартует и сразу server_down.emit (падение на первой итерации), пользователь видит "офлайн". Хорошо бы сделать более точную диагностику.
Причина может быть в _post с retry - если первый запрос к серверу упал по таймауту или SSL. Проверим: httpx.Client с verify - если ca.pem не настроен... но пользователь уже зарегистрировался, значит связь есть.
Возможно, ошибка в /api/v1/sessions при отсутствии сессии? Но у нас for r in db.fetch_unsynced_sessions() - если пусто, цикл не выполняется, функция возвращает True.
Похоже, sync просто не отправляет запрос и статус остаётся "—". А "офлайн" может появиться от server_down при падении sync.
Хм, а может в панели еще до старта было "офлайн"? Проверим main.py:
python
self.lbl_server = mk_label("—")
Начальное "—". Значит, "офлайн" появилось после server_down.emit().
Значит, sync падает с исключением. Что падает? Скорее всего _sync_records или _sync_sessions.
Причина может быть в _post - @retry декоратор с reraise=True. Если 5xx после 3 попыток, поднимется. Но 5xx у нас не должно быть с рабочим сервером.
Ещё вариант - get_computer_uid() возвращает None. Тогда X-Computer-Uid: "" ? сервер ответит 401 ? в _sync_sessions ? self.auth_failed.emit() ? self._running = False; return False ? в run() ? if not ok: break ? цикл завершается. Не "офлайн".
Хм. Тогда что?
Может быть, проблема в другом - httpx.Client падает при построении из-за pinning? Смотрю http_client.py:
python
def _pinning_enabled() -> bool:
    if not PINNED_CERT_SHA256 or set(PINNED_CERT_SHA256) == {"0"}:
        return False
Если TRACKER_PIN пустой ? False ? pinning отключён. Ok.
Возможно, проблема с SSL - если сертификат самоподписанный, а ca.pem не найден. Но регистрация прошла! Значит, запрос к register был успешен. И http_client тот же самый.
Ладно, не буду гадать. Давайте:
Улучшим логику статуса - добавим _check_connection при старте
Добавим логирование в sync.py
Пользователь потом проверит логи
Также важный момент - я в предыдущем сообщении модифицировал sync.py через .Replace(), который мог не сработать. Давайте перезапишем sync.py целиком с нуля.
Ещё - в _sync_records при отсутствии batch:
python
batch = db.fetch_unsynced(limit=BATCH_SIZE)
if not batch:
    return True
Возврат True. Хорошо.
_sync_sessions возвращает True если нет сессий.
Тогда run() продолжает цикл. Что тогда вызывает server_down?
Возможно, db.enforce_size_limit() или что-то в _fetch_client_config.
Или ошибка при вызове http_client.get (при обращении к _fetch_client_config). Хотя там try/except.
Хм. Может быть, get_computer_uid() в _headers бросает? Смотрим registration.py:
python
def get_computer_uid():
    return _safe_keyring_get("computer_uid")
Внутри _safe_keyring_get может быть исключение. Но у него есть fallback внутри.
Ок, давайте просто напишем надёжную версию sync.py с подробным логированием, чтобы понять, что происходит.
Также исправим логику статуса в main.py - "онлайн" сразу при старте если сервер отвечает.
Финальный план:
Полный sync.py с:
connected сигналом
_check_connection() при старте
логированием каждого шага
main.py - подписать connected ? "? онлайн"
Пишу.
Также подумаю о http_client.get - возможно, он возвращает response с ошибкой (не бросает), а sync пытается его использовать. Но нет, у нас resp.status_code == 200 проверки.
Пишу решение.
Один момент: _check_connection() использует /api/v1/version - публичный endpoint без авторизации. Это хорошо для проверки связи.
Также надо учесть - если http_client.get используется, а httpx.Client создаётся при первом вызове - может падать на первом запросе. Добавлю логирование.
Ок, пишу.
Также в main.py надо сделать чтобы "? онлайн" показывалось через 2-3 секунды после старта (после того как первая проверка связи пройдёт).
Плюс, раз sync работает в отдельном потоке, а сигналы pyqt работают через очередь событий - не будет race condition.
Пишу полный sync.py и правку main.py.
Также важно: пользователь сказал "регистрация прошла успешно". Значит, HTTPS-соединение работает, ca.pem найден, httpx не падает.
Тогда почему в sync происходит что-то, что вызывает server_down?
Возможно, дело в том, что sync стартует до того как регистрация завершилась? Нет, регистрация ДО MainWindow.
Или всё же — sync стартует с пустой БД (нет last_sync_ts), и там что-то падает?
Хм, db.get_meta("last_sync_ts") возвращает None. В _update_panel: if last_sync: ? False ? ничего не делает. Ок.
Ладно, действуем. Пишу надёжную версию и просим логи. Возможно, там что-то очевидное.
Формат ответа:
Диагностика: попрошу логи
Полный новый sync.py (с connected и диагностикой)
Патч main.py на connected
Также сделаю так, чтобы при старте сразу показывалось "? онлайн" если сервер отвечает, без ожидания 30 секунд.
Ок пишу.
Причина: sync не эмитит «онлайн», если нечего отправлять
Логика такая: synced.emit(N) вызывается только когда реально отправлены записи. Если очередь пуста (только зарегистрировались, ещё ничего не собрали) — синк молча проходит, статус остаётся «—». А если что-то внутри падает — вызывается server_down ? «офлайн».
Причин для падения несколько, разберёмся по логам. Но сначала сразу поправим логику статуса: добавлю отдельный сигнал connected, лёгкую проверку связи при старте и подробное логирование, чтобы точно видеть, где спотыкается.
________________________________________
Шаг 1. Смотрим логи клиента
Выполните в PowerShell:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 60 -Encoding UTF8
Ищите строки:
client-config fetch failed: ...
sync failed: ...
Bad signature ...
401 / 403
Пришлите мне последние 30 строк.
________________________________________
Шаг 2. Новый sync.py (полная замена)
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

$sync_py = @'
import json
import logging
import threading

from PyQt6.QtCore import QObject, pyqtSignal
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

from . import crypto, db, http_client
from .config import BATCH_SIZE, SERVER_URL, SYNC_INTERVAL
from .registration import get_computer_uid

log = logging.getLogger("tracker.sync")


class SyncWorker(QObject):
    synced = pyqtSignal(int)          # успешно отправлено N записей (N>0)
    connected = pyqtSignal()          # сервер доступен (даже если нечего отправлять)
    error = pyqtSignal(str)
    server_down = pyqtSignal()
    auth_failed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._wake = threading.Event()
        self._cycles = 0

    # ============================================================
    # Главный цикл
    # ============================================================

    def run(self):
        self._running = True
        log.info("SyncWorker started; server=%s", SERVER_URL)

        # Сразу проверяем связь, чтобы UI показал «онлайн» без ожидания 30 сек
        self._check_connection()

        while self._running:
            try:
                ok = self._sync_sessions()
                if ok:
                    ok = self._sync_records()
                if not ok:
                    log.info("Sync loop stopped (auth/break)")
                    break
                db.enforce_size_limit()
            except Exception as e:
                log.warning("sync cycle failed: %s", e, exc_info=True)
                self.server_down.emit()

            # Раз в 10 циклов (~5 минут) подтягиваем настройки с сервера
            self._cycles += 1
            if self._cycles % 10 == 1:
                self._fetch_client_config()

            self._wake.wait(timeout=SYNC_INTERVAL)
            self._wake.clear()

        log.info("SyncWorker stopped")

    def stop(self):
        self._running = False
        self._wake.set()

    def trigger(self):
        self._wake.set()

    # ============================================================
    # Проверки и служебные вызовы
    # ============================================================

    def _headers(self):
        uid = get_computer_uid() or ""
        return {"X-Computer-Uid": uid}

    def _check_connection(self):
        """Лёгкий запрос — понять, отвечает ли сервер. Без авторизации."""
        try:
            r = http_client.get(f"{SERVER_URL}/api/v1/version", timeout=5.0)
            if r.status_code < 500:
                log.info("Server reachable (HTTP %s)", r.status_code)
                self.connected.emit()
            else:
                log.warning("Server reachable but %s", r.status_code)
                self.server_down.emit()
        except Exception as e:
            log.warning("Server unreachable: %s", e)
            self.server_down.emit()

    def _fetch_client_config(self):
        """Забирает настройки клиента с сервера."""
        try:
            r = http_client.get(f"{SERVER_URL}/api/v1/client-config",
                                headers=self._headers(), timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                idle = int(data.get("idle_close_minutes", 30))
                current = db.get_meta("idle_close_minutes")
                if str(idle) != current:
                    db.set_meta("idle_close_minutes", str(idle))
                    log.info("idle_close_minutes updated: %d", idle)
                # Сервер ответил 200 — считаем «онлайн»
                self.connected.emit()
            elif r.status_code in (401, 403):
                log.warning("client-config returned %s (auth)", r.status_code)
            else:
                log.warning("client-config returned %s", r.status_code)
        except Exception as e:
            log.debug("client-config fetch failed: %s", e)

    # ============================================================
    # Отправка сессий и записей
    # ============================================================

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((http_client.httpx.HTTPError,)),
           reraise=True)
    def _post(self, url, **kw):
        resp = http_client.post(url, **kw)
        if 500 <= resp.status_code < 600:
            raise http_client.httpx.HTTPStatusError(
                f"{resp.status_code}", request=resp.request, response=resp)
        return resp

    def _sync_sessions(self) -> bool:
        try:
            pending = db.fetch_unsynced_sessions()
        except Exception as e:
            log.warning("fetch_unsynced_sessions failed: %s", e)
            return True

        if not pending:
            return True

        for r in pending:
            payload = {
                "session_uid": r["session_uid"],
                "session_start": r["session_start"],
                "session_end": r["session_end"],
                "abnormal_termination": bool(r["abnormal_termination"]),
            }
            try:
                resp = self._post(f"{SERVER_URL}/api/v1/sessions",
                                  json=payload, headers=self._headers())
            except Exception as e:
                log.warning("session post failed: %s", e)
                raise

            if resp.status_code in (401, 403):
                log.warning("session post ? %s; auth failed", resp.status_code)
                self.auth_failed.emit()
                self._running = False
                return False
            if resp.status_code == 200:
                db.mark_session_synced(r["session_uid"])
                log.info("Session %s synced", r["session_uid"])
                self.connected.emit()
            else:
                log.warning("session %s ? %d", r["session_uid"], resp.status_code)

        return True

    def _sync_records(self) -> bool:
        try:
            batch = db.fetch_unsynced(limit=BATCH_SIZE)
        except Exception as e:
            log.warning("fetch_unsynced failed: %s", e)
            return True

        if not batch:
            return True

        records = [{
            "record_uid": r["record_uid"],
            "session_uid": r["session_uid"],
            "kind": r["kind"],
            "data": json.loads(r["data"]),
            "client_ts": r["client_ts"],
            "signature": r["signature"],
        } for r in batch]

        batch_sig = crypto.sign_payload({"records": records})

        try:
            resp = self._post(
                f"{SERVER_URL}/api/v1/records/batch",
                json={"records": records, "batch_signature": batch_sig},
                headers=self._headers())
        except Exception as e:
            log.warning("batch post failed: %s", e)
            raise

        if resp.status_code in (401, 403):
            log.warning("batch post ? %s; auth failed", resp.status_code)
            self.auth_failed.emit()
            self._running = False
            return False

        resp.raise_for_status()
        body = resp.json()

        server_sig = body.pop("server_signature", None)
        if not server_sig or not crypto.verify_payload(server_sig, body):
            log.error("Server signature invalid — возможен MITM")
            self.error.emit("server signature invalid")
            return False

        accepted = body.get("accepted_uuids", [])
        rejected = body.get("rejected_uuids", [])
        reasons = body.get("reasons", {})

        permanent = [u for u in rejected if reasons.get(u) == "bad_signature"]
        temporary = [u for u in rejected if u not in permanent]

        db.apply_sync_result(accepted, permanent)

        if temporary:
            log.info("temporary rejects (retry): %d", len(temporary))
        if permanent:
            log.warning("permanent rejects: %d %s", len(permanent), reasons)

        if accepted:
            try:
                from datetime import datetime, timezone as _tz
                db.set_meta("last_sync_ts", datetime.now(_tz.utc).isoformat())
            except Exception:
                pass
            log.info("Batch: accepted=%d rejected=%d", len(accepted), len(rejected))
            self.synced.emit(len(accepted))

        # Сервер ответил — значит связь есть
        self.connected.emit()
        return True
'@
[System.IO.File]::WriteAllText("$clientDir\sync.py", $sync_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/sync.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$clientDir\sync.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Шаг 3. Патч main.py — подписка на connected
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"
$mainPath = "$clientDir\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

