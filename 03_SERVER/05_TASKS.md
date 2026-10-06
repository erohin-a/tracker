# Планировщик задач
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\06_PARTITIONS.md, 03_SERVER\07_ALEMBIC.md

## Назначение
Описать фоновые задачи сервера «Трекер»: что запускается, когда, зачем, как гарантируется единственный запуск и как смотреть историю. Это карта для администратора (что происходит ночью) и для разработчика (как добавить новую задачу).

## Содержание

### Как устроен планировщик
- Библиотека: **APScheduler**.
- Запускается внутри контейнера `api`, в фоновом потоке.
- **Advisory lock PostgreSQL** гарантирует, что только один воркер gunicorn держит блокировку и запускает задачи. Остальные воркеры просто не запускают scheduler.
- Расписания хранятся в таблице `scheduled_tasks`.
- История запусков — в таблице `task_runs`.
- Управление — через страницу `/admin/scheduler`.

### Задачи (TASKS_REGISTRY)

| Имя | Label RU | Cron (default) | Enabled (default) | Что делает |
|---|---|---|---|---|
| `create_future_partitions` | Создание партиций | `0 4 1 * *` | ✅ | Создаёт партиции `records_YYYY_MM` на 12 месяцев вперёд |
| `aggregate_daily_stats` | Агрегация статистики | `0 1 * * *` | ✅ | Пересчитывает `daily_stats` за вчерашний рабочий день |
| `close_stale_sessions` | Автозакрытие зависших сессий | `*/30 * * * *` | ✅ | Закрывает сессии без `session_end` > `stale_session_hours` |
| `cleanup_trash` | Очистка корзины | `0 3 * * *` | ❌ | Физически удаляет soft-deleted записи старше 30 дней |
| `vacuum_analyze_hot_tables` | VACUUM ANALYZE | `0 2 * * 0` | ❌ | Обновляет статистику по горячим таблицам |
| `cleanup_old_admin_logins` | Очистка истории входов | `0 5 1 * *` | ❌ | Удаляет `admin_logins` старше 180 дней |
| `cleanup_old_task_runs` | Очистка истории задач | `30 5 * * 0` | ❌ | Удаляет `task_runs` старше 60 дней |

### Детали по каждой задаче

#### `create_future_partitions`
- **Зачем:** без партиции на текущий месяц запись уйдёт в `records_default`, откуда её сложно достать.
- **Что делает:** цикл по 13 месяцам (текущий + 12 вперёд), `CREATE TABLE IF NOT EXISTS records_YYYY_MM PARTITION OF records FOR VALUES FROM ... TO ...`.
- **Идемпотентно:** если партиция есть — пропускает.
- **Расписание:** 1-го числа каждого месяца в 04:00 UTC.
- **Ошибки:** при ошибке создания одной партиции — продолжает со следующей, логирует.

#### `aggregate_daily_stats`
- **Зачем:** ускорить отчёты за прошлые периоды (считаем по агрегату, а не по сырым `records`).
- **Что делает:** за вчерашний день вызывает `aggregate_range(db, yesterday, yesterday, ...)`, пишет в `daily_stats`.
- **Параметры:** `report_timezone`, `workday_start_hour`, `activity_gap_minutes` — читаются из `app_settings`.
- **Расписание:** каждый день в 01:00 UTC.
- **Возврат:** строка «День YYYY-MM-DD: сессий=N, строк daily_stats=M».

#### `close_stale_sessions`
- **Зачем:** сессия без `session_end` портит отчёты (был случай 17 часов за день).
- **Что делает:** находит сессии, где `session_end IS NULL` и `session_start < now - stale_session_hours`, ставит `session_end = MAX(records.client_ts)` для этой сессии (или `session_start`, если записей нет), `abnormal_termination = True`, пишет в `audit_log`.
- **Параметр:** `stale_session_hours` (из `app_settings`, по умолчанию 2).
- **Расписание:** каждые 30 минут.
- **Известный баг:** `NameError: WorkSession` и `NameError: AuditLog` — не были импортированы внутри функции. Исправлено добавлением `from .models import WorkSession, AuditLog`.

#### `cleanup_trash` (отключена)
- **Что делает:** удаляет `records` и `work_sessions` с `is_deleted = True` старше `days` (по умолчанию 30).
- **Особенность:** `days = 0` — удалить всё содержимое корзины.
- **Параметр:** `supports_days = True`.
- **Enabled:** по умолчанию `False`.

#### `vacuum_analyze_hot_tables` (отключена)
- **Что делает:** `VACUUM ANALYZE` для `records`, `work_sessions`, `admin_logins`, `audit_log`, `task_runs`.
- **Особенность:** требует `AUTOCOMMIT` — нельзя внутри транзакции. Использует `engine.connect().execution_options(isolation_level="AUTOCOMMIT")`.
- **Расписание:** воскресенье 02:00 UTC.

#### `cleanup_old_admin_logins` (отключена)
- **Что делает:** удаляет `admin_logins` старше 180 дней.
- **Параметр:** `supports_days = True`, `default_days = 180`.

#### `cleanup_old_task_runs` (отключена)
- **Что делает:** удаляет `task_runs` старше 60 дней.
- **Параметр:** `supports_days = True`, `default_days = 60`.

### Страница `/admin/scheduler`

**Показывает:**
- Список задач: имя, описание (RU/EN), cron, статус (вкл/выкл), последний запуск, следующий запуск, действия.
- Информацию о scheduler: `is_running`, `is_owner`, `jobs_count`.
- Историю запусков (последние 50) из `task_runs`.

**Действия:**
- **Вкл/выкл** — `POST /admin/scheduler/{name}/toggle` (только admin).
- **Ручной запуск** — `POST /admin/scheduler/{name}/trigger` (admin + operator). Для задач с `supports_days` можно передать `days`.
- **Изменить cron** — `POST /admin/scheduler/{name}/edit` (только admin). Проверка через `CronTrigger.from_crontab`.
- **Reload** — `POST /admin/scheduler/reload` — перечитать расписания из БД.

**Права:**
- `admin` — полный доступ.
- `operator` — просмотр + ручной запуск.
- `viewer` — только просмотр (через `_require_scheduler_role`).
- `hr`, `manager` — нет доступа.

### Advisory lock

- Используется `pg_try_advisory_lock(key)` в `scheduler.py`.
- Ключ — константа (обычно хеш от имени задачи/приложения).
- Только один воркер gunicorn получает блокировку и запускает scheduler.
- Остальные воркеры работают как обычные API-воркеры.
- При падении владельца — блокировка снимается, другой воркер подхватывает.

### История запусков (`task_runs`)

**Поля:**
- `task_name`, `started_at`, `finished_at`, `status`, `message`.

**Статусы:** `success`, `error`, `running`.

**Сообщение:** краткий отчёт задачи (например, «Закрыто зависших сессий: 3 (порог 2ч)»).

### Добавление новой задачи
1. Написать функцию в `server/tasks.py`, принимает `db: Session`, возвращает `str`.
2. Добавить запись в `TASKS_REGISTRY` с `label_ru`, `label_en`, `desc_ru`, `desc_en`, `default_cron`, `default_enabled`.
3. При старте `init_tasks.py` создаст запись в `scheduled_tasks`, если её нет.
4. Scheduler подхватит при `reload` или перезапуске.

### Известные баги и решения
| Баг | Причина | Решение |
|---|---|---|
| `NameError: WorkSession` в `close_stale_sessions` | Не было импорта внутри функции | Добавить `from .models import WorkSession, AuditLog` |
| `PermissionError: tasks.py` | Файл занят редактором/антивирусом | Закрыть редакторы, `copy /y`, `os.replace` |
| `SyntaxError: line 265` | Остаток `), WorkSession` от неудачного патча | Заменить на `)` |
| `500 на /admin/scheduler` | Ошибка в шаблоне или `scheduler.py` | Смотреть `docker compose logs api --tail=100` |

## Ключевые решения
- **APScheduler + advisory lock** — единственный запуск без отдельного контейнера.
- **Расписания в БД** — можно менять без пересборки.
- **История в `task_runs`** — видно, что и когда запускалось, с каким результатом.
- **Критичные задачи включены по умолчанию:** `create_future_partitions`, `aggregate_daily_stats`, `close_stale_sessions`.
- **Остальные отключены** — включаются вручную, если нужны.
- **`supports_days`** — универсальный параметр для задач очистки.
- **`close_stale_sessions` каждые 30 минут** — компромисс между частотой и нагрузкой.
- **`aggregate_daily_stats` ночью** — чтобы днём отчёты считались быстро.
- **`create_future_partitions` 1-го числа** — запас на год вперёд.

## Ссылки на код
- запросить: `server/tasks.py` — все функции задач, `TASKS_REGISTRY`
- запросить: `server/scheduler.py` — APScheduler, advisory lock, `_run_task_wrapper`, `get_scheduler`
- запросить: `server/init_tasks.py` — регистрация задач в `scheduled_tasks`
- запросить: `server/web_admin.py` — роуты `/admin/scheduler/*`
- запросить: `server/templates/scheduler.html` — страница планировщика
- запросить: `server/models.py` — `ScheduledTask`, `TaskRun`
- запросить: `server/aggregation.py` — `aggregate_range` (используется в `aggregate_daily_stats`)

## Открытые вопросы / чего не хватает
- нет данных: точный ключ advisory lock — константа в `scheduler.py`, нужно проверить.
- нет данных: есть ли healthcheck у scheduler — не описан.
- нет данных: что происходит, если scheduler не смог получить lock — не описано.
- нет данных: retention для `task_runs` — 60 дней по умолчанию, но задача отключена.
- не решено: нужен ли отдельный контейнер для scheduler.
- не решено: как быть с задачами, которые выполняются дольше интервала (например, `close_stale_sessions` > 30 мин).
- не решено: нужно ли логировать в `audit_log` ручные запуски — сейчас только `log.info`.
- не решено: должен ли `operator` видеть историю запусков.
- не решено: нужна ли задача `cleanup_old_records` (retention 90 дней).
- не решено: нужна ли задача бэкапа `pg_dump` (обсуждалась, не реализована).

Готово. Один файл выше. Следующий по индексу — 03_SERVER\06_PARTITIONS.md.