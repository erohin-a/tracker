<!-- Часть 1201 из 1409 -->
# === 3. Route /admin/reports/pivot ===
*Хлебные крошки:* === 3. Route /admin/reports/pivot ===

[◀ === 2. Endpoint /admin/api/pivot-data ===](1200_2_Endpoint_admin_api_pivot_data.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](1202_Proverka_sintaksisa.md)

---

# === 3. Route /admin/reports/pivot ===
new_route = '''@router.get("/reports/pivot", response_class=HTMLResponse)
def reports_pivot_page(request: Request, db: Session = Depends(get_db),
                        _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    employees = (db.query(Employee)
                 .filter(Employee.fired_at.is_(None))
                 .order_by(Employee.last_name, Employee.first_name)
                 .all())
    departments = (db.query(Department)
                   .filter(Department.is_active == True)
                   .order_by(Department.name)
                   .all())
    computers = (db.query(Computer)
                 .filter(Computer.is_active == True)
                 .order_by(Computer.hostname)
                 .all())
    emp_dept_map = {e.id: e.department_id for e in employees}
    return templates.TemplateResponse("reports_pivot.html", {
        "request": request,
        "employees": employees,
        "departments": departments,
        "computers": computers,
        "emp_dept_map": emp_dept_map,
        "admin": request.session.get("admin"),
        "cfg": cfg,
        "today": date.today().isoformat(),
    })


'''

anchor3 = '@router.get("/reports", response_class=HTMLResponse)'
if anchor3 not in content:
    print("ERROR: не найден /reports")
    raise SystemExit(1)
content = content.replace(anchor3, new_route + anchor3, 1)

PATH.write_text(content, encoding="utf-8")

