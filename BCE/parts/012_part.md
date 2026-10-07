# ============================================================

*Часть 12 из 100. Источник: `BCE.md`.*

[◀ --- сессии ---](011_sessii.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](013_part.md)

---

# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_admin(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=401, detail="not authenticated")
    return request.session["admin"]


def _now():
    return datetime.now(timezone.utc)


def _hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def _resolve_tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        try:
            return ZoneInfo(settings.report_timezone)
        except Exception:
            return ZoneInfo("UTC")


def _to_local(dt: Optional[datetime], tz: ZoneInfo) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)


def _fmt_dt_local(dt: Optional[datetime], tz: ZoneInfo) -> str:
    if dt is None:
        return "—"
    return _to_local(dt, tz).strftime("%d.%m.%Y %H:%M")


def _fmt_dur(seconds: int) -> str:
    if not seconds:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


templates.env.filters["dur"] = _fmt_dur


def _available_timezones():
    return [
        ("Europe/Moscow", "Москва (UTC+3)"),
        ("Europe/Kaliningrad", "Калининград (UTC+2)"),
        ("Asia/Yekaterinburg", "Екатеринбург (UTC+5)"),
        ("Asia/Novosibirsk", "Новосибирск (UTC+7)"),
        ("Asia/Krasnoyarsk", "Красноярск (UTC+7)"),
        ("Asia/Irkutsk", "Иркутск (UTC+8)"),
        ("Asia/Vladivostok", "Владивосток (UTC+10)"),
        ("UTC", "UTC"),
    ]


# ============================================================
# Логин / логаут
# ============================================================

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("admin"):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    ok_user = secrets.compare_digest(username, settings.admin_login)
    ok_pass = secrets.compare_digest(password, settings.admin_api_key)
    if ok_user and ok_pass:
        request.session["admin"] = username
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Неверный логин или ключ"},
        status_code=401,
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


# ============================================================
# Дашборд
# ============================================================

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    today_local = datetime.now(tz).date()
    today_start_local = datetime.combine(today_local, time.min, tzinfo=tz)
    today_start_utc = today_start_local.astimezone(timezone.utc)
    week_ago_utc = today_start_utc - timedelta(days=7)

    stats = {
        "employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
        "sessions_today": db.query(WorkSession).filter(
            WorkSession.session_start >= today_start_utc).count(),
        "sessions_week": db.query(WorkSession).filter(
            WorkSession.session_start >= week_ago_utc).count(),
        "records": db.query(Record).count(),
        "tokens_active": db.query(BootstrapToken).filter(
            BootstrapToken.used_at.is_(None),
            BootstrapToken.expires_at > _now(),
        ).count(),
    }

    recent_computers = (
        db.query(Computer).order_by(desc(Computer.registered_at)).limit(10).all()
    )
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_computers": recent_computers,
        "recent_audit": recent_audit,
        "admin": request.session.get("admin"),
        "tz": tz,
    })


# ============================================================
# Сотрудники
# ============================================================

@router.get("/employees", response_class=HTMLResponse)
def employees_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).order_by(Employee.last_name, Employee.first_name).all()
    return templates.TemplateResponse("employees.html", {
        "request": request, "employees": employees, "admin": request.session.get("admin"),
    })


@router.post("/employees/create")
def employee_create(
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(""),
    external_id: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    last_name = last_name.strip()
    first_name = first_name.strip()
    middle_name = middle_name.strip()
    external_id = external_id.strip()

    if not last_name or not first_name:
        raise HTTPException(400, "Фамилия и имя обязательны")

    full_name = " ".join(x for x in [last_name, first_name, middle_name] if x)
    emp = Employee(
        full_name=full_name,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name or None,
        external_id=external_id or None,
    )
    db.add(emp)
    db.flush()
    db.add(AuditLog(
        actor="admin", entity="employee", entity_id=str(emp.id),
        action="create", new_value=json.dumps({"full_name": full_name}, ensure_ascii=False),
    ))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/edit")
def employee_edit(
    emp_id: int,
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(""),
    external_id: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    emp = db.query(Employee).get(emp_id)
    if not emp:
        raise HTTPException(404)
    old = emp.full_name
    emp.last_name = last_name.strip()
    emp.first_name = first_name.strip()
    emp.middle_name = middle_name.strip() or None
    emp.external_id = external_id.strip() or None
    emp.full_name = " ".join(x for x in [emp.last_name, emp.first_name, emp.middle_name] if x)
    db.add(AuditLog(
        actor="admin", entity="employee", entity_id=str(emp_id), action="edit",
        old_value=old, new_value=emp.full_name,
    ))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/deactivate")
def employee_deactivate(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.is_active = False
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="deactivate"))
        db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/activate")
def employee_activate(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.is_active = True
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="activate"))
        db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


# ============================================================
# Компьютеры
# ============================================================

@router.get("/computers", response_class=HTMLResponse)
def computers_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).all()
    employees = db.query(Employee).filter(Employee.is_active == True).order_by(Employee.last_name).all()
    return templates.TemplateResponse("computers.html", {
        "request": request, "computers": computers, "employees": employees,
        "admin": request.session.get("admin"), "tz": tz,
    })


@router.post("/computers/{comp_id}/assign")
def computer_assign(
    comp_id: int,
    employee_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    comp = db.query(Computer).get(comp_id)
    if not comp:
        raise HTTPException(404)

    emp_id = int(employee_id) if employee_id else None
    old = comp.employee_id
    comp.employee_id = emp_id
    comp.assigned_at = _now()

    db.add(AuditLog(
        actor="admin", entity="computer", entity_id=str(comp_id), action="assign",
        old_value=str(old), new_value=str(emp_id),
    ))
    db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


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


# ============================================================
# Bootstrap-токены
# ============================================================

@router.get("/tokens", response_class=HTMLResponse)
def tokens_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    tokens = db.query(BootstrapToken).order_by(desc(BootstrapToken.id)).limit(50).all()
    return templates.TemplateResponse("tokens.html", {
        "request": request, "tokens": tokens,
        "admin": request.session.get("admin"),
        "new_token": request.query_params.get("new_token"),
        "tz": tz,
    })


@router.post("/tokens/issue")
def tokens_issue(
    ttl_hours: int = Form(24),
    issued_by: str = Form("admin"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    ttl_hours = max(1, min(ttl_hours, 24 * 30))
    raw = secrets.token_urlsafe(32)
    db.add(BootstrapToken(
        token_hash=_hash_token(raw),
        issued_by=issued_by,
        expires_at=_now() + timedelta(hours=ttl_hours),
    ))
    db.add(AuditLog(actor="admin", entity="bootstrap_token", action="issue",
                    new_value=json.dumps({"ttl_hours": ttl_hours, "issued_by": issued_by})))
    db.commit()
    return RedirectResponse(f"/admin/tokens?new_token={raw}", status_code=303)


# ============================================================
# Отчёты
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


# ============================================================
# Аудит
# ============================================================

@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    logs = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(200).all()
    return templates.TemplateResponse("audit.html", {
        "request": request, "logs": logs, "admin": request.session.get("admin"), "tz": tz,
    })
'@
[System.IO.File]::WriteAllText("$serverDir\web_admin.py", $web_admin_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  web_admin.py" -ForegroundColor Green

Write-Host "`n=== Скрипт 1 завершён ===" -ForegroundColor Cyan
После выполнения увидите:
text
OK  requirements.txt
OK  config.py
OK  web_admin.py

=== Скрипт 1 завершён ===
________________________________________
Скрипт 2 — HTML-шаблоны
Запустите вторым (тоже целиком):
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"
New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null

# ============================================================
# base.html
# ============================================================
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
    .group-header { background: #f8f9fa; font-weight: 600; }
    .app-bar { display:inline-block; height: 10px; background:#4a90e2; border-radius:2px; vertical-align:middle; }
  </style>
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container-fluid px-4">
    <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
    <div class="navbar-nav ms-auto">
      {% if admin %}
        <a class="nav-link {% if '/employees' in request.url.path %}active{% endif %}" href="/admin/employees">Сотрудники</a>
        <a class="nav-link {% if '/computers' in request.url.path %}active{% endif %}" href="/admin/computers">Компьютеры</a>
        <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}" href="/admin/tokens">Токены</a>
        <a class="nav-link {% if '/reports' in request.url.path %}active{% endif %}" href="/admin/reports">Отчёты</a>
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
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (el) {
      new bootstrap.Tooltip(el, { html: false, placement: 'top' });
    });
  });
</script>
</body>
</html>
'@
[System.IO.File]::WriteAllText("$templatesDir\base.html", $base_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  base.html" -ForegroundColor Green

# ============================================================
# reports.html
# ============================================================
$reports_html = @'
{% extends "base.html" %}
{% block title %}Отчёты{% endblock %}
{% block content %}
<h3 class="mb-4">Отчёты</h3>

<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/reports/generate" class="row g-3" id="reportForm">

      <div class="col-12">
        <label class="form-label fw-bold">Период</label>
        <div class="d-flex flex-wrap gap-2 mb-2">
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(0)">Сегодня</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(1)">Вчера</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(7)">7 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(30)">30 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setThisMonth()">Этот месяц</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setLastMonth()">Прошлый месяц</button>
        </div>
      </div>

      <div class="col-md-3">
        <label class="form-label">
          С даты
          <span class="hint" data-bs-toggle="tooltip" title="Начало периода включительно. Время трактуется в выбранном ниже часовом поясе.">?</span>
        </label>
        <input class="form-control" type="date" name="date_from" id="date_from" required value="{{ today }}">
      </div>
      <div class="col-md-3">
        <label class="form-label">
          По дату
          <span class="hint" data-bs-toggle="tooltip" title="Конец периода включительно.">?</span>
        </label>
        <input class="form-control" type="date" name="date_to" id="date_to" required value="{{ today }}">
      </div>

      <div class="col-md-3">
        <label class="form-label">Сотрудник</label>
        <select name="employee_id" class="form-select">
          <option value="">Все сотрудники</option>
          {% for e in employees %}
            <option value="{{ e.id }}">{{ e.full_name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Компьютер</label>
        <select name="computer_id" class="form-select">
          <option value="">Все компьютеры</option>
          {% for c in computers %}
            <option value="{{ c.id }}">{{ c.hostname or c.computer_uid[:14] }}</option>
          {% endfor %}
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">
          Группировка
          <span class="hint" data-bs-toggle="tooltip" title="Как сгруппировать строки в отчёте. 'Дни ? Сотрудник' — оптимально для табеля.">?</span>
        </label>
        <select name="group_by" class="form-select">
          <option value="days" selected>Дни ? Сотрудник (табель)</option>
          <option value="employees">По сотрудникам (итог за период)</option>
          <option value="computers">По компьютерам</option>
          <option value="sessions">Детально — каждая сессия</option>
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">
          Часовой пояс
          <span class="hint" data-bs-toggle="tooltip" title="В каком часовом поясе отображать время. В БД время хранится в UTC.">?</span>
        </label>
        <select name="tz_name" class="form-select">
          {% for tz_id, tz_label in timezones %}
            <option value="{{ tz_id }}" {% if tz_id == default_tz %}selected{% endif %}>{{ tz_label }}</option>
          {% endfor %}
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">Формат вывода</label>
        <select name="fmt" class="form-select">
          <option value="html">Просмотр в браузере</option>
          <option value="xlsx">Excel (XLSX)</option>
          <option value="csv">CSV</option>
        </select>
      </div>

      <div class="col-12">
        <label class="form-label fw-bold">Что показывать</label>
        <div class="d-flex flex-wrap gap-4">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_apps" id="show_apps" checked>
            <label class="form-check-label" for="show_apps">
              Топ-программы
              <span class="hint" data-bs-toggle="tooltip" title="Показывать топ активных программ за период.">?</span>
            </label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_abnormal" id="show_abnormal" checked>
            <label class="form-check-label" for="show_abnormal">
              Пометки аварийных завершений
              <span class="hint" data-bs-toggle="tooltip" title="Сессии, закрытые без нажатия «Конец работы» (авария/BSOD).">?</span>
            </label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="expand_details" id="expand_details">
            <label class="form-check-label" for="expand_details">
              Разворачивать детали внутри групп
              <span class="hint" data-bs-toggle="tooltip" title="Если включено — под каждой группой будет кнопка для показа списка сессий.">?</span>
            </label>
          </div>
        </div>
      </div>

      <div class="col-12">
        <button class="btn btn-primary">
          Сформировать отчёт
        </button>
      </div>
    </form>
  </div>
</div>

<script>
function fmt(d) {
  var y = d.getFullYear();
  var m = String(d.getMonth()+1).padStart(2,'0');
  var dd = String(d.getDate()).padStart(2,'0');
  return y + '-' + m + '-' + dd;
}
function setPeriod(daysAgo) {
  var to = new Date();
  var from = new Date();
  from.setDate(from.getDate() - daysAgo);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
function setThisMonth() {
  var now = new Date();
  var from = new Date(now.getFullYear(), now.getMonth(), 1);
  var to = new Date(now.getFullYear(), now.getMonth()+1, 0);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
function setLastMonth() {
  var now = new Date();
  var from = new Date(now.getFullYear(), now.getMonth()-1, 1);
  var to = new Date(now.getFullYear(), now.getMonth(), 0);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
</script>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\reports.html", $reports_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  reports.html" -ForegroundColor Green

# ============================================================
# report_result.html
