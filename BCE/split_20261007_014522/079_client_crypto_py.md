<!-- Часть 79 из 1409 -->
# `client/crypto.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/crypto.py`

[◀ `client/config.py`](078_client_config_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/db.py` ▶](080_client_db_py.md)

---

### `client/crypto.py`

```python
import hmac
import hashlib
import json
import math
from typing import Any
import keyring

SERVICE = "tracker"


def _validate(obj: Any) -> Any:
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("NaN/Infinity not allowed")
        return obj
    if isinstance(obj, dict):
        return {str(k): _validate(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_validate(v) for v in obj]
    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    raise ValueError(f"unsupported type: {type(obj).__name__}")


def canonical_json(obj: Any) -> bytes:
    return json.dumps(
        _validate(obj),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def get_client_secret() -> str:
    from .registration import _safe_keyring_get
    secret = _safe_keyring_get("client_secret")
    if not secret:
        raise RuntimeError("client_secret not found; register first")
    return secret


def sign_payload(payload: dict) -> str:
    secret = get_client_secret()
    return hmac.new(
        secret.encode("utf-8"),
        canonical_json(payload),
        hashlib.sha256,
    ).hexdigest()


def verify_payload(signature: str, payload: dict) -> bool:
    try:
        expected = sign_payload(payload)
    except Exception:
        return False
    return hmac.compare_digest(expected, signature)
```

