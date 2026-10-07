# Логи api

*Часть 9 из 100. Источник: `BCE.md`.*

[◀ ---------- Отчёты ----------](008_Otchety.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Version ---------- ▶](010_Version.md)

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

# --- Сессионный middleware для веб-интерфейса администратора ---
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret or settings.jwt_secret,
    session_cookie="tracker_admin",
    max_age=8 * 3600,
    same_site="lax",
    https_only=settings.web_secure_cookie,
)

# --- Подключаем веб-админку /admin/* ---
app.include_router(admin_web_router)


def _now():
    return datetime.now(timezone.utc)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_computer(x_computer_uid: str = Header(...),
                 db: Session = Depends(get_db)) -> Computer:
    comp = (db.query(Computer)
            .filter(Computer.computer_uid == x_computer_uid).first())
    if not comp or not comp.is_active:
        raise HTTPException(401, "Unknown or inactive computer")
    return comp


def decrypt_secret(comp: Computer) -> str:
    return FERNET.decrypt(comp.client_secret_enc.encode()).decode()


def require_admin(x_admin_token: Optional[str] = Header(None)):
    if x_admin_token is None:
        raise HTTPException(401, "admin token required",
                            headers={"WWW-Authenticate": "ApiKey"})
    if not secrets.compare_digest(x_admin_token, settings.admin_api_key):
        raise HTTPException(403, "admin required")


def _hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


@app.on_event("startup")
def on_startup():
    init_db()


# ---------- Admin API ----------

@app.post("/api/v1/admin/bootstrap-tokens",
          dependencies=[Depends(require_admin)])
def issue_bootstrap_token(ttl_hours: int = 24, issued_by: str = "admin",
                          db: Session = Depends(get_db)):
    ttl_hours = max(1, min(ttl_hours, 24 * 30))
    raw = secrets.token_urlsafe(32)
    db.add(BootstrapToken(
        token_hash=_hash_token(raw),
        issued_by=issued_by,
        expires_at=_now() + timedelta(hours=ttl_hours),
    ))
    db.commit()
    return {"token": raw, "expires_in_hours": ttl_hours}


@app.post("/api/v1/admin/computers/{computer_uid}/revoke",
          dependencies=[Depends(require_admin)])
def revoke_computer(computer_uid: str, db: Session = Depends(get_db)):
    comp = (db.query(Computer)
            .filter(Computer.computer_uid == computer_uid).first())
    if not comp:
        raise HTTPException(404, "not found")
    comp.is_active = False
    db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp.id),
                    action="revoke",
                    old_value=json.dumps({"uid": computer_uid}, ensure_ascii=False)))
    db.commit()
    return {"status": "revoked"}


# ---------- Register ----------

@app.post("/api/v1/computers/register", response_model=RegisterResponse)
def register_computer(payload: RegisterRequest, request: Request,
                      db: Session = Depends(get_db)):
    now = _now()
    stmt = (
        update(BootstrapToken)
        .where(BootstrapToken.token_hash == _hash_token(payload.bootstrap_token),
               BootstrapToken.used_at.is_(None),
               BootstrapToken.expires_at > now)
        .values(used_at=now, used_by_uid=payload.computer_uid)
        .returning(BootstrapToken.id, BootstrapToken.issued_by)
    )
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(401, "Invalid or expired bootstrap token")

    _, issued_by = row

    existing = (db.query(Computer)
                .filter(Computer.computer_uid == payload.computer_uid).first())
    if existing and existing.is_active:
        raise HTTPException(409, "computer_uid already registered; ask admin to revoke")

    client_secret = secrets.token_urlsafe(48)
    secret_enc = FERNET.encrypt(client_secret.encode()).decode()

    try:
        if existing:
            existing.client_secret_enc = secret_enc
            existing.secret_version = (existing.secret_version or 1) + 1
            existing.hostname = payload.hostname
            existing.os_info = payload.os_info
            existing.client_version = payload.client_version
            existing.is_active = True
            comp = existing
        else:
            comp = Computer(
                computer_uid=payload.computer_uid,
                hostname=payload.hostname,
                os_info=payload.os_info,
                client_version=payload.client_version,
                client_secret_enc=secret_enc,
                secret_version=1,
            )
            db.add(comp)
            db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "computer_uid already registered (race)")

    db.add(AuditLog(
        actor=issued_by or "system",
        entity="computer", entity_id=str(comp.id), action="register",
        new_value=json.dumps(
            {"uid": payload.computer_uid, "hostname": payload.hostname,
             "secret_version": comp.secret_version},
            ensure_ascii=False),
    ))
    db.commit()
    log.info("Registered uid=%s ip=%s", payload.computer_uid, request.client.host)

    return RegisterResponse(computer_uid=payload.computer_uid,
                            client_secret=client_secret,
                            secret_version=comp.secret_version)


# ---------- Sessions ----------

@app.post("/api/v1/sessions")
def upsert_session(payload: SessionIn, comp: Computer = Depends(get_computer),
                   db: Session = Depends(get_db)):
    start = datetime.fromisoformat(payload.session_start.replace("Z", "+00:00"))
    end = (datetime.fromisoformat(payload.session_end.replace("Z", "+00:00"))
           if payload.session_end else None)

    if end is not None and end < start:
        raise HTTPException(422, "session_end < session_start")

    ws = (db.query(WorkSession)
          .filter(WorkSession.session_uid == payload.session_uid).first())

    if ws is None:
        ws = WorkSession(
            session_uid=payload.session_uid,
            computer_id=comp.id,
            employee_id=comp.employee_id,           # ? наследуем от ПК
            session_start=start,
            session_end=end,
            abnormal_termination=payload.abnormal_termination,
            client_version=payload.client_version,
        )
        db.add(ws)
    else:
        if ws.computer_id != comp.id:
            raise HTTPException(409, "session_uid belongs to another computer")
        if end:
            ws.session_end = end
        if payload.abnormal_termination:
            ws.abnormal_termination = True

    if payload.abnormal_termination:
        db.add(AuditLog(actor=f"computer:{comp.computer_uid}",
                        entity="work_session", entity_id=payload.session_uid,
                        action="abnormal_termination"))

    comp.last_seen_at = _now()
    db.commit()
    return {"status": "ok"}


# ---------- Records ----------

@app.post("/api/v1/records/batch", response_model=RecordBatchResponse)
def ingest_records(payload: RecordBatch, request: Request,
                   comp: Computer = Depends(get_computer),
                   db: Session = Depends(get_db)):
    secret = decrypt_secret(comp)

    session_uids = {r.session_uid for r in payload.records}
    known_sessions = {
        uid for (uid,) in db.query(WorkSession.session_uid)
        .filter(WorkSession.session_uid.in_(session_uids),
                WorkSession.computer_id == comp.id).all()
    }

    if payload.batch_signature is not None:
        batch_signable = {"records": [
            {"record_uid": r.record_uid, "session_uid": r.session_uid,
             "kind": r.kind, "data": r.data, "client_ts": r.client_ts,
             "signature": r.signature}
            for r in payload.records
        ]}
        if not verify_signature(secret, batch_signable, payload.batch_signature):
            raise HTTPException(400, "batch signature invalid")

    accepted: list[str] = []
    rejected: list[str] = []
    reasons: dict[str, str] = {}

    incoming_uids = [r.record_uid for r in payload.records]
    existing_uids = {
        uid for (uid,) in db.query(Record.record_uid)
        .filter(Record.record_uid.in_(incoming_uids),
                Record.computer_id == comp.id).all()
    }

    for rec in payload.records:
        signable = {
            "record_uid": rec.record_uid,
            "session_uid": rec.session_uid,
            "kind": rec.kind,
            "data": rec.data,
            "client_ts": rec.client_ts,
        }
        if not verify_signature(secret, signable, rec.signature):
            rejected.append(rec.record_uid)
            reasons[rec.record_uid] = "bad_signature"
            continue

        if rec.record_uid in existing_uids:
            accepted.append(rec.record_uid)
            continue

        if rec.session_uid not in known_sessions:
            rejected.append(rec.record_uid)
            reasons[rec.record_uid] = "unknown_session"
            continue

        db.add(Record(
            record_uid=rec.record_uid,
            session_uid=rec.session_uid,
            computer_id=comp.id,
            kind=rec.kind,
            data=json.dumps(rec.data, ensure_ascii=False),
            client_ts=rec.client_ts_dt,
            client_ip=request.client.host,
            signature=rec.signature,
        ))
        accepted.append(rec.record_uid)

    comp.last_seen_at = _now()

    if rejected:
        db.add(AuditLog(
            actor=f"computer:{comp.computer_uid}",
            entity="record", entity_id=",".join(rejected[:20]),
            action="reject_signature",
            new_value=json.dumps({"count": len(rejected), "reasons": reasons},
                                 ensure_ascii=False),
        ))

    db.commit()

    response_payload = {
        "accepted_uuids": accepted,
        "rejected_uuids": rejected,
        "reasons": reasons,
    }
    server_signature = compute_signature(secret, response_payload)

    return RecordBatchResponse(
        accepted_uuids=accepted, rejected_uuids=rejected, reasons=reasons,
        server_signature=server_signature,
    )


