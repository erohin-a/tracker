# ============================================================

*Часть 22 из 100. Источник: `BCE.md`.*

[◀ date](021_date.md) | [Оглавление](00_BCE_INDEX.md) | [employees.html — с отделами и вкладками Активные/Уволенные ▶](023_employees_html_s_otdelami_i_vkladkami_Aktivnye_Uvolennye.md)

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
    return templates.TemplateResponse("reports.html", {
        "request": request, "employees": employees, "computers": computers,
        "departments": departments,
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


def _build_flat_records(db, employee_ids, department_id, computer_id,
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
    if department_id:
        emp_ids_in_dept = [e.id for e in db.query(Employee).filter(Employee.department_id == department_id).all()]
        q = q.filter(WorkSession.employee_id.in_(emp_ids_in_dept or [-1]))
    if computer_id:
        q = q.filter(WorkSession.computer_id == computer_id)

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


def _split_by_day(flat: list) -> list:
    groups = {}
    for r in flat:
        key = (r["workday_date"], r["employee_id"])
        g = groups.get(key)
        if g is None:
            g = {
                "date": r["workday_date"], "employee_name": r["employee_name"],
                "external_id": r["external_id"], "department_name": r["department_name"],
                "fired": r["fired"],
                "sessions_count": 0, "effective_duration": 0,
                "keyboard": 0, "mouse": 0, "abnormal": False,
                "app_stats": defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}),
                "sessions": [],
            }
            groups[key] = g
        g["sessions_count"] += 1
        g["effective_duration"] += r["effective_duration"]
        g["keyboard"] += r["keyboard"]
        g["mouse"] += r["mouse"]
        g["abnormal"] = g["abnormal"] or r["abnormal"]
        _merge_apps(g["app_stats"], r["top_apps"])
        g["sessions"].append(r)

    result = []
    for g in groups.values():
        g["worked_duration"] = _span_of_sessions(g["sessions"])
        g["top_apps"] = _apps_to_list(g["app_stats"])
        del g["app_stats"]
        result.append(g)
    result.sort(key=lambda x: (x["date"], x["employee_name"]), reverse=True)
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
        app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
        for d in days:
            all_sessions.extend(d["sessions"])
            for s in d["sessions"]:
                _merge_apps(app_stats, s["top_apps"])
        first = all_sessions[0] if all_sessions else None
        result.append({
            "employee_name": first["employee_name"] if first else "—",
            "external_id": first["external_id"] if first else None,
            "department_name": first["department_name"] if first else "—",
            "fired": first["fired"] if first else False,
            "sessions_count": len(all_sessions),
            "days_count": len(days),
            "worked_duration": sum(d["span"] for d in days),
            "effective_duration": sum(d["effective"] for d in days),
            "keyboard": sum(s["keyboard"] for s in all_sessions),
            "mouse": sum(s["mouse"] for s in all_sessions),
            "abnormal": any(s["abnormal"] for s in all_sessions),
            "top_apps": _apps_to_list(app_stats),
            "sessions": all_sessions,
        })
    result.sort(key=lambda x: x["effective_duration"], reverse=True)
    return result


def _group_by_computer(flat: list) -> list:
    by_day = defaultdict(list)
    for r in flat:
        by_day[(r["computer_id"], r["workday_date"])].append(r)
    comp_days = defaultdict(list)
    for (comp_id, day), sessions in by_day.items():
        comp_days[comp_id].append({
            "day": day, "sessions": sessions,
            "span": _span_of_sessions(sessions),
            "effective": sum(s["effective_duration"] for s in sessions),
        })

    result = []
    for comp_id, days in comp_days.items():
        all_sessions = []
        app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
        for d in days:
            all_sessions.extend(d["sessions"])
            for s in d["sessions"]:
                _merge_apps(app_stats, s["top_apps"])
        first = all_sessions[0] if all_sessions else None
        result.append({
            "computer_name": first["computer_name"] if first else "—",
            "sessions_count": len(all_sessions),
            "worked_duration": sum(d["span"] for d in days),
            "effective_duration": sum(d["effective"] for d in days),
            "keyboard": sum(s["keyboard"] for s in all_sessions),
            "mouse": sum(s["mouse"] for s in all_sessions),
            "abnormal": any(s["abnormal"] for s in all_sessions),
            "top_apps": _apps_to_list(app_stats),
            "sessions": all_sessions,
        })
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


def _build_report(db, employee_ids, department_id, computer_id,
                  date_from, date_to, group_by, tz, workday_start_hour):
    flat = _build_flat_records(db, employee_ids, department_id, computer_id,
                               date_from, date_to, tz, workday_start_hour)

    if group_by == "days":
        rows = _split_by_day(flat)
    elif group_by == "employees":
        rows = _group_by_employee(flat)
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
    """Excel-совместимое значение для отображения как времени."""
    from datetime import timedelta as _td
    return _td(seconds=seconds)


@router.post("/reports/generate")
def reports_generate(
    request: Request,
    employee_ids: List[str] = Form(default=[]),
    department_id: str = Form(""),
    computer_id: str = Form(""),
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
    dep_id = int(department_id) if department_id else None
    comp_id = int(computer_id) if computer_id else None

    report = _build_report(db, emp_ids, dep_id, comp_id, d_from, d_to,
                           group_by, tz, workday_start_hour)

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        headers = ["Группа", "Рабочий день", "Сотрудник", "1C ID", "Отдел",
                   "Компьютер", "Сессий", "Отработано", "Эффективно", "Аварийных"]
        writer.writerow(headers)
        for r in report["rows"]:
            writer.writerow(_report_row_to_list(r, report["group_by"]))
        t = report["totals"]
        writer.writerow(["ИТОГО", "", "", "", "", "",
                         t["sessions"], _fmt_dur(t["worked_duration"]),
                         _fmt_dur(t["effective_duration"]), t["abnormal"]])
        output.seek(0)
        data = "\ufeff" + output.getvalue()
        return StreamingResponse(
            iter([data]), media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.csv"},
        )

    if fmt == "xlsx":
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill

        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        headers = ["Группа", "Рабочий день", "Сотрудник", "1C ID", "Отдел",
                   "Компьютер", "Сессий", "Отработано", "Эффективно", "Аварийных"]
        ws.append(headers)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="343A40")
            c.alignment = Alignment(horizontal="center")

        for r in report["rows"]:
            row_data = _report_row_to_xlsx(r, report["group_by"])
            ws.append(row_data)
            # Форматирование последней добавленной строки
            last_row = ws.max_row
            # Длительности (колонки H, I = 8, 9)
            ws.cell(row=last_row, column=8).number_format = "[HH]:MM:SS"
            ws.cell(row=last_row, column=9).number_format = "[HH]:MM:SS"
            # Дата (колонка B = 2) — только если это дата
            date_cell = ws.cell(row=last_row, column=2)
            if isinstance(date_cell.value, date):
                date_cell.number_format = "DD.MM.YYYY"

        # Итоговая строка
        t = report["totals"]
        ws.append(["ИТОГО", "", "", "", "", "",
                   t["sessions"],
                   _hms_to_excel(t["worked_duration"]),
                   _hms_to_excel(t["effective_duration"]),
                   t["abnormal"]])
        last_row = ws.max_row
        ws.cell(row=last_row, column=8).number_format = "[HH]:MM:SS"
        ws.cell(row=last_row, column=9).number_format = "[HH]:MM:SS"
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

    return templates.TemplateResponse("report_result.html", {
        "request": request, "report": report,
        "admin": request.session.get("admin"),
        "show_apps": bool(show_apps),
        "show_abnormal": bool(show_abnormal),
        "expand_details": bool(expand_details),
    })


def _report_row_to_list(r: dict, group_by: str) -> list:
    """CSV-версия строки (всё как строки)."""
    if group_by == "days":
        return ["День ? Сотрудник", r["date"].strftime("%d.%m.%Y"),
                r["employee_name"], r.get("external_id") or "",
                r.get("department_name") or "", "",
                r["sessions_count"],
                _fmt_dur(r["worked_duration"]),
                _fmt_dur(r["effective_duration"]),
                sum(1 for s in r["sessions"] if s["abnormal"])]
    if group_by == "employees":
        return ["Сотрудник", "", r["employee_name"], r.get("external_id") or "",
                r.get("department_name") or "", "",
                r["sessions_count"],
                _fmt_dur(r["worked_duration"]),
                _fmt_dur(r["effective_duration"]),
                sum(1 for s in r["sessions"] if s["abnormal"])]
    if group_by == "computers":
        return ["Компьютер", "", "", "", "", r["computer_name"],
                r["sessions_count"],
                _fmt_dur(r["worked_duration"]),
                _fmt_dur(r["effective_duration"]),
                sum(1 for s in r["sessions"] if s["abnormal"])]
    return ["Сессия", r["date"].strftime("%d.%m.%Y"), r["employee_name"],
            r.get("external_id") or "", r.get("department_name") or "",
            r["computer_name"], 1,
            _fmt_dur(r["worked_duration"]), _fmt_dur(r["effective_duration"]),
            1 if r["abnormal"] else 0]


def _report_row_to_xlsx(r: dict, group_by: str) -> list:
    """XLSX-версия строки (типизированные значения)."""
    if group_by == "days":
        return ["День ? Сотрудник", r["date"], r["employee_name"],
                r.get("external_id") or "", r.get("department_name") or "", "",
                r["sessions_count"],
                _hms_to_excel(r["worked_duration"]),
                _hms_to_excel(r["effective_duration"]),
                sum(1 for s in r["sessions"] if s["abnormal"])]
    if group_by == "employees":
        return ["Сотрудник", "", r["employee_name"], r.get("external_id") or "",
                r.get("department_name") or "", "",
                r["sessions_count"],
                _hms_to_excel(r["worked_duration"]),
                _hms_to_excel(r["effective_duration"]),
                sum(1 for s in r["sessions"] if s["abnormal"])]
    if group_by == "computers":
        return ["Компьютер", "", "", "", "", r["computer_name"],
                r["sessions_count"],
                _hms_to_excel(r["worked_duration"]),
                _hms_to_excel(r["effective_duration"]),
                sum(1 for s in r["sessions"] if s["abnormal"])]
    return ["Сессия", r["date"], r["employee_name"],
            r.get("external_id") or "", r.get("department_name") or "",
            r["computer_name"], 1,
            _hms_to_excel(r["worked_duration"]), _hms_to_excel(r["effective_duration"]),
            1 if r["abnormal"] else 0]


# ============================================================
# Аудит
# ============================================================

@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    logs = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(200).all()
    return templates.TemplateResponse("audit.html", {
        "request": request, "logs": logs, "admin": request.session.get("admin"), "tz": tz,
    })
'@
[System.IO.File]::WriteAllText("$serverDir\web_admin.py", $web_admin_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  web_admin.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$serverDir\web_admin.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 3 — server/main.py: расширяем /api/v1/client-config
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$old = @'
@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    """Клиент подтягивает эту конфигурацию раз в 5 минут."""
    from .models import AppSetting as _AppSetting
    row = db.query(_AppSetting).filter(_AppSetting.key == "idle_close_minutes").first()
    try:
        idle = max(5, min(480, int(row.value))) if row else 30
    except (ValueError, TypeError):
        idle = 30
    return {"idle_close_minutes": idle}
'@

$new = @'
@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    """Клиент подтягивает эту конфигурацию раз в 5 минут."""
    from .models import AppSetting as _AppSetting

    def getv(key, default, mn, mx):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        try:
            return max(mn, min(mx, int(row.value))) if row else default
        except (ValueError, TypeError):
            return default

    return {
        "idle_close_minutes": getv("idle_close_minutes", 30, 5, 480),
        "sync_interval": getv("sync_interval", 30, 5, 3600),
        "batch_size": getv("batch_size", 200, 10, 1000),
        "active_window_interval": getv("active_window_interval", 5, 1, 60),
        "idle_threshold": getv("idle_threshold", 60, 10, 3600),
    }
'@

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  client-config расширен" -ForegroundColor Green
} else {
    Write-Host "  ВНИМАНИЕ: не найдена старая версия endpoint. Пропускаем." -ForegroundColor Yellow
}
python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"
________________________________________
Скрипт 4 — шаблоны: settings.html, departments.html, employees.html, reports.html, base.html
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"
New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null

# base.html — ссылка на Отделы
$base_html = @'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Tracker Admin{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { padding-bottom: 40px; }
    .table-sm td, .table-sm th { vertical-align: middle; }
    .badge-soft { background: #eef2f7; color: #334; }
    code { background: #f4f6f8; padding: 2px 6px; border-radius: 4px; }
    .hint { color: #8a94a6; cursor: help; font-size: 0.85em; margin-left: 3px; }
    .app-bar { display:inline-block; height: 10px; background:#4a90e2; border-radius:2px; vertical-align:middle; }
    details > summary { list-style: none; }
    details > summary::-webkit-details-marker { display: none; }
    .multi-select { height: 220px; }
    .fired-row { opacity: 0.65; }
  </style>
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container-fluid px-4">
    <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
    <div class="navbar-nav ms-auto">
      {% if admin %}
        <a class="nav-link {% if request.url.path == '/admin/employees' %}active{% endif %}" href="/admin/employees">Сотрудники</a>
        <a class="nav-link {% if '/departments' in request.url.path %}active{% endif %}" href="/admin/departments">Отделы</a>
        <a class="nav-link {% if '/computers' in request.url.path %}active{% endif %}" href="/admin/computers">Компьютеры</a>
        <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}" href="/admin/tokens">Токены</a>
        <a class="nav-link {% if '/reports' in request.url.path %}active{% endif %}" href="/admin/reports">Отчёты</a>
        <a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>
        <a class="nav-link {% if '/audit' in request.url.path %}active{% endif %}" href="/admin/audit">Аудит</a>
        <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
        <a class="nav-link" href="/admin/logout">Выход</a>
      {% endif %}
    </div>
  </div>
</nav>
<div class="container-fluid px-4">
  {% block content %}{% endblock %}
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {
    var tip = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tip.forEach(function (el) { new bootstrap.Tooltip(el, { html: false, placement: 'top' }); });
  });
</script>
</body>
</html>
'@
[System.IO.File]::WriteAllText("$templatesDir\base.html", $base_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  base.html" -ForegroundColor Green

# settings.html — все настройки
$settings_html = @'
{% extends "base.html" %}
{% block title %}Настройки{% endblock %}
{% block content %}
<h3 class="mb-4">Настройки системы</h3>

{% if saved %}
<div class="alert alert-success py-2">? Сохранено. Клиенты подхватят изменения в течение 5 минут.</div>
{% endif %}

<div class="card" style="max-width:900px">
  <div class="card-body">
    <form method="post" action="/admin/settings/save">

      <h5 class="mb-3">Отчёты</h5>

      <div class="row g-3 mb-3">
        <div class="col-md-6">
          <label class="form-label">
            Часовой пояс
            <span class="hint" data-bs-toggle="tooltip" title="В каком часовом поясе отображать время в отчётах. В БД хранится UTC.">?</span>
          </label>
          <select name="report_timezone" class="form-select">
            {% for tz_id, tz_label in timezones %}
              <option value="{{ tz_id }}" {% if tz_id == cfg.report_timezone %}selected{% endif %}>{{ tz_label }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Начало рабочего дня
            <span class="hint" data-bs-toggle="tooltip" title="Сессии, начавшиеся раньше этого часа, относятся к предыдущему рабочему дню. Для ночных смен.">?</span>
          </label>
          <select name="workday_start_hour" class="form-select">
            {% for h in range(0, 24) %}
              <option value="{{ h }}" {% if h == cfg.workday_start_hour %}selected{% endif %}>{{ '%02d' % h }}:00</option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Порог паузы для «Эффективно»
            <span class="hint" data-bs-toggle="tooltip" title="Если разрыв между событиями активности больше этого времени — интервал не считается «работой».">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="activity_gap_minutes" class="form-control"
                   value="{{ cfg.activity_gap_minutes }}" min="1" max="120">
            <span class="input-group-text">минут</span>
          </div>
        </div>
      </div>

      <h5 class="mb-3 mt-4">Клиенты</h5>

      <div class="row g-3 mb-3">
        <div class="col-md-6">
          <label class="form-label">
            Idle-порог (авто-закрытие сессий)
            <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="idle_close_minutes" class="form-control"
                   value="{{ cfg.idle_close_minutes }}" min="5" max="480">
            <span class="input-group-text">минут</span>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Интервал синхронизации
            <span class="hint" data-bs-toggle="tooltip" title="Как часто клиент отправляет данные на сервер.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="sync_interval" class="form-control"
                   value="{{ cfg.sync_interval }}" min="5" max="3600">
            <span class="input-group-text">секунд</span>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Размер батча
            <span class="hint" data-bs-toggle="tooltip" title="Сколько записей клиент отправляет за один запрос.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="batch_size" class="form-control"
                   value="{{ cfg.batch_size }}" min="10" max="1000">
            <span class="input-group-text">записей</span>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Период опроса активного окна
            <span class="hint" data-bs-toggle="tooltip" title="Как часто клиент проверяет активное окно.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="active_window_interval" class="form-control"
                   value="{{ cfg.active_window_interval }}" min="1" max="60">
            <span class="input-group-text">секунд</span>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Порог бездействия (idle)
            <span class="hint" data-bs-toggle="tooltip" title="Если нет активности дольше этого времени, клиент считает пользователя неактивным и записывает idle.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="idle_threshold" class="form-control"
                   value="{{ cfg.idle_threshold }}" min="10" max="3600">
            <span class="input-group-text">секунд</span>
          </div>
        </div>
      </div>

      <div class="alert alert-info py-2 small mb-3">
        Изменения доезжают до клиентов при следующем цикле синхронизации (максимум 5 минут).
      </div>

      <button class="btn btn-primary">Сохранить все настройки</button>
    </form>
  </div>
</div>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\settings.html", $settings_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  settings.html" -ForegroundColor Green

# departments.html
$departments_html = @'
{% extends "base.html" %}
{% block title %}Отделы{% endblock %}
{% block content %}
<h3 class="mb-4">Отделы</h3>

<div class="card mb-4" style="max-width:720px">
  <div class="card-header">Добавить отдел</div>
  <div class="card-body">
    <form method="post" action="/admin/departments/create" class="d-flex gap-2">
      <input class="form-control" name="name" placeholder="Название отдела" required>
      <button class="btn btn-success">+ Добавить</button>
    </form>
  </div>
</div>

<table class="table table-sm table-hover bg-white" style="max-width:900px">
  <thead><tr>
    <th>ID</th><th>Название</th><th>Сотрудников</th><th>Действия</th>
  </tr></thead>
  <tbody>
  {% for d in departments %}
    <tr>
      <td>{{ d.id }}</td>
      <td>
        <form method="post" action="/admin/departments/{{ d.id }}/rename" class="d-flex gap-1">
          <input class="form-control form-control-sm" name="name" value="{{ d.name }}" style="width:300px">
          <button class="btn btn-sm btn-outline-primary">??</button>
        </form>
      </td>
      <td>{{ counts.get(d.id, 0) }}</td>
      <td>
        <form method="post" action="/admin/departments/{{ d.id }}/delete" class="d-inline"
              onsubmit="return confirm('Удалить отдел «{{ d.name }}»? Сотрудники останутся без отдела.');">
          <button class="btn btn-sm btn-outline-danger">Удалить</button>
        </form>
      </td>
    </tr>
  {% else %}
    <tr><td colspan="4" class="text-muted">Отделов нет</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\departments.html", $departments_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  departments.html" -ForegroundColor Green

