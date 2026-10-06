<!-- Часть 365 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Отделы](364_Otdely.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](366_part.md)

---

# ============================================================

@router.get("/departments", response_class=HTMLResponse)
def departments_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    deps = db.query(Department).order_by(Department.name).all()
    counts = dict(
        db.query(Employee.department_id, __import__("sqlalchemy").func.count(Employee.id))
        .filter(Employee.fired_at.is_(None))
        .group_by(Employee.department_id).all()
    )
    return templates.TemplateResponse("departments.html", {
        "request": request, "admin": request.session.get("admin"),
        "departments": deps, "counts": counts,
    })


@router.post("/departments/create")
def department_create(name: str = Form(...), db: Session = Depends(get_db), _=Depends(current_admin)):
    name = name.strip()
    if not name:
        raise HTTPException(400, "Название обязательно")
    if db.query(Department).filter(Department.name == name).first():
        raise HTTPException(400, "Отдел с таким именем уже есть")
    d = Department(name=name)
    db.add(d)
    db.add(AuditLog(actor="admin", entity="department", action="create", new_value=name))
    db.commit()
    return RedirectResponse("/admin/departments", status_code=303)


@router.post("/departments/{dep_id}/rename")
def department_rename(dep_id: int, name: str = Form(...),
                      db: Session = Depends(get_db), _=Depends(current_admin)):
    d = db.query(Department).get(dep_id)
    if not d:
        raise HTTPException(404)
    old = d.name
    d.name = name.strip()
    db.add(AuditLog(actor="admin", entity="department", entity_id=str(dep_id),
                    action="rename", old_value=old, new_value=d.name))
    db.commit()
    return RedirectResponse("/admin/departments", status_code=303)


@router.post("/departments/{dep_id}/delete")
def department_delete(dep_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    d = db.query(Department).get(dep_id)
    if d:
        db.query(Employee).filter(Employee.department_id == dep_id).update({"department_id": None})
        db.delete(d)
        db.add(AuditLog(actor="admin", entity="department", entity_id=str(dep_id), action="delete"))
        db.commit()
    return RedirectResponse("/admin/departments", status_code=303)


