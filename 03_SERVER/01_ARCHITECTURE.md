# Архитектура сервера
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\02_API.md, 03_SERVER\03_MODELS.md, 06_DEPLOY\01_DOCKER.md

## Назначение
Описать архитектуру серверной части «Трекера»: какие компоненты входят, как они взаимодействуют, какие технологии используются и почему. Это карта для разработчика, который впервые открывает проект, и для администратора, который разворачивает сервер.

## Содержание

### Общая схема
┌──────────────────────────────────────────────────────────────┐
│ ПК СОТРУДНИКА (Windows/Linux) │
│ Tracker.exe (PyQt6) │
│ - collector (сбор активности) │
│ - sync worker (отправка раз в 30 сек) │
│ - heartbeat (раз в 3 мин) │
│ - локальная SQLite (WAL) │
│ - трей, кнопки Старт/Пауза/Стоп │
│ - reminder service │
└──────────────────────┬───────────────────────────────────────┘
│ HTTPS + HMAC-SHA256
▼
┌──────────────────────────────────────────────────────────────┐
│ СЕРВЕР (Docker Compose) │
│ nginx (443) → FastAPI → PostgreSQL │
│ - API: регистрация, сессии, записи, heartbeat, конфиг │
│ - Веб-админка: 75+ роутов │
│ - Alembic-миграции │
│ - APScheduler (планировщик) │
│ - партиционирование records по месяцам │
└──────────────────────────────────────────────────────────────┘

text

### Три контейнера
Серверная часть разворачивается через `docker-compose.yml` в трёх контейнерах.

| Контейнер | Образ | Роль |
|---|---|---|
| `db` | `postgres:16-alpine` | База данных PostgreSQL 16 |
| `api` | Собственный (`server/Dockerfile`) | FastAPI-приложение + веб-админка + планировщик |
| `nginx` | `nginx:1.27-alpine` | Reverse-proxy, терминация TLS, отдача статики |

**Порядок запуска:**
1. `db` — поднимается первым, healthcheck `pg_isready`.
2. `api` — ждёт `db` (`condition: service_healthy`), применяет миграции Alembic, запускает gunicorn.
3. `nginx` — ждёт `api`, слушает 443.

### Роли контейнеров

#### `db` (PostgreSQL 16)
- Хранит все данные: `computers`, `employees`, `work_sessions`, `records` (партиционирована), `audit_log`, `app_settings` и др.
- Volume `pgdata` — постоянное хранилище.
- Партиционирование `records` по месяцам.
- Advisory lock для планировщика.
- Healthcheck: `pg_isready -U tracker`.

#### `api` (FastAPI + gunicorn)
- **FastAPI** — асинхронный веб-фреймворк.
- **gunicorn** с 4 воркерами (`-w 4`), worker class `uvicorn.workers.UvicornWorker`.
- **SQLAlchemy 2.0** — ORM.
- **Alembic** — миграции (применяются при старте).
- **APScheduler** — планировщик задач (advisory lock гарантирует, что только один воркер запускает задачи).
- **Jinja2** — шаблоны веб-админки.
- **pydantic-settings** — конфигурация из `.env`.
- **Fernet** — шифрование `client_secret`.
- **bcrypt** — хеширование паролей админки.
- **reportlab** — PDF-экспорт.
- **openpyxl** — XLSX-экспорт.

**Что обслуживает:**
- API `/api/v1/*` — регистрация, сессии, записи, heartbeat, конфиг, версия.
- Админ API `/api/v1/admin/*` — bootstrap-токены, revoke, re-registration.
- Веб-админка `/admin/*` — 75+ роутов, все страницы.
- Pivot API `/admin/api/pivot-data`.

#### `nginx` (reverse-proxy)
- Слушает 443 (TLS).
- Терминирует HTTPS.
- Проксирует:
  - `/api/` → `http://api:8000`
  - `/admin/` → `http://api:8000`
  - `/` → редирект на `/admin/login`.
- HSTS: `Strict-Transport-Security "max-age=63072000; includeSubDomains"`.
- `client_max_body_size 10m`.
- Сертификаты монтируются из `./certs:/etc/nginx/certs:ro`.
- Конфиг: `server/nginx.conf`.

### Стек технологий
| Компонент | Технология | Почему |
|---|---|---|
| Веб-фреймворк | FastAPI | Асинхронный, быстрый, OpenAPI, Pydantic |
| ORM | SQLAlchemy 2.0 | Стандарт, Alembic «из коробки» |
| Миграции | Alembic | Единственный взрослый инструмент |
| СУБД | PostgreSQL 16 | Партиционирование, TIMESTAMPTZ, advisory locks |
| Reverse-proxy | nginx | Проверенный, гибкий, TLS |
| Контейнеризация | Docker Compose | Простой деплой, переносимость |
| Планировщик | APScheduler | Advisory lock, cron |
| Шаблоны | Jinja2 | Стандарт для FastAPI |
| Конфиг | pydantic-settings | Типизация, чтение `.env` |
| Пароли | bcrypt | Прямой, без passlib |
| Шифрование | Fernet | Обратимое шифрование `client_secret` |
| PDF | reportlab | DejaVuSans для кириллицы |
| XLSX | openpyxl | Типизированные значения, pivot-friendly |

### Потоки данных

#### 1. Регистрация ПК
1. Клиент отправляет `POST /api/v1/computers/register` с bootstrap-токеном.
2. nginx проксирует в `api:8000`.
3. FastAPI проверяет токен (хеш в `bootstrap_tokens`), генерирует `client_secret`, шифрует Fernet, сохраняет в `computers.client_secret_enc`.
4. Возвращает `client_secret` клиенту (один раз).

#### 2. Отправка записей
1. Клиент собирает activity/window/idle в локальную SQLite.
2. `SyncWorker` раз в 30 сек отправляет батч `POST /api/v1/records/batch`.
3. FastAPI проверяет HMAC каждой записи и батча.
4. Идемпотентность по `record_uid`.
5. Запись в `records` (партиционирована по `client_ts`).
6. Ответ: `accepted_uuids`, `rejected_uuids`, `server_signature`.

#### 3. Heartbeat
1. Клиент раз в 3 мин: `POST /api/v1/heartbeat`.
2. FastAPI обновляет `computers.last_seen_at`.
3. Дашборд показывает онлайн-статус по `last_seen_at` в пределах 10 мин.

#### 4. Отчёты
1. Админ выбирает фильтры в `/admin/reports`.
2. POST `/admin/reports/generate`.
3. FastAPI: `_build_report` → `_build_flat_records` → `_analyze_session` → `_aggregate_group`.
4. Возврат HTML / CSV / XLSX / PDF.

#### 5. Планировщик
1. APScheduler в `api` (только один воркер через advisory lock).
2. Задачи: `create_future_partitions`, `aggregate_daily_stats`, `close_stale_sessions`.
3. История — в `task_runs`.

#### 6. Веб-админка
1. Браузер → nginx (443) → FastAPI.
2. Сессия в cookie `tracker_admin`.
3. Jinja2-шаблоны из `server/templates/`.
4. Все действия → `audit_log`.

### Конфигурация
- Все секреты — в `D:\tracker\.env` (UTF-8 без BOM).
- `SECRET_ENCRYPTION_KEY` — Fernet-ключ.
- `JWT_SECRET` — для сессий админки.
- `ADMIN_API_KEY` — пароль `admin` + admin API token.
- `DATABASE_URL` — в `docker-compose.yml`.

### Партиционирование `records`
- `records` — `PARTITION BY RANGE (client_ts)`.
- Партиции на каждый месяц 2025–2027 + `records_default`.
- `create_future_partitions` создаёт на 12 месяцев вперёд.
- `include_object` в `alembic/env.py` исключает партиции из автогенерации.

### Аутентификация
- **Клиент → сервер:** HMAC-SHA256, `X-Computer-Uid`.
- **Админ API:** `X-Admin-Token`.
- **Веб-админка:** сессия, cookie `tracker_admin`, логин из `admin_users`, bcrypt.

### Масштабирование
- До 200 ПК без партиционирования hot-таблиц.
- При росте: партиционирование `daily_stats`, архивы.
- 4 воркера gunicorn — достаточно для 50–200 ПК.
- Планировщик — только один воркер (advisory lock).

## Ключевые решения
- **FastAPI + PostgreSQL + nginx + Docker** — скорость разработки + масштабируемость.
- **HMAC на каждой записи** — целостность данных, офлайн-режим.
- **Fernet для `client_secret`** — обратимое шифрование симметричного ключа.
- **Партиционирование `records`** — масштабирование до 100+ млн записей.
- **Advisory lock для планировщика** — гарантия одного запуска.
- **`include_object` в Alembic** — защита партиций от autogenerate.
- **gunicorn с 4 воркерами** — баланс между производительностью и памятью.
- **Jinja2 + Bootstrap 5** — быстрая разработка админки.

## Ссылки на код
- запросить: `docker-compose.yml` — три контейнера
- запросить: `server/Dockerfile` — образ api
- запросить: `server/nginx.conf` — конфиг nginx
- запросить: `server/main.py` — FastAPI-приложение
- запросить: `server/config.py` — pydantic-settings
- запросить: `server/database.py` — engine, SessionLocal
- запросить: `server/scheduler.py` — APScheduler + advisory lock
- запросить: `server/alembic/env.py` — include_object
- запросить: `server/requirements.txt` — версии зависимостей

## Открытые вопросы / чего не хватает
- нет данных: точная версия gunicorn и параметры воркеров — `-w 4` в Dockerfile.
- нет данных: есть ли healthcheck у `api` — не описан.
- нет данных: как обновляется `api` без простоя — не описано.
- не решено: нужен ли отдельный контейнер для планировщика.
- не решено: использовать ли Redis для кэша.
- не решено: нужен ли Prometheus/Grafana — в планах (P3).
- не решено: как быть с миграциями при нескольких воркерах — сейчас Alembic при старте.
- не решено: нужен ли rate limiting на API.

Готово. Один файл выше. Следующий по индексу — 03_SERVER\02_API.md.