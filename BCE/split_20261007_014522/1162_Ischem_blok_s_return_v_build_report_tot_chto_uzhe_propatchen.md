<!-- Часть 1162 из 1409 -->
# Ищем блок с return в _build_report (тот, что уже пропатчен)
*Хлебные крошки:* Ищем блок с return в _build_report (тот, что уже пропатчен)

[◀ ============================================================](1161_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1163_part.md)

---

# Ищем блок с return в _build_report (тот, что уже пропатчен)
old_return = '''    matrix = _build_program_employee_matrix(flat)
    for a in top_apps:
        a["by_employee"] = matrix.get(a["app"], [])

    return {
        "group_by": group_by, "date_from": date_from, "date_to": date_to,
        "tz_name": str(tz), "workday_start_hour": workday_start_hour,
        "rows": rows,
        "totals": {'''

new_return = '''    matrix = _build_program_employee_matrix(flat)
    for a in top_apps:
        a["by_employee"] = matrix.get(a["app"], [])

    # ---- Статистика фильтра (для строки контекста) ----
    emp_ids_in_flat = {r["employee_id"] for r in flat if r.get("employee_id")}
    dept_names = {r.get("department_name") for r in flat
                  if r.get("department_name") and r["department_name"] != "—"}
    stats = {
        "employees_count": len(emp_ids_in_flat),
        "departments_count": len(dept_names),
    }

    # ---- Сессии без привязки к сотруднику ----
    # Группируем по computer_id, собираем: hostname, UID, кол-во сессий,
    # суммарный span, первая и последняя даты.
    unattached_map = {}
    for r in flat:
        if r.get("employee_id"):
            continue
        comp_id = r.get("computer_id")
        if not comp_id:
            continue
        u = unattached_map.setdefault(comp_id, {
            "computer_id": comp_id,
            "hostname": None,
            "computer_uid": "",
            "sessions_count": 0,
            "worked_span_duration": 0,
            "first_session_local": None,
            "last_session_local": None,
            "_sessions": [],
        })
        u["sessions_count"] += 1
        u["_sessions"].append(r)
        if (u["first_session_local"] is None
                or r["start_local"] < u["first_session_local"]):
            u["first_session_local"] = r["start_local"]
        if (u["last_session_local"] is None
                or r["end_local"] > u["last_session_local"]):
            u["last_session_local"] = r["end_local"]

    # Подтягиваем hostname/uid для всех таких ПК одним запросом
    if unattached_map:
        comps = (db.query(Computer)
                 .filter(Computer.id.in_(list(unattached_map.keys())))
                 .all())
        for c in comps:
            u = unattached_map.get(c.id)
            if u:
                u["hostname"] = c.hostname
                u["computer_uid"] = c.computer_uid or ""

    # Считаем span для каждой группы (табель: первая?последняя)
    for u in unattached_map.values():
        if u["first_session_local"] and u["last_session_local"]:
            u["worked_span_duration"] = max(
                0, int((u["last_session_local"]
                        - u["first_session_local"]).total_seconds()))
        del u["_sessions"]

    unattached = sorted(unattached_map.values(),
                        key=lambda x: x["sessions_count"], reverse=True)

    # ---- Все активные сотрудники — для dropdown в блоке «Без привязки» ----
    all_employees = (db.query(Employee)
                     .filter(Employee.fired_at.is_(None))
                     .order_by(Employee.last_name, Employee.first_name)
                     .all())

    return {
        "group_by": group_by, "date_from": date_from, "date_to": date_to,
        "tz_name": str(tz), "workday_start_hour": workday_start_hour,
        "rows": rows,
        "stats": stats,
        "unattached": unattached,
        "all_employees": all_employees,
        "totals": {'''

if old_return in content:
    content = content.replace(old_return, new_return, 1)
    changes.append("_build_report расширен (stats, unattached, all_employees)")
elif '"unattached": unattached' in content:
    changes.append("SKIP: _build_report уже расширен")
else:
    changes.append("ERROR: не найден блок return в _build_report")

