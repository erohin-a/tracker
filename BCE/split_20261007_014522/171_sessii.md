<!-- Часть 171 из 1409 -->
# --- сессии ---
*Хлебные крошки:* --- сессии ---

[◀ ---------- Version ----------](170_Version.md) | [Оглавление](00_BCE_INDEX.md) | [--- записи --- ▶](172_zapisi.md)

---

# --- сессии ---

def start_session(uid: str):
    get_conn().execute(
        "INSERT OR IGNORE INTO sessions(session_uid, session_start, "
        "abnormal_termination, synced) VALUES(?,?,0,0)",
        (uid, _now_iso()),
    )
    set_meta("active_session", uid)
    set_meta("last_activity", _now_iso())


def touch_activity():
    set_meta("last_activity", _now_iso())


def close_session(uid: str, abnormal: bool = False):
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?",
        (_now_iso(), 1 if abnormal else 0, uid),
    )
    if get_meta("active_session") == uid:
        set_meta("active_session", "")


def get_active_session_uid():
    """UID незакрытой сессии, либо None."""
    return get_meta("active_session") or None


def get_session_start(uid: str):
    """ISO-строка начала сессии, либо None."""
    row = get_conn().execute(
        "SELECT session_start FROM sessions WHERE session_uid=?", (uid,)
    ).fetchone()
    return row["session_start"] if row else None


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


