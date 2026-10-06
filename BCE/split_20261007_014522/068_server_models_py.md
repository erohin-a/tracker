<!-- Часть 68 из 1409 -->
# `server/models.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/models.py`

[◀ `server/database.py`](067_server_database_py.md) | [Оглавление](00_BCE_INDEX.md) | [`server/security.py` ▶](069_server_security_py.md)

---

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

