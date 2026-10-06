<!-- Часть 350 из 1409 -->
# date
*Хлебные крошки:* date

[◀ ...](349_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](351_part.md)

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


