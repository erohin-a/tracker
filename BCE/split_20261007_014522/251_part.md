<!-- Часть 251 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Дашборд](250_Dashbord.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](252_part.md)

---

# ============================================================

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    today_local = datetime.now(tz).date()
    today_start_local = datetime.combine(today_local, time.min, tzinfo=tz)
    today_start_utc = today_start_local.astimezone(timezone.utc)
    week_ago_utc = today_start_utc - timedelta(days=7)

    stats = {
        "employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
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

    recent_computers = (
        db.query(Computer).order_by(desc(Computer.registered_at)).limit(10).all()
    )
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_computers": recent_computers,
        "recent_audit": recent_audit,
        "admin": request.session.get("admin"),
        "tz": tz,
    })


