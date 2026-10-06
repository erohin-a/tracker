<!-- Часть 444 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Сотрудники](443_Sotrudniki.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](445_part.md)

---

# ============================================================

@router.get("/employees", response_class=HTMLResponse)
def employees_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tab = request.query_params.get("tab", "active")
    q = db.query(Employee)
    if tab == "active":
        q = q.filter(Employee.fired_at.is_(None))
    elif tab == "fired":
        q = q.filter(Employee.fired_at.is_not(None))
    employees = q.order_by(Employee.last_name, Employee.first_name).all()
    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    return templates.TemplateResponse("employees.html", {
        "request": request, "employees": employees, "departments": departments,
        "admin": request.session.get("admin"), "tab": tab,
    })


@router.post("/employees/create")
def employee_create(
    last_name: str = Form(...), first_name: str = Form(...),
    middle_name: str = Form(""), external_id: str = Form(""),
    department_id: str = Form(""),
    db: Session = Depends(get_db), _=Depends(current_admin),
):
    last_name, first_name = last_name.strip(), first_name.strip()
    middle_name = middle_name.strip()
    external_id = external_id.strip()
    if not last_name or not first_name:
        raise HTTPException(400, "Фамилия и имя обязательны")
    full_name = " ".join(x for x in [last_name, first_name, middle_name] if x)
    emp = Employee(
        full_name=full_name, last_name=last_name, first_name=first_name,
        middle_name=middle_name or None, external_id=external_id or None,
        department_id=int(department_id) if department_id else None,
    )
    db.add(emp)
    db.flush()
    db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp.id),
                    action="create", new_value=json.dumps({"full_name": full_name}, ensure_ascii=False)))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/edit")
def employee_edit(
    emp_id: int, last_name: str = Form(...), first_name: str = Form(...),
    middle_name: str = Form(""), external_id: str = Form(""),
    department_id: str = Form(""),
    db: Session = Depends(get_db), _=Depends(current_admin),
):
    emp = db.query(Employee).get(emp_id)
    if not emp:
        raise HTTPException(404)
    old = emp.full_name
    emp.last_name = last_name.strip()
    emp.first_name = first_name.strip()
    emp.middle_name = middle_name.strip() or None
    emp.external_id = external_id.strip() or None
    emp.department_id = int(department_id) if department_id else None
    emp.full_name = " ".join(x for x in [emp.last_name, emp.first_name, emp.middle_name] if x)
    db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id),
                    action="edit", old_value=old, new_value=emp.full_name))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/fire")
def employee_fire(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.fired_at = _now()
        emp.is_active = False
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="fire"))
        db.commit()
    return RedirectResponse("/admin/employees?tab=fired", status_code=303)


@router.post("/employees/{emp_id}/restore")
def employee_restore(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.fired_at = None
        emp.is_active = True
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="restore"))
        db.commit()
    return RedirectResponse("/admin/employees?tab=active", status_code=303)


