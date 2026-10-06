<!-- Часть 67 из 1409 -->
# `server/database.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/database.py`

[◀ `server/config.py`](066_server_config_py.md) | [Оглавление](00_BCE_INDEX.md) | [`server/models.py` ▶](068_server_models_py.md)

---

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

