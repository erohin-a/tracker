<!-- Часть 69 из 1409 -->
# `server/security.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/security.py`

[◀ `server/models.py`](068_server_models_py.md) | [Оглавление](00_BCE_INDEX.md) | [`server/schemas.py` ▶](070_server_schemas_py.md)

---

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

