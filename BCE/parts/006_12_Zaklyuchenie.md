# 12. Заключение

*Часть 6 из 100. Источник: `BCE.md`.*

[◀ 4. Серверный модуль](005_4_Servernyy_modul.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Компьютеры ---------- ▶](007_Kompyutery.md)

---

## 12. Заключение

Данное техническое задание представляет собой расширенную и детализированную версию исходного ТЗ. Оно учитывает:

- Проблемы кроссплатформенности и пути их решения.
- Юридические требования (152-ФЗ).
- Технические риски (антивирусы, GIL, конкурентный доступ к SQLite).
- Детальную архитектуру и схему данных.
- Полный стек технологий с обоснованием выбора.
- План разработки с оценкой сроков.
- Требования к тестированию и развёртыванию.



17.09.2026
Во вложении проект Трекер. Много ещё не реализовано. Нет привязки к компьютеру нет нормальных отчётов интерфейса наверное нужно создать веб интерфейс для админа для регистрации новых сотрудников вывода отчётов. нужно создать авто установочные файлы, сделать автозапуск. проведи глубокий анализ проделанной работы. и помоги создать всё недостающие 
We need answer in Russian. User attached huge doc. They ask: "Во вложении проект Трекер. Много ещё не реализовано. Нет привязки к компьютеру нет нормальных отчётов интерфейса наверное нужно создать веб интерфейс для админа для регистрации новых сотрудников вывода отчётов. нужно создать авто установочные файлы, сделать автозапуск. проведи глубокий анализ проделанной работы. и помоги создать всё недостающие"
We need provide deep analysis and help create missing. We can't actually create files? We can outline, provide code snippets, plan, maybe complete implementation. Need be useful. Since huge context, maybe they want assistance. We need analyze current project state, gaps, propose architecture, implement missing pieces: web admin UI, reports, employee/computer binding, autoinstallers, autostart. We can provide code for FastAPI web UI with Jinja2, admin auth, CRUD employees, computers, binding, reports export CSV/Excel/PDF? Need maybe not full code but enough. We have token budget. Need craft answer.
We need understand current code. Existing server has FastAPI API, models Computer, Employee, WorkSession, Record, BootstrapToken, ClientVersion, AuditLog. Client registers computer by bootstrap token, no employee info. Records include kind/data. No employee binding. No web UI. No reports. No installer/autostart.
We should propose modifications:
Add Employee management and binding: extend Computer with employee_id? Already Employee model but Computer doesn't have employee_id. WorkSession has employee_id. Need add employee_id to Computer? Or Computer assignment via new table? Simpler: add employee_id FK to Computer, plus assigned_at. Then sessions inherit employee_id from computer at creation if not set. Registration payload should include employee info? But client currently doesn't collect employee. Could add optional employee_id/employee fields to RegisterRequest. For admin UI, admin can register employee and bind computer after registration. Better: admin UI lists computers, assign employee. Then when client creates session, server sets employee_id from computer.employee_id. Also records don't need employee.
Web admin UI:
Session-based auth with admin user. Could use simple ADMIN_API_KEY or add AdminUser model. Since existing only ADMIN_API_KEY, simplest: login page asks admin key, sets signed cookie. Or add admin users table with password hash. Better implement minimal: AdminUser model with username/password_hash/role. Use passlib, python-jose? But existing requirements lack passlib, jinja2. We can add. Or use itsdangerous for session. Simpler: use FastAPI SessionMiddleware with secret_key=JWT_SECRET, and login checks ADMIN_API_KEY. But for real roles need users. We can propose two-step: MVP use ADMIN_API_KEY login, later roles.
Pages: dashboard, employees CRUD, computers list/assign, sessions/records, reports.
Templates: base, login, employees, computers, reports, report_result.
Reports:
Endpoints: GET /admin/reports with filters employee, computer, date range, type. Generate summary from WorkSession, Record. Need parse Record data. Current records: kind activity, window, idle, idle_end. Activity data has keys/clicks/scroll. Window data has app, title. We can compute:
Session duration.
Active keyboard/mouse: sum activity counts? But no seconds. Client sends counts every 5 sec? Actually CollectorWorker flushes every 5 sec? It emits activity with counts of keys/clicks/scroll in interval. So each activity record represents 5 sec interval with some counts. We can count intervals with any activity? Or estimate active seconds = count of activity records where keys+clicks+scroll > 0 * ACTIVE_WINDOW_INTERVAL (5 sec). Better to store duration in data? Current doesn't. We can modify client to include interval_seconds. For now, report by number of activity events.
Program usage: window records are edge-triggered when window changes. Need compute duration between window records per session. Could do in SQL? Easier in Python: fetch window records ordered by client_ts, compute durations until next window/idle/session_end. This gives time per app/title.
Idle: idle records mark start, idle_end marks end. Compute idle duration.
Export CSV, Excel via openpyxl, PDF via reportlab. Add requirements.
Autoinstallers:
Client: PyInstaller onedir, Inno Setup script for Windows. Provide build.bat, installer.iss. Autostart via registry or Startup folder. Already client has autostart toggle not implemented. Implement autostart in client config/main? Could add functions in client/autostart.py. On first run, if config autostart_enabled true, create shortcut/bat in Startup. Also installer can add to startup optionally.
Server: docker compose already. Could add docker-compose.prod.yml, .env.example, scripts for backup.
Auto-update: existing updater. Need publish versions via admin UI.
We need "помоги создать всё недостающие". We can provide concrete code snippets and structure. Given answer length, we can give a complete roadmap and key code. Maybe ask what to start? But likely need answer. We can provide code for:
Server modifications: models employee_id on Computer, admin web router, templates, report service, export.
Client autostart module and integration.
Inno Setup script.
Build scripts.
Admin UI code.
Need be careful not to produce too massive unreadable. Desired oververbosity 5. But user wants deep analysis and help create. We can structure:
Глубокий анализ текущего состояния: что готово, что критично.
Целевая архитектура доработки.
Пошаговый план внедрения.
Код:
server/web_admin.py with FastAPI APIRouter, Jinja2Templates, login, dashboard, employees, computers, bind, reports.
templates/base.html, login.html, employees.html, computers.html, reports.html, report_result.html.
server/reports.py for report generation.
server/models.py changes: Computer.employee_id, AdminUser? Use existing.
client/autostart.py.
installer.iss.
Как внедрять.
Need mention that we can't physically create files, but provide ready-to-copy code. Since API, final should be answer.
Let's design code.
Server models changes:
Add to Computer: employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True); assigned_at = Column(DateTime(timezone=True))
Employee already exists. Add full_name? It has full_name, external_id, is_active. For UI, we need last_name/first_name/middle_name. Could add fields or use full_name. Simpler: add last_name, first_name, middle_name to Employee model. But existing Employee has full_name. We can add columns. Or use full_name and parse? Better add.
WorkSession already employee_id. When creating session, set employee_id from comp.employee_id.
Record: no change.
Admin web:
Use FastAPI APIRouter. Need templates dir: server/templates. Static? Use Bootstrap CDN.
Auth: simple dependency:
text
def get_current_admin(request: Request):
    if request.session.get("admin"):
        return request.session["admin"]
    raise HTTPException(401)
Need SessionMiddleware in main.py: from starlette.middleware.sessions import SessionMiddleware; app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret).
Login:
text
@router.get("/login")
@router.post("/login")
async def login(request, username, password):
    if username=="admin" and secrets.compare_digest(password, settings.admin_api_key):
        request.session["admin"]="admin"
        return RedirectResponse("/admin", 303)
Logout.
Pages:
dashboard: counts.
employees: list, create, edit, deactivate.
computers: list with employee assign dropdown, revoke.
reports: form; POST generate -> render report or download.
Report service:
Functions:
text
def generate_report(db, employee_id, computer_uid, date_from, date_to, report_type):
    sessions = query WorkSession join Computer ...
    for each session:
        duration = (session_end or now) - session_start
        records = query Record where session_uid and kind in ...
        # activity: sum counts, active_intervals = count records with keys+clicks+scroll>0
        # window: compute durations per app
Need parse JSON data. Use json.loads.
Export:
CSV using csv module.
Excel using openpyxl.
PDF using reportlab. For Cyrillic need DejaVuSans. We can provide code with font registration path.
But maybe too much. We can provide core.
Client autostart:
text
def set_autostart(enabled):
    if win: import winreg; key=HKCU\Software\Microsoft\Windows\CurrentVersion\Run; set/delete "Tracker"
    elif linux: ~/.config/autostart/tracker.desktop
Integrate in main window: checkbox. But existing UI no checkbox. We can add minimal.
Installer Inno Setup:
text
[Setup]
AppName=Tracker
AppVersion=1.2.0
DefaultDirName={localappdata}\Tracker
DefaultGroupName=Tracker
OutputBaseFilename=TrackerSetup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
[Files]
Source: "dist\Tracker\*"; DestDir: "{app}"; Flags: recursesubdirs
[Icons]
Name: "{userstartup}\Tracker"; Filename: "{app}\Tracker.exe"; Parameters: "--minimized"
Name: "{group}\Tracker"; Filename: "{app}\Tracker.exe"
[Run]
Filename: "{app}\Tracker.exe"; Description: "Запустить Tracker"; Flags: nowait postinstall skipifsilent
[Code]
...
Need bootstrap token. Installer can ask for token and write to %APPDATA%\Tracker\bootstrap.txt. Use Pascal script.
Build scripts:
client/build.bat:
text
pyinstaller build.spec --clean
Inno Setup compile.
Auto-update publish: admin UI can add ClientVersion.
We should also analyze gaps:
No employee binding: fix.
No reports: fix.
No web UI: fix.
No installers/autostart: fix.
No heartbeat: optional.
No Alembic: recommend.
We need mention security: web admin over HTTPS, session cookie secure.
Let's craft answer with sections:
Глубокий анализ: что уже есть, что критично, риски.
Архитектура доработки.
Что делать по шагам.
Код (сервер: модели, веб-админка, отчёты; клиент: автозапуск; установщик).
Как внедрить и проверить.
Что дальше.
Given final answer length, we can include code snippets. Need ensure not too massive. But user wants help create. We'll provide enough.
Let's write in Russian.
Start with "Можно сделать так". Then analysis.
Detailed analysis:
Сильные стороны: сервер/клиент, HMAC, офлайн, Docker, bootstrap.
Пробелы:
Employee не связан с Computer; WorkSession.employee_id не заполняется.
Нет веб-интерфейса.
Нет отчётов.
Нет установщиков.
Нет автозапуска.
Нет миграций.
Нет ролей.
Нет heartbeat.
Нет тестов.
Приоритеты: P0 employee binding, web UI, reports, installers, autostart. P1 Alembic, roles, heartbeat, backup. P2 Wayland, macOS, 1C.
Then architecture:
Добавить employee_id в computers.
При создании сессии брать employee_id из computer.
Веб-админка на FastAPI + Jinja2 + Bootstrap, сессия через SessionMiddleware.
Отчёты: сервис, экспорт CSV/Excel/PDF.
Установщик Inno Setup, автозапуск через реестр/Startup.
Code:
models.py patch:
python
# Employee add columns
last_name = Column(String(50))
first_name = Column(String(50))
middle_name = Column(String(50))
# Computer add
employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
assigned_at = Column(DateTime(timezone=True))
Also update WorkSession creation in main.py:
python
employee_id=comp.employee_id,
in upsert_session.
Web admin: create server/web_admin.py.
Need include requirements: jinja2, python-multipart, itsdangerous? SessionMiddleware uses itsdangerous. Add itsdangerous, jinja2, openpyxl, reportlab.
web_admin.py code:
python
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
import secrets, csv, io, json
from .database import get_db? Actually get_db in main. Better define here or import.
But main.py has get_db. We can import from .main import get_db? circular. Better move get_db to database.py. In existing code get_db in main. We can suggest moving. For snippet, define def get_db(): ... in web_admin or import from database. We'll assume from .database import SessionLocal and define.
Templates: create server/templates/base.html etc. Provide base template.
Report service: server/reports.py.
Client autostart: client/autostart.py.
Inno Setup: installer.iss.
We can also mention how to add checkbox to client main window. But code for UI might be too much. Provide function and integration line.
Let's write final. Need be concise but comprehensive.
We should note: "Я не могу создать файлы в вашей файловой системе, но ниже готовый код". That's fine.
Let's produce final answer.
Ниже — глубокий разбор текущего состояния и готовый план доработки с кодом, который можно сразу вставлять в проект. Я не могу физически создать файлы у вас на диске, но даю законченные фрагменты и структуру.
________________________________________
1. Глубокий анализ: что уже есть и что критично не хватает
Что уже сделано хорошо
Серверная часть на FastAPI + PostgreSQL + Docker.
Клиент на PyQt6 с треем, сбором активности, локальной SQLite, офлайн-режимом.
HMAC-подпись записей и батчей, bootstrap-токены, revoke.
Certificate pinning, fallback-хранилище секретов.
Разделение на сервер/клиент, есть аудит, версии клиента.
Документация очень подробная, есть список проблем и решений.
Критические пробелы
Нет привязки сотрудника к компьютеру
Employee есть в моделях, но Computer.employee_id отсутствует. WorkSession.employee_id не заполняется. В итоге отчёты невозможно строить по людям.
Нет веб-интерфейса администратора
Всё только через SQL. Нельзя завести сотрудника, привязать ПК, посмотреть отчёт, выпустить bootstrap-токен без curl.
Нет нормальных отчётов
Нет агрегации по программам, клавиатуре, мыши, простоям, нет экспорта в Excel/PDF/CSV.
Нет установщиков и автозапуска
Клиент запускается вручную. Нет .exe-инсталлятора, нет автозапуска, нет нормального first-run опыта.
Нет миграций Alembic
create_all + ручная миграция. Любое изменение схемы на проде — боль.
Нет ролей и нормальной админ-аутентификации
Только ADMIN_API_KEY. Для веб-интерфейса нужны сессии, пользователи, роли.
Нет heartbeat и нормального мониторинга
last_seen_at обновляется только при ingest. Если клиент молчит, непонятно, он офлайн или сломался.
Нет тестов
Ни модульных, ни интеграционных. Это риск при доработках.
Приоритеты
P0: привязка сотрудник–ПК, веб-админка, отчёты, установщик, автозапуск.
P1: Alembic, роли, heartbeat, бэкапы, публикация версий через UI.
P2: Wayland, macOS/Linux сборки, 1С, Prometheus.
________________________________________
2. Целевая архитектура доработки
text
???????????????????????????????????????????????????????????????
? SERVER                                                      ?
?  FastAPI                                                    ?
?   ??? /api/v1/*          — существующий API                 ?
?   ??? /admin/*           — веб-интерфейс (Jinja2 + Bootstrap)?
?   ??? /admin/reports/*   — генерация и экспорт отчётов      ?
?  PostgreSQL                                                 ?
?   ??? employees                                             ?
?   ??? computers (employee_id FK)                            ?
?   ??? work_sessions (employee_id)                           ?
?   ??? records                                               ?
???????????????????????????????????????????????????????????????
Клиент:
Добавляем autostart.py.
В MainWindow — чекбокс «Автозапуск».
Inno Setup installer: кладёт файлы, спрашивает bootstrap-токен, пишет в %APPDATA%\Tracker\bootstrap.txt, создаёт ярлык в Startup.
________________________________________
3. Сервер: привязка сотрудника к ПК
3.1. Правки server/models.py
Добавьте в Employee поля ФИО и в Computer — employee_id.
python
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    last_name = Column(String(50))
    first_name = Column(String(50))
    middle_name = Column(String(50))
    external_id = Column(String(64), unique=True)
    is_active = Column(Boolean, default=True)

class Computer(Base):
    __tablename__ = "computers"
    # ... существующие поля ...
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True))
3.2. Правка server/main.py в upsert_session
Чтобы сессия наследовала сотрудника от компьютера:
python
ws = WorkSession(
    session_uid=payload.session_uid,
    computer_id=comp.id,
    employee_id=comp.employee_id,   # <— добавить
    session_start=start,
    session_end=end,
    abnormal_termination=payload.abnormal_termination,
    client_version=payload.client_version,
)
Если сессия уже есть, можно не перезаписывать employee_id, чтобы не ломать историю.
________________________________________
4. Веб-интерфейс администратора
4.1. Зависимости
Добавьте в server/requirements.txt:
txt
jinja2==3.1.4
python-multipart==0.0.9
itsdangerous==2.2.0
openpyxl==3.1.5
reportlab==4.2.2
4.2. Подключение сессий в server/main.py
python
from starlette.middleware.sessions import SessionMiddleware
from .web_admin import router as admin_router

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret,
    session_cookie="tracker_admin",
    max_age=8 * 3600,
    same_site="strict",
    https_only=False,  # True на проде с HTTPS
)

app.include_router(admin_router)
4.3. server/web_admin.py
python
import csv
import io
import json
import secrets
from datetime import datetime, date, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import Computer, Employee, WorkSession, Record, AuditLog

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="server/templates")


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


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == "admin" and secrets.compare_digest(password, settings.admin_api_key):
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


@router.get("", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    stats = {
        "employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
        "sessions_today": db.query(WorkSession).filter(
            WorkSession.session_start >= date.today()
        ).count(),
        "records": db.query(Record).count(),
    }
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})


# ---------- Сотрудники ----------

@router.get("/employees", response_class=HTMLResponse)
def employees_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).order_by(Employee.last_name).all()
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees})


@router.post("/employees/create")
def employee_create(
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(""),
    external_id: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    full_name = " ".join(x for x in [last_name, first_name, middle_name] if x)
    emp = Employee(
        full_name=full_name,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name or None,
        external_id=external_id or None,
    )
    db.add(emp)
    db.add(AuditLog(actor="admin", entity="employee", action="create",
                    new_value=json.dumps({"full_name": full_name}, ensure_ascii=False)))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/deactivate")
def employee_deactivate(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.is_active = False
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id),
                        action="deactivate"))
        db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


