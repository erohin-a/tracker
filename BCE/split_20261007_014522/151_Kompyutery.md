<!-- Часть 151 из 1409 -->
# ---------- Компьютеры ----------
*Хлебные крошки:* ---------- Компьютеры ----------

[◀ ---------- Сотрудники ----------](150_Sotrudniki.md) | [Оглавление](00_BCE_INDEX.md) | [в __init__ после layout.addWidget(self.status): ▶](152_v_init_posle_layout_addWidgetself_status.md)

---

# ---------- Компьютеры ----------

@router.get("/computers", response_class=HTMLResponse)
def computers_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).all()
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    return templates.TemplateResponse(
        "computers.html",
        {"request": request, "computers": computers, "employees": employees},
    )


@router.post("/computers/{comp_id}/assign")
def computer_assign(
    comp_id: int,
    employee_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    comp = db.query(Computer).get(comp_id)
    if not comp:
        raise HTTPException(404)
    comp.employee_id = employee_id
    comp.assigned_at = datetime.now(timezone.utc)
    db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id),
                    action="assign", new_value=json.dumps({"employee_id": employee_id})))
    db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


@router.post("/computers/{comp_id}/revoke")
def computer_revoke(comp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    comp = db.query(Computer).get(comp_id)
    if comp:
        comp.is_active = False
        db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id),
                        action="revoke"))
        db.commit()
    return RedirectResponse("/admin/computers", status_code=303)
4.4. Шаблоны
Создайте server/templates/base.html:
html
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Tracker Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
        <a class="navbar-brand" href="/admin">Tracker Admin</a>
        <div class="navbar-nav">
            <a class="nav-link" href="/admin/employees">Сотрудники</a>
            <a class="nav-link" href="/admin/computers">Компьютеры</a>
            <a class="nav-link" href="/admin/reports">Отчёты</a>
            <a class="nav-link" href="/admin/logout">Выход</a>
        </div>
    </div>
</nav>
<div class="container">
    {% block content %}{% endblock %}
</div>
</body>
</html>
login.html:
html
{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-4">
    <h3>Вход администратора</h3>
    {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
    <form method="post">
      <input class="form-control mb-2" name="username" placeholder="Логин" value="admin">
      <input class="form-control mb-2" type="password" name="password" placeholder="ADMIN_API_KEY">
      <button class="btn btn-primary w-100">Войти</button>
    </form>
  </div>
</div>
{% endblock %}
employees.html:
html
{% extends "base.html" %}
{% block content %}
<h3>Сотрудники</h3>
<form method="post" action="/admin/employees/create" class="row g-2 mb-3">
  <div class="col"><input class="form-control" name="last_name" placeholder="Фамилия" required></div>
  <div class="col"><input class="form-control" name="first_name" placeholder="Имя" required></div>
  <div class="col"><input class="form-control" name="middle_name" placeholder="Отчество"></div>
  <div class="col"><input class="form-control" name="external_id" placeholder="1C ID"></div>
  <div class="col"><button class="btn btn-success">Добавить</button></div>
</form>
<table class="table table-sm table-striped bg-white">
  <thead><tr><th>ID</th><th>ФИО</th><th>1C</th><th>Активен</th><th></th></tr></thead>
  <tbody>
  {% for e in employees %}
    <tr>
      <td>{{ e.id }}</td>
      <td>{{ e.full_name }}</td>
      <td>{{ e.external_id or "" }}</td>
      <td>{{ "Да" if e.is_active else "Нет" }}</td>
      <td>
        {% if e.is_active %}
        <form method="post" action="/admin/employees/{{ e.id }}/deactivate">
          <button class="btn btn-sm btn-outline-danger">Деактивировать</button>
        </form>
        {% endif %}
      </td>
    </tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
computers.html:
html
{% extends "base.html" %}
{% block content %}
<h3>Компьютеры</h3>
<table class="table table-sm table-striped bg-white">
  <thead><tr><th>ID</th><th>UID</th><th>Hostname</th><th>Сотрудник</th><th>Last seen</th><th>Активен</th><th></th></tr></thead>
  <tbody>
  {% for c in computers %}
    <tr>
      <td>{{ c.id }}</td>
      <td>{{ c.computer_uid[:12] }}...</td>
      <td>{{ c.hostname or "" }}</td>
      <td>
        <form method="post" action="/admin/computers/{{ c.id }}/assign" class="d-flex">
          <select name="employee_id" class="form-select form-select-sm me-1">
            <option value="">— не привязан —</option>
            {% for e in employees %}
              <option value="{{ e.id }}" {% if c.employee_id == e.id %}selected{% endif %}>{{ e.full_name }}</option>
            {% endfor %}
          </select>
          <button class="btn btn-sm btn-primary">OK</button>
        </form>
      </td>
      <td>{{ c.last_seen_at or "" }}</td>
      <td>{{ "Да" if c.is_active else "Нет" }}</td>
      <td>
        {% if c.is_active %}
        <form method="post" action="/admin/computers/{{ c.id }}/revoke">
          <button class="btn btn-sm btn-outline-danger">Отключить</button>
        </form>
        {% endif %}
      </td>
    </tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
________________________________________
5. Отчёты
5.1. server/reports.py
python
import json
from datetime import datetime, date, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .models import WorkSession, Record, Computer, Employee


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def build_report(
    db: Session,
    employee_id: Optional[int],
    computer_id: Optional[int],
    date_from: date,
    date_to: date,
) -> dict:
    q = db.query(WorkSession).join(Computer)
    q = q.filter(WorkSession.session_start >= datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc))
    q = q.filter(WorkSession.session_start <= datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc))
    if employee_id:
        q = q.filter(WorkSession.employee_id == employee_id)
    if computer_id:
        q = q.filter(WorkSession.computer_id == computer_id)

    sessions = q.all()
    rows = []
    total_seconds = 0
    total_keyboard = 0
    total_mouse = 0
    app_totals = {}

    for ws in sessions:
        start = ws.session_start
        end = ws.session_end or datetime.now(timezone.utc)
        duration = int((end - start).total_seconds())
        total_seconds += duration

        recs = db.query(Record).filter(Record.session_uid == ws.session_uid).order_by(Record.client_ts).all()

        keyboard = 0
        mouse = 0
        window_records = []
        for r in recs:
            try:
                data = json.loads(r.data) if r.data else {}
            except Exception:
                data = {}
            if r.kind == "activity":
                keys = int(data.get("keys", 0))
                clicks = int(data.get("clicks", 0))
                scroll = int(data.get("scroll", 0))
                if keys + clicks + scroll > 0:
                    keyboard += 5  # интервал опроса 5 сек
                    mouse += 5
            elif r.kind == "window":
                window_records.append((r.client_ts, data.get("app") or data.get("title") or "unknown"))

        # длительности по окнам
        for i, (ts, app) in enumerate(window_records):
            next_ts = window_records[i + 1][0] if i + 1 < len(window_records) else end
            dur = int((next_ts - ts).total_seconds())
            if dur > 0:
                app_totals[app] = app_totals.get(app, 0) + dur

        total_keyboard += keyboard
        total_mouse += mouse

        emp = db.query(Employee).get(ws.employee_id) if ws.employee_id else None
        comp = db.query(Computer).get(ws.computer_id)
        rows.append({
            "session_uid": ws.session_uid,
            "employee": emp.full_name if emp else "—",
            "computer": comp.hostname or comp.computer_uid if comp else "—",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "duration": duration,
            "keyboard": keyboard,
            "mouse": mouse,
            "top_apps": sorted(
                [{"app": k, "seconds": v} for k, v in app_totals.items()],
                key=lambda x: x["seconds"], reverse=True
            )[:5],
        })

    return {
        "rows": rows,
        "totals": {
            "sessions": len(sessions),
            "duration": total_seconds,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "top_apps": sorted(
                [{"app": k, "seconds": v} for k, v in app_totals.items()],
                key=lambda x: x["seconds"], reverse=True
            )[:10],
        },
    }
5.2. Экспорт CSV/Excel
В web_admin.py добавьте:
python
import csv, io
from openpyxl import Workbook
from .reports import build_report


@router.get("/reports", response_class=HTMLResponse)
def reports_form(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    computers = db.query(Computer).filter(Computer.is_active == True).all()
    return templates.TemplateResponse("reports.html", {
        "request": request, "employees": employees, "computers": computers
    })


@router.post("/reports/generate")
def reports_generate(
    request: Request,
    employee_id: Optional[int] = Form(None),
    computer_id: Optional[int] = Form(None),
    date_from: str = Form(...),
    date_to: str = Form(...),
    fmt: str = Form("html"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    report = build_report(db, employee_id, computer_id, d_from, d_to)

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["session_uid", "employee", "computer", "start", "end", "duration", "keyboard", "mouse"])
        for r in report["rows"]:
            writer.writerow([r["session_uid"], r["employee"], r["computer"], r["start"], r["end"],
                             r["duration"], r["keyboard"], r["mouse"]])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=report.csv"}
        )

    if fmt == "xlsx":
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"
        ws.append(["session_uid", "employee", "computer", "start", "end", "duration", "keyboard", "mouse"])
        for r in report["rows"]:
            ws.append([r["session_uid"], r["employee"], r["computer"], r["start"], r["end"],
                       r["duration"], r["keyboard"], r["mouse"]])
        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=report.xlsx"}
        )

    return templates.TemplateResponse("report_result.html", {
        "request": request, "report": report, "date_from": date_from, "date_to": date_to
    })
reports.html:
html
{% extends "base.html" %}
{% block content %}
<h3>Отчёты</h3>
<form method="post" action="/admin/reports/generate" class="row g-2 mb-4">
  <div class="col-md-3">
    <select name="employee_id" class="form-select">
      <option value="">Все сотрудники</option>
      {% for e in employees %}<option value="{{ e.id }}">{{ e.full_name }}</option>{% endfor %}
    </select>
  </div>
  <div class="col-md-3">
    <select name="computer_id" class="form-select">
      <option value="">Все компьютеры</option>
      {% for c in computers %}<option value="{{ c.id }}">{{ c.hostname or c.computer_uid }}</option>{% endfor %}
    </select>
  </div>
  <div class="col-md-2"><input class="form-control" type="date" name="date_from" required></div>
  <div class="col-md-2"><input class="form-control" type="date" name="date_to" required></div>
  <div class="col-md-2">
    <select name="fmt" class="form-select">
      <option value="html">Просмотр</option>
      <option value="csv">CSV</option>
      <option value="xlsx">Excel</option>
    </select>
  </div>
  <div class="col-12"><button class="btn btn-primary">Сформировать</button></div>
</form>
{% endblock %}
report_result.html:
html
{% extends "base.html" %}
{% block content %}
<h3>Отчёт {{ date_from }} — {{ date_to }}</h3>
<p>Сессий: {{ report.totals.sessions }}, всего секунд: {{ report.totals.duration }},
клавиатура: {{ report.totals.keyboard }}, мышь: {{ report.totals.mouse }}</p>
<table class="table table-sm table-striped bg-white">
  <thead><tr><th>Сотрудник</th><th>ПК</th><th>Начало</th><th>Конец</th><th>Сек</th><th>Клав</th><th>Мышь</th></tr></thead>
  <tbody>
  {% for r in report.rows %}
    <tr>
      <td>{{ r.employee }}</td><td>{{ r.computer }}</td>
      <td>{{ r.start }}</td><td>{{ r.end }}</td>
      <td>{{ r.duration }}</td><td>{{ r.keyboard }}</td><td>{{ r.mouse }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
________________________________________
6. Клиент: автозапуск
6.1. client/autostart.py
python
import os
import sys
import logging
from pathlib import Path

log = logging.getLogger("tracker.autostart")

APP_NAME = "Tracker"


def set_autostart(enabled: bool) -> bool:
    if sys.platform.startswith("win"):
        return _set_autostart_windows(enabled)
    elif sys.platform.startswith("linux"):
        return _set_autostart_linux(enabled)
    else:
        log.warning("Autostart not supported on %s", sys.platform)
        return False


def _set_autostart_windows(enabled: bool) -> bool:
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            exe = sys.executable
            if exe.endswith("python.exe"):
                # запуск через pythonw -m client.main
                cmd = f'"{exe.replace("python.exe", "pythonw.exe")}" -m client.main'
            else:
                cmd = f'"{exe}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        log.exception("Autostart Windows failed: %s", e)
        return False


def _set_autostart_linux(enabled: bool) -> bool:
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    desktop = autostart_dir / "tracker.desktop"
    if enabled:
        exe = sys.executable
        content = f"""[Desktop Entry]
Type=Application
Name=Tracker
Exec={exe} -m client.main
X-GNOME-Autostart-enabled=true
"""
        desktop.write_text(content, encoding="utf-8")
    else:
        desktop.unlink(missing_ok=True)
    return True
6.2. Интеграция в client/main.py
Добавьте в MainWindow чекбокс:
python
from PyQt6.QtWidgets import QCheckBox
from .autostart import set_autostart
from .config import BASE_DIR
import json

