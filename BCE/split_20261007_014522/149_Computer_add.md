<!-- Часть 149 из 1409 -->
# Computer add
*Хлебные крошки:* Computer add

[◀ Employee add columns](148_Employee_add_columns.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Сотрудники ---------- ▶](150_Sotrudniki.md)

---

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


