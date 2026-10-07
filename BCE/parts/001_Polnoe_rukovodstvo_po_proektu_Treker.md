# Полное руководство по проекту «Трекер»

*Часть 1 из 100. Источник: `BCE.md`.*

◀ — | [Оглавление](00_BCE_INDEX.md) | [?? Папка `server/` ▶](002_Papka_server.md)

---

# Полное руководство по проекту «Трекер»

**Версия документа:** 1.0
**Дата:** 16.09.2026
**Назначение:** руководство для разработчиков, администраторов и специалистов поддержки системы учёта рабочего времени.

---

## Содержание

1. [Что это за проект](#1-что-это-за-проект)
2. [Архитектура системы](#2-архитектура-системы)
3. [Структура файлов](#3-структура-файлов)
4. [Полный список файлов с описанием](#4-полный-список-файлов-с-описанием)
5. [Пошаговая установка с нуля](#5-пошаговая-установка-с-нуля)
6. [Ежедневная работа](#6-ежедневная-работа)
7. [Проблемы, которые мы преодолели](#7-проблемы-которые-мы-преодолели)
8. [Что не реализовано](#8-что-не-реализовано)
9. [Диагностика и логи](#9-диагностика-и-логи)
10. [Что делать при типовых сбоях](#10-что-делать-при-типовых-сбоях)
11. [Безопасность и ротация секретов](#11-безопасность-и-ротация-секретов)
12. [Ограничения и предупреждения](#12-ограничения-и-предупреждения)

---

## 1. Что это за проект

**Tracker** — система учёта рабочего времени сотрудников. Состоит из **серверной** и **клиентской** частей.

### Что делает система

- **Клиент** устанавливается на ПК сотрудника, работает в фоне и собирает:
  - активность клавиатуры (только счётчик нажатий, без самих символов);
  - активность мыши (клики, скролл);
  - активное окно (имя приложения и заголовок);
  - периоды простоя (idle).
- **Клиент** отправляет данные на **сервер** по HTTPS с HMAC-подписью каждой записи.
- **Сервер** проверяет подписи, сохраняет данные в PostgreSQL, ведёт журнал аудита.
- **Администратор** может просматривать данные (пока только через SQL-запросы).

### Ключевые особенности

- **Офлайн-режим:** если сервер недоступен, клиент копит данные в локальной SQLite и отправит, когда связь появится.
- **Защита от подмены:** каждая запись подписана HMAC-SHA256 с секретом, выданным при регистрации.
- **Bootstrap-токены:** регистрация нового ПК возможна только по одноразовому токену, выданному администратором.
- **Certificate Pinning (опционально):** клиент может проверять конкретный отпечаток TLS-сертификата сервера, защищаясь от MITM.
- **Обработка аварийного завершения:** если клиент упал, при следующем запуске сессия корректно закрывается.

---

## 2. Архитектура системы

```
???????????????????????????????????????????????????????????????????
?                          WINDOWS HOST                            ?
?                                                                  ?
?   ????????????????????          ???????????????????????????????  ?
?   ?  КЛИЕНТ (PyQt6)  ?          ?   DOCKER COMPOSE            ?  ?
?   ?                  ?          ?                             ?  ?
?   ?  - collector     ?  HTTPS   ?  ?????????????????????????  ?  ?
?   ?  - sync worker   ? ???????? ?  ?  nginx (443)          ?  ?  ?
?   ?  - local SQLite  ?          ?  ?????????????????????????  ?  ?
?   ?  - tray icon     ?          ?             ?               ?  ?
?   ????????????????????          ?  ?????????????????????????  ?  ?
?                                 ?  ?  API (FastAPI)        ?  ?  ?
?                                 ?  ?  gunicorn + uvicorn   ?  ?  ?
?                                 ?  ?????????????????????????  ?  ?
?                                 ?             ?               ?  ?
?                                 ?  ?????????????????????????  ?  ?
?                                 ?  ?  PostgreSQL           ?  ?  ?
?                                 ?  ?????????????????????????  ?  ?
?                                 ???????????????????????????????  ?
???????????????????????????????????????????????????????????????????
```

### Поток данных

1. Клиент собирает событие (нажатие, окно, idle).
2. Создаёт запись `{record_uid, session_uid, kind, data, client_ts}`.
3. Считает HMAC-SHA256 от канонической JSON-строки с секретом `client_secret`.
4. Пишет запись в локальный SQLite.
5. `SyncWorker` каждые 30 секунд берёт пачку неотправленных записей, добавляет общую подпись батча и шлёт POST `/api/v1/records/batch`.
6. Сервер проверяет подпись батча, потом каждой записи, сохраняет в PostgreSQL.
7. Сервер отвечает списком принятых и отклонённых UUID.
8. Клиент помечает принятые как `synced=1`, отклонённые — как `poisoned=1` (при `bad_signature`) или оставляет на повтор (при `unknown_session`).

---

## 3. Структура файлов

```
D:\tracker\
?
??? .env                              ? секреты сервера (не в git!)
??? docker-compose.yml                ? оркестрация контейнеров
??? certs\                            ? TLS-сертификаты
?   ??? fullchain.pem
?   ??? privkey.pem
?
??? server\                           ? серверная часть
?   ??? __init__.py
?   ??? config.py
?   ??? database.py
?   ??? models.py
?   ??? schemas.py
?   ??? security.py
?   ??? main.py
?   ??? Dockerfile
?   ??? requirements.txt
?   ??? nginx.conf
?
??? client\                           ? клиентская часть
    ??? .env                          ? настройки клиента
    ??? .venv\                        ? виртуальное окружение Python
    ??? __init__.py
    ??? config.py
    ??? crypto.py
    ??? db.py
    ??? http_client.py
    ??? registration.py
    ??? collector.py
    ??? sync.py
    ??? updater.py
    ??? main.py
    ??? build.spec
    ??? version_info.txt
    ??? requirements.txt
    ??? icon.ico                      ? опционально
```

Дополнительные файлы, создаваемые **во время работы**:

```
%APPDATA%\Tracker\                    ? данные клиента на ПК сотрудника
??? data.db                           ? локальная SQLite
??? data.db-wal                       ? WAL-журнал SQLite
??? data.db-shm                       ? shared memory SQLite
??? client.log                        ? лог клиента
??? bootstrap.txt                     ? одноразовый токен регистрации (удаляется после успеха)
??? ca.pem                            ? копия сертификата сервера для проверки
??? credentials.enc                   ? fallback-хранилище секретов, если keyring не работает
```

---

## 4. Полный список файлов с описанием

### 4.1. Корень проекта

#### `docker-compose.yml`
**Назначение:** описывает три контейнера — `db`, `api`, `nginx`.
**Что важно знать:**
- `db` — PostgreSQL 16, healthcheck `pg_isready`, volume `pgdata`.
- `api` — сборка из `server/Dockerfile` с **build context = корень проекта** (а не `./server`, иначе пакет `server` не найдётся).
- `nginx` — проброшен только **порт 443** (порт 80 занят Windows `HTTP.sys`). Certificates монтируются из `./certs`.

#### `.env`
**Назначение:** секреты сервера.
**Содержимое:**
```
SECRET_ENCRYPTION_KEY=<44-символьный Fernet-ключ>
JWT_SECRET=<случайный токен>
ADMIN_API_KEY=<случайный токен>
```
**Важно:** файл должен быть в **UTF-8 без BOM**, **без пробелов** вокруг `=`. В `.gitignore`.

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

### 4.3. Папка `client/`

#### `client/requirements.txt`
PyQt6, httpx, pynput, keyring, psutil, python-dotenv, tenacity, cryptography, pywin32 (только на Windows).

#### `client/.env`
Настройки клиента:
```
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
```
**Опционально:** `TRACKER_INSECURE=1` — отключает проверку SSL (только dev).
**Опционально:** `TRACKER_CA_BUNDLE=путь` — путь к CA-сертификату.

#### `client/config.py`
Читает `.env` через `python-dotenv` (включая `override=True`). Определяет пути, интервалы, константы.

#### `client/crypto.py`
- `canonical_json` — **точно такая же**, как на сервере.
- `sign_payload` — HMAC-SHA256 с `client_secret` из keyring.
- `verify_payload` — проверка подписи от сервера.

#### `client/db.py`
Локальная SQLite. **Особенности:**
- WAL-режим, `busy_timeout=5000`, `journal_size_limit=64MB`.
- Отдельное соединение **на поток** (`threading.local`).
- `init_db` проверяет целостность, при повреждении — карантин.
- Миграция `_migrate` добавляет колонку `poisoned` в старые БД.
- `enforce_size_limit` удаляет синхронизированные записи при превышении 500 МБ.

#### `client/http_client.py`
`httpx.Client` с:
- `PinningTransport` — опциональная проверка отпечатка TLS-сертификата.
- Поддержка `TRACKER_INSECURE` (пропуск проверки SSL).
- Поддержка `TRACKER_CA_BUNDLE` (свой CA).

#### `client/registration.py`
- Хранит `computer_uid` и `client_secret` в **keyring**, fallback — в `credentials.enc` (Fernet/DPAPI).
- `ensure_registered()` — регистрирует ПК, если ещё не зарегистрирован.
- Читает bootstrap-токен из `%APPDATA%\Tracker\bootstrap.txt` или env.
- После успеха **удаляет bootstrap.txt**.

#### `client/collector.py`
`CollectorWorker(QObject)` в отдельном `QThread`:
- Слушает клавиатуру и мышь через `pynput`.
- Опрашивает активное окно каждые 5 секунд (`_get_active_window`).
- **Edge-triggered:** пишет `window` только при смене `(app, title)`.
- **Idle:** пишет `idle` один раз при переходе и `idle_end` при возврате (порог 60 сек).
- **Thread-safe:** счётчики под `threading.Lock`.
- **Wayland-детект:** по `XDG_SESSION_TYPE=wayland`.

#### `client/sync.py`
`SyncWorker(QObject)` в отдельном `QThread`:
- Каждые 30 секунд берёт непереданные записи и сессии.
- Отправляет сессии по одной, записи — пачкой (до 200).
- Проверяет подпись ответа сервера.
- **Различает** `bad_signature` (перманентно, в poisoned) и `unknown_session` (временно, повторить позже).
- Retry с exponential backoff при 5xx.
- При 401/403 — сигнал `auth_failed`, остановка sync.

#### `client/updater.py`
- `UpdateChecker` — в отдельном `QThread` проверяет `/api/v1/version` и (опционально) скачивает обновление.
- `apply_update` — запускает установщик, корректно выходит через `QApplication.quit()`.

#### `client/main.py`
**Точка входа.**
- Создаёт `QApplication`, `MainWindow`.
- Иконка в трее, скрытие окна вместо закрытия.
- Сигналы SIGTERM/SIGINT через `signal.set_wakeup_fd` + `QSocketNotifier`.
- `_start()` — регистрация, БД, запуск потоков.
- `_shutdown_workers()` — корректная остановка `CollectorWorker` и `SyncWorker` (с `QThread.quit()`).

#### `client/build.spec`
PyInstaller. **Ключевое:**
- `upx=False` (снижает ложные срабатывания антивирусов).
- `--onedir` (не `--onefile`).
- `hiddenimports` для `pynput`, `keyring`, `cryptography`.

#### `client/version_info.txt`
Метаданные PE-файла (компания, версия, copyright).

---

## 5. Пошаговая установка с нуля

### Предварительно установить

- **Python 3.11** или 3.12 (не 3.14 — PyQt6 может не работать).
- **Docker Desktop**.
- **Git**.
- **OpenSSL** (`winget install ShiningLight.OpenSSL.Light`).

### Шаг 1. Клонировать структуру

Создать папку `D:\tracker` и все подпапки согласно разделу 3. Скопировать файлы.

### Шаг 2. Создать `.env` в корне

```powershell
python -c "from cryptography.fernet import Fernet; print('SECRET_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(48))"
python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(48))"
```

Записать три строки в `D:\tracker\.env` через `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` — **без BOM**.

### Шаг 3. Создать сертификаты

```powershell
cd D:\tracker\certs
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -x509 -newkey rsa:4096 `
    -keyout privkey.pem -out fullchain.pem -days 365 -nodes `
    -subj "/CN=localhost" `
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" `
    -addext "basicConstraints=critical,CA:TRUE"
```

### Шаг 4. Запустить сервер

```powershell
cd D:\tracker
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose ps
```

Все три контейнера должны быть `Up`.

### Шаг 5. Проверить API

```powershell
curl.exe -k https://localhost/api/v1/version
```

Должен вернуться JSON.

### Шаг 6. Установить клиент

```powershell
cd D:\tracker\client
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Шаг 7. Настроить клиент

Скопировать CA-сертификат:
```powershell
Copy-Item D:\tracker\certs\fullchain.pem "$env:APPDATA\Tracker\ca.pem"
```

Создать `client\.env`:
```
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
```

### Шаг 8. Получить bootstrap-токен

```powershell
$adminKey = "ВАШ_ADMIN_API_KEY_ИЗ_ENV"
$bodyObj = @{ ttl_hours = 24; issued_by = "admin" }
$bodyJson = $bodyObj | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText("$env:TEMP\boot.json", $bodyJson, [System.Text.UTF8Encoding]::new($false))

curl.exe -k -X POST "https://localhost/api/v1/admin/bootstrap-tokens" `
    -H "X-Admin-Token: $adminKey" `
    -H "Content-Type: application/json" `
    --data-binary "@$env:TEMP\boot.json"
```

Из ответа `{"token":"...","expires_in_hours":24}` скопировать **только значение** токена и сохранить:
```powershell
[System.IO.File]::WriteAllText("$env:APPDATA\Tracker\bootstrap.txt", "ТОКЕН", [System.Text.UTF8Encoding]::new($false))
```

### Шаг 9. Запустить клиент

```powershell
cd D:\tracker
python -m client.main
```

Через 3-5 секунд — иконка в трее, через 30 секунд — первая синхронизация.

---

## 6. Ежедневная работа

### Запуск сервера

```powershell
cd D:\tracker
docker compose up -d
```

### Остановка сервера

```powershell
docker compose down
```

### Запуск клиента вручную

```powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
```

### Автозапуск клиента (Windows)

```powershell
$startup = [Environment]::GetFolderPath("Startup")
$bat = "@echo off`r`ncd /d D:\tracker`r`nclient\.venv\Scripts\pythonw.exe -m client.main"
[System.IO.File]::WriteAllText("$startup\Tracker.bat", $bat, [System.Text.UTF8Encoding]::new($false))
```

### Просмотр данных (SQL)

```powershell
# Количество записей
docker compose exec db psql -U tracker -d tracker -c "SELECT count(*) FROM records;"

# Список ПК
docker compose exec db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at FROM computers;"

# Сессии за сегодня
docker compose exec db psql -U tracker -d tracker -c "SELECT c.hostname, ws.session_start, ws.session_end FROM work_sessions ws JOIN computers c ON c.id = ws.computer_id WHERE ws.session_start >= CURRENT_DATE;"

# Активность за час
docker compose exec db psql -U tracker -d tracker -c "SELECT DATE_TRUNC('hour', client_ts) AS hour, SUM((data::json->>'keys')::int) FROM records WHERE kind='activity' AND client_ts >= NOW() - INTERVAL '24 hours' GROUP BY 1 ORDER BY 1;"
```

---

## 7. Проблемы, которые мы преодолели

| # | Симптом | Причина | Решение |
|---|---|---|---|
| 1 | `curl -k` в PowerShell не работает | `curl` — алиас `Invoke-WebRequest` | Использовать `curl.exe` |
| 2 | `ModuleNotFoundError: No module named 'server'` | `build: ./server` дал неверный build context | `build: { context: ., dockerfile: server/Dockerfile }` |
| 3 | Порт 80 занят Windows (`HTTP.sys`, PID 4) | IIS / WinRM / BranchCache | Убрать блок `listen 80`, оставить только 443 |
| 4 | `unknown directive "CN=localhost"` | Мусор от openssl-команды в `nginx.conf` | Перезаписать `nginx.conf` через here-string |
| 5 | `ModuleNotFoundError: PyQt6` | venv не активирован | `.venv\Scripts\Activate.ps1` |
| 6 | `ModuleNotFoundError: client` | Запуск из `client/`, а не из `tracker/` | `cd D:\tracker; python -m client.main` |
| 7 | `SyntaxError: def _validate(obj Any)` | Пропали `:` и `->` при копипасте | Перезаписать `crypto.py` через here-string |
| 8 | `NameError: name 'Path' is not defined` | Пропала строка `from pathlib import Path` | Перезаписать `config.py` через here-string |
| 9 | `.env` не читается | `python-dotenv` не установлен или `Path` не определён | `pip install python-dotenv` + починить `config.py` |
| 10 | `SSL: CERTIFICATE_VERIFY_FAILED: self-signed` | Python не доверяет самоподписанному сертификату | Добавить CA в `%APPDATA%\Tracker\ca.pem` + `TRACKER_CA_BUNDLE` |
| 11 | `Hostname mismatch: certificate is not valid for 'localhost'` | Сертификат без SAN | Перевыпустить с `-addext "subjectAltName=DNS:localhost,IP:127.0.0.1"` |
| 12 | `401 Unauthorized` на `/register` | Bootstrap-токен сгорел / не выпущен / неверный | Выпустить новый через `/admin/bootstrap-tokens`, сохранить **только значение** `token` |
| 13 | `Invalid or expired bootstrap token` | Токен использован | Проверить в БД, выпустить новый |
| 14 | JSON decode error при curl | PowerShell съел кавычки | Использовать `ConvertTo-Json` + `--data-binary @файл` |
| 15 | `.env` в UTF-16 с BOM | PowerShell `Out-File` | Использовать `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` |

---

## 8. Что не реализовано

### 8.1. Веб-интерфейс (пункт 4.6 ТЗ)

**Что есть сейчас:** данные можно смотреть только через SQL-запросы в терминале.

**Что не сделано:**
- Страница со списком ПК и статусом (онлайн/оффлайн).
- Выбор ПК и даты ? таблица активности.
- Графики активности по часам.
- Экспорт в CSV/Excel.
- Аутентификация администратора.

**Что уже готово для этого:** эндпоинты админа (`/admin/bootstrap-tokens`, `/admin/computers/{uid}/revoke`), `audit_log`, роли в модели данных.

**Оценка работы:** 2–4 часа на минимальный UI, день на полноценный дашборд.

### 8.2. Миграции БД (Alembic)

Сейчас используется `create_all` + ручная миграция `_migrate`. При изменении схемы на проде — Alembic.

### 8.3. Отчёты и экспорт

- Нет автоматических ежедневных/еженедельных отчётов.
- Нет email-уведомлений оффлайн-ПК.
- Нет дашборда «кто сейчас работает».

### 8.4. Heartbeat

Клиент обновляет `last_seen_at` при каждом `ingest`. Отдельного heartbeat-эндпоинта нет.

### 8.5. Ротация `client_secret`

Поле `secret_version` в БД есть, эндпоинта для ротации нет.

### 8.6. Роли пользователей

Есть только `ADMIN_API_KEY`. Модели `admin/operator/viewer` — нет.

### 8.7. Автообновление через `client_versions`

Механизм есть, но эндпоинт для публикации версии — только через SQL.

### 8.8. Экспорт в отчётные формы

- Нет выгрузки в Excel.
- Нет PDF-отчётов.
- Нет графика «рабочие часы за месяц» для бухгалтерии.

### 8.9. Работа под Wayland

Клиент детектирует Wayland, но не собирает активные окна. Нужен `evdev` для сбора клавиатуры/мыши и/или `DBus` для окон.

### 8.10. macOS / Linux сборки

Скрипты для сборки `.app`/`.deb` не написаны. Только `.exe`.

---

## 9. Диагностика и логи

### Логи клиента

```powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 50 -Encoding UTF8
```

**Что искать:**
- `Loaded .env from ...` — .env подхватился.
- `Registered as ...` — регистрация прошла.
- `Sync: accepted=N rejected=0` — данные уходят.
- `Registration failed` — ошибка регистрации (с traceback).
- `sync failed` — проблема с сервером.

### Логи сервера

```powershell
cd D:\tracker
docker compose logs api --tail=50
docker compose logs nginx --tail=50
docker compose logs db --tail=20
```

**Что искать:**
- `Registered uid=...` — регистрация прошла.
- `Ingest: comp=... accepted=N rejected=M` — батч обработан.
- `Bad signature for ...` — HMAC не сошлась.
- `POST /api/v1/computers/register HTTP/1.1" 401` — ошибка регистрации.

### Проверка БД

```powershell
# Все компьютеры
docker compose exec db psql -U tracker -d tracker -c "SELECT id, computer_uid, hostname, last_seen_at FROM computers;"

# Все сессии
docker compose exec db psql -U tracker -d tracker -c "SELECT * FROM work_sessions ORDER BY id DESC LIMIT 10;"

# Bootstrap-токены
docker compose exec db psql -U tracker -d tracker -c "SELECT id, LEFT(token_hash,12), expires_at, used_at FROM bootstrap_tokens ORDER BY id DESC LIMIT 10;"

# Аудит
docker compose exec db psql -U tracker -d tracker -c "SELECT created_at, actor, action, entity FROM audit_log ORDER BY id DESC LIMIT 20;"
```

---

## 10. Что делать при типовых сбоях

| Симптом | Решение |
|---|---|
| `docker compose ps` — api в `Restarting` | `docker compose logs api --tail=50` ? искать причину |
| nginx не поднимается | `docker compose logs nginx --tail=50` — обычно сертификат или порт |
| Порт 443 занят | `netstat -ano \| findstr :443` ? сменить порт в `docker-compose.yml` |
| Клиент висит на «Инициализация» | Открыть `client.log` в UTF-8, смотреть `Registration failed` |
| `401 Unauthorized` | Bootstrap-токен сгорел — выпустить новый |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Проверить `ca.pem`, перевыпустить сертификат с SAN |
| `Hostname mismatch` | Сертификат без SAN для `localhost` |
| `getaddrinfo failed` | `.env` не читается, `SERVER_URL` дефолтный |
| Клиент не пишет данные | `pynput` не работает — Wayland? нет прав? |
| «Синхронизировано 0» | Сервер отвергает батч: `unknown_session` или `bad_signature`. Проверить `docker compose logs api` |
| `.env` игнорируется | UTF-16 BOM ? перезаписать через `WriteAllText` |
| PowerShell съедает кавычки | Использовать `ConvertTo-Json` + `--data-binary @файл` |

---

## 11. Безопасность и ротация секретов

### Что где хранится

| Секрет | Где | Кто использует |
|---|---|---|
| `SECRET_ENCRYPTION_KEY` | `.env` в корне | `client_secret_enc` в БД |
| `JWT_SECRET` | `.env` | резерв (не используется) |
| `ADMIN_API_KEY` | `.env` | эндпоинты `/api/v1/admin/*` |
| `client_secret` | keyring на ПК | HMAC-подпись записей |
| TLS-приватный ключ | `certs/privkey.pem` | nginx |

### Ротация `ADMIN_API_KEY`

```powershell
# 1. Остановить
cd D:\tracker
docker compose down

# 2. Новый ключ
python -c "import secrets; print(secrets.token_urlsafe(48))"

# 3. Заменить в .env через notepad
notepad .env

# 4. Запустить
docker compose up -d
docker compose exec api printenv ADMIN_API_KEY
```

### Ротация `SECRET_ENCRYPTION_KEY`

**Внимание:** при смене этого ключа старые `client_secret` перестанут расшифровываться, и все клиенты получат `bad_signature`. **Придётся перерегистрировать все ПК.**

Правильный путь:
```powershell
docker compose down -v   # обнуляет БД
# Сменить ключ в .env
docker compose up -d --build
# Перерегистрировать все ПК
```

### Что делать если `client_secret` утёк

1. На сервере: `POST /api/v1/admin/computers/{uid}/revoke` с `X-Admin-Token`.
2. На ПК: удалить `%APPDATA%\Tracker\credentials.enc` и keyring-запись.
3. Выпустить новый bootstrap-токен, запустить клиент заново.

---

## 12. Ограничения и предупреждения

### Юридические (152-ФЗ)

- Клиент собирает **только счётчики** нажатий, **не сами символы** (`COLLECT_KEYSTROKE_CHARS=False`).
- Собираются названия приложений и заголовки окон — это может содержать ПДн (ФИО в заголовке документа).
- **Нужно** письменное согласие сотрудников и приказ о введении мониторинга.
- **Нужно** уведомление в Роскомнадзор об обработке ПДн.
- **Нужно** описать меры защиты (ст. 19 152-ФЗ).

### Технические

- **Порт 80** не используется — только 443.
- **Сертификат самоподписанный** — для прода нужен валидный (Let's Encrypt или коммерческий).
- **Локальная SQLite не шифруется** — данные могут быть прочитаны локальным админом.
- **Pinning отключён** по умолчанию — включить через `TRACKER_PIN`.
- **Веб-интерфейса нет** — отчёты только через SQL.
- **Только Windows** сборка `.exe`. Для Linux/macOS — пересобрать.

### Производительность

- При 500+ ПК стоит рассмотреть партиционирование `records` по дате.
- `client_versions` — для автообновления; не забыть заполнять.
- PostgreSQL volume `pgdata` — **бэкапить регулярно**.

### Бэкап

```powershell
# Дамп БД
docker compose exec db pg_dump -U tracker tracker > backup_$(Get-Date -Format yyyyMMdd).sql

# Восстановление
Get-Content backup_20260916.sql | docker compose exec -T db psql -U tracker -d tracker
```

---

## Контакты и ссылки

- **ТЗ:** см. исходный документ.
- **Git-репозиторий:** (добавить)
- **Confluence/вики:** (добавить)
- **Ответственный за сервер:** (добавить)
- **Ответственный за клиент:** (добавить)

---

## Что делать дальше (roadmap)

1. **Ротация `ADMIN_API_KEY`** — заменил
2. **Включить pinning** — `TRACKER_PIN` в `client/.env`.
3. **Добавить веб-интерфейс** — минимальный UI для отчётов.
4. **Настроить автозапуск клиента** — `.bat` в Startup.
5. **Настроить бэкап PostgreSQL** — ежедневный `pg_dump`.
6. **Юридическое оформление** — согласия, приказ, уведомление РКН.
7. **Добавить отчёты** — ежедневные/еженедельные выгрузки в Excel.
8. **Собрать `.exe`** — для распространения на ПК сотрудников.
9. **Обновить `client_versions`** — для работы автообновления.
10. **Alembic** — для безопасных миграций схемы.

---

# Полный код всех файлов проекта «Трекер»

Ниже — финальные версии **всех** файлов. Скопированы с учётом всех правок, которые мы делали в процессе отладки.

---

## ?? Корень `D:\tracker\`

### `.env`

```ini
SECRET_ENCRYPTION_KEY=ЗАМЕНИТЕ_НА_ВАШ_FERNET_КЛЮЧ
JWT_SECRET=ЗАМЕНИТЕ_НА_ВАШ_JWT_СЕКРЕТ
ADMIN_API_KEY=ЗАМЕНИТЕ_НА_ВАШ_ADMIN_КЛЮЧ
```

Сгенерировать:
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: tracker
      POSTGRES_PASSWORD: tracker
      POSTGRES_DB: tracker
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracker"]
      interval: 5s
      retries: 10
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: server/Dockerfile
    environment:
      DATABASE_URL: postgresql+psycopg2://tracker:tracker@db:5432/tracker
      SECRET_ENCRYPTION_KEY: "${SECRET_ENCRYPTION_KEY}"
      JWT_SECRET: "${JWT_SECRET}"
      ADMIN_API_KEY: "${ADMIN_API_KEY}"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:1.27-alpine
    ports:
      - "443:443"
    volumes:
      - ./server/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  pgdata:
```

---

