<!-- Часть 150 из 1409 -->
# ---------- Сотрудники ----------
*Хлебные крошки:* ---------- Сотрудники ----------

[◀ Computer add](149_Computer_add.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Компьютеры ---------- ▶](151_Kompyutery.md)

---

# ---------- Сотрудники ----------

@router.get("/employees", response_class=HTMLResponse)
def employees_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).order_by(Employee.last_name).all()
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees})


@router.post("/employees/create")
def employee_create(
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(""),
    external_id: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    full_name = " ".join(x for x in [last_name, first_name, middle_name] if x)
    emp = Employee(
        full_name=full_name,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name or None,
        external_id=external_id or None,
    )
    db.add(emp)
    db.add(AuditLog(actor="admin", entity="employee", action="create",
                    new_value=json.dumps({"full_name": full_name}, ensure_ascii=False)))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/deactivate")
def employee_deactivate(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.is_active = False
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id),
                        action="deactivate"))
        db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


