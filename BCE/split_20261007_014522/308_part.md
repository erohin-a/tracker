<!-- Часть 308 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Настройки](307_Nastroyki.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](309_part.md)

---

# ============================================================

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    idle = get_idle_close_minutes(db)
    saved = request.query_params.get("saved") == "1"
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "admin": request.session.get("admin"),
        "idle_close_minutes": idle,
        "saved": saved,
    })


@router.post("/settings/save")
def settings_save(
    idle_close_minutes: int = Form(30),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    idle_close_minutes = max(5, min(480, int(idle_close_minutes)))
    old = get_app_setting(db, "idle_close_minutes", "30")
    set_app_setting(db, "idle_close_minutes", str(idle_close_minutes))
    db.add(AuditLog(
        actor="admin", entity="app_setting", entity_id="idle_close_minutes",
        action="update",
        old_value=old, new_value=str(idle_close_minutes),
    ))
    db.commit()
    return RedirectResponse("/admin/settings?saved=1", status_code=303)


