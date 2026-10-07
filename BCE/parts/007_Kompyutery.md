# ---------- Компьютеры ----------

*Часть 7 из 100. Источник: `BCE.md`.*

[◀ 12. Заключение](006_12_Zaklyuchenie.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Отчёты ---------- ▶](008_Otchety.md)

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

# в __init__ после layout.addWidget(self.status):
self.autostart_cb = QCheckBox("Автозапуск")
self.autostart_cb.setChecked(self._load_autostart_setting())
self.autostart_cb.stateChanged.connect(self._on_autostart_changed)
layout.addWidget(self.autostart_cb)

def _load_autostart_setting(self) -> bool:
    cfg = BASE_DIR / "config.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text(encoding="utf-8")).get("autostart_enabled", False)
        except Exception:
            pass
    return False

def _on_autostart_changed(self, state):
    enabled = state == 2  # Qt.CheckState.Checked
    ok = set_autostart(enabled)
    if ok:
        cfg = BASE_DIR / "config.json"
        data = {}
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
            except Exception:
                pass
        data["autostart_enabled"] = enabled
        cfg.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
________________________________________
7. Установщик Windows (Inno Setup)
Создайте installer.iss:
ini
[Setup]
AppName=Tracker
AppVersion=1.2.0
DefaultDirName={localappdata}\Tracker
DefaultGroupName=Tracker
OutputBaseFilename=TrackerSetup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
WizardStyle=modern

[Files]
Source: "client\dist\Tracker\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\Tracker"; Filename: "{app}\Tracker.exe"
Name: "{userstartup}\Tracker"; Filename: "{app}\Tracker.exe"; Parameters: "--minimized"

[Run]
Filename: "{app}\Tracker.exe"; Description: "Запустить Tracker"; Flags: nowait postinstall skipifsilent

[Code]
var
  TokenPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  TokenPage := CreateInputQueryPage(wpSelectTasks,
    'Bootstrap-токен', 'Введите одноразовый токен',
    'Получите токен у администратора и вставьте сюда. Он будет сохранён в %APPDATA%\Tracker\bootstrap.txt');
  TokenPage.Add('Токен:', False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Token: String;
  Dir: String;
begin
  if CurStep = ssPostInstall then
  begin
    Token := TokenPage.Values[0];
    if Token <> '' then
    begin
      Dir := ExpandConstant('{userappdata}\Tracker');
      ForceDirectories(Dir);
      SaveStringToFile(Dir + '\bootstrap.txt', Token, False);
    end;
  end;
end;
Сборка:
powershell
cd D:\tracker\client
pyinstaller build.spec --clean
cd ..
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
________________________________________
8. Что делать по шагам
Обновить модели
Добавить employee_id в Computer, поля ФИО в Employee, поправить upsert_session.
Пересобрать сервер
docker compose down, docker compose up -d --build.
Если БД уже есть — вручную ALTER TABLE или подключить Alembic.
Добавить веб-админку
Создать server/web_admin.py, server/templates/*, подключить SessionMiddleware и роутер в main.py.
Добавить отчёты
Создать server/reports.py, добавить эндпоинты и шаблоны.
Проверить
Зайти на https://localhost/admin/login, ввести admin и ADMIN_API_KEY.
Создать сотрудника, привязать компьютер, сформировать отчёт.
Клиент: автозапуск
Добавить client/autostart.py, чекбокс в главное окно.
Собрать установщик
pyinstaller build.spec, затем Inno Setup.
Обновить requirements
Не забыть jinja2, python-multipart, itsdangerous, openpyxl, reportlab.
Alembic (следующий шаг)
Инициализировать alembic, создать миграцию на текущую схему, дальше менять только через миграции.
________________________________________
9. Что ещё стоит сделать в ближайшее время
Heartbeat-эндпоинт /api/v1/heartbeat — клиент раз в 5 минут шлёт X-Computer-Uid, сервер обновляет last_seen_at.
Роли admin/operator/viewer — таблица admin_users, хеш пароля через passlib.
Публикация версий через UI — форма добавления записи в client_versions.
Бэкап PostgreSQL — cron + pg_dump, хранение 30 дней.
Тесты — pytest для API, моки для pynput.
Если хотите, могу следующим сообщением выдать:
полный server/web_admin.py с PDF-экспортом;
Alembic-миграцию под новые поля;
готовый build.bat и installer.iss под вашу структуру;
код heartbeat и ролей.
Давай начнем с создания вэб интерфейса
The user wants to start with creating the web interface. Let me provide a complete, working implementation of the web admin interface for the Tracker project. I need to be thorough and give them everything they need to actually run this.
Let me structure this properly:
Requirements update
Server config updates for admin credentials
web_admin.py - main router
Templates (base, login, dashboard, employees, computers, reports)
Static files if needed
Integration into main.py
Testing instructions
I should be practical and give working code. Let me write it out carefully.
Key considerations:
The existing project uses ADMIN_API_KEY for API admin auth
I need a separate login for the web UI (or reuse ADMIN_API_KEY)
Session middleware needed
Jinja2 templates
Bootstrap 5 via CDN (simpler)
Need to handle the existing models (Computer, Employee, WorkSession, Record, BootstrapToken, AuditLog, ClientVersion)
Let me also think about what pages are needed:
Login
Dashboard (stats)
Employees (list, create, edit, deactivate)
Computers (list, assign to employee, revoke)
Bootstrap tokens (issue new)
Reports (list, generate, export)
Audit log
Let me write this carefully and completely.
I should be careful about:
DateTime handling (timezone-aware)
SQLAlchemy 2.0 style vs 1.x style - the existing code uses 1.x style (db.query())
The BootstrapToken issuance logic needs to be reused from main.py
Let me structure the answer well with clear sections.
Веб-интерфейс администратора «Трекер» — пошаговая реализация
Ниже — готовый к запуску код. Разбито на шаги: сначала подготовка, потом файлы, потом подключение и проверка.
________________________________________
Шаг 0. Что получится в итоге
Страницы:
/admin/login — вход по логину/паролю.
/admin — дашборд со статистикой.
/admin/employees — CRUD сотрудников.
/admin/computers — список ПК, привязка к сотрудникам, revoke.
/admin/tokens — выпуск bootstrap-токенов.
/admin/reports — форма отчёта + просмотр + экспорт CSV/XLSX.
/admin/audit — журнал аудита.
Аутентификация — сессия (cookie), логин admin + ADMIN_API_KEY из .env. Позже легко заменить на таблицу admin_users с ролями.
________________________________________
Шаг 1. Дополнить зависимости сервера
server/requirements.txt — добавьте:
txt
jinja2==3.1.4
itsdangerous==2.2.0
openpyxl==3.1.5
python-multipart==0.0.9
Пересоберёте образ позже.
________________________________________
Шаг 2. Дополнить server/config.py
Добавьте в Settings (внутри server/config.py):
python
class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tracker:tracker@db:5432/tracker"
    secret_encryption_key: str = ""
    jwt_secret: str = ""
    admin_api_key: str = ""

    # ? новые поля для веб-интерфейса
    admin_login: str = "admin"
    session_secret: str = ""   # если пусто — используем jwt_secret
    web_secure_cookie: bool = False  # True на проде с HTTPS

    class Config:
        env_file = ".env"
Ничего больше не трогаем — если session_secret пуст, в main.py подставим jwt_secret.
________________________________________
Шаг 3. Создать структуру шаблонов
text
server/
??? templates/
?   ??? base.html
?   ??? login.html
?   ??? dashboard.html
?   ??? employees.html
?   ??? computers.html
?   ??? tokens.html
?   ??? reports.html
?   ??? report_result.html
?   ??? audit.html
??? web_admin.py
________________________________________
Шаг 4. server/web_admin.py
Полностью готовый файл:
python
"""
Веб-интерфейс администратора для проекта «Трекер».
Аутентификация: сессия (cookie), логин admin + ADMIN_API_KEY.
"""
import csv
import io
import json
import secrets
from datetime import datetime, date, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from .config import FERNET, settings
from .database import SessionLocal
from .models import (
    AuditLog, BootstrapToken, ClientVersion, Computer, Employee, Record, WorkSession,
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="server/templates")


# ---------- Утилиты ----------

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
    import hashlib
    return hashlib.sha256(t.encode()).hexdigest()


def _fmt_dt(dt):
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")


def _fmt_dur(seconds: int) -> str:
    if not seconds:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# Регистрируем фильтры Jinja
templates.env.filters["dt"] = _fmt_dt
templates.env.filters["dur"] = _fmt_dur


# ---------- Логин / логаут ----------

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


# ---------- Дашборд ----------

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    today = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
    week_ago = today - timedelta(days=7)

    stats = {
        "employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
        "sessions_today": db.query(WorkSession).filter(WorkSession.session_start >= today).count(),
        "sessions_week": db.query(WorkSession).filter(WorkSession.session_start >= week_ago).count(),
        "records": db.query(Record).count(),
        "tokens_active": db.query(BootstrapToken).filter(
            BootstrapToken.used_at.is_(None),
            BootstrapToken.expires_at > _now(),
        ).count(),
    }

    # последние 10 зарегистрированных ПК
    recent_computers = (
        db.query(Computer).order_by(desc(Computer.registered_at)).limit(10).all()
    )
    # последние 10 действий
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_computers": recent_computers,
        "recent_audit": recent_audit,
        "admin": request.session.get("admin"),
    })


# ---------- Сотрудники ----------

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


# ---------- Компьютеры ----------

@router.get("/computers", response_class=HTMLResponse)
def computers_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).all()
    employees = db.query(Employee).filter(Employee.is_active == True).order_by(Employee.last_name).all()
    return templates.TemplateResponse("computers.html", {
        "request": request, "computers": computers, "employees": employees,
        "admin": request.session.get("admin"),
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


# ---------- Bootstrap-токены ----------

@router.get("/tokens", response_class=HTMLResponse)
def tokens_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tokens = db.query(BootstrapToken).order_by(desc(BootstrapToken.id)).limit(50).all()
    return templates.TemplateResponse("tokens.html", {
        "request": request, "tokens": tokens,
        "admin": request.session.get("admin"),
        "new_token": request.query_params.get("new_token"),
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
    # показываем токен один раз через query param
    return RedirectResponse(f"/admin/tokens?new_token={raw}", status_code=303)


