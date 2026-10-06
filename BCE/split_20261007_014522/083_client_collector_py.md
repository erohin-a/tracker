<!-- Часть 83 из 1409 -->
# `client/collector.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/collector.py`

[◀ `client/registration.py`](082_client_registration_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/sync.py` ▶](084_client_sync_py.md)

---

### `client/collector.py`

```python
import json
import logging
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone

from PyQt6.QtCore import QObject, pyqtSignal

from . import crypto, db
from .config import ACTIVE_WINDOW_INTERVAL, IDLE_THRESHOLD

log = logging.getLogger("tracker.collector")

try:
    from pynput import keyboard, mouse
    PYNPUT_OK = True
except Exception as e:
    PYNPUT_OK = False
    log.warning("pynput unavailable: %s", e)

try:
    import psutil
except ImportError:
    psutil = None


def _get_active_window() -> dict:
    result = {"title": "", "pid": None, "app": "", "platform": "unknown"}
    try:
        if sys.platform.startswith("win"):
            import ctypes
            u = ctypes.windll.user32
            hwnd = u.GetForegroundWindow()
            n = u.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(hwnd, buf, n + 1)
            pid = ctypes.c_ulong()
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            result.update(title=buf.value, pid=pid.value, platform="win32")
        elif sys.platform == "darwin":
            from AppKit import NSWorkspace  # type: ignore
            app = NSWorkspace.sharedWorkspace().activeApplication()
            result.update(title=app.get("NSApplicationName", ""),
                          pid=app.get("NSApplicationProcessIdentifier"),
                          platform="darwin")
        else:
            from Xlib import display  # type: ignore
            d = display.Display()
            wid = d.screen().root.get_full_property(
                d.intern_atom("_NET_ACTIVE_WINDOW"), 0).value[0]
            win = d.create_resource_object("window", wid)
            name = win.get_wm_name() or ""
            prop = win.get_full_property(d.intern_atom("_NET_WM_PID"), 0)
            pid = prop.value[0] if prop else None
            result.update(title=name, pid=pid, platform="linux")
    except Exception as e:
        result["error"] = str(e)
        return result

    if psutil and result.get("pid"):
        try:
            result["app"] = psutil.Process(result["pid"]).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return result


class CollectorWorker(QObject):
    error = pyqtSignal(str)
    started_ok = pyqtSignal()

    def __init__(self, session_uid: str):
        super().__init__()
        self.session_uid = session_uid
        self._running = False
        self._kb_listener = None
        self._ms_listener = None
        self._lock = threading.Lock()
        self._pending = {"keys": 0, "clicks": 0, "scroll": 0}
        self._last_input = time.monotonic()
        self._was_idle = False
        self._last_app = None
        self._last_title = None
        self._is_wayland = os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"

    def run(self):
        self._running = True
        if self._is_wayland:
            log.warning("XDG_SESSION_TYPE=wayland: активное окно недоступно")
            self.error.emit("Wayland: активное окно недоступно")

        if PYNPUT_OK:
            try:
                self._kb_listener = keyboard.Listener(on_press=self._on_key)
                self._ms_listener = mouse.Listener(
                    on_click=self._on_click, on_scroll=self._on_scroll)
                self._kb_listener.start()
                self._ms_listener.start()
                self.started_ok.emit()
            except Exception as e:
                self.error.emit(f"listeners: {e}")

        try:
            while self._running:
                self._emit_window()
                self._flush()
                end = time.time() + ACTIVE_WINDOW_INTERVAL
                while self._running and time.time() < end:
                    time.sleep(0.2)
        finally:
            self._stop_listeners()

    def stop(self):
        self._running = False

    def _stop_listeners(self):
        for l in (self._kb_listener, self._ms_listener):
            if l is not None:
                try:
                    l.stop()
                except Exception:
                    pass

    def _on_key(self, key):
        with self._lock:
            self._pending["keys"] += 1
            self._last_input = time.monotonic()

    def _on_click(self, x, y, button, pressed):
        if pressed:
            with self._lock:
                self._pending["clicks"] += 1
                self._last_input = time.monotonic()

    def _on_scroll(self, x, y, dx, dy):
        with self._lock:
            self._pending["scroll"] += 1
            self._last_input = time.monotonic()

    def _is_idle(self):
        with self._lock:
            return time.monotonic() - self._last_input > IDLE_THRESHOLD

    def _emit_window(self):
        if self._is_idle():
            if not self._was_idle:
                self._write("idle", {"type": "idle"})
                self._was_idle = True
            return
        if self._was_idle:
            self._write("idle_end", {"type": "idle_end"})
            self._was_idle = False

        info = _get_active_window()
        if info.get("error"):
            return
        app, title = info.get("app") or "", info.get("title") or ""
        if app == self._last_app and title == self._last_title:
            return
        self._last_app, self._last_title = app, title
        self._write("window", {"type": "window", **info})

    def _flush(self):
        with self._lock:
            counts = dict(self._pending)
            self._pending.update({"keys": 0, "clicks": 0, "scroll": 0})
        if any(counts.values()):
            self._write("activity", {"type": "activity", **counts})

    def _write(self, kind: str, data: dict):
        try:
            rid = str(uuid.uuid4())
            ts = datetime.now(timezone.utc).isoformat()
            payload = {"record_uid": rid, "session_uid": self.session_uid,
                       "kind": kind, "data": data, "client_ts": ts}
            sig = crypto.sign_payload(payload)
            db.insert_record(rid, self.session_uid, kind,
                             json.dumps(data, ensure_ascii=False), ts, sig)
        except Exception as e:
            log.exception("write failed")
            self.error.emit(str(e))
```

