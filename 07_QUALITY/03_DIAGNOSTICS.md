# Диагностика
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 07_QUALITY\02_KNOWN_ISSUES.md, 09_OPS\01_RUNBOOK.md, 03_SERVER\05_TASKS.md

## Назначение
Собрать в одном месте инструменты и команды для диагностики «Трекера»: логи, SQL-проверки, состояние планировщика, health-чеки. Это карта для администратора, который разбирается с инцидентом, и для разработчика, который ищет причину бага.

## Содержание

### Логи

#### API (FastAPI)
```powershell
cd D:\tracker
docker compose logs api --tail=100
docker compose logs api -f                 # следить в реальном времени
docker compose logs api --since 30m        # за последние 30 минут
Что искать: Traceback, Error, Exception, NameError, IntegrityError, DataError, alembic.

Nginx
powershell
docker compose logs nginx --tail=50
Что искать: cannot load certificate, host not found in upstream, bind() to 0.0.0.0:443 failed, unknown directive.

PostgreSQL
powershell
docker compose logs db --tail=50
Что искать: could not connect, database does not exist, FATAL, PANIC.

Клиент
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 100 -Encoding UTF8
Что искать: getaddrinfo failed, SSL: CERTIFICATE_VERIFY_FAILED, 401, 500, sync failed, Registration failed.

Сохранение трейсбеков
Middleware для логирования 500 в server/main.py:

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
Позволяет видеть полный фрейм в docker compose logs api.

SQL-проверки
Все команды выполняются из D:\tracker:

powershell
docker compose exec -T db psql -U tracker -d tracker -c "<SQL>"
Общее состояние
sql
-- Все таблицы
\dt

-- Размер БД
SELECT pg_size_pretty(pg_database_size('tracker'));

-- Текущая ревизия Alembic
SELECT * FROM alembic_version;
Компьютеры
sql
-- Все ПК
SELECT id, computer_uid, hostname, last_seen_at, is_active, deleted_at
FROM computers ORDER BY id;

-- Онлайн (heartbeat < 10 мин)
SELECT hostname, last_seen_at
FROM computers
WHERE last_seen_at >= NOW() - INTERVAL '10 minutes';

-- Отозванные
SELECT id, hostname, computer_uid FROM computers WHERE is_active = false;
Сотрудники
sql
-- Активные
SELECT id, full_name, external_id, department_id
FROM employees WHERE fired_at IS NULL ORDER BY last_name;

-- Уволенные
SELECT id, full_name, fired_at FROM employees WHERE fired_at IS NOT NULL;
Сессии
sql
-- Сессии за сегодня
SELECT c.hostname, ws.session_start, ws.session_end, ws.abnormal_termination
FROM work_sessions ws
JOIN computers c ON c.id = ws.computer_id
WHERE ws.session_start >= CURRENT_DATE;

-- Незакрытые сессии
SELECT session_uid, session_start, session_end
FROM work_sessions WHERE session_end IS NULL;

-- Аварийные за последние 24 часа
SELECT session_uid, session_start, session_end
FROM work_sessions
WHERE abnormal_termination = true
  AND session_start >= NOW() - INTERVAL '24 hours';
Записи
sql
-- Общее количество
SELECT COUNT(*) FROM records;

-- За сегодня
SELECT COUNT(*) FROM records WHERE client_ts >= CURRENT_DATE;

-- По типам
SELECT kind, COUNT(*) FROM records GROUP BY kind;

-- Очередь на сервере (не должно быть)
SELECT COUNT(*) FROM records WHERE signature IS NULL;
Партиции
sql
-- Список партиций
SELECT tablename FROM pg_tables
WHERE tablename LIKE 'records_%' AND tablename != 'records'
ORDER BY tablename;

-- Записи в records_default (должно быть 0)
SELECT COUNT(*) FROM records_default;

-- Размер партиций
SELECT relname AS partition,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
WHERE relname LIKE 'records_%'
ORDER BY pg_total_relation_size(relid) DESC;
Bootstrap-токены
sql
-- Активные
SELECT id, LEFT(token_hash,12), expires_at, used_at
FROM bootstrap_tokens
WHERE used_at IS NULL AND expires_at > NOW()
ORDER BY id DESC;

-- Последние 10
SELECT id, LEFT(token_hash,12), expires_at, used_at, used_by_uid
FROM bootstrap_tokens ORDER BY id DESC LIMIT 10;
Аудит
sql
-- Последние 20 действий
SELECT created_at, actor, entity, entity_id, action
FROM audit_log ORDER BY id DESC LIMIT 20;

-- Действия за 24 часа
SELECT created_at, actor, entity, action
FROM audit_log
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY id DESC;
Настройки
sql
SELECT key, value FROM app_settings ORDER BY key;
Планировщик
sql
-- Задачи
SELECT name, enabled, schedule_cron, last_run_at, last_run_status
FROM scheduled_tasks ORDER BY id;

-- Последние запуски
SELECT task_name, started_at, finished_at, status, message
FROM task_runs ORDER BY id DESC LIMIT 20;
Проверка планировщика
Список задач
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron FROM scheduled_tasks ORDER BY id;"
Ручной запуск задачи
powershell
docker compose exec -T api python -c @"
from server.database import SessionLocal
from server import tasks
db = SessionLocal()
try:
    result = tasks.close_stale_sessions(db)
    print('OK:', result)
finally:
    db.close()
"@
Аналогично для create_future_partitions, aggregate_daily_stats.

Проверка, что scheduler работает
powershell
docker compose logs api --tail=50 | Select-String "scheduler"
Ищите строки вида Scheduler started, Job ... executed, Advisory lock acquired.

Проверка партиций на будущее
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT tablename FROM pg_tables WHERE tablename LIKE 'records_%' ORDER BY tablename;"
Убедитесь, что есть партиции на 12 месяцев вперёд.

Health-чеки
Docker
powershell
docker info | Select-String "Server Version"
docker compose ps
API
powershell
curl.exe -k https://localhost/api/v1/version
curl.exe -k https://localhost/admin/login -I
БД
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT 1;"
docker compose exec -T db psql -U tracker -d tracker -c "\dt"
Сертификат
powershell
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -dates
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -fingerprint -sha256
Планировщик
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM task_runs WHERE started_at >= NOW() - INTERVAL '1 hour';"
Свободное место
powershell
Get-PSDrive D | Select-Object Used, Free
docker system df
Быстрая диагностика за 30 секунд
powershell
cd D:\tracker

# 1. Docker запущен?
docker info | Select-String "Server Version"

# 2. Контейнеры живы?
docker compose ps

# 3. API отвечает?
curl.exe -k https://localhost/api/v1/version

# 4. БД видит таблицы?
docker compose exec -T db psql -U tracker -d tracker -c "\dt"

# 5. Последние ошибки API?
docker compose logs api --tail=30

# 6. Планировщик работает?
docker compose exec -T db psql -U tracker -d tracker -c "SELECT task_name, status, started_at FROM task_runs ORDER BY id DESC LIMIT 5;"
Если все шесть шагов успешны — сервер работает. Если где-то ошибка — смотрите соответствующий раздел.

Типовые проблемы и где искать
Симптом	Где искать	Файл KB
500 на API	docker compose logs api --tail=100	07_QUALITY\02_KNOWN_ISSUES.md
Клиент «офлайн»	curl.exe -k https://localhost/api/v1/version, client.log	07_QUALITY\02_KNOWN_ISSUES.md
getaddrinfo failed	client.log	07_QUALITY\02_KNOWN_ISSUES.md
Сессия висит 17 часов	SELECT * FROM work_sessions WHERE session_end IS NULL;	07_QUALITY\02_KNOWN_ISSUES.md
Партиции удалены	SELECT tablename FROM pg_tables WHERE tablename LIKE 'records_%';	03_SERVER\06_PARTITIONS.md
Задача падает	SELECT * FROM task_runs WHERE status='error' ORDER BY id DESC;	03_SERVER\05_TASKS.md
Отчёт не считается	docker compose logs api --tail=100	02_METRICS\02_REPORTS.md
PDF с крокозябрами	Проверить server/fonts/DejaVuSans.ttf	07_QUALITY\02_KNOWN_ISSUES.md
Диагностика клиента
Проверка локальной БД
powershell
sqlite3 "$env:APPDATA\Tracker\data.db"
sql
-- Размер
SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size();

-- Очередь на отправку
SELECT COUNT(*) FROM records WHERE synced = 0;
SELECT COUNT(*) FROM sessions WHERE synced = 0;

-- Отравленные
SELECT COUNT(*) FROM records WHERE poisoned = 1;

-- Мета
SELECT * FROM meta;
Проверка регистрации
powershell
Get-Content "$env:APPDATA\Tracker\config.json" -Raw
Test-Path "$env:APPDATA\Tracker\credentials.enc"
Проверка сертификата
powershell
Test-Path "$env:APPDATA\Tracker\ca.pem"
Проверка автозапуска
powershell
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" | Select-Object Tracker
Сбор диагностики для разработчика
При проблеме, которую не удаётся решить, собрать:

powershell
cd D:\tracker

# Логи
docker compose logs api --tail=200 > D:\tracker\_diag_api.log
docker compose logs nginx --tail=100 > D:\tracker\_diag_nginx.log
docker compose logs db --tail=100 > D:\tracker\_diag_db.log

# Клиент
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 200 > D:\tracker\_diag_client.log

# Состояние
docker compose ps > D:\tracker\_diag_ps.log
docker compose exec -T db psql -U tracker -d tracker -c "\dt" > D:\tracker\_diag_tables.log
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM records;" > D:\tracker\_diag_counts.log

# Версия
curl.exe -k https://localhost/api/v1/version > D:\tracker\_diag_version.log
Прислать разработчику.

Что НЕ реализовано
Автоматическая диагностика (health-страница).

Мониторинг (Prometheus/Grafana) — P3.

Алерты (Telegram/Email) — P2.

Просмотр логов клиента в админке — P2.

Автоматический сбор диагностики по кнопке.

Ключевые решения
Логи — основной источник. docker compose logs api — первое, что смотреть.

SQL-проверки — для данных. Партиции, сессии, записи, аудит.

Планировщик — через task_runs. История запусков и ошибок.

Health-чеки — короткие. 30 секунд на общую проверку.

Сбор диагностики — в отдельные файлы. Удобно прислать разработчику.

Middleware для 500. Полные трейсбеки в логах.

Клиентские логи — в %APPDATA%\Tracker\client.log. Основной источник.

SQLite-проверки — через sqlite3. Очередь, мета, регистрация.

Ссылки на код
запросить: server/main.py — middleware для 500, все API-роуты

запросить: server/tasks.py — функции задач, TASKS_REGISTRY

запросить: server/scheduler.py — APScheduler, advisory lock

запросить: client/db.py — структура SQLite, таблицы

запросить: client/config.py — DB_PATH, LOG_PATH, CONFIG_FILE

запросить: client/main.py — логика запуска, сигналы

запросить: server/models.py — модели для SQL-проверок

Открытые вопросы / чего не хватает
нет данных: есть ли отдельная страница /admin/health — нет.

нет данных: реализован ли сбор диагностики автоматически — нет.

нет данных: есть ли мониторинг — нет.

нет данных: тестировались ли SQL-проверки на больших объёмах — не подтверждено.

не решено: нужен ли healthcheck у API.

не решено: нужен ли Prometheus/Grafana (P3).

не решено: нужны ли алерты (P2).

не решено: нужна ли кнопка «Собрать диагностику» в админке.

не решено: где хранить собранные диагностики (файлы, БД).

не решено: нужно ли логировать клиентские ошибки на сервере (P2).

не решено: как быть с диагностикой на удалённых ПК (без физического доступа).

не решено: нужны ли автотесты для health-чеков.

Готово. Один файл выше. Следующий по индексу — 07_QUALITY\04_SECURITY.md.