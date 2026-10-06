<!-- Часть 111 из 1409 -->
# 4.2. Хранение данных
*Хлебные крошки:* Техническое задание на разработку системы учёта рабочего времени удалённых сотрудников «Трекер» (расширенная версия) / 4. Серверный модуль / 4.2. Хранение данных

[◀ 4.1. Приём данных](110_4_1_Priem_dannyh.md) | [Оглавление](00_BCE_INDEX.md) | [4.3. Объединение записей сотрудника ▶](112_4_3_Obedinenie_zapisey_sotrudnika.md)

---

### 4.2. Хранение данных

#### 4.2.1. Схема базы данных (обновлённая)

**Таблица `employees`:**

```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    "1c_id" TEXT UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `computers`:**

```sql
CREATE TABLE computers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    computer_id TEXT UNIQUE NOT NULL,
    employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    machine_name TEXT,
    mac_address TEXT,
    os_info TEXT,
    last_seen_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `work_sessions`:**

```sql
CREATE TABLE work_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    employee_id INTEGER REFERENCES employees(id),
    computer_id TEXT REFERENCES computers(computer_id),
    session_start TIMESTAMP NOT NULL,
    session_end TIMESTAMP,
    pc_boot_time TIMESTAMP,
    pc_shutdown_time TIMESTAMP,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_by TEXT,
    edited_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `program_usage`:**

```sql
CREATE TABLE program_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    session_id INTEGER REFERENCES work_sessions(id) ON DELETE CASCADE,
    process_name TEXT NOT NULL,
    window_title TEXT,
    usage_seconds INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `activity_log`:**

```sql
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    session_id INTEGER REFERENCES work_sessions(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('keyboard', 'mouse')),
    active_seconds INTEGER NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `sync_log`:**

```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    computer_id TEXT NOT NULL,
    employee_id INTEGER REFERENCES employees(id),
    records_count INTEGER NOT NULL,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT
);
```

**Таблица `audit_log`:**

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.2. Миграции

- Использовать **Alembic** для управления миграциями схемы.
- Все изменения схемы — только через миграции.
- При развёртывании: `alembic upgrade head`.

