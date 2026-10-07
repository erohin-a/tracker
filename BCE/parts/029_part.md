# ============================================================

*Часть 29 из 100. Источник: `BCE.md`.*

[◀ --- 2. Проверяем связь ---](028_2_Proveryaem_svyaz.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](030_part.md)

---

# ============================================================

@router.get("/reports", response_class=HTMLResponse)
def reports_form(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tab = request.query_params.get("emp_tab", "active")
    q = db.query(Employee)
    if tab == "active":
        q = q.filter(Employee.fired_at.is_(None))
    elif tab == "fired":
        q = q.filter(Employee.fired_at.is_not(None))
    employees = q.order_by(Employee.last_name, Employee.first_name).all()

    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    computers = db.query(Computer).filter(Computer.is_active == True).order_by(Computer.hostname).all()

    # Карта для JS-фильтрации: employee_id -> department_id
    emp_dept_map = {e.id: e.department_id for e in employees}

    return templates.TemplateResponse("reports.html", {
        "request": request, "employees": employees, "computers": computers,
        "departments": departments,
        "emp_dept_map": emp_dept_map,
        "admin": request.session.get("admin"),
        "cfg": cfg,
        "today": date.today().isoformat(),
    })


def _load_records_for_sessions(db: Session, session_uids: list) -> dict:
    if not session_uids:
        return {}
    recs = (db.query(Record)
            .filter(Record.session_uid.in_(session_uids))
            .order_by(Record.client_ts).all())
    by_session = defaultdict(list)
    for r in recs:
        by_session[r.session_uid].append(r)
    return by_session


def _analyze_session(ws: WorkSession, recs, tz: ZoneInfo, gap_minutes: int) -> dict:
    start_local = _to_local(ws.session_start, tz)
    end_local = _to_local(ws.session_end or _now(), tz)

    first_event_local = None
    last_event_local = None
    gap = timedelta(minutes=gap_minutes)

    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    current_window = None
    current_window_started_local = None

    events = []
    for r in recs:
        try:
            data = json.loads(r.data) if r.data else {}
        except Exception:
            data = {}
        events.append({"ts_local": _to_local(r.client_ts, tz), "kind": r.kind, "data": data})
    events.sort(key=lambda x: x["ts_local"])

    for i, ev in enumerate(events):
        ts = ev["ts_local"]
        if first_event_local is None:
            first_event_local = ts
        last_event_local = ts
        kind = ev["kind"]
        data = ev["data"]

        if kind == "window":
            if current_window is not None and current_window_started_local is not None:
                dur = int((ts - current_window_started_local).total_seconds())
                if dur > 0:
                    app_stats[current_window]["seconds"] += dur
            app = data.get("app") or data.get("title") or "unknown"
            current_window = app
            current_window_started_local = ts
        elif kind == "activity":
            keys = int(data.get("keys", 0) or 0)
            clicks = int(data.get("clicks", 0) or 0)
            scroll = int(data.get("scroll", 0) or 0)
            if i > 0:
                delta = (ts - events[i - 1]["ts_local"]).total_seconds()
                if delta > gap.total_seconds():
                    if current_window is not None and current_window_started_local is not None:
                        dur = int((events[i - 1]["ts_local"] - current_window_started_local).total_seconds())
                        if dur > 0:
                            app_stats[current_window]["seconds"] += dur
                    current_window_started_local = ts
            if current_window is not None:
                if keys > 0:
                    app_stats[current_window]["keyboard"] += 5
                if clicks + scroll > 0:
                    app_stats[current_window]["mouse"] += 5

    if current_window is not None and current_window_started_local is not None and last_event_local is not None:
        dur = int((last_event_local - current_window_started_local).total_seconds())
        if dur > 0:
            app_stats[current_window]["seconds"] += dur

    if first_event_local and last_event_local:
        effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
    else:
        effective_duration = 0

    full_duration = max(0, int((end_local - start_local).total_seconds()))

    top_apps = sorted(
        [{"app": k, "seconds": v["seconds"], "keyboard": v["keyboard"], "mouse": v["mouse"]}
         for k, v in app_stats.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:15]

    return {
        "session_uid": ws.session_uid,
        "start_local": start_local,
        "end_local": end_local,
        "date_local": start_local.date(),
        "full_duration": full_duration,
        "effective_duration": effective_duration,
        "keyboard": sum(v["keyboard"] for v in app_stats.values()),
        "mouse": sum(v["mouse"] for v in app_stats.values()),
        "abnormal": bool(ws.abnormal_termination),
        "top_apps": top_apps,
        "employee_id": ws.employee_id,
        "computer_id": ws.computer_id,
    }


def _build_flat_records(db, employee_ids, department_ids, computer_ids,
                        date_from, date_to, tz, workday_start_hour):
    start_local = datetime.combine(date_from, time.min, tzinfo=tz)
    end_local = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=tz)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    q = (db.query(WorkSession)
         .filter(WorkSession.session_start >= start_utc,
                 WorkSession.session_start < end_utc))
    if employee_ids:
        q = q.filter(WorkSession.employee_id.in_(employee_ids))
    if department_ids:
        emp_ids_in_dept = [e.id for e in db.query(Employee)
                           .filter(Employee.department_id.in_(department_ids)).all()]
        q = q.filter(WorkSession.employee_id.in_(emp_ids_in_dept or [-1]))
    if computer_ids:
        q = q.filter(WorkSession.computer_id.in_(computer_ids))

    sessions = q.order_by(WorkSession.session_start).all()
    if not sessions:
        return []

    session_uids = [ws.session_uid for ws in sessions]
    recs_by_session = _load_records_for_sessions(db, session_uids)

    emp_ids = {ws.employee_id for ws in sessions if ws.employee_id}
    comp_ids = {ws.computer_id for ws in sessions if ws.computer_id}
    employees = {e.id: e for e in db.query(Employee).filter(Employee.id.in_(emp_ids)).all()} if emp_ids else {}
    computers = {c.id: c for c in db.query(Computer).filter(Computer.id.in_(comp_ids)).all()} if comp_ids else {}
    departments = {d.id: d for d in db.query(Department).all()}

    cfg = get_settings_dict(db)
    flat = []
    for ws in sessions:
        info = _analyze_session(ws, recs_by_session.get(ws.session_uid, []), tz,
                                cfg["activity_gap_minutes"])
        emp = employees.get(ws.employee_id) if ws.employee_id else None
        comp = computers.get(ws.computer_id)
        dept = departments.get(emp.department_id) if emp and emp.department_id else None
        info["employee_name"] = emp.full_name if emp else "— не привязан —"
        info["external_id"] = emp.external_id if emp else None
        info["department_name"] = dept.name if dept else "—"
        info["fired"] = bool(emp and emp.fired_at) if emp else False
        info["computer_name"] = (comp.hostname or comp.computer_uid) if comp else "—"
        info["workday_date"] = _workday_date(info["start_local"], workday_start_hour)
        flat.append(info)
    return flat


def _span_of_sessions(sessions: list) -> int:
    if not sessions:
        return 0
    first = min(s["start_local"] for s in sessions)
    last = max(s["end_local"] for s in sessions)
    return max(0, int((last - first).total_seconds()))


def _merge_apps(target: dict, source_apps: list) -> None:
    for a in source_apps:
        t = target[a["app"]]
        t["seconds"] += a["seconds"]
        t["keyboard"] += a["keyboard"]
        t["mouse"] += a["mouse"]


def _apps_to_list(app_dict: dict, limit: int = 15) -> list:
    return sorted(
        [{"app": k, **v} for k, v in app_dict.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:limit]


def _aggregate_group(sessions: list, extra_fields: dict) -> dict:
    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    for s in sessions:
        _merge_apps(app_stats, s["top_apps"])
    result = {
        **extra_fields,
        "sessions_count": len(sessions),
        "effective_duration": sum(s["effective_duration"] for s in sessions),
        "keyboard": sum(s["keyboard"] for s in sessions),
        "mouse": sum(s["mouse"] for s in sessions),
        "abnormal": any(s["abnormal"] for s in sessions),
        "worked_duration": _span_of_sessions(sessions),
        "top_apps": _apps_to_list(app_stats),
        "sessions": sessions,
    }
    return result


def _split_by_day(flat: list) -> list:
    groups = {}
    for r in flat:
        key = (r["workday_date"], r["employee_id"])
        g = groups.setdefault(key, {"_sessions": [], "date": r["workday_date"],
                                    "employee_name": r["employee_name"],
                                    "external_id": r["external_id"],
                                    "department_name": r["department_name"],
                                    "fired": r["fired"]})
        g["_sessions"].append(r)
    result = []
    for g in groups.values():
        sessions = g.pop("_sessions")
        result.append(_aggregate_group(sessions, g))
    result.sort(key=lambda x: (x["date"], x["employee_name"]), reverse=True)
    return result


def _split_by_month(flat: list) -> list:
    groups = {}
    for r in flat:
        d = r["workday_date"]
        key = (d.year, d.month, r["employee_id"])
        g = groups.setdefault(key, {"_sessions": [], "year": d.year, "month": d.month,
                                    "month_name": RU_MONTHS[d.month],
                                    "employee_name": r["employee_name"],
                                    "external_id": r["external_id"],
                                    "department_name": r["department_name"],
                                    "fired": r["fired"]})
        g["_sessions"].append(r)
    result = []
    for g in groups.values():
        sessions = g.pop("_sessions")
        agg = _aggregate_group(sessions, g)
        agg["days_count"] = len({s["workday_date"] for s in sessions})
        result.append(agg)
    result.sort(key=lambda x: (x["year"], x["month"], x["employee_name"]), reverse=True)
    return result


def _group_by_employee(flat: list) -> list:
    by_day = defaultdict(list)
    for r in flat:
        by_day[(r["employee_id"], r["workday_date"])].append(r)
    emp_days = defaultdict(list)
    for (emp_id, day), sessions in by_day.items():
        emp_days[emp_id].append({
            "day": day, "sessions": sessions,
            "span": _span_of_sessions(sessions),
            "effective": sum(s["effective_duration"] for s in sessions),
        })

    result = []
    for emp_id, days in emp_days.items():
        all_sessions = []
        for d in days:
            all_sessions.extend(d["sessions"])
        first = all_sessions[0] if all_sessions else None
        agg = _aggregate_group(all_sessions, {
            "employee_name": first["employee_name"] if first else "—",
            "external_id": first["external_id"] if first else None,
            "department_name": first["department_name"] if first else "—",
            "fired": first["fired"] if first else False,
            "days_count": len(days),
        })
        agg["worked_duration"] = sum(d["span"] for d in days)
        result.append(agg)
    result.sort(key=lambda x: x["effective_duration"], reverse=True)
    return result


def _group_by_department(flat: list) -> list:
    groups = defaultdict(list)
    for r in flat:
        groups[r["department_name"]].append(r)
    result = []
    for dept, sessions in groups.items():
        agg = _aggregate_group(sessions, {"department_name": dept})
        agg["days_count"] = len({s["workday_date"] for s in sessions})
        agg["employees_count"] = len({s["employee_id"] for s in sessions})
        result.append(agg)
    result.sort(key=lambda x: x["effective_duration"], reverse=True)
    return result


def _group_by_computer(flat: list) -> list:
    groups = defaultdict(list)
    for r in flat:
        groups[r["computer_name"]].append(r)
    result = []
    for comp, sessions in groups.items():
        agg = _aggregate_group(sessions, {"computer_name": comp})
        agg["days_count"] = len({s["workday_date"] for s in sessions})
        result.append(agg)
    result.sort(key=lambda x: x["effective_duration"], reverse=True)
    return result


def _group_by_session(flat: list) -> list:
    result = []
    for r in flat:
        result.append({
            "session_uid": r["session_uid"], "date": r["workday_date"],
            "employee_name": r["employee_name"], "external_id": r["external_id"],
            "department_name": r["department_name"], "fired": r["fired"],
            "computer_name": r["computer_name"],
            "start_local": r["start_local"], "end_local": r["end_local"],
            "worked_duration": r["full_duration"],
            "effective_duration": r["effective_duration"],
            "keyboard": r["keyboard"], "mouse": r["mouse"],
            "abnormal": r["abnormal"], "top_apps": r["top_apps"], "sessions": [],
        })
    result.sort(key=lambda x: x["start_local"], reverse=True)
    return result


def _build_program_employee_matrix(flat: list) -> dict:
    matrix = defaultdict(lambda: defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}))
    for r in flat:
        emp_key = (r["employee_name"], r.get("external_id") or "")
        for a in r["top_apps"]:
            m = matrix[a["app"]][emp_key]
            m["seconds"] += a["seconds"]
            m["keyboard"] += a["keyboard"]
            m["mouse"] += a["mouse"]
    result = {}
    for app, emps in matrix.items():
        rows = []
        for (name, ext_id), stats in emps.items():
            rows.append({"employee_name": name, "external_id": ext_id,
                         "seconds": stats["seconds"], "keyboard": stats["keyboard"],
                         "mouse": stats["mouse"]})
        rows.sort(key=lambda x: x["seconds"], reverse=True)
        result[app] = rows
    return result


def _build_report(db, employee_ids, department_ids, computer_ids,
                  date_from, date_to, group_by, tz, workday_start_hour):
    flat = _build_flat_records(db, employee_ids, department_ids, computer_ids,
                               date_from, date_to, tz, workday_start_hour)

    if group_by == "days":
        rows = _split_by_day(flat)
    elif group_by == "months":
        rows = _split_by_month(flat)
    elif group_by == "employees":
        rows = _group_by_employee(flat)
    elif group_by == "departments":
        rows = _group_by_department(flat)
    elif group_by == "computers":
        rows = _group_by_computer(flat)
    else:
        rows = _group_by_session(flat)

    total_worked = sum(r.get("worked_duration", 0) for r in rows)
    total_effective = sum(r.get("effective_duration", 0) for r in rows)
    total_keyboard = sum(r.get("keyboard", 0) for r in rows)
    total_mouse = sum(r.get("mouse", 0) for r in rows)
    total_abnormal = sum(1 for r in rows if r.get("abnormal"))

    app_totals = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    for r in flat:
        for a in r["top_apps"]:
            app_totals[a["app"]]["seconds"] += a["seconds"]
            app_totals[a["app"]]["keyboard"] += a["keyboard"]
            app_totals[a["app"]]["mouse"] += a["mouse"]
    top_apps = _apps_to_list(app_totals, limit=20)

    matrix = _build_program_employee_matrix(flat)
    for a in top_apps:
        a["by_employee"] = matrix.get(a["app"], [])

    return {
        "group_by": group_by, "date_from": date_from, "date_to": date_to,
        "tz_name": str(tz), "workday_start_hour": workday_start_hour,
        "rows": rows,
        "totals": {
            "sessions": len(flat), "worked_duration": total_worked,
            "effective_duration": total_effective, "keyboard": total_keyboard,
            "mouse": total_mouse, "abnormal": total_abnormal, "top_apps": top_apps,
        },
    }


def _hms_to_excel(seconds: int):
    from datetime import timedelta as _td
    return _td(seconds=seconds)


@router.post("/reports/generate")
def reports_generate(
    request: Request,
    employee_ids: List[str] = Form(default=[]),
    department_ids: List[str] = Form(default=[]),
    computer_ids: List[str] = Form(default=[]),
    date_from: str = Form(...),
    date_to: str = Form(...),
    group_by: str = Form("days"),
    fmt: str = Form("html"),
    show_apps: str = Form(""),
    show_abnormal: str = Form(""),
    expand_details: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    if d_to < d_from:
        raise HTTPException(400, "date_to < date_from")

    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    workday_start_hour = cfg["workday_start_hour"]

    emp_ids = [int(x) for x in employee_ids if x and x.isdigit()] or None
    dep_ids = [int(x) for x in department_ids if x and x.isdigit()] or None
    comp_ids = [int(x) for x in computer_ids if x and x.isdigit()] or None

    report = _build_report(db, emp_ids, dep_ids, comp_ids, d_from, d_to,
                           group_by, tz, workday_start_hour)

    if fmt == "csv":
        return _render_csv(report, date_from, date_to)
    if fmt == "xlsx":
        return _render_xlsx(report, date_from, date_to)

    return templates.TemplateResponse("report_result.html", {
        "request": request, "report": report,
        "admin": request.session.get("admin"),
        "show_apps": bool(show_apps),
        "show_abnormal": bool(show_abnormal),
        "expand_details": bool(expand_details),
    })


def _render_csv(report: dict, date_from: str, date_to: str):
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    headers = ["Рабочий день", "Год", "Месяц", "Число",
               "Сотрудник", "1C ID", "Отдел", "Компьютер",
               "Сессий", "Отработано", "Эффективно"]
    writer.writerow(headers)
    for r in report["rows"]:
        writer.writerow(_report_row_to_list(r, report["group_by"]))
    t = report["totals"]
    writer.writerow(["ИТОГО", "", "", "", "", "", "", "",
                     t["sessions"], _fmt_dur(t["worked_duration"]),
                     _fmt_dur(t["effective_duration"])])
    output.seek(0)
    data = "\ufeff" + output.getvalue()
    return StreamingResponse(
        iter([data]), media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.csv"},
    )


def _render_xlsx(report: dict, date_from: str, date_to: str):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "Report"

    headers = ["Рабочий день", "Год", "Месяц", "Число",
               "Сотрудник", "1C ID", "Отдел", "Компьютер",
               "Сессий", "Отработано", "Эффективно"]
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="343A40")
        c.alignment = Alignment(horizontal="center")

    for r in report["rows"]:
        row_data = _report_row_to_xlsx(r, report["group_by"])
        ws.append(row_data)
        last_row = ws.max_row
        # Колонки 10 и 11 (J, K) — длительности
        ws.cell(row=last_row, column=10).number_format = "[HH]:MM:SS"
        ws.cell(row=last_row, column=11).number_format = "[HH]:MM:SS"

    t = report["totals"]
    ws.append(["ИТОГО", "", "", "", "", "", "", "",
               t["sessions"],
               _hms_to_excel(t["worked_duration"]),
               _hms_to_excel(t["effective_duration"])])
    last_row = ws.max_row
    ws.cell(row=last_row, column=10).number_format = "[HH]:MM:SS"
    ws.cell(row=last_row, column=11).number_format = "[HH]:MM:SS"
    for c in ws[last_row]:
        c.font = Font(bold=True)

    for col in ws.columns:
        length = max((len(str(c.value)) for c in col if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(length + 2, 60)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.xlsx"},
    )


def _row_date_parts(r: dict):
    """Возвращает (дата_или_None, год, месяц_название, число)."""
    d = r.get("date")
    if d is None:
        # Для группировок без конкретной даты
        return (None, r.get("year"), r.get("month_name"), None)
    return (d, d.year, RU_MONTHS[d.month], d.day)


def _report_row_to_list(r: dict, group_by: str) -> list:
    d, year, month_name, day = _row_date_parts(r)
    if group_by in ("days", "months"):
        return [
            d.strftime("%d.%m.%Y") if d else "",
            year or "", month_name or "", day or "",
            r.get("employee_name", ""), r.get("external_id") or "",
            r.get("department_name") or "", "",
            r.get("sessions_count", 0),
            _fmt_dur(r.get("worked_duration", 0)),
            _fmt_dur(r.get("effective_duration", 0)),
        ]
    if group_by == "employees":
        return [
            "", "", "", "",
            r.get("employee_name", ""), r.get("external_id") or "",
            r.get("department_name") or "", "",
            r.get("sessions_count", 0),
            _fmt_dur(r.get("worked_duration", 0)),
            _fmt_dur(r.get("effective_duration", 0)),
        ]
    if group_by == "departments":
        return [
            "", "", "", "",
            "", "", r.get("department_name", ""), "",
            r.get("sessions_count", 0),
            _fmt_dur(r.get("worked_duration", 0)),
            _fmt_dur(r.get("effective_duration", 0)),
        ]
    if group_by == "computers":
        return [
            "", "", "", "",
            "", "", "", r.get("computer_name", ""),
            r.get("sessions_count", 0),
            _fmt_dur(r.get("worked_duration", 0)),
            _fmt_dur(r.get("effective_duration", 0)),
        ]
    # sessions
    return [
        d.strftime("%d.%m.%Y") if d else "",
        year or "", month_name or "", day or "",
        r.get("employee_name", ""), r.get("external_id") or "",
        r.get("department_name") or "", r.get("computer_name", ""),
        1,
        _fmt_dur(r.get("worked_duration", 0)),
        _fmt_dur(r.get("effective_duration", 0)),
    ]


def _report_row_to_xlsx(r: dict, group_by: str) -> list:
    d, year, month_name, day = _row_date_parts(r)
    if group_by in ("days", "months"):
        return [
            d if d else "",
            year or "", month_name or "", day or "",
            r.get("employee_name", ""), r.get("external_id") or "",
            r.get("department_name") or "", "",
            r.get("sessions_count", 0),
            _hms_to_excel(r.get("worked_duration", 0)),
            _hms_to_excel(r.get("effective_duration", 0)),
        ]
    if group_by == "employees":
        return [
            "", "", "", "",
            r.get("employee_name", ""), r.get("external_id") or "",
            r.get("department_name") or "", "",
            r.get("sessions_count", 0),
            _hms_to_excel(r.get("worked_duration", 0)),
            _hms_to_excel(r.get("effective_duration", 0)),
        ]
    if group_by == "departments":
        return [
            "", "", "", "",
            "", "", r.get("department_name", ""), "",
            r.get("sessions_count", 0),
            _hms_to_excel(r.get("worked_duration", 0)),
            _hms_to_excel(r.get("effective_duration", 0)),
        ]
    if group_by == "computers":
        return [
            "", "", "", "",
            "", "", "", r.get("computer_name", ""),
            r.get("sessions_count", 0),
            _hms_to_excel(r.get("worked_duration", 0)),
            _hms_to_excel(r.get("effective_duration", 0)),
        ]
    return [
        d if d else "",
        year or "", month_name or "", day or "",
        r.get("employee_name", ""), r.get("external_id") or "",
        r.get("department_name") or "", r.get("computer_name", ""),
        1,
        _hms_to_excel(r.get("worked_duration", 0)),
        _hms_to_excel(r.get("effective_duration", 0)),
    ]


# ============================================================
# Аудит
