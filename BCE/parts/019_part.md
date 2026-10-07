# ============================================================

*Часть 19 из 100. Источник: `BCE.md`.*

[◀ in _check_idle_session:](018_in_check_idle_session.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](020_part.md)

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
        [{"app": k, "seconds": v["seconds"],
          "keyboard": v["keyboard"], "mouse": v["mouse"]}
         for k, v in app_stats.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:15]

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


def _span_of_sessions(sessions: list) -> int:
    """Разница между стартом первой и концом последней сессии."""
    if not sessions:
        return 0
    first = min(s["start_local"] for s in sessions)
    last = max(s["end_local"] for s in sessions)
    return max(0, int((last - first).total_seconds()))


def _merge_apps(target: dict, source_apps: list) -> None:
    """Добавляет данные из source_apps (list of {app, seconds, keyboard, mouse}) в target-словарь."""
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
                "date": r["workday_date"],
                "employee_name": r["employee_name"],
                "external_id": r["external_id"],
                "sessions_count": 0,
                "effective_duration": 0,
                "keyboard": 0,
                "mouse": 0,
                "abnormal": False,
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
    # Промежуточная группировка по (emp_id, day)
    by_day = defaultdict(list)
    for r in flat:
        by_day[(r["employee_id"], r["workday_date"])].append(r)

    # Для каждого сотрудника собираем дни
    emp_days = defaultdict(list)
    for (emp_id, day), sessions in by_day.items():
        emp_days[emp_id].append({
            "day": day,
            "sessions": sessions,
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
            "day": day,
            "sessions": sessions,
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
            "session_uid": r["session_uid"],
            "date": r["workday_date"],
            "employee_name": r["employee_name"],
            "external_id": r["external_id"],
            "computer_name": r["computer_name"],
            "start_local": r["start_local"],
            "end_local": r["end_local"],
            "worked_duration": r["full_duration"],
            "effective_duration": r["effective_duration"],
            "keyboard": r["keyboard"],
            "mouse": r["mouse"],
            "abnormal": r["abnormal"],
            "top_apps": r["top_apps"],
            "sessions": [],
        })
    result.sort(key=lambda x: x["start_local"], reverse=True)
    return result


def _build_program_employee_matrix(flat: list) -> dict:
    """app -> [{employee_name, external_id, seconds, keyboard, mouse}, ...]"""
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
            rows.append({
                "employee_name": name,
                "external_id": ext_id,
                "seconds": stats["seconds"],
                "keyboard": stats["keyboard"],
                "mouse": stats["mouse"],
            })
        rows.sort(key=lambda x: x["seconds"], reverse=True)
        result[app] = rows
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
        "group_by": group_by,
        "date_from": date_from,
        "date_to": date_to,
        "tz_name": str(tz),
        "workday_start_hour": workday_start_hour,
        "rows": rows,
        "totals": {
            "sessions": len(flat),
            "worked_duration": total_worked,
            "effective_duration": total_effective,
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
        "Сессий", "Отработано (сек)", "Эффективно (сек)", "Аварийных",
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
                r["worked_duration"],
                r["effective_duration"],
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        elif group_by == "employees":
            rows.append([
                "Сотрудник", "",
                r["employee_name"],
                r.get("external_id") or "",
                "",
                r["sessions_count"],
                r["worked_duration"],
                r["effective_duration"],
                sum(1 for s in r["sessions"] if s["abnormal"]),
            ])
        elif group_by == "computers":
            rows.append([
                "Компьютер", "", "", "", r["computer_name"],
                r["sessions_count"],
                r["worked_duration"],
                r["effective_duration"],
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
                r["worked_duration"],
                r["effective_duration"],
                1 if r["abnormal"] else 0,
            ])

    t = report["totals"]
    rows.append([
        "ИТОГО", "", "", "", "",
        t["sessions"], t["worked_duration"], t["effective_duration"], t["abnormal"],
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

Write-Host "`n--- Проверка синтаксиса ---" -ForegroundColor Cyan
python -c "import ast; ast.parse(open(r'$serverDir\models.py', encoding='utf-8').read()); ast.parse(open(r'$serverDir\web_admin.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — шаблоны (base, settings, reports, report_result)
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

# ============================================================
# base.html — добавляем ссылку "Настройки"
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
    .app-bar { display:inline-block; height: 10px; background:#4a90e2; border-radius:2px; vertical-align:middle; }
    details > summary { list-style: none; }
    details > summary::-webkit-details-marker { display: none; }
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
# settings.html (новый)
# ============================================================
$settings_html = @'
{% extends "base.html" %}
{% block title %}Настройки{% endblock %}
{% block content %}
<h3 class="mb-4">Настройки системы</h3>

{% if saved %}
<div class="alert alert-success py-2">? Настройки сохранены. Клиенты подхватят изменения в течение 5 минут.</div>
{% endif %}

<div class="card" style="max-width:720px">
  <div class="card-body">
    <form method="post" action="/admin/settings/save">
      <div class="mb-3">
        <label class="form-label">
          Закрывать «висящие» сессии через
          <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени, клиент автоматически закроет сессию временем последней активности. Клиенты получают новое значение при следующей синхронизации (максимум через 5 минут).">?</span>
        </label>
        <div class="input-group" style="max-width:260px">
          <input type="number" name="idle_close_minutes" class="form-control"
                 value="{{ idle_close_minutes }}" min="5" max="480" required>
          <span class="input-group-text">минут без активности</span>
        </div>
        <div class="form-text">
          Рекомендуется 30 минут. Минимум 5, максимум 480 (8 часов).
        </div>
      </div>

      <div class="alert alert-info py-2 small mb-3">
        <strong>Как это работает:</strong> клиент на каждом ПК раз в 5 минут получает
        актуальное значение с сервера. Если с последней активности прошло больше
        указанного времени — сессия закрывается автоматически, причём временем
        <em>последней активности</em>, а не моментом срабатывания таймера.
        Сессия помечается как «аварийная».
      </div>

      <button class="btn btn-primary">Сохранить</button>
    </form>
  </div>
</div>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\settings.html", $settings_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  settings.html" -ForegroundColor Green

# ============================================================
# reports.html — обновляем справку по колонкам
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
        <label class="form-label">С даты</label>
        <input class="form-control" type="date" name="date_from" id="date_from" required value="{{ today }}">
      </div>
      <div class="col-md-3">
        <label class="form-label">По дату</label>
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
          <span class="hint" data-bs-toggle="tooltip" title="Сессии, начавшиеся раньше этого часа, относятся к предыдущему рабочему дню. Для ночных смен.">?</span>
        </label>
        <select name="workday_start_hour" class="form-select">
          {% for h in range(0, 24) %}
            <option value="{{ h }}" {% if h == default_workday_start %}selected{% endif %}>{{ '%02d' % h }}:00</option>
          {% endfor %}
        </select>
      </div>

      <div class="col-md-2">
        <label class="form-label">Формат</label>
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
            <label class="form-check-label" for="show_apps">Топ-программы (с разбивкой по сотрудникам)</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_abnormal" id="show_abnormal" checked>
            <label class="form-check-label" for="show_abnormal">Пометки аварийных завершений</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="expand_details" id="expand_details">
            <label class="form-check-label" for="expand_details">Разворачивать детали (сессии и программы)</label>
          </div>
        </div>
      </div>

      <div class="col-12">
        <div class="alert alert-secondary py-2 small mb-0">
          <strong>Что означают колонки:</strong>
          <ul class="mb-0 mt-1">
            <li><strong>Отработано</strong> — от старта первой сессии до конца последней сессии за день (включает перерывы между сессиями).</li>
            <li><strong>Эффективно</strong> — сумма активного времени во всех сессиях (без больших пауз &gt; 5 минут).</li>
          </ul>
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
# report_result.html — новая логика колонок + топ программ с разбивкой
