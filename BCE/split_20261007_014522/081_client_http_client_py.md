<!-- Часть 81 из 1409 -->
# `client/http_client.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/http_client.py`

[◀ `client/db.py`](080_client_db_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/registration.py` ▶](082_client_registration_py.md)

---

### `client/http_client.py`

```python
import hashlib
import logging
import os
import threading
from typing import Optional

import httpx

from .config import PINNED_CERT_SHA256, SSL_CA_BUNDLE

log = logging.getLogger("tracker.http")


def _pinning_enabled() -> bool:
    if not PINNED_CERT_SHA256 or set(PINNED_CERT_SHA256) == {"0"}:
        return False
    if len(PINNED_CERT_SHA256) != 64:
        log.error("PIN length %d != 64, pinning disabled", len(PINNED_CERT_SHA256))
        return False
    try:
        int(PINNED_CERT_SHA256, 16)
    except ValueError:
        log.error("PIN not hex, pinning disabled")
        return False
    return True


def _resolve_verify():
    """Возвращает True/False или путь к CA bundle."""
    v = os.environ.get("TRACKER_INSECURE", "").strip().lower()
    if v in ("1", "true", "yes"):
        log.warning("SSL verification DISABLED (TRACKER_INSECURE=1) — только для dev!")
        return False
    if SSL_CA_BUNDLE and os.path.exists(SSL_CA_BUNDLE):
        log.info("Using CA bundle: %s", SSL_CA_BUNDLE)
        return SSL_CA_BUNDLE
    return True


class PinningTransport(httpx.HTTPTransport):
    def __init__(self, pinned_sha256: str, **kwargs):
        super().__init__(**kwargs)
        self._pinned = pinned_sha256.lower()
        self._verified_fps: set[str] = set()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        response = super().handle_request(request)
        if request.url.scheme != "https":
            return response

        stream = response.extensions.get("network_stream")
        if stream is None:
            raise httpx.ConnectError("pinning: no network_stream")
        ssl_obj = stream.get_extra_info("ssl_object")
        if ssl_obj is None:
            try:
                stream.close()
            except Exception:
                pass
            raise httpx.ConnectError("pinning: no ssl_object")

        der = ssl_obj.getpeercert(binary_form=True)
        if der is None:
            try:
                stream.close()
            except Exception:
                pass
            raise httpx.ConnectError("pinning: peer cert missing")
        fp = hashlib.sha256(der).hexdigest().lower()
        if fp in self._verified_fps:
            return response
        if fp != self._pinned:
            try:
                stream.close()
            except Exception:
                pass
            raise httpx.ConnectError(
                f"pinning failed: expected {self._pinned[:16]}..., got {fp[:16]}..."
            )
        self._verified_fps.add(fp)
        return response


_client_lock = threading.Lock()
_client: Optional[httpx.Client] = None


def _build_client() -> httpx.Client:
    verify = _resolve_verify()
    if _pinning_enabled():
        log.info("Pinning ENABLED (%s...)", PINNED_CERT_SHA256[:16])
        transport = PinningTransport(
            pinned_sha256=PINNED_CERT_SHA256, verify=verify, retries=2,
        )
    else:
        log.warning("Pinning DISABLED")
        transport = httpx.HTTPTransport(verify=verify, retries=2)
    return httpx.Client(
        transport=transport,
        timeout=httpx.Timeout(20.0, connect=10.0),
        headers={"User-Agent": "Tracker/1.2"},
    )


def get_client() -> httpx.Client:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = _build_client()
    return _client


def close_client():
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
            _client = None


def get(url, **kw):
    return get_client().get(url, **kw)


def post(url, **kw):
    return get_client().post(url, **kw)
```

