# Партиционирование
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\03_MODELS.md, 03_SERVER\07_ALEMBIC.md, 03_SERVER\05_TASKS.md

## Назначение
Описать партиционирование таблицы `records` в PostgreSQL: зачем, как устроено, как создаются партиции, как защищены от Alembic, что делать при сбое. Это критичная часть системы, без неё производительность падает при росте данных.

## Содержание

### Зачем партиционирование
- **Объём:** 50 сотрудников × 6400 записей в день = 320 000 записей в день. За год — 120 млн записей.
- **Проблема обычной таблицы:**
  - `SELECT ... WHERE client_ts >= '2026-08-01'` — сканирует всё.
  - `DELETE FROM records WHERE client_ts < '2025-01-01'` — часами.
- **Решение — партиционирование:**
  - `records` разбита на `records_YYYY_MM` по месяцам.
  - PostgreSQL сам маршрутизирует INSERT в нужную партицию.
  - Запрос по диапазону дат сканирует только нужные партиции (partition pruning).
  - Удаление старого месяца — `DROP TABLE records_2025_09` — мгновенно.

### Как устроено
```sql
CREATE TABLE records (
    id BIGSERIAL,
    record_uid VARCHAR(64) NOT NULL,
    session_uid VARCHAR(64) NOT NULL,
    computer_id INTEGER NOT NULL,
    kind VARCHAR(32) NOT NULL,
    data TEXT,
    client_ts TIMESTAMPTZ NOT NULL,
    ...
) PARTITION BY RANGE (client_ts);
Партиции:

records_2025_01 … records_2025_12

records_2026_01 … records_2026_12

records_2027_01 … records_2027_12

records_default — для дат вне диапазона.

Границы партиции:

sql
CREATE TABLE records_2026_10 PARTITION OF records
FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
Каждая партиция покрывает свой месяц в UTC.

Уникальные индексы на партиционированной таблице
record_uid — уникален на всю таблицу. PostgreSQL 16 поддерживает уникальный индекс на партиционированной таблице, если он включает ключ партиционирования. Поэтому проверка дубликатов идёт по всей таблице, а не по партиции.

computer_id — FK работает.

Индексы наследуются: ix_records_computer_ts (computer_id, client_ts), ix_records_session_uid, ix_records_record_uid.

Создание партиций
Автоматически (задача планировщика)
Задача create_future_partitions (см. 03_SERVER\05_TASKS.md).

Запускается 1-го числа каждого месяца в 04:00 UTC.

Создаёт партиции на 12 месяцев вперёд (плюс текущий = 13).

Идемпотентно: CREATE TABLE IF NOT EXISTS + проверка pg_class.

Критично: если партиции нет, запись уйдёт в records_default, откуда её потом сложно достать.

Вручную (при необходимости)
sql
CREATE TABLE records_2028_01 PARTITION OF records
FOR VALUES FROM ('2028-01-01') TO ('2028-02-01');
Или через планировщик: /admin/scheduler → create_future_partitions → «Запустить сейчас».

Защита от Alembic: include_object
Проблема: Alembic --autogenerate видит records_YYYY_MM в information_schema как обычные таблицы. В Base.metadata их нет (только родительская records). Alembic пытается удалить все партиции при генерации любой миграции → катастрофа.

Решение: хук include_object в server/alembic/env.py.

python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True
Подключается в context.configure(...) в обоих режимах (offline и online):

python
context.configure(
    ...,
    include_object=include_object,
)
Что исключает:

Все таблицы, начинающиеся на records_, кроме самой records.

Партиции records_YYYY_MM.

Партицию records_default.

Что НЕ исключает:

Таблицу records (родительскую).

Другие таблицы, случайно не начинающиеся на records_.

Известные проблемы и решения
Проблема	Причина	Решение
Alembic пытается удалить партиции	Нет include_object в env.py	Добавить include_object в оба режима
records_default заполняется	Нет партиции на текущий месяц	Запустить create_future_partitions
Миграция содержит op.drop_table('records_2025_01')	Autogenerate без фильтра	Вручную удалить эти операции из миграции
Ошибка при CREATE TABLE ... PARTITION OF	Партиция уже существует	Использовать IF NOT EXISTS + проверка pg_class
record_uid дублируется между партициями	Нет уникального индекса на всю таблицу	Проверить, что индекс уникален и включает ключ партиционирования
Проверка состояния партиций
Список всех партиций:

sql
SELECT tablename FROM pg_tables
WHERE tablename LIKE 'records_%' AND tablename != 'records'
ORDER BY tablename;
Размер партиций:

sql
SELECT relname AS partition,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
WHERE relname LIKE 'records_%'
ORDER BY pg_total_relation_size(relid) DESC;
Есть ли записи в records_default:

sql
SELECT COUNT(*) FROM records_default;
Если > 0 — это проблема: значит, на какой-то месяц не было партиции.

Как достать записи из records_default и переложить в партицию:

Создать партицию на нужный месяц (если ещё нет).

INSERT INTO records SELECT * FROM records_default WHERE client_ts >= 'YYYY-MM-01' AND client_ts < 'YYYY-MM+1-01';

DELETE FROM records_default WHERE client_ts >= 'YYYY-MM-01' AND client_ts < 'YYYY-MM+1-01';

Retention сырых данных
Обсуждалось: хранить сырые records 90 дней, агрегаты — вечно.

Не реализовано.

Если реализовать — через DROP TABLE records_YYYY_MM для месяцев старше 90 дней (быстро) или через DELETE (медленно).

Другие hot-таблицы
daily_stats — обсуждалось партиционирование (P3), не реализовано.

audit_log — не партиционирован, но retention через cleanup_old_* (не включено).

task_runs — не партиционирован, retention через cleanup_old_task_runs (не включено).

Ключевые решения
Партиционирование records по client_ts — покрывает основной объём данных.

Гранулярность — месяц. Компромисс: не слишком много партиций, не слишком мало.

Запас на 12 месяцев вперёд. Задача create_future_partitions держит буфер.

records_default как страховка. Но лучше в него не попадать.

include_object в обоих режимах Alembic. Критично для autogenerate.

CREATE TABLE IF NOT EXISTS + проверка pg_class. Идемпотентность создания.

Уникальный record_uid на всю таблицу. Идемпотентность по всей системе, а не по партиции.

Ссылки на код
запросить: server/alembic/env.py — include_object, run_migrations_offline, run_migrations_online

запросить: server/tasks.py — create_future_partitions

запросить: server/models.py — модель Record (без __table_args__ с партиционированием — оно в миграции)

запросить: server/alembic/versions/939e3d0b6f4c_partition_records_by_month.py — миграция партиционирования

запросить: server/web_admin.py — _build_flat_records, работа с records через ORM

Открытые вопросы / чего не хватает
нет данных: retention сырых records — обсуждался 90 дней, не реализован.

нет данных: есть ли записи в records_default сейчас — нужно проверить SQL-запросом.

нет данных: партиционированы ли daily_stats — нет, в планах (P3).

нет данных: как удаляются старые партиции — вручную через DROP TABLE, автоматики нет.

не решено: нужна ли автоматическая задача drop_old_partitions (retention).

не решено: переводить ли daily_stats и audit_log на партиционирование.

не решено: как быть с records_default — периодически проверять и чистить.

не решено: нужно ли разделить records дополнительно по kind (activity/window/idle) — избыточно.

не решено: как архивировать старые партиции в отдельную БД.

не решено: использовать ли pg_partman для управления партициями — сейчас всё на своём коде.

Готово. Один файл выше. Следующий по индексу — 03_SERVER\07_ALEMBIC.md.