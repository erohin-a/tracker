<!-- Часть 1200 из 1409 -->
# === 2. Endpoint /admin/api/pivot-data ===
*Хлебные крошки:* === 2. Endpoint /admin/api/pivot-data ===

[◀ === 1. Функция _build_pivot_data ===](1199_1_Funktsiya_build_pivot_data.md) | [Оглавление](00_BCE_INDEX.md) | [=== 3. Route /admin/reports/pivot === ▶](1201_3_Route_admin_reports_pivot.md)

---

# === 2. Endpoint /admin/api/pivot-data ===
new_endpoint = '''@router.post("/api/pivot-data")
def pivot_data(
    request: Request,
    employee_ids: List[str] = Form(default=[]),
    department_ids: List[str] = Form(default=[]),
    computer_ids: List[str] = Form(default=[]),
    date_from: str = Form(...),
    date_to: str = Form(...),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    """Возвращает плоские строки для pivot-таблицы (JSON)."""
    try:
        d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(400, f"Неверный формат даты: {e}")
    if d_to < d_from:
        raise HTTPException(400, "date_to < date_from")
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    emp_ids = [int(x) for x in employee_ids if x and x.isdigit()] or None
    dep_ids = [int(x) for x in department_ids if x and x.isdigit()] or None
    comp_ids = [int(x) for x in computer_ids if x and x.isdigit()] or None
    rows = _build_pivot_data(db, emp_ids, dep_ids, comp_ids, d_from, d_to,
                              tz, cfg["workday_start_hour"])
    return {
        "rows": rows,
        "total": len(rows),
        "date_from": date_from,
        "date_to": date_to,
    }


'''

anchor2 = '@router.post("/reports/generate")'
if anchor2 not in content:
    print("ERROR: не найден /reports/generate")
    raise SystemExit(1)
content = content.replace(anchor2, new_endpoint + anchor2, 1)

