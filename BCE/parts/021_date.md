# date

*Часть 21 из 100. Источник: `BCE.md`.*

[◀ ============================================================](020_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](022_part.md)

---

# date
cell = ws.cell(row=r, column=c, value=date_obj)
cell.number_format = 'DD.MM.YYYY'
But our _report_to_table returns lists. Need to change to work with cell objects. Or return typed values (timedelta, date).
Let me refactor _report_to_table to return:
headers: list of strings
rows_data: list of lists with mixed types
For CSV we'll convert to string.
For XLSX we'll write and set formats.
Actually I'll create a separate _report_to_xlsx function that does everything directly.
Client main.py changes:
Fix time display: db.get_session_start(uid) returns UTC ISO string. Need to convert to local time for display.
python
from datetime import datetime, timezone

def _local_time_str(iso_str):
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%H:%M:%S")
    except:
        return "—"
Panel additions:
Current session duration (updates every second via QTimer)
Last sync time
Records pending to sync
Connection status indicator
Current window/app
Let me be realistic about scope. This response will be huge. Let me split it.
Actually, I'll do it in this response but keep it tight. Let me write efficient PowerShell scripts.
Let me plan the response:
Часть 1 — Анализ и предложения (short)
Часть 2 — Скрипт 1: server/models.py (departments, employee.department_id, employee.fired_at)
Часть 3 — Скрипт 2: server/web_admin.py (full rewrite with all features)
Часть 4 — Скрипт 3: templates (base, settings, employees, departments, reports, report_result)
Часть 5 — Скрипт 4: client/main.py (time fix + panel)
Часть 6 — Скрипт 5: DB migration + rebuild
Часть 7 — Мои предложения
Let me write.
Actually, for reports, "выбрать нескольких сотрудников" - I need to change from single employee_id to employee_ids list. Use <select multiple> which sends multiple values with same name.
FastAPI: employee_ids: List[str] = Form([]) - hmm, need to check syntax. Actually:
python
from typing import List
employee_ids: List[str] = Form(default=[])
Or better with newer FastAPI:
python
employee_ids: list[str] = Form(default=[])
Should work. But might have issues. Let me use that.
Actually simplest: make it a comma-separated string. More reliable.
Let me use checkbox list with name="employee_ids" — then it sends employee_ids=1&employee_ids=2&employee_ids=3. FastAPI with List[str] should pick that up.
Hmm, there can be issues with Form and List in older FastAPI. Let me use comma-separated to be safe:
HTML: use JS to collect checked checkboxes into a hidden field as CSV
Or: send employee_ids as a single form field with comma-separated values
I'll use <select multiple> with name employee_ids and rely on FastAPI's List[str] parsing. That works in FastAPI 0.100+.
Actually looking at FastAPI docs, this should be:
python
from typing import List
employee_ids: List[str] = Form([])
Yeah that works.
But when nothing selected, empty list. Good.
Actually there is a known issue: if using List[str] = Form(...) and nothing selected, it errors. Use default [].
OK let me proceed.
Given the response length, I'll split into two messages but keep it in this one response. Let me be efficient.
Let me reduce scope slightly: I'll do everything except maybe PDF, and keep code tight.
Actually - to reduce complexity, let me combine server side changes into fewer scripts.
Let me write.
I'll compress the web_admin.py by keeping it mostly the same as before, but:
Add AppSetting helpers for timezone, workday_start, activity_gap
Add Department model handling
Multi-select for employees
Department filter
Fired employees tab
Excel formatting fix
Let me write it out.
One more consideration - the _build_report and _build_flat_records signatures need to change. Let me use a config object.
OK let me just write. Response will be long.
Actually, given length constraints, I'll:
Give short intro with suggestions
Give server models.py
Give server web_admin.py (long)
Give templates
Give client main.py
Give migration + rebuild script
Give suggestions at the end
Let me start writing.
For the client time display: db.get_session_start returns ISO with tzinfo=utc. Need to convert to local for display.
For the client panel: I'll add:
Current session duration (live updating)
Sync status (last sync time + pending records count)
Connection indicator (online/offline)
Current app/program
These are genuinely useful. Let me add them.
For panel, I'll use QLabels with a QTimer updating every second. Simple.
OK let me write.
Also - "Часовой пояс Начало рабочего дня. Какие еще есть переменные" - let me list all:
report_timezone - DEFAULT_TIMEZONE
workday_start_hour
activity_gap_minutes
idle_close_minutes
Кстати SYNC_INTERVAL, BATCH_SIZE, ACTIVE_WINDOW_INTERVAL, IDLE_THRESHOLD on client — these are client-side, harder to make server-configurable
MAX_DB_SIZE_MB client-side
I'll move report_timezone, workday_start_hour, activity_gap_minutes to settings. Client-side settings are harder (would need to also fetch).
Actually, I can add to /api/v1/client-config:
sync_interval
batch_size
active_window_interval
idle_threshold
Let me include those too.
OK writing now. Being efficient.
Let me be careful about how I write List[str] = Form([]) — in FastAPI with python-multipart this works.
Structure of response:
________________________________________
Что делаем
Список задач + мои предложения
Скрипт 1 — сервер: models.py
Скрипт 2 — сервер: web_admin.py + main.py patch
Скрипт 3 — сервер: шаблоны
Скрипт 4 — клиент: main.py
Скрипт 5 — миграция БД + пересборка
Мои предложения (в конце)
Go.
Actually let me reduce the size. The report_result.html is huge already and I'm running out of space. Let me keep report_result.html changes minimal — just handle the case where employee_id might now be multiple, and pass through.
Actually report_result.html doesn't need major changes since it just renders report.rows. The main changes are in web_admin.py.
Let me write the response now.
Разбор задач + реализация + предложения
Что делаем по пунктам
Время в клиенте — сейчас показывается UTC, нужно локальное.
Панель клиента — добавлю: текущая сессия, счётчик времени, статус синка, последняя синхронизация, активное окно.
Настройки в админке — переношу туда: часовой пояс, начало рабочего дня, порог паузы (activity_gap), idle-порог. Их уже 4 — все в одной форме.
Excel — длительности как [ЧЧ]:ММ:СС (Excel понимает как время), дата как ДД.ММ.ГГГГ.
Несколько сотрудников в отчёте — мультивыбор через <select multiple>.
Уволенные — отдельная вкладка + фильтр в отчёте.
Отделы — новая сущность + фильтр в отчётах.
Мои предложения (что стоит добавить позже)
Праздничные/нерабочие дни — чтобы не считать переработку в выходные.
Плановая норма часов на месяц — сравнение «факт/план».
Отчёт «Опоздания» — сравнение фактического старта с настройкой «начало рабочего дня».
Telegram-уведомления офлайн-ПК.
График активности по часам для сотрудника — Chart.js.
Экспорт по расписанию — «каждый понедельник в 9:00 отчёт по продажам на почту».
Колонка «Онлайн/Оффлайн» — heartbeat-эндпоинт, чтобы видеть живых.
Массовая привязка ПК — загрузить Excel/CSV «hostname ? сотрудник».
Логирование входов в админку — кто когда заходил.
________________________________________
Скрипт 1 — сервер: models.py
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

$models_py = @'
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime,
    ForeignKey, Text, Index,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _utcnow():
    return datetime.now(timezone.utc)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class Computer(Base):
    __tablename__ = "computers"

    id = Column(Integer, primary_key=True)
    computer_uid = Column(String(64), unique=True, nullable=False, index=True)
    hostname = Column(String(255))
    os_info = Column(String(255))
    client_version = Column(String(32))
    client_secret_enc = Column(Text, nullable=False)
    secret_version = Column(Integer, nullable=False, default=1)
    registered_at = Column(DateTime(timezone=True), default=_utcnow)
    last_seen_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True))


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    last_name = Column(String(50))
    first_name = Column(String(50))
    middle_name = Column(String(50))
    external_id = Column(String(64), unique=True)
    is_active = Column(Boolean, default=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fired_at = Column(DateTime(timezone=True), nullable=True)


class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(BigInteger, primary_key=True)
    session_uid = Column(String(64), unique=True, nullable=False, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    session_start = Column(DateTime(timezone=True), nullable=False)
    session_end = Column(DateTime(timezone=True))
    abnormal_termination = Column(Boolean, default=False, nullable=False)
    client_version = Column(String(32))
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class Record(Base):
    __tablename__ = "records"

    id = Column(BigInteger, primary_key=True)
    record_uid = Column(String(64), unique=True, nullable=False, index=True)
    session_uid = Column(String(64), index=True, nullable=False)
    computer_id = Column(Integer, ForeignKey("computers.id"), nullable=False)
    kind = Column(String(32), nullable=False)
    data = Column(Text)
    client_ts = Column(DateTime(timezone=True), nullable=False)
    client_ip = Column(String(64))
    signature = Column(String(128), nullable=False)
    received_at = Column(DateTime(timezone=True), default=_utcnow)

    __table_args__ = (Index("ix_records_computer_ts", "computer_id", "client_ts"),)


class BootstrapToken(Base):
    __tablename__ = "bootstrap_tokens"

    id = Column(Integer, primary_key=True)
    token_hash = Column(String(128), unique=True, nullable=False, index=True)
    issued_by = Column(String(128))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    used_by_uid = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class ClientVersion(Base):
    __tablename__ = "client_versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(32), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    download_url = Column(String(512), nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    release_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True)
    actor = Column(String(128))
    entity = Column(String(64), nullable=False)
    entity_id = Column(String(64))
    action = Column(String(32), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
'@
[System.IO.File]::WriteAllText("$serverDir\models.py", $models_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  models.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$serverDir\models.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — сервер: web_admin.py (полный)
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

$web_admin_py = @'
"""
Веб-интерфейс администратора для проекта «Трекер».
"""
import csv
import hashlib
import io
import json
import secrets
from collections import defaultdict
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional, List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import (
    AppSetting, AuditLog, BootstrapToken, Computer, Department,
    Employee, Record, WorkSession,
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="server/templates")


# ============================================================
# Утилиты
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


def get_app_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else default


def set_app_setting(db: Session, key: str, value: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row:
        row.value = value
    else:
        db.add(AppSetting(key=key, value=value))


def get_app_setting_int(db: Session, key: str, default: int, minv: int, maxv: int) -> int:
    try:
        return max(minv, min(maxv, int(get_app_setting(db, key, str(default)))))
    except (ValueError, TypeError):
        return default


def get_settings_dict(db: Session) -> dict:
    return {
        "idle_close_minutes": get_app_setting_int(db, "idle_close_minutes", settings.idle_close_minutes, 5, 480),
        "workday_start_hour": get_app_setting_int(db, "workday_start_hour", settings.workday_start_hour, 0, 23),
        "activity_gap_minutes": get_app_setting_int(db, "activity_gap_minutes", settings.activity_gap_minutes, 1, 120),
        "report_timezone": get_app_setting(db, "report_timezone", settings.report_timezone),
        "sync_interval": get_app_setting_int(db, "sync_interval", 30, 5, 3600),
        "batch_size": get_app_setting_int(db, "batch_size", 200, 10, 1000),
        "active_window_interval": get_app_setting_int(db, "active_window_interval", 5, 1, 60),
        "idle_threshold": get_app_setting_int(db, "idle_threshold", 60, 10, 3600),
    }


def _resolve_tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        try:
            return ZoneInfo(settings.report_timezone)
        except Exception:
            return ZoneInfo("UTC")


def _to_local(dt, tz: ZoneInfo):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)


def _fmt_dur(seconds: int) -> str:
    if not seconds:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_dt_global(dt):
    if dt is None:
        return "—"
    try:
        tz = ZoneInfo(settings.report_timezone)
    except Exception:
        tz = ZoneInfo("UTC")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")


templates.env.filters["dur"] = _fmt_dur
templates.env.filters["dt"] = _fmt_dt_global


def _available_timezones():
    return [
        ("Europe/Moscow", "Москва (UTC+3)"),
        ("Europe/Kaliningrad", "Калининград (UTC+2)"),
        ("Europe/Samara", "Самара (UTC+4)"),
        ("Asia/Yekaterinburg", "Екатеринбург (UTC+5)"),
        ("Asia/Omsk", "Омск (UTC+6)"),
        ("Asia/Novosibirsk", "Новосибирск (UTC+7)"),
        ("Asia/Krasnoyarsk", "Красноярск (UTC+7)"),
        ("Asia/Irkutsk", "Иркутск (UTC+8)"),
        ("Asia/Yakutsk", "Якутск (UTC+9)"),
        ("Asia/Vladivostok", "Владивосток (UTC+10)"),
        ("UTC", "UTC"),
    ]


def _workday_date(start_local: datetime, workday_start_hour: int) -> date:
    if start_local.hour < workday_start_hour:
        return (start_local - timedelta(days=1)).date()
    return start_local.date()


# ============================================================
# Логин / логаут
# ============================================================

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("admin"):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    ok_user = secrets.compare_digest(username, settings.admin_login)
    ok_pass = secrets.compare_digest(password, settings.admin_api_key)
    if ok_user and ok_pass:
        request.session["admin"] = username
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Неверный логин или ключ"},
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
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    today_local = datetime.now(tz).date()
    today_start_utc = datetime.combine(today_local, time.min, tzinfo=tz).astimezone(timezone.utc)
    week_ago_utc = today_start_utc - timedelta(days=7)

    stats = {
        "employees": db.query(Employee).filter(Employee.fired_at.is_(None)).count(),
        "departments": db.query(Department).filter(Department.is_active == True).count(),
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
    recent_computers = db.query(Computer).order_by(desc(Computer.registered_at)).limit(10).all()
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "stats": stats,
        "recent_computers": recent_computers, "recent_audit": recent_audit,
        "admin": request.session.get("admin"), "tz": tz,
    })


# ============================================================
# Настройки
# ============================================================

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    return templates.TemplateResponse("settings.html", {
        "request": request, "admin": request.session.get("admin"),
        "cfg": cfg,
        "timezones": _available_timezones(),
        "saved": request.query_params.get("saved") == "1",
    })


@router.post("/settings/save")
def settings_save(
    idle_close_minutes: int = Form(30),
    workday_start_hour: int = Form(6),
    activity_gap_minutes: int = Form(5),
    report_timezone: str = Form("Europe/Moscow"),
    sync_interval: int = Form(30),
    batch_size: int = Form(200),
    active_window_interval: int = Form(5),
    idle_threshold: int = Form(60),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    new_vals = {
        "idle_close_minutes": max(5, min(480, int(idle_close_minutes))),
        "workday_start_hour": max(0, min(23, int(workday_start_hour))),
        "activity_gap_minutes": max(1, min(120, int(activity_gap_minutes))),
        "report_timezone": report_timezone,
        "sync_interval": max(5, min(3600, int(sync_interval))),
        "batch_size": max(10, min(1000, int(batch_size))),
        "active_window_interval": max(1, min(60, int(active_window_interval))),
        "idle_threshold": max(10, min(3600, int(idle_threshold))),
    }
    for k, v in new_vals.items():
        old = get_app_setting(db, k, "")
        if str(old) != str(v):
            set_app_setting(db, k, str(v))
            db.add(AuditLog(actor="admin", entity="app_setting", entity_id=k,
                            action="update", old_value=str(old), new_value=str(v)))
    db.commit()
    return RedirectResponse("/admin/settings?saved=1", status_code=303)


# ============================================================
# Отделы
# ============================================================

@router.get("/departments", response_class=HTMLResponse)
def departments_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    deps = db.query(Department).order_by(Department.name).all()
    counts = dict(
        db.query(Employee.department_id, __import__("sqlalchemy").func.count(Employee.id))
        .filter(Employee.fired_at.is_(None))
        .group_by(Employee.department_id).all()
    )
    return templates.TemplateResponse("departments.html", {
        "request": request, "admin": request.session.get("admin"),
        "departments": deps, "counts": counts,
    })


@router.post("/departments/create")
def department_create(name: str = Form(...), db: Session = Depends(get_db), _=Depends(current_admin)):
    name = name.strip()
    if not name:
        raise HTTPException(400, "Название обязательно")
    if db.query(Department).filter(Department.name == name).first():
        raise HTTPException(400, "Отдел с таким именем уже есть")
    d = Department(name=name)
    db.add(d)
    db.add(AuditLog(actor="admin", entity="department", action="create", new_value=name))
    db.commit()
    return RedirectResponse("/admin/departments", status_code=303)


@router.post("/departments/{dep_id}/rename")
def department_rename(dep_id: int, name: str = Form(...),
                      db: Session = Depends(get_db), _=Depends(current_admin)):
    d = db.query(Department).get(dep_id)
    if not d:
        raise HTTPException(404)
    old = d.name
    d.name = name.strip()
    db.add(AuditLog(actor="admin", entity="department", entity_id=str(dep_id),
                    action="rename", old_value=old, new_value=d.name))
    db.commit()
    return RedirectResponse("/admin/departments", status_code=303)


@router.post("/departments/{dep_id}/delete")
def department_delete(dep_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    d = db.query(Department).get(dep_id)
    if d:
        db.query(Employee).filter(Employee.department_id == dep_id).update({"department_id": None})
        db.delete(d)
        db.add(AuditLog(actor="admin", entity="department", entity_id=str(dep_id), action="delete"))
        db.commit()
    return RedirectResponse("/admin/departments", status_code=303)


# ============================================================
# Сотрудники
# ============================================================

@router.get("/employees", response_class=HTMLResponse)
def employees_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tab = request.query_params.get("tab", "active")
    q = db.query(Employee)
    if tab == "active":
        q = q.filter(Employee.fired_at.is_(None))
    elif tab == "fired":
        q = q.filter(Employee.fired_at.is_not(None))
    employees = q.order_by(Employee.last_name, Employee.first_name).all()
    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    return templates.TemplateResponse("employees.html", {
        "request": request, "employees": employees, "departments": departments,
        "admin": request.session.get("admin"), "tab": tab,
    })


@router.post("/employees/create")
def employee_create(
    last_name: str = Form(...), first_name: str = Form(...),
    middle_name: str = Form(""), external_id: str = Form(""),
    department_id: str = Form(""),
    db: Session = Depends(get_db), _=Depends(current_admin),
):
    last_name, first_name = last_name.strip(), first_name.strip()
    middle_name = middle_name.strip()
    external_id = external_id.strip()
    if not last_name or not first_name:
        raise HTTPException(400, "Фамилия и имя обязательны")
    full_name = " ".join(x for x in [last_name, first_name, middle_name] if x)
    emp = Employee(
        full_name=full_name, last_name=last_name, first_name=first_name,
        middle_name=middle_name or None, external_id=external_id or None,
        department_id=int(department_id) if department_id else None,
    )
    db.add(emp)
    db.flush()
    db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp.id),
                    action="create", new_value=json.dumps({"full_name": full_name}, ensure_ascii=False)))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/edit")
def employee_edit(
    emp_id: int, last_name: str = Form(...), first_name: str = Form(...),
    middle_name: str = Form(""), external_id: str = Form(""),
    department_id: str = Form(""),
    db: Session = Depends(get_db), _=Depends(current_admin),
):
    emp = db.query(Employee).get(emp_id)
    if not emp:
        raise HTTPException(404)
    old = emp.full_name
    emp.last_name = last_name.strip()
    emp.first_name = first_name.strip()
    emp.middle_name = middle_name.strip() or None
    emp.external_id = external_id.strip() or None
    emp.department_id = int(department_id) if department_id else None
    emp.full_name = " ".join(x for x in [emp.last_name, emp.first_name, emp.middle_name] if x)
    db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id),
                    action="edit", old_value=old, new_value=emp.full_name))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/fire")
def employee_fire(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.fired_at = _now()
        emp.is_active = False
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="fire"))
        db.commit()
    return RedirectResponse("/admin/employees?tab=fired", status_code=303)


@router.post("/employees/{emp_id}/restore")
def employee_restore(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.fired_at = None
        emp.is_active = True
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="restore"))
        db.commit()
    return RedirectResponse("/admin/employees?tab=active", status_code=303)


# ============================================================
# Компьютеры
# ============================================================

@router.get("/computers", response_class=HTMLResponse)
def computers_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).all()
    employees = (db.query(Employee)
                 .filter(Employee.fired_at.is_(None))
                 .order_by(Employee.last_name).all())
    return templates.TemplateResponse("computers.html", {
        "request": request, "computers": computers, "employees": employees,
        "admin": request.session.get("admin"), "tz": tz,
    })


@router.post("/computers/{comp_id}/assign")
def computer_assign(comp_id: int, employee_id: Optional[str] = Form(None),
                    db: Session = Depends(get_db), _=Depends(current_admin)):
    comp = db.query(Computer).get(comp_id)
    if not comp:
        raise HTTPException(404)
    emp_id = int(employee_id) if employee_id else None
    old = comp.employee_id
    comp.employee_id = emp_id
    comp.assigned_at = _now()
    db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id),
                    action="assign", old_value=str(old), new_value=str(emp_id)))
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
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    tokens = db.query(BootstrapToken).order_by(desc(BootstrapToken.id)).limit(50).all()
    return templates.TemplateResponse("tokens.html", {
        "request": request, "tokens": tokens,
        "admin": request.session.get("admin"),
        "new_token": request.query_params.get("new_token"), "tz": tz,
    })


@router.post("/tokens/issue")
def tokens_issue(ttl_hours: int = Form(24), issued_by: str = Form("admin"),
                 db: Session = Depends(get_db), _=Depends(current_admin)):
    ttl_hours = max(1, min(ttl_hours, 24 * 30))
    raw = secrets.token_urlsafe(32)
    db.add(BootstrapToken(token_hash=_hash_token(raw), issued_by=issued_by,
                          expires_at=_now() + timedelta(hours=ttl_hours)))
    db.add(AuditLog(actor="admin", entity="bootstrap_token", action="issue",
                    new_value=json.dumps({"ttl_hours": ttl_hours, "issued_by": issued_by})))
    db.commit()
    return RedirectResponse(f"/admin/tokens?new_token={raw}", status_code=303)


# ============================================================
# Отчёты
