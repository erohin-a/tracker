<!-- Часть 71 из 1409 -->
# `server/main.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/main.py`

[◀ `server/schemas.py`](070_server_schemas_py.md) | [Оглавление](00_BCE_INDEX.md) | [`server/Dockerfile` ▶](072_server_Dockerfile.md)

---

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

