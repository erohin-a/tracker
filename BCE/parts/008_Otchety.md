# ---------- Отчёты ----------

*Часть 8 из 100. Источник: `BCE.md`.*

[◀ ---------- Компьютеры ----------](007_Kompyutery.md) | [Оглавление](00_BCE_INDEX.md) | [Логи api ▶](009_Logi_api.md)

---

# ---------- Отчёты ----------

@router.get("/reports", response_class=HTMLResponse)
def reports_form(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).filter(Employee.is_active == True).order_by(Employee.last_name).all()
    computers = db.query(Computer).filter(Computer.is_active == True).order_by(Computer.hostname).all()
    return templates.TemplateResponse("reports.html", {
        "request": request, "employees": employees, "computers": computers,
        "admin": request.session.get("admin"),
    })


def _build_report(db: Session, employee_id: Optional[int], computer_id: Optional[int],
                  date_from: date, date_to: date) -> dict:
    dt_from = datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
    dt_to = datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc)

    q = db.query(WorkSession).filter(
        WorkSession.session_start >= dt_from,
        WorkSession.session_start <= dt_to,
    )
    if employee_id:
        q = q.filter(WorkSession.employee_id == employee_id)
    if computer_id:
        q = q.filter(WorkSession.computer_id == computer_id)

    sessions = q.order_by(WorkSession.session_start).all()

    rows = []
    total_seconds = 0
    total_keyboard = 0
    total_mouse = 0
    app_totals: dict[str, int] = {}

    for ws in sessions:
        start = ws.session_start
        end = ws.session_end or _now()
        duration = max(0, int((end - start).total_seconds()))
        total_seconds += duration

        recs = (db.query(Record)
                .filter(Record.session_uid == ws.session_uid)
                .order_by(Record.client_ts).all())

        keyboard = 0
        mouse = 0
        windows = []  # (ts, app_name)
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
                windows.append((r.client_ts, app))

        for i, (ts, app) in enumerate(windows):
            next_ts = windows[i + 1][0] if i + 1 < len(windows) else end
            dur = max(0, int((next_ts - ts).total_seconds()))
            if dur > 0:
                app_totals[app] = app_totals.get(app, 0) + dur

        total_keyboard += keyboard
        total_mouse += mouse

        emp = db.query(Employee).get(ws.employee_id) if ws.employee_id else None
        comp = db.query(Computer).get(ws.computer_id)

        rows.append({
            "session_uid": ws.session_uid,
            "employee": emp.full_name if emp else "—",
            "computer": (comp.hostname or comp.computer_uid) if comp else "—",
            "start": start,
            "end": end,
            "duration": duration,
            "keyboard": keyboard,
            "mouse": mouse,
            "abnormal": ws.abnormal_termination,
        })

    top_apps = sorted(
        [{"app": k, "seconds": v} for k, v in app_totals.items()],
        key=lambda x: x["seconds"], reverse=True,
    )

    return {
        "rows": rows,
        "totals": {
            "sessions": len(sessions),
            "duration": total_seconds,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "top_apps": top_apps[:10],
        },
        "date_from": date_from,
        "date_to": date_to,
    }


@router.post("/reports/generate")
def reports_generate(
    request: Request,
    employee_id: str = Form(""),
    computer_id: str = Form(""),
    date_from: str = Form(...),
    date_to: str = Form(...),
    fmt: str = Form("html"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    if d_to < d_from:
        raise HTTPException(400, "date_to < date_from")

    emp_id = int(employee_id) if employee_id else None
    comp_id = int(computer_id) if computer_id else None

    report = _build_report(db, emp_id, comp_id, d_from, d_to)

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["session_uid", "employee", "computer", "start", "end",
                         "duration_sec", "keyboard_sec", "mouse_sec", "abnormal"])
        for r in report["rows"]:
            writer.writerow([
                r["session_uid"], r["employee"], r["computer"],
                r["start"].isoformat(), r["end"].isoformat(),
                r["duration"], r["keyboard"], r["mouse"], int(r["abnormal"]),
            ])
        writer.writerow([])
        writer.writerow(["ИТОГО", "", "", "", "",
                         report["totals"]["duration"],
                         report["totals"]["keyboard"],
                         report["totals"]["mouse"], ""])
        output.seek(0)
        # BOM для Excel
        data = "\ufeff" + output.getvalue()
        return StreamingResponse(
            iter([data]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.csv"},
        )

    if fmt == "xlsx":
        from openpyxl import Workbook
        from openpyxl.styles import Font

        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        headers = ["session_uid", "employee", "computer", "start", "end",
                   "duration_sec", "keyboard_sec", "mouse_sec", "abnormal"]
        ws.append(headers)
        for c in ws[1]:
            c.font = Font(bold=True)

        for r in report["rows"]:
            ws.append([
                r["session_uid"], r["employee"], r["computer"],
                r["start"].strftime("%Y-%m-%d %H:%M:%S"),
                r["end"].strftime("%Y-%m-%d %H:%M:%S"),
                r["duration"], r["keyboard"], r["mouse"], int(r["abnormal"]),
            ])

        ws.append([])
        ws.append(["ИТОГО", "", "", "", "",
                   report["totals"]["duration"],
                   report["totals"]["keyboard"],
                   report["totals"]["mouse"], ""])

        # Автоширина
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
        "request": request, "report": report, "admin": request.session.get("admin"),
    })


# ---------- Аудит ----------

@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    logs = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(200).all()
    return templates.TemplateResponse("audit.html", {
        "request": request, "logs": logs, "admin": request.session.get("admin"),
    })
________________________________________
Шаг 5. Шаблоны
server/templates/base.html
html
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
  </style>
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container">
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
<div class="container">
  {% block content %}{% endblock %}
</div>
</body>
</html>
server/templates/login.html
html
{% extends "base.html" %}
{% block title %}Вход{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-4">
    <div class="card shadow-sm">
      <div class="card-body">
        <h4 class="card-title mb-3">Вход администратора</h4>
        {% if error %}<div class="alert alert-danger py-2">{{ error }}</div>{% endif %}
        <form method="post" action="/admin/login">
          <div class="mb-2">
            <label class="form-label">Логин</label>
            <input class="form-control" name="username" value="admin" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Ключ (ADMIN_API_KEY)</label>
            <input class="form-control" type="password" name="password" required>
          </div>
          <button class="btn btn-primary w-100">Войти</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
server/templates/dashboard.html
html
{% extends "base.html" %}
{% block content %}
<h3 class="mb-4">Дашборд</h3>

<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Сотрудники</div>
    <div class="fs-3">{{ stats.employees }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Компьютеры</div>
    <div class="fs-3">{{ stats.computers }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий сегодня</div>
    <div class="fs-3">{{ stats.sessions_today }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий за 7 дней</div>
    <div class="fs-3">{{ stats.sessions_week }}</div>
  </div></div></div>
</div>

<div class="row g-3 mb-4">
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Всего записей</div>
    <div class="fs-4">{{ stats.records }}</div>
  </div></div></div>
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Активных bootstrap-токенов</div>
    <div class="fs-4">{{ stats.tokens_active }}</div>
  </div></div></div>
</div>

<div class="row g-3">
  <div class="col-md-6">
    <div class="card">
      <div class="card-header">Последние зарегистрированные ПК</div>
      <div class="card-body p-0">
        <table class="table table-sm mb-0">
          <thead><tr><th>Hostname</th><th>UID</th><th>Регистрация</th></tr></thead>
          <tbody>
          {% for c in recent_computers %}
            <tr>
              <td>{{ c.hostname or '—' }}</td>
              <td><code>{{ c.computer_uid[:12] }}…</code></td>
              <td>{{ c.registered_at | dt }}</td>
            </tr>
          {% else %}
            <tr><td colspan="3" class="text-muted">Нет данных</td></tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <div class="col-md-6">
    <div class="card">
      <div class="card-header">Последние действия</div>
      <div class="card-body p-0">
        <table class="table table-sm mb-0">
          <thead><tr><th>Время</th><th>Сущность</th><th>Действие</th></tr></thead>
          <tbody>
          {% for a in recent_audit %}
            <tr>
              <td>{{ a.created_at | dt }}</td>
              <td>{{ a.entity }} #{{ a.entity_id or '—' }}</td>
              <td><span class="badge badge-soft">{{ a.action }}</span></td>
            </tr>
          {% else %}
            <tr><td colspan="3" class="text-muted">Нет данных</td></tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{% endblock %}
server/templates/employees.html
html
{% extends "base.html" %}
{% block content %}
<h3 class="mb-4">Сотрудники</h3>

<div class="card mb-4">
  <div class="card-header">Добавить сотрудника</div>
  <div class="card-body">
    <form method="post" action="/admin/employees/create" class="row g-2">
      <div class="col-md-3"><input class="form-control" name="last_name" placeholder="Фамилия *" required></div>
      <div class="col-md-3"><input class="form-control" name="first_name" placeholder="Имя *" required></div>
      <div class="col-md-3"><input class="form-control" name="middle_name" placeholder="Отчество"></div>
      <div class="col-md-2"><input class="form-control" name="external_id" placeholder="1C ID"></div>
      <div class="col-md-1"><button class="btn btn-success w-100">+</button></div>
    </form>
  </div>
</div>

<table class="table table-sm table-hover bg-white">
  <thead><tr>
    <th>ID</th><th>ФИО</th><th>1C</th><th>Активен</th><th>Действия</th>
  </tr></thead>
  <tbody>
  {% for e in employees %}
    <tr>
      <td>{{ e.id }}</td>
      <td>
        <form method="post" action="/admin/employees/{{ e.id }}/edit" class="d-flex gap-1">
          <input class="form-control form-control-sm" name="last_name" value="{{ e.last_name or '' }}" style="width:130px">
          <input class="form-control form-control-sm" name="first_name" value="{{ e.first_name or '' }}" style="width:110px">
          <input class="form-control form-control-sm" name="middle_name" value="{{ e.middle_name or '' }}" style="width:130px">
          <input class="form-control form-control-sm" name="external_id" value="{{ e.external_id or '' }}" placeholder="1C" style="width:90px">
          <button class="btn btn-sm btn-outline-primary">??</button>
        </form>
      </td>
      <td>{{ e.external_id or '—' }}</td>
      <td>
        {% if e.is_active %}<span class="badge bg-success">Да</span>
        {% else %}<span class="badge bg-secondary">Нет</span>{% endif %}
      </td>
      <td>
        {% if e.is_active %}
          <form method="post" action="/admin/employees/{{ e.id }}/deactivate" class="d-inline">
            <button class="btn btn-sm btn-outline-danger">Деактивировать</button>
          </form>
        {% else %}
          <form method="post" action="/admin/employees/{{ e.id }}/activate" class="d-inline">
            <button class="btn btn-sm btn-outline-success">Активировать</button>
          </form>
        {% endif %}
      </td>
    </tr>
  {% else %}
    <tr><td colspan="5" class="text-muted">Сотрудников пока нет</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
server/templates/computers.html
html
{% extends "base.html" %}
{% block content %}
<h3 class="mb-4">Компьютеры</h3>

<table class="table table-sm table-hover bg-white">
  <thead><tr>
    <th>ID</th><th>Hostname</th><th>UID</th><th>Сотрудник</th>
    <th>Last seen</th><th>Статус</th><th>Действия</th>
  </tr></thead>
  <tbody>
  {% for c in computers %}
    <tr>
      <td>{{ c.id }}</td>
      <td>{{ c.hostname or '—' }}</td>
      <td><code title="{{ c.computer_uid }}">{{ c.computer_uid[:14] }}…</code></td>
      <td>
        <form method="post" action="/admin/computers/{{ c.id }}/assign" class="d-flex gap-1">
          <select name="employee_id" class="form-select form-select-sm">
            <option value="">— не привязан —</option>
            {% for e in employees %}
              <option value="{{ e.id }}" {% if c.employee_id == e.id %}selected{% endif %}>
                {{ e.full_name }}
              </option>
            {% endfor %}
          </select>
          <button class="btn btn-sm btn-primary">OK</button>
        </form>
      </td>
      <td>{{ c.last_seen_at | dt }}</td>
      <td>
        {% if c.is_active %}<span class="badge bg-success">Активен</span>
        {% else %}<span class="badge bg-secondary">Отключён</span>{% endif %}
      </td>
      <td>
        {% if c.is_active %}
          <form method="post" action="/admin/computers/{{ c.id }}/revoke" class="d-inline">
            <button class="btn btn-sm btn-outline-danger">Отключить</button>
          </form>
        {% else %}
          <form method="post" action="/admin/computers/{{ c.id }}/activate" class="d-inline">
            <button class="btn btn-sm btn-outline-success">Включить</button>
          </form>
        {% endif %}
      </td>
    </tr>
  {% else %}
    <tr><td colspan="7" class="text-muted">Компьютеров пока нет</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
server/templates/tokens.html
html
{% extends "base.html" %}
{% block content %}
<h3 class="mb-4">Bootstrap-токены</h3>

{% if new_token %}
<div class="alert alert-success">
  <strong>Токен создан — скопируйте его сейчас, второй раз не покажем:</strong>
  <div class="mt-2"><code id="newtok">{{ new_token }}</code></div>
  <button class="btn btn-sm btn-outline-secondary mt-2"
          onclick="navigator.clipboard.writeText(document.getElementById('newtok').innerText)">Скопировать</button>
</div>
{% endif %}

<div class="card mb-4">
  <div class="card-header">Выпустить новый токен</div>
  <div class="card-body">
    <form method="post" action="/admin/tokens/issue" class="row g-2">
      <div class="col-md-3">
        <label class="form-label">TTL (часы)</label>
        <input class="form-control" type="number" name="ttl_hours" value="24" min="1" max="720">
      </div>
      <div class="col-md-4">
        <label class="form-label">Кто выдал</label>
        <input class="form-control" name="issued_by" value="admin">
      </div>
      <div class="col-md-2 d-flex align-items-end">
        <button class="btn btn-primary w-100">Выпустить</button>
      </div>
    </form>
  </div>
</div>

<table class="table table-sm bg-white">
  <thead><tr><th>ID</th><th>Hash</th><th>Кто выдал</th><th>Истекает</th><th>Использован</th><th>Кем</th></tr></thead>
  <tbody>
  {% for t in tokens %}
    <tr>
      <td>{{ t.id }}</td>
      <td><code>{{ t.token_hash[:12] }}…</code></td>
      <td>{{ t.issued_by or '—' }}</td>
      <td>{{ t.expires_at | dt }}</td>
      <td>{% if t.used_at %}<span class="badge bg-secondary">{{ t.used_at | dt }}</span>{% else %}<span class="badge bg-success">нет</span>{% endif %}</td>
      <td>{{ t.used_by_uid or '—' }}</td>
    </tr>
  {% else %}
    <tr><td colspan="6" class="text-muted">Токенов пока нет</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
server/templates/reports.html
html
{% extends "base.html" %}
{% block content %}
<h3 class="mb-4">Отчёты</h3>

<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/reports/generate" class="row g-3">
      <div class="col-md-4">
        <label class="form-label">Сотрудник</label>
        <select name="employee_id" class="form-select">
          <option value="">Все сотрудники</option>
          {% for e in employees %}<option value="{{ e.id }}">{{ e.full_name }}</option>{% endfor %}
        </select>
      </div>
      <div class="col-md-4">
        <label class="form-label">Компьютер</label>
        <select name="computer_id" class="form-select">
          <option value="">Все компьютеры</option>
          {% for c in computers %}<option value="{{ c.id }}">{{ c.hostname or c.computer_uid[:14] }}</option>{% endfor %}
        </select>
      </div>
      <div class="col-md-2">
        <label class="form-label">С даты</label>
        <input class="form-control" type="date" name="date_from" required>
      </div>
      <div class="col-md-2">
        <label class="form-label">По дату</label>
        <input class="form-control" type="date" name="date_to" required>
      </div>
      <div class="col-md-3">
        <label class="form-label">Формат</label>
        <select name="fmt" class="form-select">
          <option value="html">Просмотр</option>
          <option value="csv">CSV</option>
          <option value="xlsx">Excel (XLSX)</option>
        </select>
      </div>
      <div class="col-12">
        <button class="btn btn-primary">Сформировать</button>
      </div>
    </form>
  </div>
</div>
{% endblock %}
server/templates/report_result.html
html
{% extends "base.html" %}
{% block content %}
<h3 class="mb-3">Отчёт {{ report.date_from }} — {{ report.date_to }}</h3>

<div class="row g-3 mb-3">
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий</div>
    <div class="fs-4">{{ report.totals.sessions }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Всего времени</div>
    <div class="fs-4">{{ report.totals.duration | dur }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Клавиатура</div>
    <div class="fs-4">{{ report.totals.keyboard | dur }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Мышь</div>
    <div class="fs-4">{{ report.totals.mouse | dur }}</div>
  </div></div></div>
</div>

<div class="row g-3 mb-4">
  <div class="col-md-6">
    <div class="card">
      <div class="card-header">Топ программ</div>
      <div class="card-body p-0">
        <table class="table table-sm mb-0">
          <thead><tr><th>Программа</th><th>Время</th></tr></thead>
          <tbody>
          {% for a in report.totals.top_apps %}
            <tr><td>{{ a.app }}</td><td>{{ a.seconds | dur }}</td></tr>
          {% else %}
            <tr><td colspan="2" class="text-muted">Нет данных</td></tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<table class="table table-sm table-hover bg-white">
  <thead><tr>
    <th>Сотрудник</th><th>ПК</th><th>Начало</th><th>Конец</th>
    <th>Длительность</th><th>Клав.</th><th>Мышь</th><th>Аварийное</th>
  </tr></thead>
  <tbody>
  {% for r in report.rows %}
    <tr>
      <td>{{ r.employee }}</td>
      <td>{{ r.computer }}</td>
      <td>{{ r.start | dt }}</td>
      <td>{{ r.end | dt }}</td>
      <td>{{ r.duration | dur }}</td>
      <td>{{ r.keyboard | dur }}</td>
      <td>{{ r.mouse | dur }}</td>
      <td>{% if r.abnormal %}<span class="badge bg-warning text-dark">да</span>{% endif %}</td>
    </tr>
  {% else %}
    <tr><td colspan="8" class="text-muted">Нет сессий за выбранный период</td></tr>
  {% endfor %}
  </tbody>
</table>

<a class="btn btn-outline-secondary" href="/admin/reports">? Назад</a>
{% endblock %}
server/templates/audit.html
html
{% extends "base.html" %}
{% block content %}
<h3 class="mb-4">Аудит (последние 200)</h3>
<table class="table table-sm bg-white">
  <thead><tr><th>ID</th><th>Время</th><th>Actor</th><th>Entity</th><th>Entity ID</th><th>Action</th><th>Old ? New</th></tr></thead>
  <tbody>
  {% for l in logs %}
    <tr>
      <td>{{ l.id }}</td>
      <td>{{ l.created_at | dt }}</td>
      <td>{{ l.actor or '—' }}</td>
      <td>{{ l.entity }}</td>
      <td>{{ l.entity_id or '—' }}</td>
      <td><span class="badge badge-soft">{{ l.action }}</span></td>
      <td>
        <small class="text-muted">
          {{ (l.old_value or '')[:40] }}{% if l.old_value and l.old_value|length > 40 %}…{% endif %}
          {% if l.new_value %} ? {{ l.new_value[:60] }}{% if l.new_value|length > 60 %}…{% endif %}{% endif %}
        </small>
      </td>
    </tr>
  {% else %}
    <tr><td colspan="7" class="text-muted">Пусто</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
________________________________________
Шаг 6. Дополнить модели (если ещё не сделано)
В server/models.py:
В Employee должны быть поля ФИО (если их ещё нет):
python
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    last_name = Column(String(50))      # ? добавить
    first_name = Column(String(50))     # ? добавить
    middle_name = Column(String(50))    # ? добавить
    external_id = Column(String(64), unique=True)
    is_active = Column(Boolean, default=True)
В Computer — привязка к сотруднику:
python
class Computer(Base):
    # ... существующие поля ...
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True))
В WorkSession — employee_id должен существовать (в исходнике он уже есть).
Если БД уже поднята и в ней есть данные, а колонок ещё нет — либо сносим volume (docker compose down -v), либо вручную:
sql
ALTER TABLE computers ADD COLUMN employee_id INTEGER REFERENCES employees(id);
ALTER TABLE computers ADD COLUMN assigned_at TIMESTAMPTZ;
ALTER TABLE employees ADD COLUMN last_name VARCHAR(50);
ALTER TABLE employees ADD COLUMN first_name VARCHAR(50);
ALTER TABLE employees ADD COLUMN middle_name VARCHAR(50);
________________________________________
Шаг 7. Подключить роутер и сессии в server/main.py
В самое начало файла, после существующих импортов:
python
from starlette.middleware.sessions import SessionMiddleware
from .web_admin import router as admin_web_router
После создания app = FastAPI(...):
python
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret or settings.jwt_secret,
    session_cookie="tracker_admin",
    max_age=8 * 3600,
    same_site="lax",       # для прода можно "strict"
    https_only=settings.web_secure_cookie,  # True на HTTPS
)

app.include_router(admin_web_router)
Добавьте в server/config.py в Settings поля session_secret: str = "" и web_secure_cookie: bool = False — если ещё не сделали.
________________________________________
Шаг 8. Пересобрать и запустить
powershell
cd D:\tracker

# Проверьте, что .env содержит ADMIN_API_KEY и JWT_SECRET
docker compose down
docker compose up -d --build

