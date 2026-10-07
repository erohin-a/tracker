# in _check_idle_session:

*Часть 18 из 100. Источник: `BCE.md`.*

[◀ ============================================================](017_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](019_part.md)

---

# in _check_idle_session:
idle = db.get_idle_close_minutes(IDLE_DEFAULT)
closed_uid = db.auto_close_idle_session(idle)
OK. Now let me really write.
Actually for client main.py the import statement I added before was:
python
from .config import IDLE_CLOSE_MINUTES
I'll use a PowerShell replace to change it.
Hmm, actually easier to just add a new import without removing the old. Let me add:
python
from .config import IDLE_CLOSE_MINUTES as IDLE_CLOSE_MINUTES_DEFAULT
But then in code IDLE_CLOSE_MINUTES unused. Messy.
Let me just leave IDLE_CLOSE_MINUTES in config as default and modify main.py:
python
idle = db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)
closed_uid = db.auto_close_idle_session(idle)
Change db.auto_close_idle_session(IDLE_CLOSE_MINUTES) ? db.auto_close_idle_session(db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)).
Simple replace.
OK, writing.
Let me finalize size. This will be a big response, but let's go.
For base.html — add nav link:
html
<a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>
For settings.html — simple form:
html
{% extends "base.html" %}
{% block title %}Настройки{% endblock %}
{% block content %}
<h3 class="mb-4">Настройки системы</h3>

{% if saved %}
<div class="alert alert-success py-2">Настройки сохранены</div>
{% endif %}

<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/settings/save">
      <div class="mb-3">
        <label class="form-label">
          Закрывать «висящие» сессии через (минут без активности)
          <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени, клиент автоматически закроет сессию временем последней активности. Клиенты получают новое значение при следующей синхронизации (макс. 5 минут).">?</span>
        </label>
        <input type="number" name="idle_close_minutes" class="form-control" value="{{ idle_close_minutes }}" min="5" max="480" style="max-width:200px">
        <div class="form-text">Рекомендуемое значение: 30 мин. Минимум 5, максимум 480.</div>
      </div>
      <button class="btn btn-primary">Сохранить</button>
    </form>
  </div>
</div>
{% endblock %}
OK. Now writing the full response. Let me be efficient.
Actually — user might appreciate a note about how client picks up the setting. Let me mention: "клиент подтянет через ?5 минут".
Alright, going to write now.
Let me also make sure the report_result.html handles the new columns and top_programs expansion well.
Column structure for top programs table:
| Программа | Время | Клавиатура | Мышь | (bar) |
Each program row followed by an optional hidden expansion row.
html
<table class="table table-sm mb-0">
  <thead><tr>
    <th style="width:35%">Программа</th>
    <th>Время</th>
    <th>Клавиатура</th>
    <th>Мышь</th>
    <th style="width:30%"></th>
  </tr></thead>
  <tbody>
  {% for a in report.totals.top_apps %}
    <tr>
      <td>{{ a.app }}</td>
      <td style="white-space:nowrap">{{ a.seconds | dur }}</td>
      <td>{{ a.keyboard | dur }}</td>
      <td>{{ a.mouse | dur }}</td>
      <td>
        <span class="app-bar" style="width: {{ (a.seconds / max_app_seconds * 100) if max_app_seconds else 0 }}%"></span>
      </td>
    </tr>
    {% if a.by_employee and a.by_employee|length > 1 %}
      <tr>
        <td colspan="5" class="p-0 bg-light">
          <details>
            <summary style="padding:6px 12px;cursor:pointer;color:#555;font-size:0.9em">
              ? Развернуть по сотрудникам ({{ a.by_employee|length }})
            </summary>
            <div style="padding:8px 12px">
              <table class="table table-sm mb-0">
                <thead><tr><th>Сотрудник</th><th>1C ID</th><th>Время</th><th>Клавиатура</th><th>Мышь</th></tr></thead>
                <tbody>
                {% for e in a.by_employee %}
                  <tr>
                    <td>{{ e.employee_name }}</td>
                    <td><code>{{ e.external_id or '—' }}</code></td>
                    <td>{{ e.seconds | dur }}</td>
                    <td>{{ e.keyboard | dur }}</td>
                    <td>{{ e.mouse | dur }}</td>
                  </tr>
                {% endfor %}
                </tbody>
              </table>
            </div>
          </details>
        </td>
      </tr>
    {% endif %}
  {% endfor %}
  </tbody>
</table>
Good.
Now writing all scripts.
One more thing — the server /api/v1/client-config should ideally require X-Computer-Uid. But it's just idle minutes, low sensitivity. Let me make it public for simplicity. Actually, let me require nothing and return default if no header.
OK writing.
Let me combine server main.py patch into script 3 along with anything else server-side. Since main.py is stable, I'll do a PowerShell insert.
Alright, final structure:
Script 1: server/models.py (add AppSetting) + server/web_admin.py (full replacement)
Script 2: server/templates: base.html, settings.html (new), reports.html, report_result.html
Script 3: server/main.py patch (add endpoint)
Script 4: client patches (db.py add helper, sync.py add config fetch, main.py use db value)
Script 5: rebuild + test instructions
Let me write it all.
Hmm — models.py only has one new class. Instead of replacing whole file I'll use a PowerShell replace to insert AppSetting before class AuditLog. That way I don't have to retype it all. But user asked "if you change the code, give me the whole file". Hmm. Let me give full models.py anyway — it's short.
OK writing now. Let me focus.
Настраиваемый idle-порог + новая логика отчёта
Что изменится
Настройки в админке — страница /admin/settings, поле «Закрывать висящие сессии через N минут».
Клиент подтягивает это значение с сервера раз в 5 минут.
«Отработано» = от старта первой сессии до конца последней сессии за день.
«Эффективное время» = сумма эффективных времён (то, что раньше было «Отработано»).
Топ программ — кликабельные, показывают разбивку по сотрудникам.
________________________________________
Скрипт 1 — серверные Python-файлы
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

# ============================================================
# models.py — добавляем AppSetting
# ============================================================
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
    """Настройки приложения (key-value), редактируемые через админку."""
    __tablename__ = "app_settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
'@
[System.IO.File]::WriteAllText("$serverDir\models.py", $models_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  models.py" -ForegroundColor Green

# ============================================================
# web_admin.py
# ============================================================
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
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import (
    AppSetting, AuditLog, BootstrapToken, Computer, Employee, Record, WorkSession,
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


def get_idle_close_minutes(db: Session) -> int:
    try:
        return max(5, min(480, int(get_app_setting(db, "idle_close_minutes", "30"))))
    except (ValueError, TypeError):
        return 30


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
        ("Asia/Yekaterinburg", "Екатеринбург (UTC+5)"),
        ("Asia/Novosibirsk", "Новосибирск (UTC+7)"),
        ("Asia/Krasnoyarsk", "Красноярск (UTC+7)"),
        ("Asia/Irkutsk", "Иркутск (UTC+8)"),
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
# Настройки
# ============================================================

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    idle = get_idle_close_minutes(db)
    saved = request.query_params.get("saved") == "1"
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "admin": request.session.get("admin"),
        "idle_close_minutes": idle,
        "saved": saved,
    })


@router.post("/settings/save")
def settings_save(
    idle_close_minutes: int = Form(30),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    idle_close_minutes = max(5, min(480, int(idle_close_minutes)))
    old = get_app_setting(db, "idle_close_minutes", "30")
    set_app_setting(db, "idle_close_minutes", str(idle_close_minutes))
    db.add(AuditLog(
        actor="admin", entity="app_setting", entity_id="idle_close_minutes",
        action="update",
        old_value=old, new_value=str(idle_close_minutes),
    ))
    db.commit()
    return RedirectResponse("/admin/settings?saved=1", status_code=303)


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
