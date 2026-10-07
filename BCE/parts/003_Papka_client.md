# ?? Папка `client/`

*Часть 3 из 100. Источник: `BCE.md`.*

[◀ ?? Папка `server/`](002_Papka_server.md) | [Оглавление](00_BCE_INDEX.md) | [?? Сертификаты `D:\tracker\certs\` ▶](004_Sertifikaty_D_tracker_certs.md)

---

## ?? Папка `client/`

### `client/__init__.py`

```python
# Пустой файл. Делает папку client Python-пакетом.
```

### `client/requirements.txt`

```txt
PyQt6==6.7.1
httpx==0.27.0
pynput==1.7.7
keyring==25.2.1
psutil==5.9.8
python-dotenv>=1.0
tenacity>=8.2
cryptography>=42.0
pywin32; sys_platform == "win32"
```

### `client/.env`

```ini
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
```

### `client/config.py`

```python
import logging as _logging
import os
from pathlib import Path

_log = _logging.getLogger("tracker.config")

try:
    from dotenv import load_dotenv
    _candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent / ".env",
        Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
    ]
    _loaded_from = None
    for p in _candidates:
        if p.exists():
            load_dotenv(p, override=True)
            _loaded_from = p
            break
    if _loaded_from:
        _log.info("Loaded .env from %s", _loaded_from)
    else:
        _log.warning(".env not found in %s", [str(p) for p in _candidates])
except ImportError:
    _log.error("python-dotenv not installed; .env will NOT be read")


APP_NAME = "Tracker"
CLIENT_VERSION = os.environ.get("TRACKER_VERSION", "1.0.0")

if os.name == "nt":
    BASE_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    BASE_DIR = Path.home() / f".{APP_NAME.lower()}"
BASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "data.db"
LOG_PATH = BASE_DIR / "client.log"
DOWNLOAD_DIR = BASE_DIR / "updates"
DOWNLOAD_DIR.mkdir(exist_ok=True)

SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://tracker.example.com")
SSL_CA_BUNDLE = os.environ.get("TRACKER_CA_BUNDLE", str(BASE_DIR / "ca.pem"))
PINNED_CERT_SHA256 = os.environ.get("TRACKER_PIN", "").strip().lower()

SYNC_INTERVAL = 30
ACTIVE_WINDOW_INTERVAL = 5
IDLE_THRESHOLD = 60
MAX_DB_SIZE_MB = 500
BATCH_SIZE = 200
COLLECT_KEYSTROKE_CHARS = False
```

### `client/crypto.py`

```python
import hmac
import hashlib
import json
import math
from typing import Any
import keyring

SERVICE = "tracker"


def _validate(obj: Any) -> Any:
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("NaN/Infinity not allowed")
        return obj
    if isinstance(obj, dict):
        return {str(k): _validate(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_validate(v) for v in obj]
    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    raise ValueError(f"unsupported type: {type(obj).__name__}")


def canonical_json(obj: Any) -> bytes:
    return json.dumps(
        _validate(obj),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def get_client_secret() -> str:
    from .registration import _safe_keyring_get
    secret = _safe_keyring_get("client_secret")
    if not secret:
        raise RuntimeError("client_secret not found; register first")
    return secret


def sign_payload(payload: dict) -> str:
    secret = get_client_secret()
    return hmac.new(
        secret.encode("utf-8"),
        canonical_json(payload),
        hashlib.sha256,
    ).hexdigest()


def verify_payload(signature: str, payload: dict) -> bool:
    try:
        expected = sign_payload(payload)
    except Exception:
        return False
    return hmac.compare_digest(expected, signature)
```

### `client/db.py`

```python
import sqlite3
import threading
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone

from .config import DB_PATH, MAX_DB_SIZE_MB

log = logging.getLogger("tracker.db")
_local = threading.local()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_uid           TEXT PRIMARY KEY,
    session_start         TEXT NOT NULL,
    session_end           TEXT,
    abnormal_termination  INTEGER DEFAULT 0,
    synced                INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS records (
    record_uid   TEXT PRIMARY KEY,
    session_uid  TEXT NOT NULL,
    kind         TEXT NOT NULL,
    data         TEXT NOT NULL,
    client_ts    TEXT NOT NULL,
    signature    TEXT,
    synced       INTEGER DEFAULT 0,
    poisoned     INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_records_synced  ON records(synced, poisoned);
CREATE INDEX IF NOT EXISTS ix_records_session ON records(session_uid);
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


def get_conn() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH), timeout=10,
                               isolation_level=None, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA journal_size_limit=67108864;")
        conn.row_factory = sqlite3.Row
        _local.conn = conn
    return conn


def close_conn():
    conn = getattr(_local, "conn", None)
    if conn is not None:
        try:
            conn.close()
        finally:
            _local.conn = None


def _migrate(conn):
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(records);")}
    if "poisoned" not in cols:
        conn.execute("ALTER TABLE records ADD COLUMN poisoned INTEGER DEFAULT 0;")


def _quarantine_corrupt_db():
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(DB_PATH) + suffix)
        if p.exists():
            try:
                p.rename(p.with_name(p.name + f".corrupt.{stamp}"))
            except OSError as e:
                log.error("rename %s failed: %s", p, e)


def init_db():
    if DB_PATH.exists():
        try:
            c = sqlite3.connect(str(DB_PATH))
            res = c.execute("PRAGMA integrity_check;").fetchone()
            c.close()
            if not res or res[0] != "ok":
                log.critical("DB integrity failed: %s. Quarantine.", res)
                _quarantine_corrupt_db()
        except sqlite3.DatabaseError as e:
            log.critical("Not a database: %s. Quarantine.", e)
            _quarantine_corrupt_db()

    conn = get_conn()
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    except sqlite3.OperationalError as e:
        log.warning("wal_checkpoint: %s", e)
    conn.executescript(SCHEMA)
    _migrate(conn)


def set_meta(key, value):
    get_conn().execute(
        "INSERT INTO meta(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))


def get_meta(key, default=None):
    row = get_conn().execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def start_session(uid: str):
    get_conn().execute(
        "INSERT OR IGNORE INTO sessions(session_uid, session_start, "
        "abnormal_termination, synced) VALUES(?,?,0,0)", (uid, _now_iso()))
    set_meta("active_session", uid)
    set_meta("last_activity", _now_iso())


def touch_activity():
    set_meta("last_activity", _now_iso())


def close_session(uid: str, abnormal: bool = False):
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?", (_now_iso(), 1 if abnormal else 0, uid))
    if get_meta("active_session") == uid:
        set_meta("active_session", "")


def detect_abnormal_termination():
    active = get_meta("active_session")
    if not active:
        return
    last = get_meta("last_activity")
    try:
        last_dt = datetime.fromisoformat(last) if last else datetime.now(timezone.utc)
    except ValueError:
        last_dt = datetime.now(timezone.utc)
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - last_dt > timedelta(hours=12):
        log.warning("Abnormal termination of %s", active)
        close_session(active, abnormal=True)


def insert_record(record_uid, session_uid, kind, data_json, client_ts, signature):
    get_conn().execute(
        "INSERT OR IGNORE INTO records(record_uid, session_uid, kind, data, "
        "client_ts, signature) VALUES(?,?,?,?,?,?)",
        (record_uid, session_uid, kind, data_json, client_ts, signature))
    touch_activity()


def fetch_unsynced(limit: int = 500):
    return get_conn().execute(
        "SELECT * FROM records WHERE synced=0 AND poisoned=0 "
        "ORDER BY client_ts ASC LIMIT ?", (limit,)).fetchall()


def apply_sync_result(accepted, permanent_rejected):
    if not accepted and not permanent_rejected:
        return
    conn = get_conn()
    try:
        conn.execute("BEGIN")
        if accepted:
            q = f"UPDATE records SET synced=1 WHERE record_uid IN ({','.join('?'*len(accepted))})"
            conn.execute(q, accepted)
        if permanent_rejected:
            q = (f"UPDATE records SET synced=1, poisoned=1 "
                 f"WHERE record_uid IN ({','.join('?'*len(permanent_rejected))})")
            conn.execute(q, permanent_rejected)
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def fetch_unsynced_sessions():
    return get_conn().execute("SELECT * FROM sessions WHERE synced=0").fetchall()


def mark_session_synced(uid):
    get_conn().execute("UPDATE sessions SET synced=1 WHERE session_uid=?", (uid,))


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
        "ORDER BY client_ts ASC LIMIT 50000)")
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    n = int(get_meta("vacuum_counter", "0")) + 1
    set_meta("vacuum_counter", str(n))
    if n % 10 == 0:
        try:
            conn.execute("VACUUM;")
        except sqlite3.OperationalError as e:
            log.warning("VACUUM: %s", e)
```

### `client/http_client.py`

```python
import hashlib
import logging
import os
import threading
from typing import Optional

import httpx

from .config import PINNED_CERT_SHA256, SSL_CA_BUNDLE

log = logging.getLogger("tracker.http")


def _pinning_enabled() -> bool:
    if not PINNED_CERT_SHA256 or set(PINNED_CERT_SHA256) == {"0"}:
        return False
    if len(PINNED_CERT_SHA256) != 64:
        log.error("PIN length %d != 64, pinning disabled", len(PINNED_CERT_SHA256))
        return False
    try:
        int(PINNED_CERT_SHA256, 16)
    except ValueError:
        log.error("PIN not hex, pinning disabled")
        return False
    return True


def _resolve_verify():
    """Возвращает True/False или путь к CA bundle."""
    v = os.environ.get("TRACKER_INSECURE", "").strip().lower()
    if v in ("1", "true", "yes"):
        log.warning("SSL verification DISABLED (TRACKER_INSECURE=1) — только для dev!")
        return False
    if SSL_CA_BUNDLE and os.path.exists(SSL_CA_BUNDLE):
        log.info("Using CA bundle: %s", SSL_CA_BUNDLE)
        return SSL_CA_BUNDLE
    return True


class PinningTransport(httpx.HTTPTransport):
    def __init__(self, pinned_sha256: str, **kwargs):
        super().__init__(**kwargs)
        self._pinned = pinned_sha256.lower()
        self._verified_fps: set[str] = set()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        response = super().handle_request(request)
        if request.url.scheme != "https":
            return response

        stream = response.extensions.get("network_stream")
        if stream is None:
            raise httpx.ConnectError("pinning: no network_stream")
        ssl_obj = stream.get_extra_info("ssl_object")
        if ssl_obj is None:
            try:
                stream.close()
            except Exception:
                pass
            raise httpx.ConnectError("pinning: no ssl_object")

        der = ssl_obj.getpeercert(binary_form=True)
        if der is None:
            try:
                stream.close()
            except Exception:
                pass
            raise httpx.ConnectError("pinning: peer cert missing")
        fp = hashlib.sha256(der).hexdigest().lower()
        if fp in self._verified_fps:
            return response
        if fp != self._pinned:
            try:
                stream.close()
            except Exception:
                pass
            raise httpx.ConnectError(
                f"pinning failed: expected {self._pinned[:16]}..., got {fp[:16]}..."
            )
        self._verified_fps.add(fp)
        return response


_client_lock = threading.Lock()
_client: Optional[httpx.Client] = None


def _build_client() -> httpx.Client:
    verify = _resolve_verify()
    if _pinning_enabled():
        log.info("Pinning ENABLED (%s...)", PINNED_CERT_SHA256[:16])
        transport = PinningTransport(
            pinned_sha256=PINNED_CERT_SHA256, verify=verify, retries=2,
        )
    else:
        log.warning("Pinning DISABLED")
        transport = httpx.HTTPTransport(verify=verify, retries=2)
    return httpx.Client(
        transport=transport,
        timeout=httpx.Timeout(20.0, connect=10.0),
        headers={"User-Agent": "Tracker/1.2"},
    )


def get_client() -> httpx.Client:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = _build_client()
    return _client


def close_client():
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
            _client = None


def get(url, **kw):
    return get_client().get(url, **kw)


def post(url, **kw):
    return get_client().post(url, **kw)
```

### `client/registration.py`

```python
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


def _safe_keyring_get(key: str) -> str | None:
    v = None
    try:
        v = keyring.get_password(SERVICE, key)
    except Exception as e:
        log.warning("keyring.get(%s): %s", key, e)
    fv = _load_fallback().get(key)
    if v and fv and v != fv:
        log.warning("keyring/fallback mismatch for %s (используем keyring)", key)
    return v or fv


def ensure_registered(bootstrap_token: str | None = None) -> str:
    uid = _safe_keyring_get("computer_uid")
    secret = _safe_keyring_get("client_secret")
    if uid and secret:
        return uid

    token = bootstrap_token or os.environ.get("TRACKER_BOOTSTRAP_TOKEN")
    if not token:
        tf = BASE_DIR / "bootstrap.txt"
        if tf.exists():
            token = tf.read_text(encoding="utf-8").strip()
    if not token:
        raise RuntimeError(
            "Bootstrap token required. Получите у администратора и положите "
            f"в {BASE_DIR / 'bootstrap.txt'}")

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
    try:
        (BASE_DIR / "bootstrap.txt").unlink(missing_ok=True)
    except OSError:
        pass
    log.info("Registered as %s (secret_version=%s)", uid, data.get("secret_version"))
    return uid


def get_computer_uid() -> str | None:
    return _safe_keyring_get("computer_uid")
```

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

### `client/sync.py`

```python
import json
import logging
import time

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

    def run(self):
        self._running = True
        while self._running:
            try:
                if not self._sync_sessions():
                    break
                if not self._sync_records():
                    break
                db.enforce_size_limit()
            except Exception as e:
                log.warning("sync failed: %s", e)
                self.server_down.emit()
            end = time.time() + SYNC_INTERVAL
            while self._running and time.time() < end:
                time.sleep(0.5)

    def stop(self):
        self._running = False

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
            "record_uid": r["record_uid"], "session_uid": r["session_uid"],
            "kind": r["kind"], "data": json.loads(r["data"]),
            "client_ts": r["client_ts"], "signature": r["signature"],
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
```

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

### `client/build.spec`

```python
import os

_hidden = [
    'pynput.keyboard._win32', 'pynput.mouse._win32',
    'pynput.keyboard._xorg', 'pynput.mouse._xorg',
    'keyring.backends.Windows', 'keyring.backends.SecretService',
    'keyring.backends.kwallet', 'keyring.backends.libsecret',
    'cryptography', 'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.backends.openssl.backend',
]

_datas = [(f, '.') for f in ('icon.ico',) if os.path.exists(f)]
_ver = {'version': 'version_info.txt'} if os.path.exists('version_info.txt') else {}
_icon = 'icon.ico' if os.path.exists('icon.ico') else None

a = Analysis(['main.py'], pathex=['.'], binaries=[], datas=_datas,
             hiddenimports=_hidden, hookspath=[], runtime_hooks=[],
             excludes=[], noarchive=False)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='Tracker',
          debug=False, strip=False, upx=False, console=False,
          icon=_icon, **_ver)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
               strip=False, upx=False, name='Tracker')
```

### `client/version_info.txt`

```
VSVersionInfo(
  ffi=FixedFileInfo(filevers=(1,2,0,0), prodvers=(1,2,0,0),
                    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1,
                    subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
        StringStruct('CompanyName', 'Your Company LLC'),
        StringStruct('FileDescription', 'Employee Tracker Client'),
        StringStruct('FileVersion', '1.2.0.0'),
        StringStruct('InternalName', 'Tracker'),
        StringStruct('LegalCopyright', '© Your Company LLC'),
        StringStruct('OriginalFilename', 'Tracker.exe'),
        StringStruct('ProductName', 'Tracker'),
        StringStruct('ProductVersion', '1.2.0.0'),
    ])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
```

---

