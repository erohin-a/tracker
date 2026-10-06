# Локальная БД
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 04_CLIENT\03_SYNC.md, 04_CLIENT\02_COLLECTOR.md, 03_SERVER\03_MODELS.md

## Назначение
Описать локальную SQLite-базу клиента «Трекер»: зачем она нужна, как устроена, какие таблицы и функции, как работает офлайн-режим и восстановление после сбоев. Это эталон для разработчика, который дорабатывает буфер, и для администратора, который разбирается с «данные не отправляются».

## Содержание

### Зачем нужна локальная БД
- **Офлайн-first:** если сервер недоступен, данные не теряются.
- **Накопление:** клиент может неделями работать без сети, потом отправить всё.
- **Быстрая запись:** SQLite с WAL не блокирует читателей и писателей.
- **Восстановление:** после краха клиента данные не теряются.
- **Метаданные:** активная сессия, последняя активность, состояние паузы.

### Расположение и параметры

**Файл:** `%APPDATA%\Tracker\data.db` (Windows) или `~/.tracker/data.db` (Linux).

**Режимы PRAGMA:**
```sql
PRAGMA journal_mode=WAL;         -- Write-Ahead Logging
PRAGMA busy_timeout=5000;        -- ждать 5 сек при блокировке
PRAGMA synchronous=NORMAL;       -- компромисс скорость/надёжность
PRAGMA foreign_keys=ON;          -- включить FK
PRAGMA journal_size_limit=67108864;  -- 64 МБ лимит WAL
check_same_thread=False — соединение используется из разных потоков, безопасность обеспечивается через threading.local() и threading.Lock.

Таймаут соединения: 10 секунд (sqlite3.connect(..., timeout=10)).

Схема БД
Таблица sessions
Поле	Тип	Описание
session_uid	TEXT PK	UUID v4
session_start	TEXT	ISO 8601 UTC
session_end	TEXT, nullable	ISO 8601 UTC
abnormal_termination	INTEGER (0/1)	аварийное закрытие
pause_seconds	INTEGER, default 0	сумма кнопки «Пауза»
synced	INTEGER (0/1)	отправлено ли на сервер
Таблица records
Поле	Тип	Описание
record_uid	TEXT PK	UUID v4
session_uid	TEXT	ссылка на сессию
kind	TEXT	activity / window / idle / idle_end
data	TEXT	JSON
client_ts	TEXT	ISO 8601 UTC
signature	TEXT, nullable	HMAC-SHA256
synced	INTEGER (0/1)	отправлено ли
poisoned	INTEGER (0/1)	permanent reject от сервера
Индексы:

ix_records_synced ON records(synced, poisoned)

ix_records_session ON records(session_uid)

Таблица meta
Поле	Тип	Описание
key	TEXT PK	
value	TEXT	
Ключи meta:

Ключ	Что хранит
active_session	UID текущей незакрытой сессии (или пусто)
last_activity	ISO-время последней активности (для idle-детекта)
pause.started_at	ISO-время начала паузы (или пусто)
idle_close_minutes	Порог авто-закрытия сессии (с сервера)
last_sync	ISO-время последней успешной синхронизации
vacuum_counter	Счётчик для VACUUM раз в 10 циклов
Инициализация (init_db)
Порядок:

Проверка существования файла БД.

PRAGMA integrity_check — проверка целостности.

Если БД повреждена — карантин (переименовать с суффиксом .corrupt.YYYYMMDD_HHMMSS).

PRAGMA wal_checkpoint(TRUNCATE) — сброс WAL.

conn.executescript(SCHEMA) — создание таблиц.

_migrate(conn) — миграции (добавление новых полей).

Карантин (_quarantine_corrupt_db):

Переименовывает data.db, data.db-wal, data.db-shm в *.corrupt.YYYYMMDD_HHMMSS.

Создаётся новая пустая БД.

Данные теряются, но клиент запускается.

Миграции (_migrate)
Простой способ добавления новых полей в SQLite:

python
def _migrate(conn):
    # records.poisoned
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(records);")}
    if "poisoned" not in cols:
        conn.execute("ALTER TABLE records ADD COLUMN poisoned INTEGER DEFAULT 0;")

    # sessions.pause_seconds
    scols = {r["name"] for r in conn.execute("PRAGMA table_info(sessions);")}
    if "pause_seconds" not in scols:
        conn.execute("ALTER TABLE sessions ADD COLUMN pause_seconds INTEGER DEFAULT 0;")
Правила:

Проверяем наличие поля через PRAGMA table_info.

Если поля нет — ALTER TABLE ADD COLUMN.

Не удаляем и не меняем существующие поля — только добавляем.

Для полного сброса — quarantine + новая БД.

Функции работы с meta
python
def set_meta(key, value):
    get_conn().execute(
        "INSERT INTO meta(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )

def get_meta(key, default=None):
    row = get_conn().execute(
        "SELECT value FROM meta WHERE key=?", (key,)
    ).fetchone()
    return row["value"] if row else default
Функции работы с сессиями
start_session(uid)
INSERT OR IGNORE INTO sessions(session_uid, session_start, abnormal_termination, synced) VALUES(?,?,0,0).

Устанавливает meta.active_session = uid.

Устанавливает meta.last_activity = now.

close_session(uid, abnormal=False)
UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 WHERE session_uid=?.

session_end = now (ISO UTC).

Очищает meta.active_session, если это та же сессия.

close_session_at(uid, end_iso, abnormal=True)
UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 WHERE session_uid=? AND session_end IS NULL.

Закрывает конкретным временем (не now).

Используется при аварийном закрытии — end_iso = last_activity.

Очищает meta.active_session.

get_active_session_uid()
Возвращает meta.active_session или None.

get_session_start(uid)
Возвращает session_start для указанной сессии.

get_session_end(uid)
Возвращает session_end или None.

get_last_session_record_ts(uid)
SELECT MAX(client_ts) FROM records WHERE session_uid = ?.

Источник 1 для определения last_activity.

Аварийное завершение (detect_abnormal_termination)
Назначение: закрыть «висящую» сессию от прошлого запуска клиента.

Алгоритм:

Проверить meta.active_session. Если пусто — выход.

Определить last_activity:

Источник 1: MAX(client_ts) из records для этой сессии (самый надёжный).

Источник 2: meta.last_activity.

Источник 3: session_start (крайний случай).

Если с последней активности прошло < 12 часов — ничего не делаем (возможно, тот же рабочий день, пользователь сам разберётся через UnclosedSessionDialog).

Если ≥ 12 часов — закрываем сессию:

close_session_at(uid, last_activity, abnormal=True).

log.warning("Abnormal termination of %s — closing at last activity %s", ...).

Ключевое отличие от старой версии:

Раньше: session_end = now → давало 17 часов работы за ночь.

Сейчас: session_end = last_activity → реальное время последней активности.

Порог 12 часов: если сессия была брошена 3 часа назад (например, пользователь ушёл на обед и клиент перезапустился) — диалог даст решить вручную.

Авто-закрытие по idle (auto_close_idle_session)
Назначение: закрыть сессию, если пользователь бездействует дольше idle_close_minutes (по умолчанию 30 мин).

Алгоритм:

Проверить meta.active_session. Если пусто — выход.

Взять meta.last_activity. Если пусто — выход.

Если now - last_activity < idle_minutes * 60 — выход.

Иначе:

UPDATE sessions SET session_end=?, abnormal_termination=1, synced=0 WHERE session_uid=? AND session_end IS NULL.

end_iso = last_activity (не now).

Очистить meta.active_session.

log.warning("Auto-closed idle session %s (last activity %s)", ...).

Возвращает UID закрытой сессии или None.

Вызывается: раз в минуту из main.py (QTimer).

Настройка idle_close_minutes: приходит с сервера через client-config, хранится в meta. get_idle_close_minutes(default=30) читает и валидирует (5–480).

Пауза
start_pause()
set_meta("pause.started_at", now).

end_pause(session_uid)
Читает pause.started_at.

Считает длительность dur = now - started.

UPDATE sessions SET pause_seconds = COALESCE(pause_seconds, 0) + ? WHERE session_uid = ?.

Очищает pause.started_at.

Возвращает dur (секунды).

Идемпотентно: если пауза не была активна — return 0.

is_paused()
bool(get_meta("pause.started_at")).

get_pause_seconds(session_uid)
Читает pause_seconds из БД.

Прибавляет текущую активную паузу, если она идёт.

Возвращает max(0, total).

clear_pause_state()
Полный сброс pause.started_at (для новой сессии).

Работа с записями
insert_record(record_uid, session_uid, kind, data_json, client_ts, signature)
INSERT OR IGNORE INTO records(...) VALUES(?,?,?,?,?,?).

touch_activity() — обновляет meta.last_activity.

fetch_unsynced(limit=500)
SELECT * FROM records WHERE synced=0 AND poisoned=0 ORDER BY client_ts ASC LIMIT ?.

Используется в SyncWorker.

apply_sync_result(accepted, permanent_rejected)
Транзакция:

accepted → UPDATE records SET synced=1 WHERE record_uid IN (...).

permanent_rejected → UPDATE records SET synced=1, poisoned=1 WHERE record_uid IN (...).

COMMIT при успехе, ROLLBACK при ошибке.

fetch_unsynced_sessions()
SELECT * FROM sessions WHERE synced=0.

mark_session_synced(uid)
UPDATE sessions SET synced=1 WHERE session_uid=?.

Лимит размера (enforce_size_limit)
Назначение: не дать БД расти бесконечно.

Алгоритм:

Считает размер data.db + data.db-wal + data.db-shm.

Если < MAX_DB_SIZE_MB (500 МБ) — выход.

Иначе:

DELETE FROM records WHERE record_uid IN (SELECT record_uid FROM records WHERE synced=1 ORDER BY client_ts ASC LIMIT 50000).

PRAGMA wal_checkpoint(TRUNCATE).

vacuum_counter++. Если % 10 == 0 — VACUUM.

log.warning("DB > %d MB, pruning", ...).

Почему 50000: удаляем пачками, чтобы не блокировать надолго.

Почему VACUUM раз в 10: VACUUM тяжёлый, не нужно каждый раз.

Что удаляется: только синхронизированные записи (synced=1). Несинхронизированные — остаются.

Транзакции
apply_sync_result — единственная функция с явной транзакцией:

python
conn.execute("BEGIN")
try:
    # ...
    conn.execute("COMMIT")
except Exception:
    conn.execute("ROLLBACK")
    raise
Остальные операции — isolation_level=None (autocommit) в connect(), каждая операция коммитится сразу. Для метаданных и одиночных записей этого достаточно.

Восстановление после краха
Сценарий: клиент упал, ПК выключили.

Что происходит при следующем запуске:

init_db() — проверка целостности.

detect_abnormal_termination():

Если сессия была активна и прошло < 12 ч — UnclosedSessionDialog.

Если ≥ 12 ч — автозакрытие по last_activity.

clear_pause_state() — сброс «зависшей» паузы.

SyncWorker отправляет накопленное.

Диалог UnclosedSessionDialog:

Три варианта:

Продолжить — продлить старую сессию.
Завершить по последней активности (рекомендуется) — session_end = last_activity.
Завершить сейчас — session_end = now.
Известные проблемы и решения
Проблема	Причина	Решение
pause_seconds > total_sec	Двойное вычитание паузы	Не вычитать в _analyze_session
17 часов за день	close_session ставил end = now	close_session_at(last_activity)
database is locked	Долгая транзакция	busy_timeout=5000
disk I/O error	Антивирус блокирует файл	Добавить папку в исключения
Повреждённая БД	Краш во время записи	integrity_check + карантин
WAL растёт бесконечно	Нет checkpoint	PRAGMA wal_checkpoint(TRUNCATE)
no such table	Не вызван init_db	Вызвать при старте
Дубликаты record_uid	INSERT OR IGNORE не сработал	Проверить PK
Проверка БД вручную
Открыть SQLite:

powershell
sqlite3 "$env:APPDATA\Tracker\data.db"
Проверить размер:

sql
SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size();
Проверить unsynced:

sql
SELECT COUNT(*) FROM records WHERE synced = 0;
SELECT COUNT(*) FROM sessions WHERE synced = 0;
Проверить poisoned:

sql
SELECT COUNT(*) FROM records WHERE poisoned = 1;
Проверить meta:

sql
SELECT * FROM meta;
Резервная копия
Скопировать файл:

powershell
Copy-Item "$env:APPDATA\Tracker\data.db" "$env:APPDATA\Tracker\data.db.backup"
Важно: копировать, когда клиент закрыт (иначе WAL может быть не сброшен).

Ключевые решения
SQLite + WAL — офлайн-first, транзакции, не блокирует читателей.

check_same_thread=False + threading.local — доступ из разных потоков.

busy_timeout=5000 — ждём при блокировке, не падаем.

PRAGMA integrity_check при старте — обнаружение повреждений.

Карантин повреждённой БД — клиент запускается, данные теряются.

Миграции через ALTER TABLE — просто, без Alembic.

meta как key/value — гибко для новых настроек.

close_session_at(last_activity) — защита от «17 часов».

detect_abnormal_termination с порогом 12 ч — не трогаем свежие сессии.

auto_close_idle_session раз в минуту — не копим «висящие».

enforce_size_limit с 500 МБ — не даём БД расти бесконечно.

apply_sync_result в транзакции — консистентность.

Ссылки на код
запросить: client/db.py — вся логика SQLite

запросить: client/config.py — DB_PATH, MAX_DB_SIZE_MB, IDLE_CLOSE_MINUTES

запросить: client/main.py — вызовы init_db, detect_abnormal_termination, auto_close_idle_session

запросить: client/unclosed_dialog.py — диалог восстановления

запросить: client/sync.py — использование fetch_unsynced, apply_sync_result

запросить: client/collector.py — insert_record, touch_activity

Открытые вопросы / чего не хватает
нет данных: есть ли PRAGMA foreign_keys на самом деле (в коде — ON, но FK не объявлены в схеме).

нет данных: точный размер MAX_DB_SIZE_MB — 500 МБ по коду.

нет данных: что происходит при VACUUM — блокирует ли запись.

нет данных: тестировалась ли БД на больших объёмах (100+ МБ).

не решено: нужна ли поддержка шифрования локальной БД (SQLCipher).

не решено: как быть с миграциями при добавлении нового поля в records.

не решено: нужен ли ANALYZE для оптимизации запросов.

не решено: как обрабатывать disk I/O error при антивирусе.

не решено: нужно ли периодическое VACUUM по расписанию.

не решено: как быть с очень большими сессиями (например, 12 часов) — рекорды уходят в БД.

не решено: должен ли enforce_size_limit удалять poisoned-записи.

не решено: где хранить last_sync — в meta или в отдельной таблице.

Готово. Один файл выше. Следующий по индексу — 04_CLIENT\05_REMINDERS.md.