<!-- Часть 435 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Дашборд](434_Dashbord.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](436_part.md)

---

# ============================================================

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    today_local = datetime.now(tz).date()
    today_start_utc = datetime.combine(today_local, time.min, tzinfo=tz).astimezone(timezone.utc)
    week_ago_utc = today_start_utc - timedelta(days=7)

    # Онлайн/оффлайн: считаем компьютер онлайн, если last_seen_at в пределах N минут
    heartbeat_window = 10
    cutoff_online = _now() - timedelta(minutes=heartbeat_window)

    stats = {
        "employees": db.query(Employee).filter(Employee.fired_at.is_(None)).count(),
        "departments": db.query(Department).filter(Department.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
        "computers_online": db.query(Computer).filter(
            Computer.is_active == True,
            Computer.last_seen_at >= cutoff_online,
        ).count(),
        "sessions_today": db.query(WorkSession).filter(
            WorkSession.session_start >= today_start_utc).count(),
        "sessions_week": db.query(WorkSession).filter(
            WorkSession.session_start >= week_ago_utc).count(),
        "records": db.query(Record).count(),
        "tokens_active": db.query(BootstrapToken).filter(
            BootstrapToken.used_at.is_(None),
            BootstrapToken.expires_at > _now(),
        ).count(),
    }

    recent_computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).limit(15).all()
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "stats": stats,
        "recent_computers": recent_computers, "recent_audit": recent_audit,
        "admin": request.session.get("admin"), "tz": tz,
        "heartbeat_window": heartbeat_window,
    })


