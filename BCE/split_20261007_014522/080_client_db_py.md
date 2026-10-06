<!-- Часть 80 из 1409 -->
# `client/db.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/db.py`

[◀ `client/crypto.py`](079_client_crypto_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/http_client.py` ▶](081_client_http_client_py.md)

---

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

