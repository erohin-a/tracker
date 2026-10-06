<!-- Часть 66 из 1409 -->
# `server/config.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/config.py`

[◀ `server/requirements.txt`](065_server_requirements_txt.md) | [Оглавление](00_BCE_INDEX.md) | [`server/database.py` ▶](067_server_database_py.md)

---

### `server/config.py`

```python
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

_PLACEHOLDERS = {"", "CHANGE_ME", "CHANGE_ME_JWT", "CHANGE_ME_32_BYTE_BASE64_KEY"}


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tracker:tracker@db:5432/tracker"
    secret_encryption_key: str = ""
    jwt_secret: str = ""
    admin_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()


def _fail(name: str, hint: str):
    raise RuntimeError(f"{name} не задан или placeholder.\n{hint}")


if settings.secret_encryption_key in _PLACEHOLDERS:
    _fail("SECRET_ENCRYPTION_KEY",
          'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
if settings.jwt_secret in _PLACEHOLDERS:
    _fail("JWT_SECRET",
          'python -c "import secrets; print(secrets.token_urlsafe(48))"')
if settings.admin_api_key in _PLACEHOLDERS:
    _fail("ADMIN_API_KEY",
          'python -c "import secrets; print(secrets.token_urlsafe(48))"')

try:
    FERNET = Fernet(settings.secret_encryption_key.encode())
except Exception as e:
    raise RuntimeError(f"SECRET_ENCRYPTION_KEY некорректен: {e}") from e
```

