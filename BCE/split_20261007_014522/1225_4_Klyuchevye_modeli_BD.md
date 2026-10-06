<!-- Часть 1225 из 1409 -->
# 4. Ключевые модели БД
*Хлебные крошки:* Трекер — учёт рабочего времени. Handoff-документ / 4. Ключевые модели БД

[◀ 3. Команды](1224_3_Komandy.md) | [Оглавление](00_BCE_INDEX.md) | [5. Метрики отчётов — как считаем ▶](1226_5_Metriki_otchetov_kak_schitaem.md)

---

## 4. Ключевые модели БД

| Таблица | Назначение |
|---|---|
| `computers` | Зарегистрированные ПК. Поля: `computer_uid`, `client_secret_enc` (Fernet), `employee_id`, `deleted_at`, `is_active`, `last_seen_at` |
| `employees` | Сотрудники: `full_name`, `last_name`, `first_name`, `middle_name`, `external_id` (1C ID), `department_id`, `fired_at` |
| `departments` | Отделы |
| `work_sessions` | Сессии: `session_uid`, `computer_id`, `employee_id`, `session_start`, `session_end`, `abnormal_termination`, `pause_seconds` |
| `records` | Записи активности. **Партиционирована** по месяцам `client_ts`. Поля: `record_uid`, `session_uid`, `kind` (activity/window/idle/idle_end), `data` (JSON), `client_ts`, `signature` |
| `bootstrap_tokens` | Одноразовые токены регистрации |
| `client_versions` | Реестр версий клиента для автообновления |
| `audit_log` | Журнал аудита |
| `app_settings` | Настройки приложения (key/value) |
| `calendar_days` | Календарь рабочих/нерабочих дней |
| `admin_users` | Пользователи админки (bcrypt + role + language + department_id) |
| `admin_logins` | История входов |
| `scheduled_tasks` / `task_runs` | Планировщик и история |
| `api_keys` | Для внешних интеграций |
| `daily_stats` | Агрегаты по дням (для быстрых отчётов) |
| `employee_settings` | Персональные настройки напоминаний сотрудника |

---

