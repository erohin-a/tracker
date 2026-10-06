<!-- Часть 163 из 1409 -->
# Логи api
*Хлебные крошки:* Логи api

[◀ Проверьте, что .env содержит ADMIN_API_KEY и JWT_SECRET](162_Proverte_chto_env_soderzhit_ADMIN_API_KEY_i_JWT_SECRET.md) | [Оглавление](00_BCE_INDEX.md) | [--- Сессионный middleware для веб-интерфейса администратора --- ▶](164_Sessionnyy_middleware_dlya_veb_interfeysa_administratora.md)

---

# Логи api
docker compose logs api --tail=100
Если БД пустая, create_all создаст таблицы уже с новыми полями.
________________________________________
Шаг 9. Проверка
Откройте в браузере:
https://localhost/admin/login
(сначала примите самоподписанный сертификат).
Логин admin, пароль = ADMIN_API_KEY из D:\tracker\.env.
Перейдите в Сотрудники ? добавьте пару человек.
Перейдите в Компьютеры ? привяжите существующий ПК к сотруднику.
Перейдите в Токены ? выпустите новый bootstrap-токен (он покажется один раз).
Перейдите в Отчёты ? выберите период и нажмите «Сформировать».
Попробуйте форматы CSV и Excel.
Аудит покажет все ваши действия.
________________________________________
Шаг 10. Частые проблемы
Симптом	Причина	Решение
TemplateNotFound	неверная директория шаблонов	шаблоны должны быть в server/templates/, а контейнер работать из /app, где server/ — пакет
ModuleNotFoundError: itsdangerous	не обновлён requirements.txt	добавить и docker compose up -d --build
Сессия не сохраняется	https_only=True, а работаете по http	оставить web_secure_cookie=False в dev
401 сразу после логина	пароль не совпадает с ADMIN_API_KEY	проверьте .env и docker compose exec api printenv ADMIN_API_KEY
Отчёт пуст	WorkSession.employee_id не заполняется	в upsert_session добавить employee_id=comp.employee_id
Excel падает на импорте	не установлен openpyxl	pip install openpyxl в контейнере через requirements.txt
________________________________________
Что дальше (следующая итерация)
Логично сделать сразу после того, как админка заработает:
Heartbeat-эндпоинт /api/v1/heartbeat — чтобы на дашборде видеть «онлайн/оффлайн».
Публикация версий клиента через UI — форма добавляет запись в client_versions, чтобы работало автообновление.
PDF-экспорт отчётов (reportlab) — по образцу XLSX.
Роли (admin/operator/viewer) — таблица admin_users, хеш пароля через passlib.
Alembic — чтобы подобные правки схемы не требовали сноса БД.
Скажите, какой пункт делаем следующим — выдам такой же готовый код.
Этот ответ сгенерирован AI, только для справки.
Начиная с шага 6 пункт 3 я начал путаться напиши что куда конкретно вставлять как для чайника, а лучше если меняешь код в файле то давай весь целиком что бы лишних символов я не вставил
User wants full file contents, not fragments. Need to be very explicit. Let me provide complete files for server/models.py, server/config.py, server/main.py, server/requirements.txt. Also mention web_admin.py is new full file (already given). Let me produce full files.
I need to reconstruct the full files with new fields added.
Let me write out everything cleanly.
server/config.py - full
server/models.py - full
server/main.py - full
server/requirements.txt - full
Then instructions step by step for a beginner.
Пошаговая инструкция «для чайника» — какие файлы менять целиком
Я дам полные версии файлов — копируйте их от первой до последней строки и заменяйте существующие. Ничего дополнительно вставлять руками не нужно.
Порядок действий:
Меняем server/requirements.txt
Меняем server/config.py
Меняем server/models.py
Меняем server/main.py
Создаём server/web_admin.py (новый файл)
Создаём папку server/templates/ и кладём туда 9 HTML-файлов (даю отдельным сообщением или ниже)
Пересобираем Docker
Начнём.
________________________________________
Файл 1 из 4 — server/requirements.txt
Откройте D:\tracker\server\requirements.txt, удалите всё содержимое и вставьте это:
txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
gunicorn==22.0.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
pydantic==2.7.4
pydantic-settings==2.3.0
cryptography==42.0.8
python-multipart==0.0.9
jinja2==3.1.4
itsdangerous==2.2.0
openpyxl==3.1.5
Сохраните.
________________________________________
Файл 2 из 4 — server/config.py
Откройте D:\tracker\server\config.py, удалите всё содержимое и вставьте:
python
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

_PLACEHOLDERS = {"", "CHANGE_ME", "CHANGE_ME_JWT", "CHANGE_ME_32_BYTE_BASE64_KEY"}


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tracker:tracker@db:5432/tracker"
    secret_encryption_key: str = ""
    jwt_secret: str = ""
    admin_api_key: str = ""

    # --- Веб-интерфейс администратора ---
    admin_login: str = "admin"          # логин для входа в /admin
    session_secret: str = ""            # если пусто — используется jwt_secret
    web_secure_cookie: bool = False     # на проде с HTTPS поставьте True

    class Config:
        env_file = ".env"


settings = Settings()


def _fail(name: str, hint: str):
    raise RuntimeError(f"{name} не задан или placeholder.\n{hint}")


if settings.secret_encryption_key in _PLACEHOLDERS:
    _fail(
        "SECRET_ENCRYPTION_KEY",
        'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"',
    )

if settings.jwt_secret in _PLACEHOLDERS:
    _fail(
        "JWT_SECRET",
        'python -c "import secrets; print(secrets.token_urlsafe(48))"',
    )

if settings.admin_api_key in _PLACEHOLDERS:
    _fail(
        "ADMIN_API_KEY",
        'python -c "import secrets; print(secrets.token_urlsafe(48))"',
    )

try:
    FERNET = Fernet(settings.secret_encryption_key.encode())
except Exception as e:
    raise RuntimeError(f"SECRET_ENCRYPTION_KEY некорректен: {e}") from e
Сохраните.
________________________________________
Файл 3 из 4 — server/models.py
Откройте D:\tracker\server\models.py, удалите всё содержимое и вставьте:
python
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

    # --- привязка к сотруднику ---
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True))


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    # --- ФИО по частям (используется веб-интерфейсом) ---
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
Сохраните.
________________________________________
Файл 4 из 4 — server/main.py
Откройте D:\tracker\server\main.py, удалите всё содержимое и вставьте:
python
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .config import FERNET, settings
from .database import SessionLocal, init_db
from .models import (
    AuditLog, BootstrapToken, ClientVersion, Computer, Record, WorkSession,
)
from .schemas import (
    RecordBatch, RecordBatchResponse, RegisterRequest, RegisterResponse,
    SessionIn, VersionResponse,
)
from .security import compute_signature, verify_signature
from .web_admin import router as admin_web_router

log = logging.getLogger("tracker.server")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Employee Tracker API", version="1.3.0")

