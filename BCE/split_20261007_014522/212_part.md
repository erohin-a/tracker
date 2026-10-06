<!-- Часть 212 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Отчёты](211_Otchety.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](213_part.md)

---

# ============================================================

@router.get("/reports", response_class=HTMLResponse)
def reports_form(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).filter(Employee.is_active == True).order_by(Employee.last_name).all()
    computers = db.query(Computer).filter(Computer.is_active == True).order_by(Computer.hostname).all()
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "employees": employees,
        "computers": computers,
        "admin": request.session.get("admin"),
        "timezones": _available_timezones(),
        "default_tz": settings.report_timezone,
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


def _analyze_session(ws: WorkSession, recs, tz: ZoneInfo) -> dict:
    start_local = _to_local(ws.session_start, tz)
    end_local = _to_local(ws.session_end or _now(), tz)
    duration = max(0, int((end_local - start_local).total_seconds()))

    keyboard = 0
    mouse = 0
    windows = []
    for r in recs:
        try:
            data = json.loads(r.data) if r.data else {}
        except Exception:
            data = {}
        if r.kind == "activity":
            keys = int(data.get("keys", 0) or 0)
            clicks = int(data.get("clicks", 0) or 0)
            scroll = int(data.get("scroll", 0) or 0)
            if keys > 0:
                keyboard += 5
            if clicks + scroll > 0:
                mouse += 5
        elif r.kind == "window":
            app = data.get("app") or data.get("title") or "unknown"
            windows.append((_to_local(r.client_ts, tz), app))

    app_totals = defaultdict(int)
    for i, (ts, app) in enumerate(windows):
        next_ts = windows[i + 1][0] if i + 1 < len(windows) else end_local
        dur = max(0, int((next_ts - ts).total_seconds()))
        if dur > 0:
            app_totals[app] += dur

    top_apps = sorted(
        [{"app": k, "seconds": v} for k, v in app_totals.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:10]

    return {
        "session_uid": ws.session_uid,
        "start_local": start_local,
        "end_local": end_local,
        "date_local": start_local.date(),
        "duration": duration,
        "keyboard": keyboard,
        "mouse": mouse,
        "abnormal": bool(ws.abnormal_termination),
        "top_apps": top_apps,
        "employee_id": ws.employee_id,
        "computer_id": ws.computer_id,
    }


def _build_flat_records(db: Session, employee_id, computer_id,
                        date_from: date, date_to: date, tz: ZoneInfo) -> list:
    start_local = datetime.combine(date_from, time.min, tzinfo=tz)
    end_local = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=tz)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    q = (db.query(WorkSession)
         .filter(WorkSession.session_start >= start_utc,
                 WorkSession.session_start < end_utc))
    if employee_id:
        q = q.filter(WorkSession.employee_id == employee_id)
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

    flat = []
    for ws in sessions:
        info = _analyze_session(ws, recs_by_session.get(ws.session_uid, []), tz)
        emp = employees.get(ws.employee_id) if ws.employee_id else None
        comp = computers.get(ws.computer_id)
        info["employee_name"] = emp.full_name if emp else "— не привязан —"
        info["computer_name"] = (comp.hostname or comp.computer_uid) if comp else "—"
        flat.append(info)
    return flat


def _split_by_day(flat: list) -> list:
    groups = {}
    for r in flat:
        key = (r["date_local"], r["employee_id"])
        g = groups.get(key)
        if g is None:
            g = {
                "date": r["date_local"],
                "employee_name": r["employee_name"],
                "sessions_count": 0,
                "duration": 0,
                "keyboard": 0,
                "mouse": 0,
                "abnormal": False,
                "app_totals": defaultdict(int),
                "sessions": [],
            }
            groups[key] = g
        g["sessions_count"] += 1
        g["duration"] += r["duration"]
        g["keyboard"] += r["keyboard"]
        g["mouse"] += r["mouse"]
        g["abnormal"] = g["abnormal"] or r["abnormal"]
        for a in r["top_apps"]:
            g["app_totals"][a["app"]] += a["seconds"]
        g["sessions"].append(r)

    result = []
    for g in groups.values():
        g["top_apps"] = sorted(
            [{"app": k, "seconds": v} for k, v in g["app_totals"].items()],
            key=lambda x: x["seconds"], reverse=True,
        )[:10]
        del g["app_totals"]
        result.append(g)
    result.sort(key=lambda x: (x["date"], x["employee_name"]), reverse=True)
    return result


def _group_by_employee(flat: list) -> list:
    groups = {}
    for r in flat:
        key = r["employee_id"]
        g = groups.get(key)
        if g is None:
            g = {
                "employee_name": r["employee_name"],
                "sessions_count": 0,
                "days": set(),
                "duration": 0,
                "keyboard": 0,
                "mouse": 0,
                "abnormal": False,
                "app_totals": defaultdict(int),
                "sessions": [],
            }
            groups[key] = g
        g["sessions_count"] += 1
        g["days"].add(r["date_local"])
        g["duration"] += r["duration"]
        g["keyboard"] += r["keyboard"]
        g["mouse"] += r["mouse"]
        g["abnormal"] = g["abnormal"] or r["abnormal"]
        for a in r["top_apps"]:
            g["app_totals"][a["app"]] += a["seconds"]
        g["sessions"].append(r)

    result = []
    for g in groups.values():
        g["days_count"] = len(g["days"])
        del g["days"]
        g["top_apps"] = sorted(
            [{"app": k, "seconds": v} for k, v in g["app_totals"].items()],
            key=lambda x: x["seconds"], reverse=True,
        )[:10]
        del g["app_totals"]
        result.append(g)
    result.sort(key=lambda x: x["duration"], reverse=True)
    return result


def _group_by_computer(flat: list) -> list:
    groups = {}
    for r in flat:
        key = r["computer_id"]
        g = groups.get(key)
        if g is None:
            g = {
                "computer_name": r["computer_name"],
                "sessions_count": 0,
                "duration": 0,
                "keyboard": 0,
                "mouse": 0,
                "abnormal": False,
                "app_totals": defaultdict(int),
                "sessions": [],
            }
            groups[key] = g
        g["sessions_count"] += 1
        g["duration"] += r["duration"]
        g["keyboard"] += r["keyboard"]
        g["mouse"] += r["mouse"]
        g["abnormal"] = g["abnormal"] or r["abnormal"]
        for a in r["top_apps"]:
            g["app_totals"][a["app"]] += a["seconds"]
        g["sessions"].append(r)

    result = []
    for g in groups.values():
        g["top_apps"] = sorted(
            [{"app": k, "seconds": v} for k, v in g["app_totals"].items()],
            key=lambda x: x["seconds"], reverse=True,
        )[:10]
        del g["app_totals"]
        result.append(g)
    result.sort(key=lambda x: x["duration"], reverse=True)
    return result


def _group_by_session(flat: list) -> list:
    result = []
    for r in flat:
        result.append({
            "session_uid": r["session_uid"],
            "date": r["date_local"],
            "employee_name": r["employee_name"],
            "computer_name": r["computer_name"],
            "start_local": r["start_local"],
            "end_local": r["end_local"],
            "duration": r["duration"],
            "keyboard": r["keyboard"],
            "mouse": r["mouse"],
            "abnormal": r["abnormal"],
            "top_apps": r["top_apps"],
            "sessions": [],
        })
    result.sort(key=lambda x: x["start_local"], reverse=True)
    return result


def _build_report(db: Session, employee_id, computer_id,
                  date_from: date, date_to: date, group_by: str, tz: ZoneInfo) -> dict:
    flat = _build_flat_records(db, employee_id, computer_id, date_from, date_to, tz)

    if group_by == "days":
        rows = _split_by_day(flat)
    elif group_by == "employees":
        rows = _group_by_employee(flat)
    elif group_by == "computers":
        rows = _group_by_computer(flat)
    else:
        rows = _group_by_session(flat)

    total_duration = sum(r["duration"] for r in flat)
    total_keyboard = sum(r["keyboard"] for r in flat)
    total_mouse = sum(r["mouse"] for r in flat)
    total_abnormal = sum(1 for r in flat if r["abnormal"])

    app_totals = defaultdict(int)
    for r in flat:
        for a in r["top_apps"]:
            app_totals[a["app"]] += a["seconds"]
    top_apps = sorted(
        [{"app": k, "seconds": v} for k, v in app_totals.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:10]

    return {
        "group_by": group_by,
        "date_from": date_from,
        "date_to": date_to,
        "tz_name": str(tz),
        "rows": rows,
        "totals": {
            "sessions": len(flat),
            "duration": total_duration,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "abnormal": total_abnormal,
            "top_apps": top_apps,
        },
    }


@router.post("/reports/generate")
def reports_generate(
    request: Request,
    employee_id: str = Form(""),
    computer_id: str = Form(""),
    date_from: str = Form(...),
    date_to: str = Form(...),
    group_by: str = Form("days"),
    tz_name: str = Form("Europe/Moscow"),
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

    emp_id = int(employee_id) if employee_id else None
    comp_id = int(computer_id) if computer_id else None

    tz = _resolve_tz(tz_name)
    report = _build_report(db, emp_id, comp_id, d_from, d_to, group_by, tz)

    if fmt in ("csv", "xlsx"):
        headers, rows_data = _report_to_table(report)
        filename = f"report_{group_by}_{date_from}_{date_to}"

        if fmt == "csv":
            output = io.StringIO()
            writer = csv.writer(output, delimiter=";")
            writer.writerow(headers)
            for row in rows_data:
                writer.writerow(row)
            output.seek(0)
            data = "\ufeff" + output.getvalue()
            return StreamingResponse(
                iter([data]),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
            )

        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill

        wb = Workbook()
        ws = wb.active
        ws.title = "Report"
        ws.append(headers)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="343A40")
            c.alignment = Alignment(horizontal="center")
        for row in rows_data:
            ws.append(row)
        for col in ws.columns:
            length = max((len(str(c.value)) for c in col if c.value is not None), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(length + 2, 60)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
        )

    return templates.TemplateResponse("report_result.html", {
        "request": request,
        "report": report,
        "admin": request.session.get("admin"),
        "show_apps": bool(show_apps),
        "show_abnormal": bool(show_abnormal),
        "expand_details": bool(expand_details),
    })


def _report_to_table(report: dict):
    headers = [
        "Группа", "День", "Сотрудник", "Компьютер",
        "Сессий", "Длительность (сек)", "Клавиатура (сек)", "Мышь (сек)",
        "Аварийных",
    ]
    rows = []
    group_by = report["group_by"]

    for r in report["rows"]:
        if group_by == "days":
            rows.append([
                "День ? Сотрудник",
                r["date"].strftime("%Y-%m-%d"),
                r["employee_name"],
                "",
                r["sessions_count"],
                r["duration"],
                r["keyboard"],
                r["mouse"],
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        elif group_by == "employees":
            rows.append([
                "Сотрудник", "", r["employee_name"], "",
                r["sessions_count"], r["duration"], r["keyboard"], r["mouse"],
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        elif group_by == "computers":
            rows.append([
                "Компьютер", "", "", r["computer_name"],
                r["sessions_count"], r["duration"], r["keyboard"], r["mouse"],
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        else:
            rows.append([
                "Сессия",
                r["date"].strftime("%Y-%m-%d"),
                r["employee_name"],
                r["computer_name"],
                1,
                r["duration"],
                r["keyboard"],
                r["mouse"],
                1 if r["abnormal"] else 0,
            ])

    t = report["totals"]
    rows.append([
        "ИТОГО", "", "", "",
        t["sessions"], t["duration"], t["keyboard"], t["mouse"], t["abnormal"],
    ])

    return headers, rows


