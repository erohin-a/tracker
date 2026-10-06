<!-- Часть 447 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Компьютеры](446_Kompyutery.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](448_part.md)

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
    heartbeat_window = 10
    cutoff_online = _now() - timedelta(minutes=heartbeat_window)
    return templates.TemplateResponse("computers.html", {
        "request": request, "computers": computers, "employees": employees,
        "admin": request.session.get("admin"), "tz": tz,
        "cutoff_online": cutoff_online,
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


@router.post("/computers/bulk-assign")
async def computers_bulk_assign(request: Request,
                                db: Session = Depends(get_db), _=Depends(current_admin)):
    """
    Массовая привязка ПК из CSV.
    Формат CSV (разделитель ; или ,): hostname; 1C_ID
    Или: hostname; ФИО
    """
    form = await request.form()
    file = form.get("csv_file")
    if not file:
        raise HTTPException(400, "Файл не загружен")

    raw = (await file.read()).decode("utf-8-sig", errors="replace")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

    # Определяем разделитель
    delimiter = ";"
    if lines and "," in lines[0] and ";" not in lines[0]:
        delimiter = ","

    header_skipped = False
    assigned = 0
    not_found_emp = []
    not_found_comp = []
    errors = []

    for i, ln in enumerate(lines):
        parts = [p.strip() for p in ln.split(delimiter)]
        if len(parts) < 2:
            errors.append(f"Строка {i+1}: < 2 колонок")
            continue
        hostname, key = parts[0], parts[1]

        # Пропускаем заголовок
        if not header_skipped and hostname.lower() in ("hostname", "пк", "компьютер"):
            header_skipped = True
            continue

        # Ищем сотрудника по 1C ID или ФИО
        emp = None
        if key:
            emp = db.query(Employee).filter(Employee.external_id == key).first()
            if not emp:
                emp = db.query(Employee).filter(Employee.full_name.ilike(f"%{key}%")).first()

        comp = db.query(Computer).filter(
            (Computer.hostname == hostname) | (Computer.computer_uid == hostname)
        ).first()

        if not comp:
            not_found_comp.append(hostname)
            continue
        if not emp:
            not_found_emp.append(key)
            continue

        comp.employee_id = emp.id
        comp.assigned_at = _now()
        assigned += 1

    db.add(AuditLog(actor="admin", entity="computer", action="bulk_assign",
                    new_value=json.dumps({"assigned": assigned,
                                          "not_found_comp": len(not_found_comp),
                                          "not_found_emp": len(not_found_emp)},
                                         ensure_ascii=False)))
    db.commit()

    msg = f"Привязано: {assigned}."
    if not_found_comp:
        msg += f" Не найдены ПК: {len(not_found_comp)} ({', '.join(not_found_comp[:5])})."
    if not_found_emp:
        msg += f" Не найдены сотрудники: {len(not_found_emp)} ({', '.join(not_found_emp[:5])})."
    if errors:
        msg += f" Ошибок в строках: {len(errors)}."

    return RedirectResponse(f"/admin/computers?bulk_msg={msg}", status_code=303)


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


