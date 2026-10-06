<!-- Часть 156 из 1409 -->
# ---------- Дашборд ----------
*Хлебные крошки:* ---------- Дашборд ----------

[◀ ---------- Логин / логаут ----------](155_Login_logaut.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Сотрудники ---------- ▶](157_Sotrudniki.md)

---

# ---------- Дашборд ----------

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    today = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
    week_ago = today - timedelta(days=7)

    stats = {
        "employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
        "sessions_today": db.query(WorkSession).filter(WorkSession.session_start >= today).count(),
        "sessions_week": db.query(WorkSession).filter(WorkSession.session_start >= week_ago).count(),
        "records": db.query(Record).count(),
        "tokens_active": db.query(BootstrapToken).filter(
            BootstrapToken.used_at.is_(None),
            BootstrapToken.expires_at > _now(),
        ).count(),
    }

    # последние 10 зарегистрированных ПК
    recent_computers = (
        db.query(Computer).order_by(desc(Computer.registered_at)).limit(10).all()
    )
    # последние 10 действий
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_computers": recent_computers,
        "recent_audit": recent_audit,
        "admin": request.session.get("admin"),
    })


