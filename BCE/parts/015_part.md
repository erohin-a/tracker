# ============================================================

*Часть 15 из 100. Источник: `BCE.md`.*

[◀ ============================================================](014_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](016_part.md)

---

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
        "default_workday_start": settings.workday_start_hour,
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


def _analyze_session(ws: WorkSession, recs, tz: ZoneInfo,
                     gap_minutes: int) -> dict:
    """
    Считает метрики по одной сессии.

    Ключевые моменты:
    - Клавиатура/мышь привязываются к программам (по активному окну).
    - Разрывы между событиями > gap_minutes не считаются «работой».
    """
    start_local = _to_local(ws.session_start, tz)
    end_local = _to_local(ws.session_end or _now(), tz)

    # Логическое «время начала/конца» — по фактическим событиям
    first_event_local = None
    last_event_local = None
    gap = timedelta(minutes=gap_minutes)

    # Разбивка по программам: {app: {"seconds": int, "keyboard": int, "mouse": int}}
    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})

    # Разбивка по времени активности (для эффективной длительности)
    active_seconds_total = 0
    current_window = None
    current_window_started_local = None

    # Первый проход: собираем «сырые» данные
    events = []
    for r in recs:
        try:
            data = json.loads(r.data) if r.data else {}
        except Exception:
            data = {}
        events.append({
            "ts_local": _to_local(r.client_ts, tz),
            "kind": r.kind,
            "data": data,
        })
    events.sort(key=lambda x: x["ts_local"])

    for i, ev in enumerate(events):
        ts = ev["ts_local"]
        if first_event_local is None:
            first_event_local = ts
        last_event_local = ts

        kind = ev["kind"]
        data = ev["data"]

        if kind == "window":
            # Закрываем предыдущее окно
            if current_window is not None and current_window_started_local is not None:
                dur = int((ts - current_window_started_local).total_seconds())
                if dur > 0:
                    app_stats[current_window]["seconds"] += dur
            # Открываем новое
            app = data.get("app") or data.get("title") or "unknown"
            current_window = app
            current_window_started_local = ts

        elif kind == "activity":
            keys = int(data.get("keys", 0) or 0)
            clicks = int(data.get("clicks", 0) or 0)
            scroll = int(data.get("scroll", 0) or 0)

            # Проверяем разрыв: если от прошлого события > gap — не считаем этот интервал активным
            if i > 0:
                delta = (ts - events[i - 1]["ts_local"]).total_seconds()
                if delta > gap.total_seconds():
                    # Большой разрыв — перезапускаем окно
                    if current_window is not None:
                        # Закрываем окно на времени последнего события
                        if current_window_started_local is not None:
                            dur = int((events[i - 1]["ts_local"] - current_window_started_local).total_seconds())
                            if dur > 0:
                                app_stats[current_window]["seconds"] += dur
                        current_window_started_local = ts

            # 5 секунд — интервал опроса клиента
            if current_window is not None:
                if keys > 0:
                    app_stats[current_window]["keyboard"] += 5
                    active_seconds_total += 5
                if clicks + scroll > 0:
                    app_stats[current_window]["mouse"] += 5

    # Закрываем последнее окно
    if current_window is not None and current_window_started_local is not None and last_event_local is not None:
        dur = int((last_event_local - current_window_started_local).total_seconds())
        if dur > 0:
            app_stats[current_window]["seconds"] += dur

    # Эффективная длительность = от первой активности до последней
    if first_event_local and last_event_local:
        effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
    else:
        effective_duration = 0

    # Полная длительность сессии (для информации)
    full_duration = max(0, int((end_local - start_local).total_seconds()))

    # Топ программ с клавиатурой/мышью
    top_apps = sorted(
        [{"app": k, "seconds": v["seconds"],
          "keyboard": v["keyboard"], "mouse": v["mouse"]}
         for k, v in app_stats.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:15]

    # Суммы по программам
    total_keyboard = sum(v["keyboard"] for v in app_stats.values())
    total_mouse = sum(v["mouse"] for v in app_stats.values())

    return {
        "session_uid": ws.session_uid,
        "start_local": start_local,
        "end_local": end_local,
        "date_local": start_local.date(),
        "full_duration": full_duration,
        "effective_duration": effective_duration,
        "keyboard": total_keyboard,
        "mouse": total_mouse,
        "abnormal": bool(ws.abnormal_termination),
        "top_apps": top_apps,
        "employee_id": ws.employee_id,
        "computer_id": ws.computer_id,
    }


def _build_flat_records(db: Session, employee_id, computer_id,
                        date_from: date, date_to: date, tz: ZoneInfo,
                        workday_start_hour: int) -> list:
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
        info = _analyze_session(ws, recs_by_session.get(ws.session_uid, []), tz,
                                settings.activity_gap_minutes)
        emp = employees.get(ws.employee_id) if ws.employee_id else None
        comp = computers.get(ws.computer_id)
        info["employee_name"] = emp.full_name if emp else "— не привязан —"
        info["external_id"] = emp.external_id if emp else None
        info["computer_name"] = (comp.hostname or comp.computer_uid) if comp else "—"
        info["workday_date"] = _workday_date(info["start_local"], workday_start_hour)
        flat.append(info)
    return flat


def _split_by_day(flat: list) -> list:
    groups = {}
    for r in flat:
        key = (r["workday_date"], r["employee_id"])
        g = groups.get(key)
        if g is None:
            g = {
                "date": r["workday_date"],
                "employee_name": r["employee_name"],
                "external_id": r["external_id"],
                "sessions_count": 0,
                "duration": 0,
                "keyboard": 0,
                "mouse": 0,
                "abnormal": False,
                "app_stats": defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}),
                "sessions": [],
            }
            groups[key] = g
        g["sessions_count"] += 1
        g["duration"] += r["effective_duration"]
        g["keyboard"] += r["keyboard"]
        g["mouse"] += r["mouse"]
        g["abnormal"] = g["abnormal"] or r["abnormal"]
        for a in r["top_apps"]:
            g["app_stats"][a["app"]]["seconds"] += a["seconds"]
            g["app_stats"][a["app"]]["keyboard"] += a["keyboard"]
            g["app_stats"][a["app"]]["mouse"] += a["mouse"]
        g["sessions"].append(r)

    result = []
    for g in groups.values():
        g["top_apps"] = sorted(
            [{"app": k, **v} for k, v in g["app_stats"].items()],
            key=lambda x: x["seconds"], reverse=True,
        )[:15]
        del g["app_stats"]
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
                "external_id": r["external_id"],
                "sessions_count": 0,
                "days": set(),
                "duration": 0,
                "keyboard": 0,
                "mouse": 0,
                "abnormal": False,
                "app_stats": defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}),
                "sessions": [],
            }
            groups[key] = g
        g["sessions_count"] += 1
        g["days"].add(r["workday_date"])
        g["duration"] += r["effective_duration"]
        g["keyboard"] += r["keyboard"]
        g["mouse"] += r["mouse"]
        g["abnormal"] = g["abnormal"] or r["abnormal"]
        for a in r["top_apps"]:
            g["app_stats"][a["app"]]["seconds"] += a["seconds"]
            g["app_stats"][a["app"]]["keyboard"] += a["keyboard"]
            g["app_stats"][a["app"]]["mouse"] += a["mouse"]
        g["sessions"].append(r)

    result = []
    for g in groups.values():
        g["days_count"] = len(g["days"])
        del g["days"]
        g["top_apps"] = sorted(
            [{"app": k, **v} for k, v in g["app_stats"].items()],
            key=lambda x: x["seconds"], reverse=True,
        )[:15]
        del g["app_stats"]
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
                "app_stats": defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}),
                "sessions": [],
            }
            groups[key] = g
        g["sessions_count"] += 1
        g["duration"] += r["effective_duration"]
        g["keyboard"] += r["keyboard"]
        g["mouse"] += r["mouse"]
        g["abnormal"] = g["abnormal"] or r["abnormal"]
        for a in r["top_apps"]:
            g["app_stats"][a["app"]]["seconds"] += a["seconds"]
            g["app_stats"][a["app"]]["keyboard"] += a["keyboard"]
            g["app_stats"][a["app"]]["mouse"] += a["mouse"]
        g["sessions"].append(r)

    result = []
    for g in groups.values():
        g["top_apps"] = sorted(
            [{"app": k, **v} for k, v in g["app_stats"].items()],
            key=lambda x: x["seconds"], reverse=True,
        )[:15]
        del g["app_stats"]
        result.append(g)
    result.sort(key=lambda x: x["duration"], reverse=True)
    return result


def _group_by_session(flat: list) -> list:
    result = []
    for r in flat:
        result.append({
            "session_uid": r["session_uid"],
            "date": r["workday_date"],
            "employee_name": r["employee_name"],
            "external_id": r["external_id"],
            "computer_name": r["computer_name"],
            "start_local": r["start_local"],
            "end_local": r["end_local"],
            "duration": r["effective_duration"],
            "full_duration": r["full_duration"],
            "keyboard": r["keyboard"],
            "mouse": r["mouse"],
            "abnormal": r["abnormal"],
            "top_apps": r["top_apps"],
            "sessions": [],
        })
    result.sort(key=lambda x: x["start_local"], reverse=True)
    return result


def _build_report(db: Session, employee_id, computer_id,
                  date_from: date, date_to: date, group_by: str,
                  tz: ZoneInfo, workday_start_hour: int) -> dict:
    flat = _build_flat_records(db, employee_id, computer_id, date_from, date_to,
                               tz, workday_start_hour)

    if group_by == "days":
        rows = _split_by_day(flat)
    elif group_by == "employees":
        rows = _group_by_employee(flat)
    elif group_by == "computers":
        rows = _group_by_computer(flat)
    else:
        rows = _group_by_session(flat)

    total_duration = sum(r["effective_duration"] for r in flat)
    total_full_duration = sum(r["full_duration"] for r in flat)
    total_keyboard = sum(r["keyboard"] for r in flat)
    total_mouse = sum(r["mouse"] for r in flat)
    total_abnormal = sum(1 for r in flat if r["abnormal"])

    app_totals = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    for r in flat:
        for a in r["top_apps"]:
            app_totals[a["app"]]["seconds"] += a["seconds"]
            app_totals[a["app"]]["keyboard"] += a["keyboard"]
            app_totals[a["app"]]["mouse"] += a["mouse"]
    top_apps = sorted(
        [{"app": k, **v} for k, v in app_totals.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:15]

    return {
        "group_by": group_by,
        "date_from": date_from,
        "date_to": date_to,
        "tz_name": str(tz),
        "workday_start_hour": workday_start_hour,
        "rows": rows,
        "totals": {
            "sessions": len(flat),
            "duration": total_duration,
            "full_duration": total_full_duration,
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
    workday_start_hour: int = Form(6),
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

    workday_start_hour = max(0, min(23, int(workday_start_hour)))
    emp_id = int(employee_id) if employee_id else None
    comp_id = int(computer_id) if computer_id else None

    tz = _resolve_tz(tz_name)
    report = _build_report(db, emp_id, comp_id, d_from, d_to, group_by, tz,
                           workday_start_hour)

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
        "Группа", "Рабочий день", "Сотрудник", "1C ID", "Компьютер",
        "Сессий", "Эффективных (сек)", "Полных (сек)", "Аварийных",
    ]
    rows = []
    group_by = report["group_by"]

    for r in report["rows"]:
        if group_by == "days":
            rows.append([
                "День ? Сотрудник",
                r["date"].strftime("%Y-%m-%d"),
                r["employee_name"],
                r.get("external_id") or "",
                "",
                r["sessions_count"],
                r["duration"],
                sum(s["full_duration"] for s in r["sessions"]),
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        elif group_by == "employees":
            rows.append([
                "Сотрудник", "",
                r["employee_name"],
                r.get("external_id") or "",
                "",
                r["sessions_count"],
                r["duration"],
                sum(s["full_duration"] for s in r["sessions"]),
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        elif group_by == "computers":
            rows.append([
                "Компьютер", "", "", "", r["computer_name"],
                r["sessions_count"],
                r["duration"],
                sum(s["full_duration"] for s in r["sessions"]),
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        else:
            rows.append([
                "Сессия",
                r["date"].strftime("%Y-%m-%d"),
                r["employee_name"],
                r.get("external_id") or "",
                r["computer_name"],
                1,
                r["duration"],
                r["full_duration"],
                1 if r["abnormal"] else 0,
            ])

    t = report["totals"]
    rows.append([
        "ИТОГО", "", "", "", "",
        t["sessions"], t["duration"], t["full_duration"], t["abnormal"],
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

# Проверка синтаксиса
Write-Host "`n--- Проверка синтаксиса Python ---" -ForegroundColor Cyan
python -c "import ast; ast.parse(open(r'$serverDir\config.py', encoding='utf-8').read()); ast.parse(open(r'$serverDir\web_admin.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — шаблоны reports.html и report_result.html
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

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
          <span class="hint" data-bs-toggle="tooltip" title="Начало периода включительно.">?</span>
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
            <option value="{{ e.id }}">{{ e.full_name }}{% if e.external_id %} ({{ e.external_id }}){% endif %}</option>
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
          <span class="hint" data-bs-toggle="tooltip" title="Как сгруппировать строки в отчёте.">?</span>
        </label>
        <select name="group_by" class="form-select">
          <option value="days" selected>Рабочие дни ? Сотрудник (табель)</option>
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

      <div class="col-md-2">
        <label class="form-label">
          Начало рабочего дня
          <span class="hint" data-bs-toggle="tooltip" title="Час, с которого начинается новый рабочий день. Сессии, начавшиеся раньше этого часа, относятся к предыдущему рабочему дню. Полезно для ночных смен.">?</span>
        </label>
        <select name="workday_start_hour" class="form-select">
          {% for h in range(0, 24) %}
            <option value="{{ h }}" {% if h == default_workday_start %}selected{% endif %}>{{ '%02d' % h }}:00</option>
          {% endfor %}
        </select>
      </div>

      <div class="col-md-2">
        <label class="form-label">Формат вывода</label>
        <select name="fmt" class="form-select">
          <option value="html">Просмотр</option>
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
              Топ-программы (с разбивкой клавиатуры/мыши)
            </label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_abnormal" id="show_abnormal" checked>
            <label class="form-check-label" for="show_abnormal">
              Пометки аварийных завершений
            </label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="expand_details" id="expand_details">
            <label class="form-check-label" for="expand_details">
              Разворачивать детали (сессии и программы)
            </label>
          </div>
        </div>
      </div>

      <div class="col-12">
        <button class="btn btn-primary">Сформировать отчёт</button>
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
