<!-- Часть 70 из 1409 -->
# `server/schemas.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/schemas.py`

[◀ `server/security.py`](069_server_security_py.md) | [Оглавление](00_BCE_INDEX.md) | [`server/main.py` ▶](071_server_main_py.md)

---

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

