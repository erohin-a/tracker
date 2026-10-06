# Логи
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 07_QUALITY\03_DIAGNOSTICS.md, 07_QUALITY\02_KNOWN_ISSUES.md, 99_RAW\01_CHAT_HISTORY.md

## Назначение
Собрать эталонные примеры логов «Трекера»: серверных, клиентских, Docker, nginx, планировщика. Показать, как выглядят нормальные логи и как — ошибочные. Это справочник для администратора, который ищет в логах причину, и для разработчика, который читает логи при отладке.

## Содержание

### Где какие логи

| Лог | Где | Что внутри |
|---|---|---|
| API (uvicorn) | `docker compose logs api` | Запросы, ошибки Python, Alembic |
| Nginx | `docker compose logs nginx` | HTTP-запросы, ошибки TLS |
| PostgreSQL | `docker compose logs db` | Подключения, ошибки БД |
| Клиент | `%APPDATA%\Tracker\client.log` | Синхронизация, регистрация, темы |
| Планировщик | `docker compose logs api \| Select-String scheduler` | Задачи, advisory lock |
| Задача (история) | `task_runs` в БД | Запуски задач, статусы |

---

### Нормальные логи

#### API при старте
INFO: Started server process [1]
INFO: Waiting for application startup.
INFO: Applying Alembic migrations...
INFO: Alembic upgrade head complete
INFO: Scheduler started (advisory lock acquired)
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

text

**Что важно:**
- Alembic применил миграции.
- Scheduler запустился и получил advisory lock.
- Uvicorn слушает 8000.

#### API при обычном запросе
INFO: 172.18.0.1:54321 - "POST /api/v1/computers/register HTTP/1.1" 200 OK
INFO: 172.18.0.1:54322 - "POST /api/v1/sessions HTTP/1.1" 200 OK
INFO: 172.18.0.1:54323 - "POST /api/v1/records/batch HTTP/1.1" 200 OK
INFO: 172.18.0.1:54324 - "POST /api/v1/heartbeat HTTP/1.1" 200 OK
INFO: 172.18.0.1:54325 - "GET /api/v1/client-config HTTP/1.1" 200 OK

text

**Что важно:**
- Все 200 OK.
- IP `172.18.0.1` — Docker-шлюз (nginx).
- Реальный IP клиента — в заголовке `X-Real-IP`.

#### Nginx при обычном запросе
172.18.0.1 - - [02/Oct/2026:09:00:00 +0000] "POST /api/v1/heartbeat HTTP/2.0" 200 12
172.18.0.1 - - [02/Oct/2026:09:00:30 +0000] "POST /api/v1/records/batch HTTP/2.0" 200 1234

text

**Что важно:**
- HTTP/2.0 — HTTP/2 работает.
- Код 200.
- Размер ответа.

#### PostgreSQL при старте
database system is ready to accept connections

text

#### Клиент при старте
2026-10-02 09:00:00,000 INFO tracker.config Loaded .env from C:\Users\user...\client.env
2026-10-02 09:00:00,100 INFO tracker.db DB initialized
2026-10-02 09:00:00,200 INFO tracker.registration Computer registered: uuid-...
2026-10-02 09:00:00,300 INFO tracker.sync SyncWorker started
2026-10-02 09:00:00,400 INFO tracker.reminder ReminderService started
2026-10-02 09:00:00,500 INFO tracker.themes Applied light theme

text

**Что важно:**
- `.env` загружен из `client/.env`.
- БД инициализирована.
- Регистрация прошла.
- Все сервисы запущены.

#### Клиент при синхронизации
2026-10-02 09:00:30,000 INFO tracker.sync Sync started
2026-10-02 09:00:30,100 INFO tracker.sync Sessions sent: 1
2026-10-02 09:00:30,200 INFO tracker.sync Records sent: 50 accepted, 0 rejected
2026-10-02 09:00:30,300 INFO tracker.sync Sync completed

text

#### Клиент при heartbeat
2026-10-02 09:03:00,000 INFO tracker.sync Heartbeat OK

text

#### Планировщик при запуске задачи
2026-10-02 04:00:00,000 INFO tracker.scheduler Running task: create_future_partitions
2026-10-02 04:00:00,500 INFO tracker.tasks Created partition: records_2027_10
2026-10-02 04:00:00,600 INFO tracker.tasks Created partition: records_2027_11
2026-10-02 04:00:00,700 INFO tracker.tasks Created partition: records_2027_12
2026-10-02 04:00:00,800 INFO tracker.scheduler Task completed: create_future_partitions (0.8s)

text

---

### Ошибочные логи

#### 1. `NameError: WorkSession`
2026-09-25 20:30:00,000 ERROR tracker.scheduler Task close_stale_sessions failed
Traceback (most recent call last):
File "/app/server/scheduler.py", line 123, in _run_task_wrapper
result = func(db, **kwargs)
File "/app/server/tasks.py", line 250, in close_stale_sessions
stale = db.query(WorkSession)...
NameError: name 'WorkSession' is not defined

text

**Причина:** нет импорта внутри функции.
**Решение:** `from .models import WorkSession, AuditLog`.

#### 2. `DataError: value too long`
sqlalchemy.exc.DataError: (psycopg2.errors.StringDataRightTruncation) value too long for type character varying(64)

[SQL: INSERT INTO audit_log (actor, entity, entity_id, action, new_value, created_at)
VALUES (%(actor)s, %(entity)s, %(entity_id)s, %(action)s, %(new_value)s, %(created_at)s)]

[parameters: {'actor': 'computer:ed1ef589-...',
'entity': 'record',
'entity_id': '50c5db31-...,9586575e-...,4349cd93-...',
'action': 'reject_signature',
'new_value': '{"count": 20, "reasons": {...}}'}]

text

**Причина:** список UUID в `entity_id` превысил 64 символа.
**Решение:** только первый UUID, остальное — в `new_value`.

#### 3. `IntegrityError` на batch
sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "records_record_uid_key"
DETAIL: Key (record_uid)=(abc-123) already exists.

text

**Причина:** `record_uid` уже существует с другим `computer_id`.
**Решение:** искать по всей таблице, `try/except IntegrityError`.

#### 4. `getaddrinfo failed`
2026-09-17 22:47:03,174 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed
2026-09-17 22:47:32,444 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed

text

**Причина:** Python резолвит `localhost` в IPv6 `::1`, Docker не пробрасывает.
**Решение:** `https://127.0.0.1` в `client/.env`.

#### 5. `SSL: CERTIFICATE_VERIFY_FAILED`
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1006)

text

**Причина:** нет `ca.pem` в `%APPDATA%\Tracker\`.
**Решение:** скопировать `fullchain.pem` в `%APPDATA%\Tracker\ca.pem`.

#### 6. `Hostname mismatch`
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch, certificate is not valid for 'localhost'. (_ssl.c:1006)

text

**Причина:** сертификат без SAN.
**Решение:** перевыпустить с `subjectAltName`.

#### 7. `401 Unauthorized` при регистрации
INFO: 172.18.0.1:54321 - "POST /api/v1/computers/register HTTP/1.1" 401 Unauthorized

text
Ответ:
```json
{"detail": "Invalid or expired bootstrap token"}
Причина: токен сгорел или истёк.
Решение: выпустить новый.

8. 409 Conflict на sessions
text
INFO: 172.18.0.1:54321 - "POST /api/v1/sessions HTTP/1.1" 409 Conflict
Ответ:

json
{"detail": "session_uid belongs to another computer"}
Причина: сессия принадлежит другому ПК.
Решение: возвращать 200 OK.

9. QObject::killTimer
text
QObject::killTimer: Timers cannot be stopped from another thread
QObject::~QObject: Timers cannot be stopped from another thread
Причина: QTimer уничтожается не в том потоке.
Решение: не критично, косметика.

10. ModuleNotFoundError: PyQt6
text
ModuleNotFoundError: No module named 'PyQt6'
Причина: venv не активирован.
Решение: client\.venv\Scripts\Activate.ps1.

11. ModuleNotFoundError: client
text
ModuleNotFoundError: No module named 'client'
Причина: запуск из D:\tracker\client.
Решение: python -m client.main из D:\tracker.

12. ModuleNotFoundError: server
text
ModuleNotFoundError: No module named 'server'
Причина: неверный build.context в docker-compose.yml.
Решение: context: ., dockerfile: server/Dockerfile.

13. SyntaxError: line 265
text
SyntaxError: invalid syntax (<unknown>, line 265)
Причина: остаток ), WorkSession после патча.
Решение: заменить на ).

14. PermissionError: tasks.py
text
PermissionError: [Errno 13] Permission denied: 'D:\\tracker\\server\\tasks.py'
Причина: файл занят редактором/антивирусом.
Решение: copy /y или os.replace.

15. nginx: unknown directive
text
nginx: [emerg] unknown directive "CN=localhost" in /etc/nginx/conf.d/default.conf:5
Причина: мусор в nginx.conf.
Решение: перезаписать конфиг.

16. api в Restarting
text
tracker-api  | Traceback (most recent call last):
tracker-api  |   File "/app/server/main.py", line 10, in <module>
tracker-api  |     from .web_admin import router
tracker-api  | ImportError: cannot import name 'router'
Причина: ошибка в импорте Python.
Решение: исправить импорт, down && up -d --build.

17. 500 на дашборде
text
INFO: 172.18.0.1:54321 - "GET /admin HTTP/1.1" 500 Internal Server Error
text
jinja2.exceptions.UndefinedError: 'cutoff_online' is undefined
Причина: не передан в контекст шаблона.
Решение: добавить cutoff_online=cutoff_online.

18. PDF NameError: Paragraph
text
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 143, in app
    await app(scope, receive, send)
  ...
  File "/app/server/web_admin.py", line 1445, in cell
    return Paragraph(str(text if text is not None else ""),
NameError: name 'Paragraph' is not defined
Причина: импорт внутри другой функции.
Решение: импорт в начале _pdf_table_data.

19. Alembic пытается удалить партиции
text
INFO  [alembic.runtime.migration] Running upgrade ... -> ...
INFO  [alembic.autogenerate] Detected removed table 'records_2025_01'
INFO  [alembic.autogenerate] Detected removed table 'records_2025_02'
...
Причина: нет include_object в env.py.
Решение: добавить фильтр records_*.

20. Клиент в офлайне
text
2026-10-02 10:00:00,000 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed
2026-10-02 10:00:30,000 WARNING tracker.sync sync failed: timeout
2026-10-02 10:01:00,000 WARNING tracker.sync retry #3 in 4s
2026-10-02 10:01:04,000 WARNING tracker.sync sync failed: timeout
Причина: сервер недоступен.
Решение: проверить сеть, дождаться восстановления.

21. auth_failed
text
2026-10-02 10:00:00,000 ERROR tracker.sync auth_failed: 401 Unauthorized
2026-10-02 10:00:00,100 WARNING tracker.sync stopping sync (auth failed)
Причина: client_secret сгорел или ПК отозван.
Решение: перерегистрация.

22. pause_seconds > total_sec
text
WARNING tracker.db pause_seconds=3600 > total_sec=60
или аномально длинные сессии в отчёте.

Причина: close_session ставил end = now, pause_seconds вычитались дважды.
Решение: close_session_at(last_activity), не вычитать дважды.

Логи планировщика (task_runs)
Нормальный запуск
#	Дата/время	Статус	Сообщение
65	25.09.2026 21:30	✅ успех	Зависших сессий нет (порог 2ч)
66	25.09.2026 21:40	✅ успех	Зависших сессий нет (порог 2ч)
67	25.09.2026 22:00	✅ успех	Создано партиций: 0, уже было: 13
Ошибочный запуск
#	Дата/время	Статус	Сообщение
63	25.09.2026 20:30	❌ ошибка	NameError: name 'WorkSession' is not defined
64	25.09.2026 20:54	❌ ошибка	NameError: name 'AuditLog' is not defined
Как посмотреть:

powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT id, task_name, status, message FROM task_runs ORDER BY id DESC LIMIT 20;"
Как сохранять трейсбеки
Middleware для логирования 500
python
@app.middleware("http")
async def log_500(request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        log.exception("Unhandled error on %s %s", request.method, request.url.path)
        raise
    if response.status_code >= 500:
        log.error("Server error %s on %s %s",
                  response.status_code, request.method, request.url.path)
    return response
Логирование в файл
powershell
docker compose logs -f api > D:\tracker\_api_live.log
Фильтр по ошибкам
powershell
docker compose logs api --tail=500 | Select-String "Traceback|Error|Exception"
Что искать в логах при проблемах
Симптом	Что искать	Где
Клиент офлайн	getaddrinfo, SSL, 401, timeout	client.log
500 на API	Traceback, NameError, DataError	docker compose logs api
Контейнер упал	ImportError, ModuleNotFoundError	Логи контейнера
Nginx не работает	cannot load, unknown directive, bind()	docker compose logs nginx
Задача падает	task_runs.message	SQL
Отчёт не считается	Traceback при POST /admin/reports/generate	docker compose logs api
Партиции не создаются	Логи create_future_partitions	docker compose logs api | Select-String partition
PDF с крокозябрами	DejaVuSans	Проверить файл шрифта
Что НЕ сохранено в чате
Полные Python-трейсбеки с фреймами File "...", line N для многих ошибок.

Полный лог docker compose logs api при 500.

Полный лог uvicorn с INFO: 127.0.0.1:xxxxx - "POST ..." 500.

Логи nginx в момент ошибок.

Как сохранять логи на будущее
Включить middleware для 500.

Логировать в файл _api_live.log.

Сохранять task_runs (уже есть).

Использовать Select-String для фильтрации.

Не выбрасывать логи после инцидента.

Ключевые решения
Логи — основной источник диагностики. Всегда смотреть в первую очередь.

Middleware для 500 — обязателен. Даёт полный трейсбек.

task_runs — история задач. Замена логам планировщика.

client.log — всё о клиенте. Синхронизация, регистрация, темы.

docker compose logs — стандартные команды. Без внешних систем.

Фильтрация через Select-String. Быстро найти ошибку.

Трейсбеки сохранять в файлы. Удобно прислать разработчику.

Реальные значения секретов не логировать. Только факты.

Ссылки на код
запросить: server/main.py — middleware, API-роуты

запросить: server/tasks.py — задачи планировщика

запросить: server/scheduler.py — APScheduler, логирование

запросить: client/db.py — логи клиента

запросить: client/sync.py — логи синхронизации

запросить: client/config.py — LOG_PATH, logging

запросить: server/web_admin.py — логи PDF, отчётов

запросить: server/alembic/env.py — логи миграций

Открытые вопросы / чего не хватает
нет данных: полные трейсбеки для многих ошибок — не сохранились.

нет данных: логи в момент инцидентов — не сохранились.

нет данных: есть ли логирование в файл на сервере — нет.

нет данных: настроен ли rotation логов Docker — по умолчанию.

нет данных: сколько хранятся логи Docker — по умолчанию до перезапуска.

не решено: нужно ли логирование в файл на сервере.

не решено: нужен ли внешний сбор логов (ELK, Loki) — P3.

не решено: нужна ли структурированная логирование (JSON).

не решено: как хранить логи долгосрочно.

не решено: нужна ли страница /admin/logs для просмотра логов.

не решено: как логировать клиентские ошибки на сервере (P2).

не решено: нужен ли docker compose logs в ротации.

не решено: как быть с логированием в проде (больше данных).

не решено: нужны ли алерты на ошибки (P2).

не решено: как логировать 403 (отказы в доступе).

не решено: как избежать логирования секретов.

не решено: как логировать долгие SQL-запросы.

не решено: нужен ли APM (Application Performance Monitoring).

не решено: как тестировать логирование.

Готово. Один файл выше. Все файлы из 00_INDEX.md созданы.