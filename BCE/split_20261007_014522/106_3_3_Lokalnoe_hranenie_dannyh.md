<!-- Часть 106 из 1409 -->
# 3.3. Локальное хранение данных
*Хлебные крошки:* Техническое задание на разработку системы учёта рабочего времени удалённых сотрудников «Трекер» (расширенная версия) / 3. Клиентский модуль / 3.3. Локальное хранение данных

[◀ 3.2. Сбор данных](105_3_2_Sbor_dannyh.md) | [Оглавление](00_BCE_INDEX.md) | [3.4. Синхронизация с сервером ▶](107_3_4_Sinhronizatsiya_s_serverom.md)

---

### 3.3. Локальное хранение данных

#### 3.3.1. Структура базы данных SQLite

```sql
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,           -- UUID записи для синхронизации
    type TEXT NOT NULL,                   -- 'session', 'program_usage', 'activity'
    session_uuid TEXT,                    -- Ссылка на сессию (для program_usage и activity)
    computer_id TEXT NOT NULL,
    employee_last_name TEXT NOT NULL,
    employee_first_name TEXT NOT NULL,
    employee_middle_name TEXT,
    data TEXT NOT NULL,                   -- JSON-сериализованные данные записи
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_synced BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMP
);

CREATE INDEX idx_is_synced ON records(is_synced);
CREATE INDEX idx_created_at ON records(created_at);
CREATE INDEX idx_session_uuid ON records(session_uuid);
```

**Обоснование:** Использование JSON для поля `data` позволяет гибко менять схему без миграций. Поле `uuid` обеспечивает идемпотентность при повторной отправке.

#### 3.3.2. Режим WAL и конкурентный доступ

- **Включить режим WAL:** `PRAGMA journal_mode=WAL;`
- **Установить таймаут блокировки:** `PRAGMA busy_timeout=5000;` (5 секунд).
- **Обоснование:** WAL позволяет читателям и писателям работать параллельно, что критически важно при одновременной записи из потока сбора данных и чтении из потока синхронизации.
- **Проблема:** WAL-файлы могут накапливаться при аварийном завершении. **Решение:** При запуске клиента выполнять `PRAGMA wal_checkpoint(TRUNCATE);`.

#### 3.3.3. Расположение файлов

| Файл | Windows | Linux |
|------|---------|-------|
| `data.db` | `%APPDATA%/Tracker/data.db` | `~/.tracker/data.db` |
| `config.json` | `%APPDATA%/Tracker/config.json` | `~/.tracker/config.json` |
| `logs/` | `%APPDATA%/Tracker/logs/` | `~/.tracker/logs/` |

**Права доступа:**
- Windows: Файлы создаются с правами текущего пользователя.
- Linux: `chmod 600` для `data.db` и `config.json`.

