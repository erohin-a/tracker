<!-- Часть 438 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Настройки](437_Nastroyki.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](439_part.md)

---

# ============================================================

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    return templates.TemplateResponse("settings.html", {
        "request": request, "admin": request.session.get("admin"),
        "cfg": cfg,
        "timezones": _available_timezones(),
        "saved": request.query_params.get("saved") == "1",
    })


@router.post("/settings/save")
def settings_save(
    idle_close_minutes: int = Form(30),
    workday_start_hour: int = Form(6),
    activity_gap_minutes: int = Form(5),
    report_timezone: str = Form("Europe/Moscow"),
    sync_interval: int = Form(30),
    batch_size: int = Form(200),
    active_window_interval: int = Form(5),
    idle_threshold: int = Form(60),
    count_weekends: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    new_vals = {
        "idle_close_minutes": max(5, min(480, int(idle_close_minutes))),
        "workday_start_hour": max(0, min(23, int(workday_start_hour))),
        "activity_gap_minutes": max(1, min(120, int(activity_gap_minutes))),
        "report_timezone": report_timezone,
        "sync_interval": max(5, min(3600, int(sync_interval))),
        "batch_size": max(10, min(1000, int(batch_size))),
        "active_window_interval": max(1, min(60, int(active_window_interval))),
        "idle_threshold": max(10, min(3600, int(idle_threshold))),
        "count_weekends": "1" if count_weekends else "0",
    }
    for k, v in new_vals.items():
        old = get_app_setting(db, k, "")
        if str(old) != str(v):
            set_app_setting(db, k, str(v))
            db.add(AuditLog(actor="admin", entity="app_setting", entity_id=k,
                            action="update", old_value=str(old), new_value=str(v)))
    db.commit()
    return RedirectResponse("/admin/settings?saved=1", status_code=303)


