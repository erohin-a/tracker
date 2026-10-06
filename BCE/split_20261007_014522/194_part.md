<!-- Часть 194 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Утилиты](193_Utility.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](195_part.md)

---

# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_admin(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=401, detail="not authenticated")
    return request.session["admin"]


def _now():
    return datetime.now(timezone.utc)


def _hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def _resolve_tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        try:
            return ZoneInfo(settings.report_timezone)
        except Exception:
            return ZoneInfo("UTC")


def _to_local(dt: Optional[datetime], tz: ZoneInfo) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)


def _fmt_dt_local(dt: Optional[datetime], tz: ZoneInfo) -> str:
    if dt is None:
        return "—"
    return _to_local(dt, tz).strftime("%d.%m.%Y %H:%M")


def _fmt_dur(seconds: int) -> str:
    if not seconds:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


templates.env.filters["dur"] = _fmt_dur


def _available_timezones():
    return [
        ("Europe/Moscow", "Москва (UTC+3)"),
        ("Europe/Kaliningrad", "Калининград (UTC+2)"),
        ("Asia/Yekaterinburg", "Екатеринбург (UTC+5)"),
        ("Asia/Novosibirsk", "Новосибирск (UTC+7)"),
        ("Asia/Krasnoyarsk", "Красноярск (UTC+7)"),
        ("Asia/Irkutsk", "Иркутск (UTC+8)"),
        ("Asia/Vladivostok", "Владивосток (UTC+10)"),
        ("UTC", "UTC"),
    ]


