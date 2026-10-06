# 00_INDEX.md — карта KB проекта «Трекер»

Корень KB: `D:\tracker\docs\`

| Путь | Тема | Что внутри (2–3 строки) | Статус | Зависимости |
|---|---|---|---|---|
| `00_AI_CONTEXT_PROMPT.md` | Промпт для AI-чатов | Правила работы с KB, шаблон KB-файла, стиль, инструкция «один чат — один файл» | черновик | — |
| `01_PRODUCT\01_OVERVIEW.md` | Обзор продукта | Назначение, границы системы, что собирает/не собирает, целевые пользователи | черновик | — |
| `01_PRODUCT\02_USER_ROLES.md` | Роли и права | admin/operator/hr/manager/viewer, матрица доступа, department_id для manager | черновик | `03_SERVER\04_AUTH.md` |
| `01_PRODUCT\03_ADMIN_UI.md` | Веб-админка | Карта страниц, навигация, ключевые сценарии администратора | черновик | `03_SERVER\09_TEMPLATES.md` |
| `01_PRODUCT\04_CLIENT_UI.md` | Клиентский интерфейс | Окно, трей, кнопки Старт/Пауза/Стоп, статусы, настройки | черновик | `04_CLIENT\06_SETTINGS_UI.md` |
| `01_PRODUCT\05_SCP_UI.md` | SCP | Назначение SCP, вкладки, сценарии администратора сервера | черновик | `05_SCP\01_OVERVIEW.md` |
| `01_PRODUCT\06_GLOSSARY.md` | Глоссарий | Термины: сессия, запись, span, union, интенсивная, эффективная, пауза | черновик | `02_METRICS\01_METRICS.md` |
| `02_METRICS\01_METRICS.md` | 5 метрик отчётов | Определения Отработано/С трекером/Интенсивная/Эффективно/Пауза, формулы, примеры, краевые случаи | черновик | — |
| `02_METRICS\02_REPORTS.md` | Отчёты | Группировки, фильтры, HTML-вид, детализация, блок «Без привязки» | черновик | `02_METRICS\01_METRICS.md` |
| `02_METRICS\03_PIVOT.md` | Pivot-таблица (удалено) | Веб-pivot на PivotTable.js убран 06.10.2026. Сводные строим в Excel из XLSX | черновик | — |
| `02_METRICS\04_EXPORTS.md` | Экспорт отчётов | CSV/XLSX, новые колонки, формат HH:MM:SS. PDF убран — печать через браузер (Ctrl+P) | черновик | `02_METRICS\02_REPORTS.md` |
| `02_METRICS\05_CALENDAR.md` | Календарь | Рабочие/нерабочие дни, генерация, подсветка, workday_start_hour | черновик | `03_SERVER\10_SETTINGS.md` |
| `02_METRICS\06_SCHEDULES.md` | Графики работы | Шаблоны графиков, привязка к отделам/сотрудникам, будущие отчёты опозданий | черновик | `03_SERVER\03_MODELS.md` |
| `03_SERVER\01_ARCHITECTURE.md` | Архитектура сервера | FastAPI + PostgreSQL + nginx + Docker, потоки данных, роли контейнеров | черновик | — |
| `03_SERVER\02_API.md` | API | Все эндпоинты `/api/v1/*` и `/admin/api/*`, авторизация, форматы | черновик | `03_SERVER\04_AUTH.md` |
| `03_SERVER\03_MODELS.md` | Модели БД | Таблицы, поля, связи, партиционирование records, soft delete | черновик | `03_SERVER\07_ALEMBIC.md` |
| `03_SERVER\04_AUTH.md` | Аутентификация | HMAC клиента, bootstrap-токены, сессии админки, bcrypt, роли | черновик | — |
| `03_SERVER\05_TASKS.md` | Планировщик | APScheduler, advisory lock, create_future_partitions, close_stale_sessions, daily_stats | черновик | `03_SERVER\06_PARTITIONS.md` |
| `03_SERVER\06_PARTITIONS.md` | Партиционирование | records по месяцам, include_object в Alembic, защита от drop партиций | черновик | `03_SERVER\07_ALEMBIC.md` |
| `03_SERVER\07_ALEMBIC.md` | Миграции | 6 миграций, цепочка, правила autogenerate, include_object | черновик | — |
| `03_SERVER\08_I18N.md` | i18n сервера | RU/EN словарь, Jinja hook, contextvars, переключатель языка | черновик | `03_SERVER\09_TEMPLATES.md` |
| `03_SERVER\09_TEMPLATES.md` | Шаблоны | ~25 HTML-шаблонов, base.html, навигация, роли, Bootstrap | черновик | — |
| `03_SERVER\10_SETTINGS.md` | Настройки | AppSetting, глобальные настройки, report_timezone, stale_session_hours | черновик | `03_SERVER\03_MODELS.md` |
| `04_CLIENT\01_ARCHITECTURE.md` | Архитектура клиента | PyQt6, потоки, трей, локальная SQLite, httpx, keyring | черновик | — |
| `04_CLIENT\02_COLLECTOR.md` | Сбор активности | pynput, активное окно, idle, edge-triggered window, счётчики | черновик | `02_METRICS\01_METRICS.md` |
| `04_CLIENT\03_SYNC.md` | Синхронизация | SyncWorker, батчи, HMAC, client-config, heartbeat, retry/backoff | черновик | `03_SERVER\02_API.md` |
| `04_CLIENT\04_LOCAL_DB.md` | Локальная БД | SQLite WAL, миграции, авто-закрытие сессий, pause_seconds | черновик | `04_CLIENT\03_SYNC.md` |
| `04_CLIENT\05_REMINDERS.md` | Напоминания | ReminderService, пороги, повторы, EOD, персональные настройки | черновик | `03_SERVER\10_SETTINGS.md` |
| `04_CLIENT\06_SETTINGS_UI.md` | Окно настроек | 3 вкладки: Напоминание, Общие, Регистрация; i18n и темы | черновик | `04_CLIENT\07_THEMES_I18N.md` |
| `04_CLIENT\07_THEMES_I18N.md` | Темы и i18n клиента | QSS light/dark, retranslate, client/i18n.py, переключатели | черновик | — |
| `04_CLIENT\08_AUTOSTART_UPDATE.md` | Автозапуск и обновление | Реестр Windows, Startup, updater.py, версии клиента | черновик | `06_DEPLOY\05_UPDATES.md` |
| `04_CLIENT\09_REGISTRATION.md` | Регистрация | Bootstrap-токен, keyring, fallback credentials.enc, ca.pem | черновик | `03_SERVER\04_AUTH.md` |
| `05_SCP\01_OVERVIEW.md` | SCP обзор | Server Control Panel, назначение, запуск, зависимости | черновик | — |
| `05_SCP\02_CERTIFICATES.md` | Сертификаты | Просмотр, обновление, отпечатки, backup, ca.pem для клиента | черновик | `06_DEPLOY\02_NGINX_TLS.md` |
| `05_SCP\03_BUILD.md` | Сборка клиента | PyInstaller, Inno Setup, BuildTab, bootstrap-токен в установщике | черновик | `06_DEPLOY\06_INSTALLER.md` |
| `05_SCP\04_ADMIN.md` | Администрирование | Сброс пароля веб-админа, смена ADMIN_API_KEY, диагностика | черновик | `03_SERVER\04_AUTH.md` |
| `06_DEPLOY\01_DOCKER.md` | Docker | docker-compose.yml, db/api/nginx, volumes, healthcheck | черновик | — |
| `06_DEPLOY\02_NGINX_TLS.md` | Nginx и TLS | 443, proxy `/api/`, `/admin/`, сертификаты, HSTS | черновик | — |
| `06_DEPLOY\03_WINDOWS_SETUP.md` | Установка на Windows | Docker Desktop, сертификаты, .env, первый запуск | черновик | `06_DEPLOY\01_DOCKER.md` |
| `06_DEPLOY\04_BACKUP.md` | Бэкапы | pg_dump, ротация, хранение, восстановление | черновик | `03_SERVER\03_MODELS.md` |
| `06_DEPLOY\05_UPDATES.md` | Обновления | Публикация версий, client_versions, автообновление | черновик | `04_CLIENT\08_AUTOSTART_UPDATE.md` |
| `06_DEPLOY\06_INSTALLER.md` | Установщик | Inno Setup, PyInstaller, ярлыки, автозапуск, ca.pem | черновик | `05_SCP\03_BUILD.md` |
| `07_QUALITY\01_TESTING.md` | Тестирование | pytest, API, идемпотентность, нагрузка, антивирусы | черновик | — |
| `07_QUALITY\02_KNOWN_ISSUES.md` | Известные проблемы | getaddrinfo, 401/403, 500 batch, pause_seconds (PDF/pivot — исторические, функционал удалён) | черновик | — |
| `07_QUALITY\03_DIAGNOSTICS.md` | Диагностика | Логи API/клиента, SQL-проверки, scheduler, health | черновик | `09_OPS\01_RUNBOOK.md` |
| `07_QUALITY\04_SECURITY.md` | Безопасность | HMAC, TLS, cookie, pinning, секреты, ротация | черновик | `03_SERVER\04_AUTH.md` |
| `08_LEGAL\01_152FZ.md` | 152-ФЗ | Согласия, приказ, уведомление РКН, меры защиты | черновик | — |
| `08_LEGAL\02_CONSENTS.md` | Согласия | Шаблоны согласий и уведомлений сотрудников | черновик | `08_LEGAL\01_152FZ.md` |
| `09_OPS\01_RUNBOOK.md` | Runbook | Ежедневные/еженедельные проверки, типовые сбои, команды | черновик | `07_QUALITY\03_DIAGNOSTICS.md` |
| `09_OPS\02_MONITORING.md` | Мониторинг | Метрики, health, БД, свободное место, очередь | черновик | — |
| `09_OPS\03_ALERTS.md` | Алерты | Telegram/Email, офлайн-ПК, падение задач, ошибки 500 | черновик | `09_OPS\02_MONITORING.md` |
| `09_OPS\04_INCIDENTS.md` | Инциденты | Классификация, действия, восстановление, пост-мортем | черновик | `09_OPS\01_RUNBOOK.md` |
| `HANDOFF.md` | Сводка проекта | Паспорт, архитектура, команды, состояние, roadmap, секреты | черновик | все KB-файлы |
| `99_RAW\01_CHAT_HISTORY.md` | История чатов | Ссылки/выжимки из переписок, решения, отменённые идеи | черновик | — |
| `99_RAW\02_SCREENSHOTS.md` | Скриншоты | Описание скриншотов, что на них важно | черновик | — |
| `99_RAW\03_LOGS.md` | Логи | Эталонные примеры логов, traceback’и, диагностические выводы | черновик | — |