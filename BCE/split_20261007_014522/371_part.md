<!-- Часть 371 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Компьютеры](370_Kompyutery.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](372_part.md)

---

# ============================================================

@router.get("/computers", response_class=HTMLResponse)
def computers_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).all()
    employees = (db.query(Employee)
                 .filter(Employee.fired_at.is_(None))
                 .order_by(Employee.last_name).all())
    return templates.TemplateResponse("computers.html", {
        "request": request, "computers": computers, "employees": employees,
        "admin": request.session.get("admin"), "tz": tz,
    })


@router.post("/computers/{comp_id}/assign")
def computer_assign(comp_id: int, employee_id: Optional[str] = Form(None),
                    db: Session = Depends(get_db), _=Depends(current_admin)):
    comp = db.query(Computer).get(comp_id)
    if not comp:
        raise HTTPException(404)
    emp_id = int(employee_id) if employee_id else None
    old = comp.employee_id
    comp.employee_id = emp_id
    comp.assigned_at = _now()
    db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id),
                    action="assign", old_value=str(old), new_value=str(emp_id)))
    db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


@router.post("/computers/{comp_id}/revoke")
def computer_revoke(comp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    comp = db.query(Computer).get(comp_id)
    if comp:
        comp.is_active = False
        db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id), action="revoke"))
        db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


@router.post("/computers/{comp_id}/activate")
def computer_activate(comp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    comp = db.query(Computer).get(comp_id)
    if comp:
        comp.is_active = True
        db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id), action="activate"))
        db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


