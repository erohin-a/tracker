# Миграции (Alembic)
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\03_MODELS.md, 03_SERVER\06_PARTITIONS.md

## Назначение
Описать систему миграций Alembic в «Трекере»: список миграций, цепочку, правила autogenerate, защиту партиций, типовые ошибки и команды. Это эталон для разработчика, который меняет схему БД.

## Содержание

### Что такое Alembic в проекте
- Alembic — инструмент миграций для SQLAlchemy.
- Все изменения схемы БД — только через миграции. Не через `create_all`.
- Расположение: `server/alembic/`.
- Конфиг: `server/alembic.ini`.
- Версии: `server/alembic/versions/`.
- URL БД берётся из `settings.database_url`, а не из `alembic.ini`.

### Список миграций (6 штук)

| # | Файл | Что делает |
|---|---|---|
| 1 | `35d67a73f181_baseline.py` | Базовая схема: все таблицы (`computers`, `employees`, `departments`, `work_sessions`, `records`, `bootstrap_tokens`, `audit_log`, `app_settings`, `calendar_days`, `admin_users`, `admin_logins`, `scheduled_tasks`, `task_runs`, `api_keys`, `daily_stats`, `backup_config`) |
| 2 | `939e3d0b6f4c_partition_records_by_month.py` | Партиционирование `records` по месяцам (2025–2027 + `records_default`) |
| 3 | `ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py` | Добавление `schedules`, soft-delete полей в `records` и `work_sessions` |
| 4 | `2602b71902d4_add_employee_settings.py` | Создание `employee_settings` |
| 5 | `b02da1230e4d_add_computer_soft_delete.py` | Soft-delete для `computers` (`deleted_at`, `deleted_by`) |
| 6 | `0f13ad394b65_add_admin_users_department_id.py` | Добавление `department_id` в `admin_users` (для роли manager) |

### Цепочка миграций
35d67a73f181 (baseline)
↓
939e3d0b6f4c (partition records)
↓
ecb1e3f89300 (schedules, soft delete)
↓
2602b71902d4 (employee_settings)
↓
b02da1230e4d (computer soft delete)
↓
0f13ad394b65 (admin_users.department_id) ← head

text

Проверка текущей ревизии:
```powershell
docker compose exec -T api alembic -c /app/server/alembic.ini current
env.py — ключевые моменты
Путь к проекту:

python
_HERE = os.path.dirname(os.path.abspath(__file__))     # /app/server/alembic
_SERVER_DIR = os.path.dirname(_HERE)                    # /app/server
_APP_DIR = os.path.dirname(_SERVER_DIR)                 # /app
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)
Нужно, чтобы from server.models import Base работал и в контейнере, и локально.

URL БД из настроек:

python
config.set_main_option("sqlalchemy.url", settings.database_url)
Эталон метаданных:

python
target_metadata = Base.metadata
Защита партиций — include_object:

python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True
Подключается в context.configure(...) в обоих режимах:

run_migrations_offline — include_object=include_object

run_migrations_online — include_object=include_object

Режимы:

offline — alembic upgrade head --sql — генерирует SQL без подключения к БД.

online — обычный alembic upgrade head — применяет к БД.

script.py.mako — шаблон миграции
На английском, без русских комментариев. Изначально был русский, но при генерации на Windows кодировка ломалась — получались «крокозябры» в docstring. Английский вариант исключает проблему.

Содержит:

docstring с message, up_revision, down_revision, create_date.

revision, down_revision, branch_labels, depends_on.

def upgrade() и def downgrade().

Команды
Создать миграцию:

powershell
docker compose exec -T api alembic -c /app/server/alembic.ini revision --autogenerate -m "описание"
Применить все миграции:

powershell
docker compose exec -T api alembic -c /app/server/alembic.ini upgrade head
Откатить одну:

powershell
docker compose exec -T api alembic -c /app/server/alembic.ini downgrade -1
Текущая ревизия:

powershell
docker compose exec -T api alembic -c /app/server/alembic.ini current
История:

powershell
docker compose exec -T api alembic -c /app/server/alembic.ini history
SQL без применения:

powershell
docker compose exec -T api alembic -c /app/server/alembic.ini upgrade head --sql > migrate.sql
Правило: всегда проверять миграцию перед применением
После revision --autogenerate:

Открыть сгенерированный файл.

Проверить, нет ли операций op.drop_table('records_YYYY_MM').

Проверить, нет ли op.drop_table('records_default').

Если есть — удалить вручную.

Проверить, что нет лишних drop_column, alter_column для полей, которые не менялись.

Только после этого — upgrade head.

Известные проблемы и решения
Проблема	Причина	Решение
Autogenerate пытается удалить партиции records_YYYY_MM	Нет include_object в env.py	Добавить include_object в оба режима
В миграции 37 операций drop_table	Autogenerate без фильтра	Очистить миграцию вручную Python-патчером
«Крокозябры» в docstring миграции	Русские комментарии в .mako + Windows-кодировка	Переписать script.py.mako на английский
ModuleNotFoundError: No module named 'server'	Неверный sys.path	Добавить _APP_DIR в sys.path в env.py
Alembic не видит таблицы	target_metadata не тот Base	Проверить импорт from server.models import Base
Миграция падает на CREATE TABLE ... PARTITION	Партиция уже есть	Использовать IF NOT EXISTS в ручных миграциях
Партиционирование в миграциях
Миграция 939e3d0b6f4c_partition_records_by_month.py:

Создаёт партиции records_2025_01 … records_2027_12 + records_default.

Цикл по годам и месяцам.

Для каждой партиции — CREATE TABLE records_YYYY_MM PARTITION OF records FOR VALUES FROM ... TO ....

Идемпотентность: IF NOT EXISTS.

После этой миграции любые дальнейшие миграции должны проходить с include_object. Иначе Alembic попытается удалить все партиции.

Что делать, если миграция сломала БД
Сделать бэкап (если возможно):

powershell
docker compose exec -T db pg_dump -U tracker tracker > backup.sql
Откатить:

powershell
docker compose exec -T api alembic -c /app/server/alembic.ini downgrade -1
Если откат не работает — восстановить из бэкапа:

powershell
Get-Content backup.sql | docker compose exec -T db psql -U tracker -d tracker
Исправить миграцию и применить снова.

Что НЕ делать
Не использовать create_all. Только Alembic.

Не менять models.py без миграции. Иначе схема разойдётся с БД.

Не применять autogenerate без проверки. Особенно с партициями.

Не удалять миграции из цепочки. Только добавлять новые.

Не редактировать применённые миграции. Если нужно исправить — новая миграция.

Ключевые решения
6 миграций, линейная цепочка. Никаких ветвлений.

env.py с include_object. Критично для партиций.

URL БД из settings, а не из alembic.ini. Один источник правды.

script.py.mako на английском. Защита от «крокозябр».

compare_type=True. Ловит изменения типов колонок.

poolclass=pool.NullPool. Alembic не держит пул соединений.

Проверка миграции перед применением. Обязательный шаг.

Откат через downgrade -1. Работает, но нужен бэкап.

Ссылки на код
запросить: server/alembic.ini — конфиг

запросить: server/alembic/env.py — include_object, run_migrations_offline, run_migrations_online

запросить: server/alembic/script.py.mako — шаблон

запросить: server/alembic/versions/ — 6 миграций

запросить: server/models.py — Base

запросить: server/config.py — settings.database_url

Открытые вопросы / чего не хватает
нет данных: точные ревизии всех 6 миграций — часть известна, часть нужно проверить командой history.

нет данных: есть ли миграции после 0f13ad394b65 — нужно проверить current.

нет данных: как часто генерируются миграции — по мере изменения моделей.

не решено: нужна ли миграция для партиционирования daily_stats.

не решено: нужно ли использовать alembic merge при ветвлении — пока не требовалось.

не решено: как быть с миграциями данных (не только схемы) — только вручную через SQL.

не решено: нужен ли отдельный скрипт для проверки миграций в CI.

не решено: как автоматизировать проверку records_* в новых миграциях — вручную.

не решено: нужно ли логировать применение миграций в audit_log — нет.

Готово. Один файл выше. Следующий по индексу — 03_SERVER\08_I18N.md.