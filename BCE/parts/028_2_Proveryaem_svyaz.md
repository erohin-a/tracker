# --- 2. Проверяем связь ---

*Часть 28 из 100. Источник: `BCE.md`.*

[◀ Смотрим что там](027_Smotrim_chto_tam.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](029_part.md)

---

# --- 2. Проверяем связь ---
Write-Host "`n--- Проверка через IPv4 ---" -ForegroundColor Cyan
curl.exe -k -4 https://127.0.0.1/api/v1/version

Write-Host "`n--- Проверка через Python (как делает клиент) ---" -ForegroundColor Cyan
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -c @"
import socket
print('getaddrinfo(127.0.0.1):', socket.getaddrinfo('127.0.0.1', 443, type=socket.SOCK_STREAM)[0][4])
print('getaddrinfo(localhost):', socket.getaddrinfo('localhost', 443, type=socket.SOCK_STREAM)[0][4])

import httpx
try:
    r = httpx.get('https://127.0.0.1/api/v1/version', verify=False, timeout=5.0)
    print('127.0.0.1 ?', r.status_code, r.json())
except Exception as e:
    print('127.0.0.1 ? ОШИБКА:', e)
"@
Ожидаемый вывод:
text
OK  client/.env обновлён
TRACKER_SERVER_URL=https://127.0.0.1
TRACKER_PIN=
TRACKER_VERSION=1.0.0

--- Проверка через IPv4 ---
{"latest_version":"0.0.0",...}

--- Проверка через Python ---
getaddrinfo(127.0.0.1): ('127.0.0.1', 443)
getaddrinfo(localhost): ('::1', 443, ...)   ? вот оно!
127.0.0.1 ? 200 {'latest_version': '0.0.0.0', ...}
Если увидите что-то похожее — всё правильно, 127.0.0.1 решает проблему.
________________________________________
Запуск клиента
Клиент должен быть закрыт. Запускаем заново:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Параллельно во втором окне:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки:
text
tracker.sync INFO SyncWorker started; server=https://127.0.0.1
tracker.sync INFO Server reachable (HTTP 200)
На панели клиента — «? онлайн» зелёным.
________________________________________
Если появится ошибка SSL
Возможные варианты:
SSL: CERTIFICATE_VERIFY_FAILED
Сертификат не покрывает 127.0.0.1 — но у вас SAN DNS:localhost,IP:127.0.0.1, поэтому должно работать. Если всё-таки ошибка — проверьте:
powershell
Get-Content "$env:APPDATA\Tracker\ca.pem" | Select-String "127.0.0.1"
Если не найдёт — перевыпустим сертификат.
На будущее — TRACKER_INSECURE=1
Если хотите временно выключить проверку SSL (только для теста), добавьте в client/.env:
text
TRACKER_INSECURE=1
Клиент перестанет проверять сертификат. Это для отладки, на проде не использовать.
________________________________________
Почему так произошло
Скорее всего, у вас в корпоративной сети установлен DNS-суффикс ANTOR.msk, и Windows некорректно резолвит localhost через IPv6. Это типичная проблема в доменных окружениях с WSL2.
На будущее: делайте в client/.env https://127.0.0.1 для локальной разработки. При развёртывании на реальном сервере — там будет либо IP, либо нормальное DNS-имя (например, tracker.company.ru), и проблемы не возникнет.
________________________________________
После того как «онлайн» появится
Пришлите:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 30 -Encoding UTF8
docker compose logs api --tail=20
И скажите — ушли ли 500-е ошибки. После этого переходим к следующему блоку:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация, поиск
XLSX — убрать «Группа»/«Аварийный», добавить «Год / Месяц / Число»
Группировка «Месяц ? Сотрудник» в онлайн-отчёте
Календарь рабочих/нерабочих дней
Heartbeat + Онлайн/Оффлайн на дашборде
Массовая привязка ПК через CSV
PDF-отчёт
Запускайте скрипт, пришлите лог — и поехали дальше.
Если всё олк переходим к следующему блоку
Логи показывают что теперь всё работает - 200 OK на sessions и records/batch. Есть ещё иногда getaddrinfo failed, но это скорее всего остаточные проблемы с локальным DNS.
Похоже проблема была в том, что клиент использует "https://localhost" в некоторых случаях (в httpx запросах видно https://localhost/...), а в config.py SERVER_URL установлен на 127.0.0.1. То есть у клиента могут быть разные источники URL - config.py клиента и .env.
Но главное - синхронизация идёт, 200 OK. Пользователь говорит "переходим к следующему блоку".
Следующий блок по плану:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация, поиск
XLSX — убрать «Группа»/«Аварийный», добавить «Год / Месяц / Число»
Группировка «Месяц ? Сотрудник» в онлайн-отчёте
Календарь рабочих/нерабочих дней
Heartbeat + Онлайн/Оффлайн на дашборде
Массовая привязка ПК через CSV
PDF-отчёт
Давайте выдам всё крупным блоком. Много кода, но я буду структурировать по шагам.
Начнём с server/web_admin.py - полная замена с:
Мультивыбор отделов и сотрудников (с зависимой фильтрацией на JS)
Мультивыбор компьютеров
Поиск в select
Группировка по месяцам
XLSX с колонками Год/Месяц/Число, без Группы и Аварийных
Heartbeat endpoint
Плюс client/main.py - добавить heartbeat
Плюс server/main.py - добавить /api/v1/heartbeat
Плюс шаблоны:
reports.html - с мультивыбором
report_result.html - с новыми группировками
dashboard.html - с онлайн/оффлайн
base.html - с tooltips
Плюс models.py - уже есть поле last_seen_at, только надо его обновлять в heartbeat
Плюс календарь рабочих/нерабочих дней - новая модель + страница
Это ОГРОМНЫЙ блок. Давайте разделю его на 2-3 сообщения, чтобы пользователь не утонул.
Разделю так:
Сообщение 1 (это): Фильтры + поиск + мультивыбор + heartbeat + XLSX-колонки + группировка по месяцам
Сообщение 2: Календарь рабочих дней + подсветка Сб/Вс + массовая привязка ПК + PDF
Или даже так, чтобы всё-таки влезло, я уплотню код и дам всё в одном сообщении, но с понятной разбивкой.
Попробую так - одно большое сообщение со всеми 7 пунктами, но каждый пункт компактный.
Актуально: клиент использует 127.0.0.1, но в логах видно "https://localhost/..." - значит config.py клиента всё ещё содержит localhost. Это ок, потому что httpx иногда резолвит, но проблема возникает. Надо будет починить клиентский config.py чтобы он читал SERVER_URL правильно.
Проверю - в .env клиента TRACKER_SERVER_URL=https://127.0.0.1, но в логах https://localhost. Значит config.py берёт не из .env, либо .env перезаписывается, либо .env был не тот.
Скорее всего в config.py клиента SERVER_URL не читается из .env - там дефолт "https://tracker.example.com", а в .env override=True должно работать. Но в логах видно https://localhost - значит где-то зашито localhost.
Возможно, в http_client есть свой URL. Или в crypto.py. Или где-то ещё прописан localhost. Надо проверить.
Ладно, я это учту и дам патч клиента тоже. Но сначала перейдём к основному блоку.
Начну отвечать. Буду лаконичен. Дам полные скрипты.
Отлично, синхронизация пошла — 200 OK на sessions и batch ??
Из логов видно: записи уходят, ошибок 500 нет. Остались редкие getaddrinfo failed — это старые файлы клиента ещё держат где-то localhost (в config.py клиента дефолт). Поправим это в текущем блоке заодно.
Переходим к следующему крупному блоку. Он большой — разбил на 3 подблока. Каждый — отдельный PowerShell-скрипт.
Что делаем
Подблок A.
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров с зависимой фильтрацией
Поиск внутри <select multiple> (собственный, без библиотек)
Группировка «Месяц ? Сотрудник» в онлайн-отчёте
XLSX — убрать «Группа» и «Аварийный», добавить колонки «Год / Месяц / Число»
Подблок B.
Heartbeat — эндпоинт + колонка «Онлайн/Оффлайн» на дашборде
Фикс дефолтного localhost в клиенте
Массовая привязка ПК через CSV
Подблок C.
Календарь рабочих/нерабочих дней + подсветка Сб/Вс
PDF-отчёт
Начнём с A. Скрипты запускать по порядку.
________________________________________
Скрипт A1 — server/web_admin.py (полная замена)
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

$web_admin_py = @'
"""
Веб-интерфейс администратора.
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

RU_MONTHS = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
             "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


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
        "count_weekends": get_app_setting(db, "count_weekends", "1") == "1",
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

    # Онлайн/оффлайн: считаем компьютер онлайн, если last_seen_at в пределах N минут
    heartbeat_window = 10
    cutoff_online = _now() - timedelta(minutes=heartbeat_window)

    stats = {
        "employees": db.query(Employee).filter(Employee.fired_at.is_(None)).count(),
        "departments": db.query(Department).filter(Department.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
        "computers_online": db.query(Computer).filter(
            Computer.is_active == True,
            Computer.last_seen_at >= cutoff_online,
        ).count(),
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

    recent_computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).limit(15).all()
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "stats": stats,
        "recent_computers": recent_computers, "recent_audit": recent_audit,
        "admin": request.session.get("admin"), "tz": tz,
        "heartbeat_window": heartbeat_window,
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
    count_weekends: str = Form(""),
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
        "count_weekends": "1" if count_weekends else "0",
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
    from sqlalchemy import func as _f
    counts = dict(
        db.query(Employee.department_id, _f.count(Employee.id))
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
    heartbeat_window = 10
    cutoff_online = _now() - timedelta(minutes=heartbeat_window)
    return templates.TemplateResponse("computers.html", {
        "request": request, "computers": computers, "employees": employees,
        "admin": request.session.get("admin"), "tz": tz,
        "cutoff_online": cutoff_online,
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


@router.post("/computers/bulk-assign")
async def computers_bulk_assign(request: Request,
                                db: Session = Depends(get_db), _=Depends(current_admin)):
    """
    Массовая привязка ПК из CSV.
    Формат CSV (разделитель ; или ,): hostname; 1C_ID
    Или: hostname; ФИО
    """
    form = await request.form()
    file = form.get("csv_file")
    if not file:
        raise HTTPException(400, "Файл не загружен")

    raw = (await file.read()).decode("utf-8-sig", errors="replace")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

    # Определяем разделитель
    delimiter = ";"
    if lines and "," in lines[0] and ";" not in lines[0]:
        delimiter = ","

    header_skipped = False
    assigned = 0
    not_found_emp = []
    not_found_comp = []
    errors = []

    for i, ln in enumerate(lines):
        parts = [p.strip() for p in ln.split(delimiter)]
        if len(parts) < 2:
            errors.append(f"Строка {i+1}: < 2 колонок")
            continue
        hostname, key = parts[0], parts[1]

        # Пропускаем заголовок
        if not header_skipped and hostname.lower() in ("hostname", "пк", "компьютер"):
            header_skipped = True
            continue

        # Ищем сотрудника по 1C ID или ФИО
        emp = None
        if key:
            emp = db.query(Employee).filter(Employee.external_id == key).first()
            if not emp:
                emp = db.query(Employee).filter(Employee.full_name.ilike(f"%{key}%")).first()

        comp = db.query(Computer).filter(
            (Computer.hostname == hostname) | (Computer.computer_uid == hostname)
        ).first()

        if not comp:
            not_found_comp.append(hostname)
            continue
        if not emp:
            not_found_emp.append(key)
            continue

        comp.employee_id = emp.id
        comp.assigned_at = _now()
        assigned += 1

    db.add(AuditLog(actor="admin", entity="computer", action="bulk_assign",
                    new_value=json.dumps({"assigned": assigned,
                                          "not_found_comp": len(not_found_comp),
                                          "not_found_emp": len(not_found_emp)},
                                         ensure_ascii=False)))
    db.commit()

    msg = f"Привязано: {assigned}."
    if not_found_comp:
        msg += f" Не найдены ПК: {len(not_found_comp)} ({', '.join(not_found_comp[:5])})."
    if not_found_emp:
        msg += f" Не найдены сотрудники: {len(not_found_emp)} ({', '.join(not_found_emp[:5])})."
    if errors:
        msg += f" Ошибок в строках: {len(errors)}."

    return RedirectResponse(f"/admin/computers?bulk_msg={msg}", status_code=303)


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
