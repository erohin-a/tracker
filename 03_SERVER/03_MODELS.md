### Файл: 03_SERVER\03_MODELS.md

```markdown
# Модели БД
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\07_ALEMBIC.md, 03_SERVER\06_PARTITIONS.md

## Назначение
Описать структуру базы данных «Трекера»: все таблицы, поля, связи, особенности (партиционирование, soft delete, timezone). Это эталон для разработчика, который вносит изменения в схему, и для администратора, который пишет SQL-проверки.

## Содержание

### Общие принципы
- ORM — SQLAlchemy 2.0 (`server/models.py`).
- Base — `declarative_base()`.
- Все timestamps — `DateTime(timezone=True)` (UTC).
- `_utcnow()` — `datetime.now(timezone.utc)` как default.
- Идентификаторы: PK — `Integer` или `BigInteger`, уникальные — `String(64)` (UID).
- Soft delete — через `is_deleted` / `deleted_at` / `deleted_by`.
- Партиционирование — только `records`.

### Список таблиц
| Таблица | Назначение | Особенности |
|---|---|---|
| `departments` | Отделы | |
| `employees` | Сотрудники | `schedule_id` FK |
| `computers` | ПК | Fernet-секрет, soft delete |
| `work_sessions` | Сессии | soft delete, `pause_seconds` |
| `records` | Записи активности | **партиционирована** по `client_ts` |
| `bootstrap_tokens` | Bootstrap-токены | хеш, TTL, одноразовые |
| `client_versions` | Версии клиента | для автообновления |
| `audit_log` | Аудит | все действия админов |
| `app_settings` | Настройки | key/value |
| `calendar_days` | Календарь | рабочие/нерабочие дни |
| `admin_users` | Пользователи админки | bcrypt, роль, `department_id` |
| `admin_logins` | История входов | успех/отказ |
| `scheduled_tasks` | Задачи планировщика | cron, enabled |
| `task_runs` | История запусков задач | статус, сообщение |
| `api_keys` | Ключи для внешних интеграций | хеш, scopes |
| `daily_stats` | Агрегаты по дням | для быстрых отчётов |
| `backup_config` | Настройки бэкапов | расписание, retention |
| `employee_settings` | Персональные настройки напоминаний | nullable = «как у всех» |
| `schedules` | Графики работы | шаблоны планового времени |

### Детали по таблицам

#### `departments`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `name` | String(128), unique | |
| `is_active` | Boolean, default True | |
| `schedule_id` | FK → `schedules.id` | График отдела (nullable) |
| `created_at` | DateTime | |

#### `employees`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `full_name` | String(255) | ФИО целиком |
| `last_name` | String(50) | |
| `first_name` | String(50) | |
| `middle_name` | String(50) | |
| `external_id` | String(64), unique | 1C ID |
| `is_active` | Boolean | |
| `department_id` | FK → `departments.id` | |
| `schedule_id` | FK → `schedules.id` | |
| `fired_at` | DateTime, nullable | дата увольнения |

**Soft delete:** через `fired_at`. Уволенный сотрудник остаётся в БД.

#### `computers`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `computer_uid` | String(64), unique, index | UUID v4 |
| `hostname` | String(255) | |
| `os_info` | String(255) | |
| `client_version` | String(32) | |
| `client_secret_enc` | Text | Fernet-шифрование |
| `secret_version` | Integer, default 1 | |
| `registered_at` | DateTime | |
| `last_seen_at` | DateTime | heartbeat |
| `is_active` | Boolean | |
| `employee_id` | FK → `employees.id` | привязка |
| `assigned_at` | DateTime | |
| `deleted_at` | DateTime | soft delete |
| `deleted_by` | String(128) | |

#### `work_sessions`
| Поле | Тип | Описание |
|---|---|---|
| `id` | BigInteger PK | |
| `session_uid` | String(64), unique, index | |
| `computer_id` | FK → `computers.id` | |
| `employee_id` | FK → `employees.id` | |
| `session_start` | DateTime | |
| `session_end` | DateTime, nullable | |
| `abnormal_termination` | Boolean | |
| `client_version` | String(32) | |
| `pause_seconds` | Integer, default 0 | сумма кнопки «Пауза» |
| `created_at` | DateTime | |
| `is_deleted` | Boolean | soft delete |
| `deleted_at` | DateTime | |
| `deleted_by` | String(128) | |

#### `records` (партиционирована)
| Поле | Тип | Описание |
|---|---|---|
| `id` | BigInteger PK | |
| `record_uid` | String(64), unique, index | |
| `session_uid` | String(64), index | |
| `computer_id` | FK → `computers.id` | |
| `kind` | String(32) | `activity` / `window` / `idle` / `idle_end` |
| `data` | Text | JSON |
| `client_ts` | DateTime | партиционирование по нему |
| `client_ip` | String(64) | |
| `signature` | String(128) | HMAC-SHA256 |
| `received_at` | DateTime | |
| `is_deleted` | Boolean | soft delete |
| `deleted_at` | DateTime | |
| `deleted_by` | String(128) | |

**Индексы:**
- `ix_records_computer_ts` — `(computer_id, client_ts)`.

**Партиционирование:** `PARTITION BY RANGE (client_ts)` — см. `03_SERVER\06_PARTITIONS.md`.

#### `bootstrap_tokens`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `token_hash` | String(128), unique, index | sha256 |
| `issued_by` | String(128) | |
| `expires_at` | DateTime | TTL |
| `used_at` | DateTime, nullable | |
| `used_by_uid` | String(64) | UID ПК |
| `created_at` | DateTime | |

#### `client_versions`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `version` | String(32), unique | |
| `release_date` | DateTime | |
| `download_url` | String(512) | |
| `mandatory` | Boolean | |
| `release_notes` | Text | |
| `created_at` | DateTime | |

#### `audit_log`
| Поле | Тип | Описание |
|---|---|---|
| `id` | BigInteger PK | |
| `actor` | String(128) | |
| `entity` | String(64) | |
| `entity_id` | String(64) | **важно:** не переполнять |
| `action` | String(32) | |
| `old_value` | Text | |
| `new_value` | Text | |
| `created_at` | DateTime | |

**Известный баг:** `entity_id` переполнялся списком UUID (>64) → `DataError`. Решение: только первый UUID, остальное — в `new_value`.

#### `app_settings`
| Поле | Тип | Описание |
|---|---|---|
| `key` | String(64), PK | |
| `value` | Text | |
| `updated_at` | DateTime | |

**Ключи:** `idle_close_minutes`, `workday_start_hour`, `activity_gap_minutes`, `report_timezone`, `sync_interval`, `batch_size`, `active_window_interval`, `idle_threshold`, `stale_session_hours`, `count_weekends`, `reminder_enabled`, `reminder_threshold_minutes`, `reminder_repeat_minutes`, `reminder_max_per_day`, `end_of_day_hour`, `end_of_day_minute`.

#### `calendar_days`
| Поле | Тип | Описание |
|---|---|---|
| `day` | String(10), PK | ISO `YYYY-MM-DD` |
| `is_working` | Boolean | |
| `note` | String(255) | |
| `updated_at` | DateTime | |

#### `admin_users`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `username` | String(64), unique, index | |
| `password_hash` | String(255) | bcrypt |
| `full_name` | String(255) | |
| `email` | String(255) | |
| `role` | String(32) | admin/operator/hr/manager/viewer |
| `is_active` | Boolean | |
| `language` | String(8) | ru/en |
| `department_id` | FK → `departments.id` | для manager |
| `created_at` | DateTime | |
| `last_login_at` | DateTime | |

#### `admin_logins`
| Поле | Тип | Описание |
|---|---|---|
| `id` | BigInteger PK | |
| `user_id` | FK → `admin_users.id` | |
| `username` | String(64) | |
| `ip_address` | String(64) | |
| `user_agent` | String(255) | |
| `success` | Boolean | |
| `created_at` | DateTime | |

#### `scheduled_tasks`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `name` | String(64), unique | |
| `label_ru`, `label_en` | String(255) | |
| `desc_ru`, `desc_en` | Text | |
| `enabled` | Boolean | |
| `schedule_cron` | String(64) | |
| `last_run_at` | DateTime | |
| `last_run_status` | String(32) | |
| `last_run_duration_ms` | Integer | |

#### `task_runs`
| Поле | Тип | Описание |
|---|---|---|
| `id` | BigInteger PK | |
| `task_name` | String(64) | |
| `started_at` | DateTime | |
| `finished_at` | DateTime | |
| `status` | String(32) | |
| `message` | Text | |

#### `api_keys`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `name` | String(128) | |
| `key_hash` | String(128), unique, index | |
| `scopes` | String(255) | |
| `created_by` | String(64) | |
| `created_at` | DateTime | |
| `last_used_at` | DateTime | |
| `expires_at` | DateTime | |
| `is_active` | Boolean | |

#### `daily_stats`
| Поле | Тип | Описание |
|---|---|---|
| `id` | BigInteger PK | |
| `day` | String(10), index | |
| `employee_id` | FK, index | |
| `computer_id` | FK | |
| `app_name` | String(128) | |
| `total_seconds` | Integer | |
| `keyboard_seconds` | Integer | |
| `mouse_seconds` | Integer | |
| `effective_seconds` | Integer | |
| `sessions_count` | Integer | |
| `created_at` | DateTime | |

#### `backup_config`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `enabled` | Boolean | |
| `path` | String(512) | |
| `schedule_cron` | String(64) | |
| `retention_days` | Integer, default 30 | |
| `last_backup_at` | DateTime | |

#### `employee_settings`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `employee_id` | FK, unique, index | |
| `reminder_enabled` | Boolean, nullable | NULL = «как у всех» |
| `reminder_threshold_minutes` | Integer, nullable | |
| `reminder_repeat_minutes` | Integer, nullable | |
| `reminder_max_per_day` | Integer, nullable | |
| `end_of_day_hour` | Integer, nullable | |
| `end_of_day_minute` | Integer, nullable | |
| `updated_at` | DateTime | |
| `updated_by` | String(128) | |

#### `schedules`
| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer PK | |
| `name` | String(128), unique | |
| `description` | Text | |
| `is_active` | Boolean | |
| `work_start_minute` | Integer | минуты от 00:00 |
| `work_end_minute` | Integer | |
| `late_threshold_minutes` | Integer | |
| `overtime_threshold_minutes` | Integer | |
| `flexible_hours_per_day` | Integer | 0 = обычный |
| `lunch_enabled` | Boolean | |
| `lunch_start_minute` | Integer, nullable | |
| `lunch_end_minute` | Integer, nullable | |
| `work_mon` … `work_sun` | Boolean | 7 полей |
| `created_at` | DateTime | |

### Связи между таблицами
```
departments 1──N employees
departments 1──N admin_users (для manager)
departments 0──1 schedules
schedules   1──N employees
employees   1──N computers (привязка)
employees   1──N work_sessions
employees   1──1 employee_settings
employees   1──N daily_stats
computers   1──N work_sessions
computers   1──N records
computers   1──N daily_stats
work_sessions 1──N records (по session_uid, не FK)
admin_users 1──N admin_logins
scheduled_tasks 1──N task_runs (по name)
```

### Особенности партиционирования `records`
- `PARTITION BY RANGE (client_ts)`.
- Партиции: `records_2025_01` … `records_2027_12`, `records_default`.
- Уникальность `record_uid` — на всю таблицу (PostgreSQL умеет уникальные индексы на партиционированной таблице).
- FK на `computer_id` — работает.
- Индексы — на родительской таблице, наследуются партициями.

### Soft delete
| Таблица | Поле | Что значит удалено |
|---|---|---|
| `computers` | `deleted_at IS NOT NULL` | ПК в корзине |
| `records` | `is_deleted = True` | Запись в корзине |
| `work_sessions` | `is_deleted = True` | Сессия в корзине |
| `employees` | `fired_at IS NOT NULL` | Сотрудник уволен |

Физическое удаление — через `cleanup_trash` (30 дней) или вручную в `/admin/trash`.

### Hard delete (152-ФЗ)
- Сотрудник: `POST /admin/employees/{id}/delete-forever` с подтверждением ФИО → удаляет `employees`, `work_sessions`, `records`, `daily_stats`.
- ПК: `POST /admin/computers/{id}/delete-forever` с подтверждением hostname → удаляет `computers`, `work_sessions`, `records`, `daily_stats`. С retry на FK-violation.

## Ключевые решения
- **Все timestamps — UTC.** Никаких naive datetime.
- **Партиционирование только `records`.** Самая большая таблица.
- **Soft delete для `computers`, `records`, `work_sessions`.** Данные не теряются.
- **`fired_at` для сотрудников.** Уволенные остаются для истории.
- **`pause_seconds` в `work_sessions`.** Денормализация для скорости.
- **`daily_stats` как агрегат.** Ускоряет отчёты за прошлые периоды.
- **`employee_settings` с nullable полями.** NULL = «как у всех».
- **`schedule_id` в двух местах.** Иерархия: сотрудник → отдел.
- **Версионирование секрета ПК.** `secret_version`.
- **`audit_log.entity_id` — String(64).** Не переполнять.

## Ссылки на код
- запросить: `server/models.py` — все модели
- запросить: `server/database.py` — engine, SessionLocal
- запросить: `server/alembic/env.py` — include_object
- запросить: `server/alembic/versions/` — 6 миграций

## Открытые вопросы / чего не хватает
- нет данных: точное имя volume `pgdata` — в docker-compose.
- нет данных: есть ли индексы на `work_sessions.session_start` — не описано.
- нет данных: партиционированы ли `daily_stats` — нет, в планах (P3).
- нет данных: retention сырых `records` — обсуждался 90 дней, не реализован.
- не решено: нужно ли FK `records.session_uid` → `work_sessions.session_uid`.
- не решено: переводить ли `daily_stats` на партиционирование.
- не решено: добавлять ли `deleted_at` в `employees` (сейчас `fired_at`).
- не решено: нужно ли поле `notes` в `computers`.
- не решено: как хранить историю смены графиков у сотрудника.
- не решено: нужна ли таблица `employee_schedule_history`.

Готово. Один файл выше. Следующий по индексу — 03_SERVER\04_AUTH.md.
```