<!-- Часть 78 из 1409 -->
# `client/config.py`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/config.py`

[◀ `client/.env`](077_client_env.md) | [Оглавление](00_BCE_INDEX.md) | [`client/crypto.py` ▶](079_client_crypto_py.md)

---

### `client/config.py`

```python
import logging as _logging
import os
from pathlib import Path

_log = _logging.getLogger("tracker.config")

try:
    from dotenv import load_dotenv
    _candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent / ".env",
        Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
    ]
    _loaded_from = None
    for p in _candidates:
        if p.exists():
            load_dotenv(p, override=True)
            _loaded_from = p
            break
    if _loaded_from:
        _log.info("Loaded .env from %s", _loaded_from)
    else:
        _log.warning(".env not found in %s", [str(p) for p in _candidates])
except ImportError:
    _log.error("python-dotenv not installed; .env will NOT be read")


APP_NAME = "Tracker"
CLIENT_VERSION = os.environ.get("TRACKER_VERSION", "1.0.0")

if os.name == "nt":
    BASE_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    BASE_DIR = Path.home() / f".{APP_NAME.lower()}"
BASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "data.db"
LOG_PATH = BASE_DIR / "client.log"
DOWNLOAD_DIR = BASE_DIR / "updates"
DOWNLOAD_DIR.mkdir(exist_ok=True)

SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://tracker.example.com")
SSL_CA_BUNDLE = os.environ.get("TRACKER_CA_BUNDLE", str(BASE_DIR / "ca.pem"))
PINNED_CERT_SHA256 = os.environ.get("TRACKER_PIN", "").strip().lower()

SYNC_INTERVAL = 30
ACTIVE_WINDOW_INTERVAL = 5
IDLE_THRESHOLD = 60
MAX_DB_SIZE_MB = 500
BATCH_SIZE = 200
COLLECT_KEYSTROKE_CHARS = False
```

