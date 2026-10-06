<!-- Часть 172 из 1409 -->
# --- записи ---
*Хлебные крошки:* --- записи ---

[◀ --- сессии ---](171_sessii.md) | [Оглавление](00_BCE_INDEX.md) | [--- config.py --- ▶](173_config_py.md)

---

# --- записи ---

def insert_record(record_uid, session_uid, kind, data_json, client_ts, signature):
    get_conn().execute(
        "INSERT OR IGNORE INTO records(record_uid, session_uid, kind, data, "
        "client_ts, signature) VALUES(?,?,?,?,?,?)",
        (record_uid, session_uid, kind, data_json, client_ts, signature),
    )
    touch_activity()


def fetch_unsynced(limit: int = 500):
    return get_conn().execute(
        "SELECT * FROM records WHERE synced=0 AND poisoned=0 "
        "ORDER BY client_ts ASC LIMIT ?", (limit,)
    ).fetchall()


def apply_sync_result(accepted, permanent_rejected):
    if not accepted and not permanent_rejected:
        return
    conn = get_conn()
    try:
        conn.execute("BEGIN")
        if accepted:
            q = f"UPDATE records SET synced=1 WHERE record_uid IN ({','.join('?' * len(accepted))})"
            conn.execute(q, accepted)
        if permanent_rejected:
            q = (f"UPDATE records SET synced=1, poisoned=1 "
                 f"WHERE record_uid IN ({','.join('?' * len(permanent_rejected))})")
            conn.execute(q, permanent_rejected)
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def fetch_unsynced_sessions():
    return get_conn().execute("SELECT * FROM sessions WHERE synced=0").fetchall()


def mark_session_synced(uid):
    get_conn().execute(
        "UPDATE sessions SET synced=1 WHERE session_uid=?", (uid,)
    )


def enforce_size_limit():
    if not DB_PATH.exists():
        return
    total = DB_PATH.stat().st_size
    for s in ("-wal", "-shm"):
        p = Path(str(DB_PATH) + s)
        if p.exists():
            total += p.stat().st_size
    if total / (1024 * 1024) < MAX_DB_SIZE_MB:
        return
    log.warning("DB > %d MB, pruning", MAX_DB_SIZE_MB)
    conn = get_conn()
    conn.execute(
        "DELETE FROM records WHERE record_uid IN ("
        "SELECT record_uid FROM records WHERE synced=1 "
        "ORDER BY client_ts ASC LIMIT 50000)"
    )
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    n = int(get_meta("vacuum_counter", "0")) + 1
    set_meta("vacuum_counter", str(n))
    if n % 10 == 0:
        try:
            conn.execute("VACUUM;")
        except sqlite3.OperationalError as e:
            log.warning("VACUUM: %s", e)
Сохраните.
________________________________________
Файл 2 — client/sync.py
Откройте D:\tracker\client\sync.py, удалите всё, вставьте:
python
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
    synced = pyqtSignal(int)
    error = pyqtSignal(str)
    server_down = pyqtSignal()
    auth_failed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._wake = threading.Event()

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

            # Спим SYNC_INTERVAL секунд, но можно разбудить через trigger()
            self._wake.wait(timeout=SYNC_INTERVAL)
            self._wake.clear()

    def stop(self):
        self._running = False
        self._wake.set()  # разбудить цикл, чтобы он увидел _running=False

    def trigger(self):
        """Немедленно разбудить цикл синхронизации (thread-safe)."""
        self._wake.set()

    def _headers(self):
        return {"X-Computer-Uid": get_computer_uid() or ""}

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
        for r in db.fetch_unsynced_sessions():
            payload = {
                "session_uid": r["session_uid"],
                "session_start": r["session_start"],
                "session_end": r["session_end"],
                "abnormal_termination": bool(r["abnormal_termination"]),
            }
            resp = self._post(f"{SERVER_URL}/api/v1/sessions",
                              json=payload, headers=self._headers())
            if resp.status_code in (401, 403):
                self.auth_failed.emit()
                self._running = False
                return False
            if resp.status_code == 200:
                db.mark_session_synced(r["session_uid"])
            else:
                log.warning("session %s ? %d", r["session_uid"], resp.status_code)
        return True

    def _sync_records(self) -> bool:
        batch = db.fetch_unsynced(limit=BATCH_SIZE)
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

        resp = self._post(
            f"{SERVER_URL}/api/v1/records/batch",
            json={"records": records, "batch_signature": batch_sig},
            headers=self._headers())

        if resp.status_code in (401, 403):
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

        self.synced.emit(len(accepted))
        return True
Сохраните.
________________________________________
Файл 3 — client/autostart.py (новый файл)
Создайте новый файл D:\tracker\client\autostart.py и вставьте:
python
import logging
import sys
from pathlib import Path

log = logging.getLogger("tracker.autostart")

APP_NAME = "Tracker"


def set_autostart(enabled: bool) -> bool:
    if sys.platform.startswith("win"):
        return _set_autostart_windows(enabled)
    elif sys.platform.startswith("linux"):
        return _set_autostart_linux(enabled)
    else:
        log.warning("Autostart not supported on %s", sys.platform)
        return False


def _set_autostart_windows(enabled: bool) -> bool:
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                             winreg.KEY_SET_VALUE)
        if enabled:
            exe = sys.executable
            if exe.lower().endswith("python.exe"):
                exe = exe[:-len("python.exe")] + "pythonw.exe"
                cmd = f'"{exe}" -m client.main'
            else:
                cmd = f'"{exe}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        log.exception("Autostart Windows failed: %s", e)
        return False


def _set_autostart_linux(enabled: bool) -> bool:
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    desktop = autostart_dir / "tracker.desktop"
    if enabled:
        exe = sys.executable
        content = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Tracker\n"
            f"Exec={exe} -m client.main\n"
            "X-GNOME-Autostart-enabled=true\n"
        )
        desktop.write_text(content, encoding="utf-8")
    else:
        desktop.unlink(missing_ok=True)
    return True
Сохраните.
________________________________________
Файл 4 — client/main.py
Откройте D:\tracker\client\main.py, удалите всё, вставьте:
python
import json
import logging
import os
import signal
import socket
import sys
import uuid
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QSocketNotifier, QThread
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QHBoxLayout, QLabel, QMainWindow, QMenu,
    QMessageBox, QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget,
)

from . import db, http_client
from .autostart import set_autostart
from .collector import CollectorWorker
from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH
from .registration import ensure_registered
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


def _short_dt(iso: str) -> str:
    if not iso:
        return "—"
    return iso[:19].replace("T", " ")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Tracker {CLIENT_VERSION}")
        self.resize(500, 280)

        # --- UI ---
        self.status = QLabel("Инициализация...")
        self.status.setStyleSheet("font-size: 14px; padding: 4px;")

        self.session_label = QLabel("Сессия: не запущена")
        self.session_label.setStyleSheet("color: #666; padding: 4px;")

        self.btn_start = QPushButton("?  Начать работу")
        self.btn_start.setStyleSheet(
            "background-color:#28a745; color:white; font-weight:bold;"
            "padding:12px; font-size:14px; border:none; border-radius:6px;"
        )
        self.btn_start.clicked.connect(self._on_start_work)

        self.btn_stop = QPushButton("?  Конец работы")
        self.btn_stop.setStyleSheet(
            "background-color:#dc3545; color:white; font-weight:bold;"
            "padding:12px; font-size:14px; border:none; border-radius:6px;"
        )
        self.btn_stop.clicked.connect(self._on_stop_work)
        self.btn_stop.setEnabled(False)

        self.autostart_cb = QCheckBox("Автозапуск при входе в систему")
        self.autostart_cb.setChecked(self._load_autostart_setting())
        self.autostart_cb.stateChanged.connect(self._on_autostart_changed)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_stop)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.session_label)
        layout.addLayout(btns)
        layout.addWidget(self.autostart_cb)

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
            ensure_registered()
        except Exception as e:
            log.exception("Registration failed")
            QMessageBox.critical(self, "Ошибка", f"Регистрация: {e}")
            self._quit()
            return

        try:
            db.init_db()
        except Exception as e:
            log.exception("DB init failed")
            QMessageBox.critical(self, "Ошибка БД", str(e))
            self._quit()
            return

        # Если в прошлый раз осталась незакрытая сессия — закрываем как аварийную
        active = db.get_active_session_uid()
        if active:
            log.warning("Найдена незакрытая сессия %s — закрываем как аварийную", active)
            try:
                db.close_session(active, abnormal=True)
            except Exception:
                log.exception("close_session on start failed")

        self.status.setText("Готов к работе")

        # Sync-воркер работает всегда — чтобы отправлять старые сессии и записи
        self._start_sync_worker()

        # Проверка обновлений
        self._check_updates()

    def _start_sync_worker(self):
        self.sync_thread = QThread()
        self.sync = SyncWorker()
        self.sync.moveToThread(self.sync_thread)
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.server_down.connect(
            lambda: self.status.setText("Offline — данные копятся локально"))
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()

    def _on_synced(self, n):
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")

    def _on_auth_failed(self):
        QMessageBox.warning(self, "Авторизация",
                            "Сервер отклонил клиента. Требуется перерегистрация.")
        self.status.setText("Ошибка авторизации")

    # --- work session ---
    def _on_start_work(self):
        if self.session_uid is not None:
            return  # уже идёт

        try:
            self.session_uid = str(uuid.uuid4())
            db.start_session(self.session_uid)
        except Exception as e:
            log.exception("start_session failed")
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать сессию: {e}")
            self.session_uid = None
            return

        # Запускаем сборщик в отдельном потоке
        self.collector_thread = QThread()
        self.collector = CollectorWorker(self.session_uid)
        self.collector.moveToThread(self.collector_thread)
        self.collector_thread.started.connect(self.collector.run)
        self.collector.error.connect(lambda m: self.status.setText(f"Сбор: {m}"))
        self.collector_thread.start()

        started = _short_dt(db.get_session_start(self.session_uid) or "")
        self.session_label.setText(
            f"Сессия: {self.session_uid[:8]}…  (с {started})")
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status.setText("Работа начата")

        # Сразу отправляем на сервер начало сессии
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

        # Останавливаем сборщик
        self._stop_collector()

        try:
            db.close_session(uid, abnormal=False)
        except Exception:
            log.exception("close_session failed")

        self.session_uid = None
        self.session_label.setText("Сессия: завершена")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status.setText("Работа завершена, синхронизация…")

        # Сразу отправляем на сервер окончание сессии
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

    # --- autostart ---
    def _load_autostart_setting(self) -> bool:
        cfg = BASE_DIR / "config.json"
        if cfg.exists():
            try:
                return json.loads(cfg.read_text(encoding="utf-8")).get(
                    "autostart_enabled", False)
            except Exception:
                pass
        return False

    def _on_autostart_changed(self, state):
        enabled = (state == 2)  # Qt.CheckState.Checked
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
        cfg.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                       encoding="utf-8")

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
            r = QMessageBox.question(
                self, "Обновление",
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

    # --- signals ---
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

        # Если сессия активна — закрываем её как аварийную
        if self.session_uid:
            try:
                db.close_session(self.session_uid, abnormal=True)
                log.info("Closed session %s on quit (abnormal=True)",
                         self.session_uid)
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
    win = MainWindow()
    win.install_signal_handlers()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
Сохраните.
________________________________________
Как запустить и проверить
Закройте все запущенные копии клиента (через трей ? «Выход»).
Запустите заново:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Должно открыться окно с двумя кнопками:
? Начать работу (зелёная, активна)
? Конец работы (красная, неактивна)
Чекбокс «Автозапуск при входе в систему»
Нажмите «Начать работу»:
Кнопка «Начать» серой становится, «Конец» — активной.
Внизу появится Сессия: xxxxxxxx… (с 2026-09-17 09:15:00).
Подождите 30 секунд или нажмите «Конец работы» — данные уйдут на сервер.
Проверьте на сервере:
Админка: https://localhost/admin/computers — появится ПК.
SQL:
powershell
docker compose exec db psql -U tracker -d tracker -c "SELECT session_uid, session_start, session_end, abnormal_termination FROM work_sessions ORDER BY id DESC LIMIT 5;"
Нажмите «Конец работы» — подтвердите. Через 1–3 секунды в БД появится session_end.
________________________________________
Как это выглядит для администратора
session_start = момент нажатия «Начать работу».
session_end = момент нажатия «Конец работы».
Разница = отработанное время.
В отчёте (/admin/reports) это готовые строки с длительностью и привязкой к сотруднику, если ПК назначен через /admin/computers.
________________________________________
Что делать, если что-то не так
Кнопка «Начать работу» ничего не делает ? смотрите %APPDATA%\Tracker\client.log, ищите start_session failed.
На сервере сессии не появляются ? docker compose logs api --tail=40, ищите POST /api/v1/sessions.
При закрытии приложения сессия помечается как аварийная — это нормально, если вы не нажали «Конец работы». Чтобы не помечалось, всегда завершайте день кнопкой.
«Конец работы» ? 409 Conflict ? на сервере в work_sessions уже есть сессия с таким session_uid от другого ПК. Маловероятно, но если случится — пришлите лог API.
Запускайте. Как заработает — переходим к следующим пунктам (heartbeat «онлайн/оффлайн», PDF-отчёты, роли).
(.venv) PS D:\tracker> cd D:\tracker >> client\.venv\Scripts\Activate.ps1 >> python -m client.main Traceback (most recent call last): File "<frozen runpy>", line 203, in _run_module_as_main File "<frozen runpy>", line 88, in _run_code File "D:\tracker\client\main.py", line 18, in <module> from .autostart import set_autostart File "D:\tracker\client\autostart.py", line 10 def set_autostart(enabled bool) - bool ^^^^ SyntaxError: invalid syntax
User wants a single PowerShell script that writes all files correctly (avoids the copy-paste issue with : and ->). I need to provide files:
server/config.py
server/requirements.txt
server/web_admin.py
server/templates/base.html
server/templates/reports.html
server/templates/report_result.html
I need to be careful with here-strings in PowerShell. Using @'...'@ (single-quoted here-string) preserves everything literally without variable expansion — that's what we want for Python and HTML.
Let me write the script carefully.
Note: In PowerShell, here-strings use @' on its own line and '@ on its own line (for literal). For HTML we could use the same.
Let me structure it:
powershell
$ErrorActionPreference = "Stop"

