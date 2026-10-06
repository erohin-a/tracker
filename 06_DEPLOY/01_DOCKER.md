# Docker
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\01_ARCHITECTURE.md, 06_DEPLOY\02_NGINX_TLS.md, 06_DEPLOY\03_WINDOWS_SETUP.md, 06_DEPLOY\04_BACKUP.md

## Назначение
Описать развёртывание сервера «Трекер» через Docker: состав `docker-compose.yml`, три контейнера, volumes, healthcheck, переменные окружения, команды. Это карта для администратора, который разворачивает сервер, и для разработчика, который дорабатывает инфраструктуру.

## Содержание

### Что разворачивается
- **Три контейнера:** `db`, `api`, `nginx`.
- **Один volume:** `pgdata` (постоянное хранилище PostgreSQL).
- **Один общий сетевой мост:** контейнеры видят друг друга по именам сервисов.
- **Один хост-порт:** 443 (nginx).

### Файл `docker-compose.yml`
- Лежит в корне `D:\tracker\docker-compose.yml`.
- Версия синтаксиса: `3.9`.
- Все три сервиса в одном файле.

### Контейнер `db`

**Образ:** `postgres:16-alpine`.

**Переменные окружения:**
| Переменная | Значение | Назначение |
|---|---|---|
| `POSTGRES_USER` | `tracker` | Пользователь БД |
| `POSTGRES_PASSWORD` | `tracker` | Пароль (для локальной разработки) |
| `POSTGRES_DB` | `tracker` | Имя БД |

**Volume:**
- `pgdata:/var/lib/postgresql/data` — постоянное хранилище.

**Healthcheck:**
```yaml
test: ["CMD-SHELL", "pg_isready -U tracker"]
interval: 5s
retries: 10
api ждёт condition: service_healthy.

Без healthcheck api может стартовать до готовности БД и упасть.

Restart policy: unless-stopped.

Порты: не публикуются наружу. Доступ только изнутри сети Docker.

Контейнер api
Сборка:

yaml
build:
  context: .
  dockerfile: server/Dockerfile
context: . — корень D:\tracker, а не ./server. Это критично: иначе COPY server/ ./server/ не сработает.

dockerfile: server/Dockerfile — путь к Dockerfile.

Переменные окружения:

Переменная	Источник	Назначение
DATABASE_URL	Захардкожен	postgresql+psycopg2://tracker:tracker@db:5432/tracker
SECRET_ENCRYPTION_KEY	${SECRET_ENCRYPTION_KEY} из .env	Fernet-ключ
JWT_SECRET	${JWT_SECRET}	Сессии админки
ADMIN_API_KEY	${ADMIN_API_KEY}	Пароль admin + admin API
Зависимости:

yaml
depends_on:
  db:
    condition: service_healthy
Ждёт готовности БД.

Применяет Alembic-миграции при старте (в server/main.py или entrypoint).

Restart policy: unless-stopped.

Порты: не публикуются наружу. Доступ через nginx.

Контейнер nginx
Образ: nginx:1.27-alpine.

Порты:

yaml
ports:
  - "443:443"
Только 443. Порт 80 не используется (занят Windows HTTP.sys).

Для HTTP-редиректа на HTTPS — не реализовано (только HTTPS).

Volumes:

yaml
volumes:
  - ./server/nginx.conf:/etc/nginx/conf.d/default.conf:ro
  - ./certs:/etc/nginx/certs:ro
nginx.conf — read-only.

certs/ — read-only (сертификаты).

Зависимости:

yaml
depends_on:
  - api
Restart policy: unless-stopped.

Volume pgdata
yaml
volumes:
  pgdata:
Где лежит:

Windows: \\wsl$\docker-desktop-data\data\docker\volumes\tracker_pgdata\_data.

Linux: /var/lib/docker/volumes/tracker_pgdata/_data.

Проверка:

powershell
docker volume ls
docker volume inspect tracker_pgdata
⚠ Опасно:

docker compose down -v удаляет volume. Все данные пропадут.

Перед этим — бэкап: pg_dump.

Сеть
Docker Compose автоматически создаёт сеть tracker_default.

api видит db по имени db.

nginx видит api по имени api.

Извне доступен только nginx:443.

Dockerfile (server/Dockerfile)
Базовый образ: python:3.11-slim.

ENV:

dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1 — не писать .pyc.

PYTHONUNBUFFERED=1 — логи сразу в stdout.

WORKDIR: /app.

Системные пакеты:

dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
build-essential — для компиляции psycopg2.

libpq-dev — заголовки PostgreSQL.

Python-зависимости:

dockerfile
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
Копирование кода:

dockerfile
COPY server/ ./server/
RUN touch /app/server/__init__.py
touch __init__.py — гарантия, что server — пакет.

Порт: EXPOSE 8000.

Команда запуска:

dockerfile
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", \
     "-b", "0.0.0.0:8000", "server.main:app"]
4 воркера gunicorn.

uvicorn worker — async.

Слушает 0.0.0.0:8000 (внутри контейнера).

Запуск
Первый запуск:

powershell
cd D:\tracker
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
Все три контейнера должны быть Up.

api — после db healthy.

nginx — после api.

Проверка:

powershell
curl.exe -k https://localhost/api/v1/version
Должен вернуться JSON.

Остановка
powershell
docker compose down          # остановить, volume сохранить
docker compose down -v       # остановить, volume удалить (СБРОС БД)
Перезапуск
Ситуация	Команда
После правки HTML	docker compose restart api
После правки Python	docker compose down && docker compose up -d --build
После правки .env	docker compose down && docker compose up -d
После правки docker-compose.yml	docker compose down && docker compose up -d
После правки nginx.conf	docker compose restart nginx
Важно: docker compose restart api НЕ перечитывает Python-код. Только rebuild.

Просмотр состояния
powershell
docker compose ps                        # список контейнеров
docker compose logs api --tail=50        # логи API
docker compose logs nginx --tail=50      # логи nginx
docker compose logs db --tail=50         # логи БД
docker compose logs -f api               # следить в реальном времени
docker compose logs --since 30m          # за последние 30 минут
Вход в контейнер
powershell
docker compose exec -it api bash         # внутрь API
docker compose exec -it db psql -U tracker -d tracker   # в psql
docker compose exec -it nginx sh         # внутрь nginx

# Неинтерактивные команды
docker compose exec -T api python -c "import server; print('OK')"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT 1;"
Флаг -T — без TTY, для скриптов.

Известные проблемы
Проблема	Причина	Решение
ModuleNotFoundError: No module named 'server'	Неверный build.context	context: ., dockerfile: server/Dockerfile
Cannot connect to Docker daemon	Docker Desktop не запущен	Запустить Docker Desktop, подождать 60 сек
api в Restarting	Ошибка Python / миграции	docker compose logs api --tail=100
nginx не поднимается	Ошибка сертификата / порт занят	docker compose logs nginx --tail=50
Порт 443 занят	Другая служба	netstat -ano | findstr :443
Порт 80 занят Windows HTTP.sys	IIS/WinRM	Использовать только 443
db unhealthy	Volume повреждён	docker compose logs db --tail=50
Volume pgdata удалён	docker compose down -v	Восстановить из бэкапа
unknown directive "CN=localhost"	Мусор в nginx.conf	Перезаписать конфиг
Долгая сборка api	build-essential + компиляция	Кэш Docker ускоряет повторные сборки
Volume pgdata — проверка
Убедиться, что volume есть:

powershell
docker volume ls | Select-String pgdata
Проверить содержимое:

powershell
docker compose exec -T db psql -U tracker -d tracker -c "\dt"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM computers;"
Если таблиц нет:

Volume либо удалён, либо БД ещё не мигрировала.

docker compose logs api --tail=100 — проверить Alembic.

Быстрая диагностика за 30 секунд
powershell
cd D:\tracker
docker info | Select-String "Server Version"     # Docker запущен?
docker compose ps                                 # контейнеры живы?
curl.exe -k https://localhost/api/v1/version      # API отвечает?
docker compose exec -T db psql -U tracker -d tracker -c "\dt"  # БД видит таблицы?
docker compose logs api --tail=30                 # последние ошибки
Что делать, если ничего не помогает
Сохранить бэкап БД:

powershell
docker compose exec -T db pg_dump -U tracker tracker > backup_$(Get-Date -Format yyyyMMdd_HHmm).sql
Полностью пересобрать:

powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 30
docker compose ps
docker compose logs api --tail=50
Если проблема в volume — не удалять. Сначала бэкап.

Если ошибка в миграции — прислать docker compose logs api --tail=100.

Ключевые решения
Три контейнера: db, api, nginx. Разделение ответственности.

context: . для api. Иначе COPY server/ не сработает.

Volume pgdata. Постоянное хранилище, не теряется при rebuild.

Только 443. Порт 80 занят Windows HTTP.sys.

Healthcheck у db. api ждёт готовности.

4 воркера gunicorn. Баланс производительности и памяти.

--no-install-recommends. Минимальный образ.

PYTHONDONTWRITEBYTECODE=1. Не мусорить .pyc.

docker compose down -v — опасно. Удаляет volume, все данные.

restart api не перечитывает Python. Только down && up -d --build.

Ссылки на код
запросить: docker-compose.yml — три контейнера

запросить: server/Dockerfile — образ api

запросить: server/nginx.conf — конфиг nginx

запросить: server/requirements.txt — зависимости

запросить: D:\tracker\.env — секреты

запросить: certs/ — сертификаты

Открытые вопросы / чего не хватает
нет данных: есть ли healthcheck у api и nginx — не описаны.

нет данных: использует ли api entrypoint для миграций — Alembic при старте.

нет данных: как обновляется api без простоя — не описано.

нет данных: есть ли restart: unless-stopped у всех — да.

нет данных: точный ключ tracker_pgdata — префикс зависит от имени проекта.

не решено: нужен ли отдельный контейнер для планировщика.

не решено: использовать ли docker swarm или k8s для масштабирования.

не решено: нужен ли Redis для кэша.

не решено: как быть с миграциями при нескольких воркерах — сейчас Alembic при старте.

не решено: нужен ли rate limiting на API (на уровне nginx).

не решено: нужен ли healthcheck у api.

не решено: логировать ли docker compose в файл.

не решено: нужен ли docker-compose.override.yml для dev-режима.

не решено: как быть с pgdata при переезде на другой сервер.

не решено: нужно ли бэкапить pgdata на уровне Docker (volume snapshot) или через pg_dump.

Готово. Один файл выше. Следующий по индексу — 06_DEPLOY\02_NGINX_TLS.md.