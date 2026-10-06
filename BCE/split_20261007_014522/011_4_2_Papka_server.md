<!-- Часть 11 из 1409 -->
# 4.2. Папка `server/`
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 4. Полный список файлов с описанием / 4.2. Папка `server/`

[◀ 4.1. Корень проекта](010_4_1_Koren_proekta.md) | [Оглавление](00_BCE_INDEX.md) | [4.3. Папка `client/` ▶](012_4_3_Papka_client.md)

---

### 4.2. Папка `server/`

#### `server/__init__.py`
Пустой. Делает `server` Python-пакетом — **обязателен** для gunicorn (`server.main:app`).

#### `server/requirements.txt`
Зависимости: fastapi, uvicorn, gunicorn, sqlalchemy, psycopg2-binary, pydantic, pydantic-settings, cryptography, python-multipart.

#### `server/config.py`
Загружает `.env`, проверяет секреты, инициализирует Fernet.
**Ключевая логика:** если `SECRET_ENCRYPTION_KEY`, `JWT_SECRET` или `ADMIN_API_KEY` пусты или равны `CHANGE_ME` — падает с понятной ошибкой.

#### `server/database.py`
SQLAlchemy engine + `SessionLocal` + `init_db()` (вызывает `create_all`).

#### `server/models.py`
ORM-модели:
- `Computer` — зарегистрированные ПК (`computer_uid`, `client_secret_enc`, `secret_version`, `is_active`).
- `Employee` — сотрудники (в текущей версии не заполняется).
- `WorkSession` — сессии (`session_start`, `session_end`, `abnormal_termination`).
- `Record` — записи активности (`record_uid`, `session_uid`, `kind`, `data`, `signature`, `client_ip`).
- `BootstrapToken` — одноразовые токены для регистрации.
- `ClientVersion` — реестр версий клиента (для авто-обновления).
- `AuditLog` — журнал аудита.

**Важно:** все timestamps — `DateTime(timezone=True)`, чтобы не смешивать naive/aware.

#### `server/schemas.py`
Pydantic-схемы запросов и ответов.
**Ключевые валидаторы:**
- `client_ts` — обязана быть **timezone-aware** строкой ISO-8601.
- `RecordBatch.records` — **max_length=500** (защита от DoS).
- `RecordBatchResponse` содержит `server_signature` — подпись ответа сервера.

#### `server/security.py`
HMAC-подпись: `canonical_json` (сортировка ключей, без пробелов, `ensure_ascii=False`, `allow_nan=False`), `compute_signature`, `verify_signature`.
**Особенность:** рекурсивно отклоняет NaN/Inf, чтобы клиент и сервер считали одинаковую строку.

#### `server/main.py`
FastAPI-приложение. **Основные эндпоинты:**

| Метод | Путь | Что делает |
|---|---|---|
| POST | `/api/v1/admin/bootstrap-tokens` | Выдаёт одноразовый токен (нужен `X-Admin-Token`) |
| POST | `/api/v1/admin/computers/{uid}/revoke` | Отключает ПК |
| POST | `/api/v1/computers/register` | Регистрирует ПК по bootstrap-токену |
| POST | `/api/v1/sessions` | Создаёт/закрывает сессию |
| POST | `/api/v1/records/batch` | Принимает пачку записей с проверкой HMAC |
| GET | `/api/v1/version` | Возвращает последнюю версию клиента |

**Особенности реализации:**
- Bootstrap-токен «сжигается» **атомарно** через `UPDATE ... RETURNING` — защита от гонки.
- Идемпотентность записей — только в рамках одного `computer_id`.
- Подпись записи проверяется **до** проверки идемпотентности.
- Ответ подписывается тем же `client_secret` — защита от MITM.

#### `server/Dockerfile`
**Ключевое:**
- `COPY server/ ./server/` — копирует папку целиком.
- `RUN touch /app/server/__init__.py`.
- `CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "server.main:app"]`.

#### `server/nginx.conf`
Reverse-proxy. **Ключевое:**
- Слушает **только 443** (IPv4 + IPv6).
- `proxy_pass http://api:8000`.
- HSTS, `client_max_body_size 10m`.

