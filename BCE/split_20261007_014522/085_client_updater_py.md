<!-- Часть 85 из 1409 -->
# `client/updater.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/updater.py`

[◀ `client/sync.py`](084_client_sync_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/main.py` ▶](086_client_main_py.md)

---

### `client/updater.py`

```python
import logging
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from . import http_client
from .config import CLIENT_VERSION, DOWNLOAD_DIR, SERVER_URL

log = logging.getLogger("tracker.updater")


class UpdateChecker(QObject):
    update_available = pyqtSignal(dict)
    update_ready = pyqtSignal(dict, str)
    no_update = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, auto_download: bool = False):
        super().__init__()
        self._auto_download = auto_download

    def run(self):
        try:
            info = check_for_update()
            if not info:
                self.no_update.emit()
                return
            if self._auto_download or info.get("mandatory"):
                try:
                    path = download_update(info["download_url"])
                    self.update_ready.emit(info, str(path))
                    return
                except Exception as e:
                    self.error.emit(f"download failed: {e}")
                    return
            self.update_available.emit(info)
        except Exception as e:
            self.error.emit(str(e))


def check_for_update() -> dict | None:
    try:
        resp = http_client.get(f"{SERVER_URL}/api/v1/version",
                               params={"current": CLIENT_VERSION})
        resp.raise_for_status()
        data = resp.json()
        if data["latest_version"] != CLIENT_VERSION:
            return data
    except Exception as e:
        log.warning("version check: %s", e)
    return None


def download_update(url: str) -> Path:
    target = DOWNLOAD_DIR / Path(url).name
    with http_client.get_client().stream("GET", url) as r:
        r.raise_for_status()
        with open(target, "wb") as f:
            for chunk in r.iter_bytes(64 * 1024):
                f.write(chunk)
    return target


def apply_update(path: Path, silent: bool = True) -> None:
    log.info("Applying update: %s", path)
    try:
        if sys.platform.startswith("win"):
            args = [str(path)] + (["/S"] if silent else [])
            subprocess.Popen(args, close_fds=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        log.exception("launch installer failed: %s", e)
        return
    QTimer.singleShot(500, QApplication.quit)
```

