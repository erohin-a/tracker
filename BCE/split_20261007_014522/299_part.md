<!-- Часть 299 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Утилиты](298_Utility.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](300_part.md)

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


def get_app_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else default


def set_app_setting(db: Session, key: str, value: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row:
        row.value = value
    else:
        db.add(AppSetting(key=key, value=value))


def get_idle_close_minutes(db: Session) -> int:
    try:
        return max(5, min(480, int(get_app_setting(db, "idle_close_minutes", "30"))))
    except (ValueError, TypeError):
        return 30


def _resolve_tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        try:
            return ZoneInfo(settings.report_timezone)
        except Exception:
            return ZoneInfo("UTC")


def _to_local(dt, tz: ZoneInfo):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)


def _fmt_dur(seconds: int) -> str:
    if not seconds:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_dt_global(dt):
    if dt is None:
        return "—"
    try:
        tz = ZoneInfo(settings.report_timezone)
    except Exception:
        tz = ZoneInfo("UTC")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")


templates.env.filters["dur"] = _fmt_dur
templates.env.filters["dt"] = _fmt_dt_global


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


def _workday_date(start_local: datetime, workday_start_hour: int) -> date:
    if start_local.hour < workday_start_hour:
        return (start_local - timedelta(days=1)).date()
    return start_local.date()


