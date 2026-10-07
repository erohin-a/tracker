# ?? Папка `server/`

*Часть 2 из 100. Источник: `BCE.md`.*

[◀ Полное руководство по проекту «Трекер»](001_Polnoe_rukovodstvo_po_proektu_Treker.md) | [Оглавление](00_BCE_INDEX.md) | [?? Папка `client/` ▶](003_Papka_client.md)

---

## ?? Папка `server/`

### `server/__init__.py`

```python
# Пустой файл. Делает папку server Python-пакетом.
```

### `server/requirements.txt`

```txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
gunicorn==22.0.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
pydantic==2.7.4
pydantic-settings==2.3.0
cryptography==42.0.8
python-multipart==0.0.9
```

### `server/config.py`

```python
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

_PLACEHOLDERS = {"", "CHANGE_ME", "CHANGE_ME_JWT", "CHANGE_ME_32_BYTE_BASE64_KEY"}


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tracker:tracker@db:5432/tracker"
    secret_encryption_key: str = ""
    jwt_secret: str = ""
    admin_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()


def _fail(name: str, hint: str):
    raise RuntimeError(f"{name} не задан или placeholder.\n{hint}")


if settings.secret_encryption_key in _PLACEHOLDERS:
    _fail("SECRET_ENCRYPTION_KEY",
          'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
if settings.jwt_secret in _PLACEHOLDERS:
    _fail("JWT_SECRET",
          'python -c "import secrets; print(secrets.token_urlsafe(48))"')
if settings.admin_api_key in _PLACEHOLDERS:
    _fail("ADMIN_API_KEY",
          'python -c "import secrets; print(secrets.token_urlsafe(48))"')

try:
    FERNET = Fernet(settings.secret_encryption_key.encode())
except Exception as e:
    raise RuntimeError(f"SECRET_ENCRYPTION_KEY некорректен: {e}") from e
```

### `server/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import Base

engine = create_engine(settings.database_url, pool_pre_ping=True,
                       pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=engine)
```

### `server/models.py`

```python
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime,
    ForeignKey, Text, Index
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


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
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
```

### `server/security.py`

```python
import hmac
import hashlib
import json
import math
from typing import Any


def _validate(obj: Any) -> Any:
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("NaN/Infinity not allowed in signed payload")
        return obj
    if isinstance(obj, dict):
        return {str(k): _validate(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_validate(v) for v in obj]
    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    raise ValueError(f"unsupported type in signed payload: {type(obj).__name__}")


def canonical_json(obj: Any) -> bytes:
    normalized = _validate(obj)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def compute_signature(secret: str, payload: Any) -> str:
    return hmac.new(secret.encode("utf-8"), canonical_json(payload),
                    hashlib.sha256).hexdigest()


def verify_signature(secret: str, payload: Any, signature: str) -> bool:
    try:
        expected = compute_signature(secret, payload)
    except ValueError:
        return False
    return hmac.compare_digest(expected, signature)
```

### `server/schemas.py`

```python
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    computer_uid: str = Field(..., min_length=8, max_length=64)
    hostname: Optional[str] = Field(None, max_length=255)
    os_info: Optional[str] = Field(None, max_length=255)
    client_version: Optional[str] = Field(None, max_length=32)
    bootstrap_token: str = Field(..., min_length=16, max_length=256)


class RegisterResponse(BaseModel):
    computer_uid: str
    client_secret: str
    secret_version: int


class RecordIn(BaseModel):
    record_uid: str = Field(..., min_length=8, max_length=64)
    session_uid: str = Field(..., min_length=8, max_length=64)
    kind: str = Field(..., min_length=1, max_length=32)
    data: Any = Field(default_factory=dict)
    client_ts: str
    signature: str = Field(..., min_length=64, max_length=128)

    @field_validator("client_ts")
    @classmethod
    def _validate_ts(cls, v: str) -> str:
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError(f"invalid client_ts: {e}") from e
        if dt.tzinfo is None:
            raise ValueError("client_ts must be timezone-aware")
        return v

    @property
    def client_ts_dt(self) -> datetime:
        return datetime.fromisoformat(self.client_ts.replace("Z", "+00:00"))


class RecordBatch(BaseModel):
    records: List[RecordIn] = Field(..., min_length=1, max_length=500)
    batch_signature: Optional[str] = Field(None, min_length=64, max_length=128)


class RecordBatchResponse(BaseModel):
    accepted_uuids: List[str]
    rejected_uuids: List[str]
    reasons: dict[str, str] = {}
    server_signature: str


class SessionIn(BaseModel):
    session_uid: str = Field(..., min_length=8, max_length=64)
    session_start: str
    session_end: Optional[str] = None
    abnormal_termination: bool = False
    client_version: Optional[str] = Field(None, max_length=32)

    @field_validator("session_start")
    @classmethod
    def _tz_start(cls, v: str) -> str:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError("session_start must be timezone-aware")
        return v

    @field_validator("session_end")
    @classmethod
    def _tz_end(cls, v):
        if v is None:
            return v
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError("session_end must be timezone-aware")
        return v


class VersionResponse(BaseModel):
    latest_version: str
    download_url: str
    mandatory: bool
    release_notes: Optional[str] = None
```

### `server/main.py`

```python
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

log = logging.getLogger("tracker.server")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Employee Tracker API", version="1.2.0")


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
    comp = db.query(Computer).filter(Computer.computer_uid == x_computer_uid).first()
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


# ---------- Admin ----------

@app.post("/api/v1/admin/bootstrap-tokens", dependencies=[Depends(require_admin)])
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
    comp = db.query(Computer).filter(Computer.computer_uid == computer_uid).first()
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

    existing = db.query(Computer).filter(
        Computer.computer_uid == payload.computer_uid
    ).first()
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

    ws = db.query(WorkSession).filter(
        WorkSession.session_uid == payload.session_uid).first()
    if ws is None:
        ws = WorkSession(
            session_uid=payload.session_uid,
            computer_id=comp.id,
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


# ---------- Version ----------

@app.get("/api/v1/version", response_model=VersionResponse)
def get_latest_version(current: str = "", db: Session = Depends(get_db)):
    latest = db.query(ClientVersion).order_by(ClientVersion.release_date.desc()).first()
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
    return VersionResponse(latest_version=latest.version,
                           download_url=latest.download_url,
                           mandatory=latest.mandatory,
                           release_notes=latest.release_notes)
```

### `server/Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Зависимости
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем пакет server целиком
COPY server/ ./server/

# Гарантируем, что это пакет (важно для относительных импортов)
RUN touch /app/server/__init__.py

EXPOSE 8000

# Указываем gunicorn'у пакет server, модуль main, объект app
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", \
     "-b", "0.0.0.0:8000", "server.main:app"]
```

### `server/nginx.conf`

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name localhost;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;

    client_max_body_size 10m;

    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

---

