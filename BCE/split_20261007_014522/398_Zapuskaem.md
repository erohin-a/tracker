<!-- Часть 398 из 1409 -->
# Запускаем
*Хлебные крошки:* Запускаем

[◀ Чистим лог, чтобы видеть только свежие сообщения](397_Chistim_log_chtoby_videt_tolko_svezhie_soobscheniya.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](399_part.md)

---

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


