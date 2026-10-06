<!-- Часть 84 из 1409 -->
# `client/sync.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/sync.py`

[◀ `client/collector.py`](083_client_collector_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/updater.py` ▶](085_client_updater_py.md)

---

### `client/sync.py`

```python
import json
import logging
import time

from PyQt6.QtCore import QObject, pyqtSignal
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

from . import crypto, db, http_client
from .config import BATCH_SIZE, SERVER_URL, SYNC_INTERVAL
from .registration import get_computer_uid

log = logging.getLogger("tracker.sync")


class SyncWorker(QObject):
    synced = pyqtSignal(int)
    error = pyqtSignal(str)
    server_down = pyqtSignal()
    auth_failed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            try:
                if not self._sync_sessions():
                    break
                if not self._sync_records():
                    break
                db.enforce_size_limit()
            except Exception as e:
                log.warning("sync failed: %s", e)
                self.server_down.emit()
            end = time.time() + SYNC_INTERVAL
            while self._running and time.time() < end:
                time.sleep(0.5)

    def stop(self):
        self._running = False

    def _headers(self):
        return {"X-Computer-Uid": get_computer_uid() or ""}

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((http_client.httpx.HTTPError,)),
           reraise=True)
    def _post(self, url, **kw):
        resp = http_client.post(url, **kw)
        if 500 <= resp.status_code < 600:
            raise http_client.httpx.HTTPStatusError(
                f"{resp.status_code}", request=resp.request, response=resp)
        return resp

    def _sync_sessions(self) -> bool:
        for r in db.fetch_unsynced_sessions():
            payload = {
                "session_uid": r["session_uid"],
                "session_start": r["session_start"],
                "session_end": r["session_end"],
                "abnormal_termination": bool(r["abnormal_termination"]),
            }
            resp = self._post(f"{SERVER_URL}/api/v1/sessions",
                              json=payload, headers=self._headers())
            if resp.status_code in (401, 403):
                self.auth_failed.emit()
                self._running = False
                return False
            if resp.status_code == 200:
                db.mark_session_synced(r["session_uid"])
            else:
                log.warning("session %s ? %d", r["session_uid"], resp.status_code)
        return True

    def _sync_records(self) -> bool:
        batch = db.fetch_unsynced(limit=BATCH_SIZE)
        if not batch:
            return True

        records = [{
            "record_uid": r["record_uid"], "session_uid": r["session_uid"],
            "kind": r["kind"], "data": json.loads(r["data"]),
            "client_ts": r["client_ts"], "signature": r["signature"],
        } for r in batch]

        batch_sig = crypto.sign_payload({"records": records})
        resp = self._post(
            f"{SERVER_URL}/api/v1/records/batch",
            json={"records": records, "batch_signature": batch_sig},
            headers=self._headers())

        if resp.status_code in (401, 403):
            self.auth_failed.emit()
            self._running = False
            return False

        resp.raise_for_status()
        body = resp.json()

        server_sig = body.pop("server_signature", None)
        if not server_sig or not crypto.verify_payload(server_sig, body):
            log.error("Server signature invalid — возможен MITM")
            self.error.emit("server signature invalid")
            return False

        accepted = body.get("accepted_uuids", [])
        rejected = body.get("rejected_uuids", [])
        reasons = body.get("reasons", {})
        permanent = [u for u in rejected if reasons.get(u) == "bad_signature"]
        temporary = [u for u in rejected if u not in permanent]

        db.apply_sync_result(accepted, permanent)
        if temporary:
            log.info("temporary rejects (retry): %d", len(temporary))
        if permanent:
            log.warning("permanent rejects: %d %s", len(permanent), reasons)

        self.synced.emit(len(accepted))
        return True
```

