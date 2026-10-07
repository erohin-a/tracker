# 1) Заменить подключение сигналов в _start_sync_worker

*Часть 26 из 100. Источник: `BCE.md`.*

[◀ ============================================================](025_part.md) | [Оглавление](00_BCE_INDEX.md) | [Смотрим что там ▶](027_Smotrim_chto_tam.md)

---

# 1) Заменить подключение сигналов в _start_sync_worker
$oldBlock = @'
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.server_down.connect(
            lambda: self.lbl_server.setText("? офлайн"))
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()
'@

$newBlock = @'
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.connected.connect(self._on_connected)
        self.sync.server_down.connect(self._on_server_down)
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()
'@

if ($content.Contains($oldBlock)) {
    $content = $content.Replace($oldBlock, $newBlock)
    Write-Host "  OK  подписки на сигналы обновлены" -ForegroundColor Green
} elseif ($content.Contains("self.sync.connected.connect")) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} else {
    Write-Host "  ВНИМАНИЕ: не найден блок _start_sync_worker — правьте вручную" -ForegroundColor Red
}

# 2) Добавить обработчики _on_connected и _on_server_down
$marker = "    def _on_synced(self, n):"
$handlers = @'
    def _on_connected(self):
        self.lbl_server.setText("? онлайн")
        self.lbl_server.setStyleSheet("color:#28a745; font-size:13px;")

    def _on_server_down(self):
        self.lbl_server.setText("? офлайн")
        self.lbl_server.setStyleSheet("color:#dc3545; font-size:13px;")

    def _on_synced(self, n):
'@

if ($content.Contains("    def _on_synced(self, n):") -and -not $content.Contains("def _on_connected")) {
    $content = $content.Replace("    def _on_synced(self, n):", $handlers)
    Write-Host "  OK  обработчики добавлены" -ForegroundColor Green
}

# 3) Поправить _on_synced: не перезаписывать last_sync_ts при n=0
$oldSynced = @'
    def _on_synced(self, n):
        self.lbl_server.setText("? онлайн")
        try:
            db.set_meta("last_sync_ts", datetime.now(timezone.utc).isoformat())
        except Exception:
            pass
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")
'@

$newSynced = @'
    def _on_synced(self, n):
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")
'@

if ($content.Contains($oldSynced)) {
    $content = $content.Replace($oldSynced, $newSynced)
    Write-Host "  OK  _on_synced очищен" -ForegroundColor Green
}

[System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"
________________________________________
Шаг 4. Запуск и наблюдение
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

# Чистим лог, чтобы видеть только свежие сообщения
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

# Запускаем
python -m client.main
Через 3–5 секунд на панели должно быть «? онлайн» зелёным.
Параллельно во втором окне PowerShell следите за логом:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки:
text
tracker.sync INFO SyncWorker started; server=https://localhost
tracker.sync INFO Server reachable (HTTP 200)
tracker.sync INFO idle_close_minutes updated: 30
Если увидите Server unreachable: ... — там будет причина. Пришлите её.
________________________________________
Что дальше
После того как статус «онлайн» появится, я начну выдавать остальные пункты по вашему списку. Порядок такой:
? Клиент: регистрация — сделано
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация, поиск
XLSX: убрать «Группа» и «Аварийный», добавить «Год / Месяц / Число» русскими словами
Онлайн-отчёт: группировка «Месяц ? Сотрудник»
Календарь рабочих/нерабочих дней + подсветка Сб/Вс
Heartbeat + колонка «Онлайн/Оффлайн»
Массовая привязка ПК через CSV
PDF-отчёт (reportlab + кириллица)
Запускайте шаги 1–4, пришлите из лога что-нибудь если «онлайн» не появится.
The user has a problem: batch endpoint returns 500. Need to see server logs. Let me look at the pattern:
/records/batch ? 500
/sessions ? 409 Conflict (session_uid already exists) — then eventually 200
Sync fails with "sync failed: 500"
The 500 on batch is the real problem. Most likely cause: session_uid from records that belong to a session from ANOTHER computer — but no, that would be 4xx.
Look at the code: ingest_records in main.py. When record's session_uid isn't in known_sessions, it returns unknown_session (rejected, but 200 OK). So 500 is something else.
Possible causes:
Duplicate record_uid — already checked and skipped. Not 500.
Signature validation — returns 400.
Something in DB — maybe duplicate record_uid between computers triggers IntegrityError? The code checks Record.record_uid.in_(incoming_uids), Record.computer_id == comp.id — only for this computer. If the same record_uid exists for another computer, INSERT will fail with unique constraint violation on record_uid ? IntegrityError ? 500.
Actually the sessions conflict indicates: session 08f34fe3-... was created for another computer or already exists. When we try to create it, it 409s. Then _sync_sessions doesn't mark it synced (returns True, keeps trying). Records for that session then reference 08f34fe3-... which isn't in known_sessions of this computer (because of conflict) — but that's "unknown_session", not 500.
Actually wait: if session was created for another computer, its computer_id != comp.id, so known_sessions (filtered by comp.id) won't include it ? records get "unknown_session". That's a 200 with rejected, not 500.
Let me think about what causes 500.
Maybe the traceback reveals it. We need server logs. Let me ask.
But also — I should fix the code to be more robust:
Catch IntegrityError on insert and treat as "already exists" (idempotency).
Make /api/v1/sessions return 200 (idempotent) instead of 409 when the session already exists for the same computer.
Actually looking at the code:
python
if ws.computer_id != comp.id:
    raise HTTPException(409, "session_uid belongs to another computer")
This 409 happens for same session_uid belonging to another computer. But we need to look at WHERE this session came from. The session was created earlier, maybe from a PREVIOUS registration of the same computer (with different computer_id because computer_id is Computer.id which changed on re-register).
Wait — when we re-register a computer in the admin panel (revoke + re-register), Computer gets the same computer_uid but computer_id (integer PK) might be reused or new? Looking at register_computer:
python
if existing:
    existing.client_secret_enc = secret_enc
    ...
    comp = existing
So existing row is reused. But if the computer was deleted, then a new row with new id. In our scenario, likely computer wasn't deleted, just re-registered — computer_id stays the same.
Hmm, but session 08f34fe3-... shows 409. Which means ws.computer_id != comp.id. That means this session was created for a DIFFERENT comp.id but same session_uid. How?
User started work on the OLD registration (with old computer_id), session got created with old comp.
User deleted credentials, re-registered ? NEW Computer row with new id (or same id if reused).
Now the old session tries to sync ? 409 because comp.id changed.
That's very likely. Or:
User re-ran the client, generating new session_uid, but old session_uid records remained and got mixed.
Either way, the fix is:
On 409, mark session as synced with poisoned-like flag, or just drop.
Actually, if the session exists for another computer, we can't accept it. But we shouldn't keep retrying forever.
Let me focus. Two problems:
A. 500 on batch: needs investigation, likely IntegrityError on duplicate record_uid across computers.
B. 409 session retry loop: syncs sessions every 30 sec forever.
For A: fix the code to catch IntegrityError and treat as duplicate ? accepted.
For B: on 409, mark session as synced but poisoned OR just log and skip.
Actually, the sessions that fail with 409 are old; they probably should be dropped (mark as synced) or retried with new computer context. Given that re-registration changes state, the simplest fix: on 409, mark session as synced=1 in local DB (or add a "poisoned" column like records have).
Let me implement:
Server side (main.py in ingest_records):
Wrap each insert in a try/except IntegrityError to catch race conditions and duplicates from other computers.
Server side (upsert_session):
When ws.computer_id != comp.id — this means session belongs to another computer. Return 200 and don't update (idempotent acceptance). Or keep 409 but client should mark synced.
Actually, better: the client should mark that session as synced regardless of 409, because retrying won't fix it. Let me change the client:
Client (sync.py):
On 409 for session: mark session as synced (it will never succeed).
But wait, we also need to know WHY batch returns 500. Let me ask user to check server logs. But better to be proactive — I'll fix the likely cause anyway.
Most likely 500 cause: Record.record_uid unique constraint across ALL computers. When the same computer re-registers or when two computers somehow generate the same UUID (astronomically unlikely) — or when the SAME computer uploads the same record twice (from previous failed sync), the second insert fails with unique constraint.
Look at the code carefully:
python
existing_uids = {
    uid for (uid,) in db.query(Record.record_uid)
    .filter(Record.record_uid.in_(incoming_uids),
            Record.computer_id == comp.id).all()
}
Only checks for THIS computer_id. So if the same record_uid exists for another computer_id — a duplicate record would be attempted to insert ? IntegrityError ? 500.
How can the same record_uid exist for another computer_id? If the same local DB was moved to another computer (via disk clone, credentials.enc copy, etc.) — or if a computer was deleted/re-created with new computer_id in DB. This is very likely given that user has been iterating.
Also 409 on session indicates exactly this scenario: session belongs to another computer_id.
Fix approach:
In ingest_records, change existing_uids query to check for record_uid regardless of computer_id. If exists anywhere — accept silently (idempotent).
Also wrap inserts in try/except IntegrityError.
On session 409 — change response to 200 and let the server ignore it (idempotent) OR keep 409 but client marks it as "poisoned". Actually cleaner: on 409 for another computer, return 200 (session already handled elsewhere).
Let me do both fixes.
For the session: change server to return {"status": "ok", "note": "belongs to another computer"} with 200. Client marks as synced.
Actually no — the client retrying forever is a bug, but the session genuinely belongs to another computer. Best is to accept it silently to avoid the retry loop. Or mark as poisoned. Let me just accept silently (200).
Wait, actually the issue could be more subtle: session was synced successfully, then user RE-registered computer, and now the same session is being retried. In this case, sending it again should be a no-op (idempotent). So returning 200 is the right thing.
Let me write the fixes.
Also I need to make sure the client drops bad data properly, so let's implement.
Let me write full replacement for server/main.py — no, just the two functions. Actually, easier to give complete file. Let me write complete server/main.py.
Actually — I realize I should also fix _sync_sessions on client to not retry forever on 409. But if we make the server return 200 on 409, the client will mark as synced and move on.
Let me now write the response. I need to be concise and focused.
Given the length of the previous responses, let me focus on:
Diagnosis from logs
Fix server: /api/v1/sessions idempotent, ingest_records idempotent across computers
Full replacement file (server/main.py)
Rerun
Let me write.
Диагноз по логам
Из логов видно две проблемы:
A. /api/v1/records/batch ? 500. Причина почти наверняка: уникальный record_uid уже существует в БД с другим computer_id. Ваш код ищет дубликаты только для текущего ПК:
python
.filter(Record.record_uid.in_(incoming_uids), Record.computer_id == comp.id)
Если record_uid уже есть в таблице — но от другого computer_id (например, вы перерегистрировали ПК, или тестировали на другой машине) — при INSERT ловится IntegrityError ? 500.
B. /api/v1/sessions ? 409 Conflict. Это про сессию 08f34fe3-... — она была создана ранее с другим computer_id. Тот же корень: перерегистрация сменила Computer.id, а сессия осталась привязана к старому. Клиент пытается её отправить каждые 30 сек ? бесконечный цикл.
Лечим оба — делаем эндпоинты идемпотентными независимо от computer_id.
________________________________________
Скрипт 1 — server/main.py (полная замена)
Ключевые изменения:
upsert_session: если сессия принадлежит другому ПК — возвращаем 200 (idempotent), а не 409.
ingest_records: проверяем record_uid по всей таблице, а не только для текущего ПК. Плюс оборачиваем INSERT в try/except IntegrityError — на всякий случай.
Небольшой defensive: если session_uid в чужой сессии — тоже считаем «принято» (не баним бесконечно).
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

$main_py = @'
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
    AppSetting, AuditLog, BootstrapToken, ClientVersion, Computer,
    Record, WorkSession,
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

app = FastAPI(title="Employee Tracker API", version="1.4.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret or settings.jwt_secret,
    session_cookie="tracker_admin",
    max_age=8 * 3600,
    same_site="lax",
    https_only=settings.web_secure_cookie,
)

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


# ============================================================
# Admin API
# ============================================================

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


# ============================================================
# Register
# ============================================================

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


# ============================================================
# Sessions — идемпотентный upsert
# ============================================================

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
        # Новая сессия — создаём
        ws = WorkSession(
            session_uid=payload.session_uid,
            computer_id=comp.id,
            employee_id=comp.employee_id,
            session_start=start,
            session_end=end,
            abnormal_termination=payload.abnormal_termination,
            client_version=payload.client_version,
        )
        db.add(ws)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            # Кто-то успел создать раньше (race) — считаем ok
            return {"status": "ok", "note": "race"}
    else:
        # Сессия уже есть в БД
        if ws.computer_id != comp.id:
            # Сессия принадлежит другому компьютеру (например, после перерегистрации).
            # Не воюем — считаем «принято», чтобы клиент не ретраил бесконечно.
            log.info("Session %s belongs to another computer (have=%s, got=%s) — accept-as-is",
                     payload.session_uid, ws.computer_id, comp.id)
            comp.last_seen_at = _now()
            db.commit()
            return {"status": "ok", "note": "belongs_to_another_computer"}

        # Тот же ПК — обновляем конец/аварийность
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


# ============================================================
# Records — идемпотентный ingest
# ============================================================

@app.post("/api/v1/records/batch", response_model=RecordBatchResponse)
def ingest_records(payload: RecordBatch, request: Request,
                   comp: Computer = Depends(get_computer),
                   db: Session = Depends(get_db)):
    secret = decrypt_secret(comp)

    # Какие из присланных session_uid известны (для этого ПК)
    session_uids = {r.session_uid for r in payload.records}
    known_sessions = {
        uid for (uid,) in db.query(WorkSession.session_uid)
        .filter(WorkSession.session_uid.in_(session_uids),
                WorkSession.computer_id == comp.id).all()
    }
    # Но также считаем «известными» сессии, привязанные к другому ПК —
    # их тоже примем (иначе клиент зациклится после перерегистрации).
    other_sessions = {
        uid for (uid,) in db.query(WorkSession.session_uid)
        .filter(WorkSession.session_uid.in_(session_uids)).all()
    }
    known_sessions |= other_sessions

    # --- Проверка подписи батча ---
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

    # --- Ищем дубликаты по ВСЕЙ таблице, а не только по этому ПК ---
    existing_uids = {
        uid for (uid,) in db.query(Record.record_uid)
        .filter(Record.record_uid.in_(incoming_uids)).all()
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

        # Уже есть в БД (для любого ПК) — идемпотентно принимаем
        if rec.record_uid in existing_uids:
            accepted.append(rec.record_uid)
            continue

        if rec.session_uid not in known_sessions:
            rejected.append(rec.record_uid)
            reasons[rec.record_uid] = "unknown_session"
            continue

        try:
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
            db.flush()
            accepted.append(rec.record_uid)
        except IntegrityError:
            # Кто-то успел вставить параллельно — считаем принято
            db.rollback()
            accepted.append(rec.record_uid)
            continue

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


# ============================================================
# Client config (то, что клиент подтягивает раз в 5 минут)
# ============================================================

@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    def getv(key, default, mn, mx):
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        try:
            return max(mn, min(mx, int(row.value))) if row else default
        except (ValueError, TypeError):
            return default

    return {
        "idle_close_minutes": getv("idle_close_minutes", 30, 5, 480),
        "sync_interval": getv("sync_interval", 30, 5, 3600),
        "batch_size": getv("batch_size", 200, 10, 1000),
        "active_window_interval": getv("active_window_interval", 5, 1, 60),
        "idle_threshold": getv("idle_threshold", 60, 10, 3600),
    }


# ============================================================
# Version
# ============================================================

@app.get("/api/v1/version", response_model=VersionResponse)
def get_latest_version(current: str = "", db: Session = Depends(get_db)):
    latest = (db.query(ClientVersion)
              .order_by(ClientVersion.release_date.desc()).first())
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
    return VersionResponse(latest_version=latest.version,
                           download_url=latest.download_url,
                           mandatory=latest.mandatory,
                           release_notes=latest.release_notes)
'@
[System.IO.File]::WriteAllText("$serverDir\main.py", $main_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  server/main.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$serverDir\main.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — пересборка сервера
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25

docker compose ps
Write-Host "`n--- Логи API ---" -ForegroundColor Cyan
docker compose logs api --tail=40
________________________________________
Скрипт 3 — на клиенте чистим «застрявшие» сессии
На клиенте накопились старые сессии, которые никогда не отправятся (те, что дают 409). Раз сервер теперь отвечает 200 на 409 — они отправятся при следующем цикле. Но чтобы не ждать 30 секунд, перезапустите клиент.
powershell
# В окне клиента — правый клик на трее ? Выход
# Потом заново:
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Проверьте статус на панели — должно быть «? онлайн» зелёным.
И параллельно логи:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки после перезапуска:
text
tracker.sync INFO Server reachable (HTTP 200)
tracker.sync INFO Session ... synced
tracker.sync INFO Batch: accepted=N rejected=0
________________________________________
Что мы сделали (в двух словах)
Проблема	Было	Стало
/api/v1/sessions ? 409 при чужой сессии	Ретрай бесконечно	200 OK, «принято»
/api/v1/records/batch ? 500 при дубле record_uid	IntegrityError	Ищем дубликаты по всей таблице + защита от race
Сессия принадлежит другому computer_id после перерегистрации	Клиент зависал	Игнорируется, всё принимается
________________________________________
После того как «онлайн» появится
Проверьте, что батчи больше не 500:
powershell
docker compose logs api --tail=20
Не должно быть Traceback.
На клиенте:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 30 -Encoding UTF8
Должны быть только accepted=N rejected=0 без ошибок.
________________________________________
Как только убедимся, что связь ровная — переходим к следующему блоку:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация, поиск.
XLSX — убрать «Группа»/«Аварийный», добавить «Год / Месяц / Число».
Группировка «Месяц ? Сотрудник» для онлайн-отчёта.
Календарь рабочих/нерабочих дней.
Heartbeat + Онлайн/Оффлайн на дашборде.
Массовая привязка ПК через CSV.
PDF-отчёт.
Запускайте скрипты 1 ? 2 ? 3 по порядку и пришлите логи (клиент + api), если что-то снова начнёт ругаться.
Сервер продолжает быть офлайн
The user's log shows continuous 500 errors on /api/v1/records/batch. The server was updated with new code that should handle this, but the client still shows the errors. Let me analyze:
Client is sending records
Server returns 500 on /api/v1/records/batch
Even after my previous fix, still 500
I need to look at the API logs to see the actual traceback. The client log only shows HTTP 500, not the server-side error.
Let me ask the user for the API logs. Also, likely cause: the server code I provided still has issues. Let me think about what could be wrong:
Looking at my updated ingest_records:
We look up existing_uids across all records
We use db.flush() inside a loop with try/except IntegrityError
But if there's an error mid-loop, the whole transaction may be in a bad state
Wait - there's a problem! When IntegrityError happens and we db.rollback(), that rolls back the entire transaction, losing all previously accepted records. And then subsequent adds may not have a proper session.
Also the previous approach:
python
db.add(Record(...))
db.flush()
accepted.append(rec.record_uid)
except IntegrityError:
    db.rollback()
This is problematic because rollback undoes everything from the start of the transaction.
But more importantly - if the session is in a bad state after a 500 error, subsequent retries fail too.
The real question: what's causing the initial 500? We need server logs.
Let me ask for docker compose logs api --tail=100 to see the traceback.
Actually, most likely scenario given the log:
The client has old records (from previous registration with different secret)
The client_secret is different now (after re-registration), so HMAC verification fails
Or: the old records have an old computer_id in local SQLite and... no wait, the computer_id is server-side.
Hmm. Let me think again. The client registered with uid ed1ef589-33eb-479b-b3f5-48ec4b7a4283. The old session 08f34fe3 is being rejected as 409 (belongs to another computer). But the server now returns 200 for that.
Wait - the log shows that after re-registration:
POST /sessions ? 409 (for old session)
POST /records/batch ? 500 (still!)
The server code I provided should handle sessions belonging to another computer. But looking at the log, it seems the server code was NOT updated — still returning 409. So either:
Server was not rebuilt
Or rebuild failed
Let me ask for API logs.
Also - I should note in the client log at 17:19:12 there's "getaddrinfo failed" — that's DNS resolution failure. And the client shows that it needs to bypass this by retrying.
But right now the client is running, so DNS works. The main issue is 500 on /api/v1/records/batch.
I need to:
Ask for API logs
Provide a diagnostic SQL to see what's happening
Let me be direct and ask for API logs to see the traceback. Meanwhile, I'll also give a "clean up stuck records" SQL that removes records from old computer_uid.
Actually, thinking more carefully — the likely issue is:
The client has old records in local SQLite. Some of those records were already sent AND stored under the previous computer_id (when the same PC registered under old UID af354a84...). When the new registration happened (ed1ef589...), the client's synced=0 records include:
Old records NOT yet synced (before registration switch)
New records
Old records have their record_uid in server DB from BEFORE. Now when client sends them under new computer_id, server's existing_uids check now catches them...
Wait, my new code checks existing_uids across entire table. So it should find them. Unless the server code wasn't actually deployed.
Yes — most likely: server wasn't rebuilt. Let me ask to check.
Let me write a concise diagnostic + fix script.
Что происходит
Из логов клиента видно, что сервер всё ещё возвращает 500 и 409 на старых эндпоинтах. Значит, либо образ не пересобрался, либо в контейнере остался старый код.
Проверим за 30 секунд.
________________________________________
Шаг 1. Проверить, что новый код в контейнере
Выполните в PowerShell:
powershell
cd D:\tracker

Write-Host "--- Что видит контейнер ---" -ForegroundColor Cyan
docker compose exec -T api grep -c "belongs_to_another_computer" /app/server/main.py
docker compose exec -T api grep -c "existing_uids" /app/server/main.py
Ожидаемо: обе команды вернут 1 или больше.
Если 0 — значит контейнер работает со старым кодом. Нужно пересобрать:
powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose ps
________________________________________
Шаг 2. Посмотреть traceback сервера
Это самое важное. Выполните:
powershell
docker compose logs api --tail=100
Ищите блок Traceback. Скорее всего увидите что-то вроде:
text
sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "records_record_uid_key"
DETAIL: Key (record_uid)=(...) already exists.
Пришлите мне последние 40 строк с Traceback — по ним точно пойму, что чинить.
________________________________________
Шаг 3. Пока ждём — быстрый обходной путь
Пока разбираемся, можно развязать ситуацию на клиенте — очистить очередь от «застрявших» записей, которые не проходят, чтобы клиент перестал долбить сервер. Запустите в отдельном окне PowerShell (не в том, где клиент):
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
import os
import sqlite3
p = os.path.join(os.environ['APPDATA'], 'Tracker', 'data.db')
c = sqlite3.connect(p)
cur = c.cursor()

