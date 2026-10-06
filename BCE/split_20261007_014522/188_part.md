<!-- Часть 188 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ config.py](187_config_py.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](189_part.md)

---

# ============================================================
$config_py = @'
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

_PLACEHOLDERS = {"", "CHANGE_ME", "CHANGE_ME_JWT", "CHANGE_ME_32_BYTE_BASE64_KEY"}


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tracker:tracker@db:5432/tracker"
    secret_encryption_key: str = ""
    jwt_secret: str = ""
    admin_api_key: str = ""

    # --- Веб-интерфейс администратора ---
    admin_login: str = "admin"
    session_secret: str = ""
    web_secure_cookie: bool = False

    # --- Отчёты ---
    report_timezone: str = "Europe/Moscow"

    class Config:
        env_file = ".env"


settings = Settings()


def _fail(name: str, hint: str):
    raise RuntimeError(f"{name} не задан или placeholder.\n{hint}")


if settings.secret_encryption_key in _PLACEHOLDERS:
    _fail(
        "SECRET_ENCRYPTION_KEY",
        'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"',
    )

if settings.jwt_secret in _PLACEHOLDERS:
    _fail(
        "JWT_SECRET",
        'python -c "import secrets; print(secrets.token_urlsafe(48))"',
    )

if settings.admin_api_key in _PLACEHOLDERS:
    _fail(
        "ADMIN_API_KEY",
        'python -c "import secrets; print(secrets.token_urlsafe(48))"',
    )

try:
    FERNET = Fernet(settings.secret_encryption_key.encode())
except Exception as e:
    raise RuntimeError(f"SECRET_ENCRYPTION_KEY некорректен: {e}") from e
'@
[System.IO.File]::WriteAllText("$serverDir\config.py", $config_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  config.py" -ForegroundColor Green

