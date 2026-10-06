<!-- Часть 86 из 1409 -->
# `client/main.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/main.py`

[◀ `client/updater.py`](085_client_updater_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/build.spec` ▶](087_client_build_spec.md)

---

### `client/main.py`

```python
import logging
import os
import signal
import socket
import sys
import uuid
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QSocketNotifier, QThread
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenu,
                             QMessageBox, QSystemTrayIcon, QVBoxLayout, QWidget)

from . import db, http_client
from .collector import CollectorWorker
from .config import CLIENT_VERSION, LOG_PATH
from .registration import ensure_registered
from .sync import SyncWorker
from .updater import UpdateChecker, apply_update

handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024,
                              backupCount=3, encoding="utf-8")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s",
                    handlers=[handler])
log = logging.getLogger("tracker.main")


def _icon_path() -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "icon.ico")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Tracker {CLIENT_VERSION}")
        self.resize(420, 180)
        self.status = QLabel("Инициализация...")
        layout = QVBoxLayout()
        layout.addWidget(self.status)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.session_uid = None
        self.collector = self.sync = None
        self.collector_thread = self.sync_thread = None
        self._signal_notifier = self._signal_socks = None
        self._build_tray()
        self._start()

    def _build_tray(self):
        self.tray = QSystemTrayIcon(self)
        ip = _icon_path()
        if os.path.exists(ip):
            self.tray.setIcon(QIcon(ip))
        else:
            self.tray.setIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_ComputerIcon))
        menu = QMenu()
        a1 = QAction("Показать", self)
        a1.triggered.connect(self.show)
        a2 = QAction("Выход", self)
        a2.triggered.connect(self._quit)
        menu.addAction(a1)
        menu.addAction(a2)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.tray.showMessage("Tracker", "Свёрнуто в трей")

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
            db.detect_abnormal_termination()
        except Exception as e:
            log.exception("DB init failed")
            QMessageBox.critical(self, "Ошибка БД", str(e))
            self._quit()
            return

        self.session_uid = str(uuid.uuid4())
        db.start_session(self.session_uid)
        self.status.setText(f"Сессия: {self.session_uid[:8]}…")

        self.collector_thread = QThread()
        self.collector = CollectorWorker(self.session_uid)
        self.collector.moveToThread(self.collector_thread)
        self.collector_thread.started.connect(self.collector.run)
        self.collector.error.connect(lambda m: self.status.setText(f"Сбор: {m}"))
        self.collector_thread.start()

        self.sync_thread = QThread()
        self.sync = SyncWorker()
        self.sync.moveToThread(self.sync_thread)
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(lambda n: self.status.setText(f"Синхронизировано {n}"))
        self.sync.server_down.connect(lambda: self.status.setText("Offline"))
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()

        self._check_updates()

    def _on_auth_failed(self):
        QMessageBox.warning(self, "Авторизация",
                            "Сервер отклонил клиента. Требуется перерегистрация.")
        self.status.setText("Ошибка авторизации")

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
            self._shutdown_workers()
            http_client.close_client()
            db.close_conn()
            from pathlib import Path
            apply_update(Path(path))
        except Exception as e:
            log.exception("apply: %s", e)

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

    def _shutdown_workers(self):
        if self.collector:
            self.collector.stop()
        if self.collector_thread:
            self.collector_thread.quit()
            if not self.collector_thread.wait(5000):
                log.warning("collector didn't stop")
        if self.session_uid:
            try:
                db.close_session(self.session_uid, abnormal=False)
            except Exception:
                log.exception("close_session")
        if self.sync:
            self.sync.stop()
        if self.sync_thread:
            self.sync_thread.quit()
            if not self.sync_thread.wait(5000):
                log.warning("sync didn't stop")

    def _quit(self):
        log.info("Shutting down")
        self._shutdown_workers()
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
```

