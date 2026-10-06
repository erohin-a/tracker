# Архитектура клиента
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 04_CLIENT\02_COLLECTOR.md, 04_CLIENT\03_SYNC.md, 04_CLIENT\04_LOCAL_DB.md, 04_CLIENT\09_REGISTRATION.md

## Назначение
Описать архитектуру клиентской части «Трекера»: какие модули входят, как взаимодействуют, какие технологии используются и почему. Это карта для разработчика, который впервые открывает клиент, и для администратора, который разворачивает его на ПК сотрудника.

## Содержание

### Общая схема
┌──────────────────────────────────────────────────────────────┐
│ ПК СОТРУДНИКА (Windows/Linux) │
│ │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ MainWindow (PyQt6) │ │
│ │ - трей (QSystemTrayIcon) │ │
│ │ - кнопки Старт/Пауза/Стоп │ │
│ │ - панель информации (infoPanel) │ │
│ │ - настройки (SettingsDialog) │ │
│ └────────────┬─────────────────────────────────────────┘ │
│ │ │
│ ┌────────────▼──────────┐ ┌──────────────────────────┐ │
│ │ CollectorWorker │ │ ActivityWatcher │ │
│ │ (только при сессии) │ │ (всегда, для напоминаний)│ │
│ │ - pynput keyboard │ │ - факт активности │ │
│ │ - pynput mouse │ │ - не пишет records │ │
│ │ - active window │ └──────────────────────────┘ │
│ │ - idle │ │
│ └────────────┬──────────┘ │
│ │ │
│ ┌────────────▼──────────┐ ┌──────────────────────────┐ │
│ │ SQLite (WAL) │ │ ReminderService │ │
│ │ - sessions │ │ - напоминание о старте │ │
│ │ - records │ │ - EOD-напоминание │ │
│ │ - meta │ │ - client-config опрос │ │
│ └────────────┬──────────┘ └──────────────────────────┘ │
│ │ │
│ ┌────────────▼──────────┐ ┌──────────────────────────┐ │
│ │ SyncWorker │ │ Registration │ │
│ │ - сессии по одной │ │ - bootstrap-токен │ │
│ │ - records батчами │ │ - keyring │ │
│ │ - heartbeat раз в 3м │ │ - credentials.enc │ │
│ │ - retry/backoff │ └──────────────────────────┘ │
│ └────────────┬──────────┘ │
│ │ │
│ │ HTTPS + HMAC-SHA256 │
│ ▼ │
│ СЕРВЕР (Docker) │
└──────────────────────────────────────────────────────────────┘

text

### Стек технологий
| Компонент | Технология | Почему |
|---|---|---|
| GUI | PyQt6 | Трей, потоки, сигналы/слоты, QSS для тем |
| HTTP-клиент | httpx | Async, HTTP/2, pinning сертификата |
| Сбор активности | pynput | Кроссплатформенность, стабильность |
| Секреты | keyring + cryptography | Нативная интеграция с Windows Credential Manager |
| Локальная БД | SQLite (WAL) | Офлайн-буфер, транзакции, надёжность |
| Шифрование | Fernet / DPAPI | Fallback при недоступности keyring |
| Упаковка | PyInstaller | Стандарт для Python → .exe |
| Установщик | Inno Setup | Планируется |

### Модули клиента

#### Основные
| Модуль | Назначение |
|---|---|
| `client/main.py` | Точка входа, MainWindow, трей, кнопки, панель информации, обработка сигналов |
| `client/collector.py` | `CollectorWorker` — сбор активности (только при сессии) |
| `client/activity_watcher.py` | Пассивный слушатель активности (всегда, для напоминаний) |
| `client/sync.py` | `SyncWorker` — отправка данных на сервер, heartbeat, client-config |
| `client/db.py` | Локальная SQLite (WAL), сессии, записи, метаданные |
| `client/reminder.py` | `ReminderService` — напоминания о старте/EOD |
| `client/reminder_settings.py` | Локальные настройки напоминаний в SQLite meta |
| `client/registration.py` | Регистрация ПК, keyring, fallback credentials.enc |
| `client/registration_dialog.py` | Диалог первого запуска (ввод bootstrap-токена) |
| `client/unclosed_dialog.py` | Диалог восстановления после краха |

#### Вспомогательные
| Модуль | Назначение |
|---|---|
| `client/config.py` | Чтение `.env`, дефолты, пути, config.json |
| `client/crypto.py` | HMAC-SHA256, canonical_json (идентичен серверному) |
| `client/http_client.py` | httpx-клиент с pinning, CA bundle, insecure |
| `client/autostart.py` | Автозапуск через реестр Windows / `.desktop` Linux |
| `client/updater.py` | Проверка версии, скачивание, установка обновления |
| `client/themes.py` | QSS light/dark/system |
| `client/i18n.py` | Словарь RU/EN, `t(key, **kwargs)` |
| `client/settings_dialog.py` | Окно настроек (3 вкладки) |

### Потоки данных

#### 1. Запуск клиента
1. `python -m client.main` из `D:\tracker`.
2. Чтение `client/.env` (приоритет) или `%APPDATA%\Tracker\.env`.
3. `init_db()` — инициализация SQLite, проверка целостности, миграции.
4. Проверка регистрации (`is_registered()`).
   - Если не зарегистрирован → `RegistrationDialog`.
5. Проверка незакрытой сессии (`detect_abnormal_termination()`).
   - Если есть → `UnclosedSessionDialog`.
6. Запуск `SyncWorker`, `ReminderService`, `ActivityWatcher`.
7. Показ главного окна + иконки в трее.

#### 2. Начало работы
1. Пользователь нажимает «▶ Начать работу».
2. `start_session(uid)` — создание записи в SQLite.
3. Запуск `CollectorWorker`.
4. Обновление состояния кнопок и панели.

#### 3. Сбор активности
1. `CollectorWorker` опрашивает активное окно каждые 5 сек.
2. Пишет `window` при смене `(app, title)`.
3. Пишет `activity` раз в 5 сек, если были key/click/scroll.
4. Пишет `idle` при переходе через порог 60 сек.
5. Пишет `idle_end` при возврате.
6. Всё — в локальную SQLite.

#### 4. Синхронизация
1. `SyncWorker` раз в 30 сек.
2. Сессии — по одной, `POST /api/v1/sessions`.
3. Records — батчами до 200, `POST /api/v1/records/batch`.
4. HMAC-подпись каждой записи и батча.
5. При 401/403 — `auth_failed`, остановка.
6. Retry с exponential backoff.

#### 5. Heartbeat
1. Раз в 3 минуты: `POST /api/v1/heartbeat`.
2. Обновляет `last_seen_at` на сервере.
3. Дашборд показывает онлайн-статус.

#### 6. Напоминания
1. `ReminderService` опрашивает `client-config` каждые 5 минут.
2. Если 15 минут есть активность, но нет сессии — показывает напоминание.
3. EOD-напоминание — если сессия идёт в заданное время.

#### 7. Завершение
1. Пользователь нажимает «■ Конец работы».
2. `close_session_at(uid, last_activity)` — закрытие сессии.
3. Остановка `CollectorWorker`.
4. `SyncWorker` отправляет оставшиеся данные.
5. При выходе — `close_session_at` с `last_activity` (не `now`).

### Локальная БД (SQLite)
**Файл:** `%APPDATA%\Tracker\data.db` (Windows) или `~/.tracker/data.db` (Linux).

**Таблицы:**
| Таблица | Назначение |
|---|---|
| `sessions` | Сессии: `session_uid`, `session_start`, `session_end`, `abnormal_termination`, `pause_seconds`, `synced` |
| `records` | Записи: `record_uid`, `session_uid`, `kind`, `data`, `client_ts`, `signature`, `synced`, `poisoned` |
| `meta` | Key/value: `active_session`, `last_activity`, `pause.started_at`, `idle_close_minutes` |

**Режим WAL:** `PRAGMA journal_mode=WAL`. Читатели и писатели не блокируют друг друга.

**Лимит размера:** 500 МБ (`MAX_DB_SIZE_MB`). При превышении — удаляются синхронизированные записи (`enforce_size_limit`).

### Хранение секретов

#### `client_secret`
- **Основное:** Windows keyring (`keyring.set_password("tracker", "client_secret", ...)`).
- **Fallback:** `%APPDATA%\Tracker\credentials.enc` (Fernet/DPAPI).
- **Удаление при перерегистрации:** только `client_secret`, `computer_uid` сохраняется.

#### `computer_uid`
- Хранится в `config.json` в `%APPDATA%\Tracker\`.
- При перерегистрации — сохраняется.

### Конфигурация

#### `client/.env`
```ini
TRACKER_SERVER_URL=https://127.0.0.1
TRACKER_PIN=
TRACKER_VERSION=1.0.0
Порядок поиска .env:

client/.env — рядом с config.py (приоритет).

%APPDATA%\Tracker\.env.

Важно: не читается серверный .env из корня D:\tracker — иначе подхватится DATABASE_URL и другие серверные переменные.

%APPDATA%\Tracker\config.json
json
{
  "language": "ru",
  "theme": "light",
  "autostart_enabled": false,
  "server_url": null,
  "cert_fingerprint": null,
  "notifications": {"offline": true, "eod": true}
}
Эффективные настройки:

get_server_url() — config.json → .env → https://127.0.0.1.

get_cert_fingerprint() — config.json → .env (TRACKER_PIN) → пусто.

get_language_code() — config.json (ru/en).

get_theme_code() — config.json (light/dark/system).

Темы
Light — светлая, по умолчанию.

Dark — тёмная.

System — системная (пока применяется как light).

Реализация: QSS в client/themes.py. Применяется через app.setStyleSheet. Сигнал theme_signals.theme_changed для уведомления окон.

i18n клиента
Словарь RU/EN в client/i18n.py.

~85 ключей.

Переключение языка требует перезапуска (в планах — retranslate).

Подключён в settings_dialog.py. В main.py — частично (хардкод по-русски).

Автозапуск
Windows: реестр HKCU\Software\Microsoft\Windows\CurrentVersion\Run.

Linux: .config/autostart/tracker.desktop.

set_autostart(enabled: bool) в client/autostart.py.

Обновление
updater.py проверяет /api/v1/version.

Если версия новее — скачивает, устанавливает.

Публикация версий через UI — не сделана (P0).

Обработка сигналов
SIGTERM/SIGINT через QSocketNotifier.

При выходе — close_session_at с last_activity.

Закрытие окна (крестиком) не завершает приложение — сворачивает в трей.

Известные проблемы и решения
Проблема	Причина	Решение
getaddrinfo failed	Python резолвит localhost в IPv6, Docker не пробрасывает	Использовать https://127.0.0.1
SSL: CERTIFICATE_VERIFY_FAILED	Нет ca.pem	Скопировать fullchain.pem в %APPDATA%\Tracker\ca.pem
Hostname mismatch	Сертификат без SAN	Перевыпустить с subjectAltName
401 Unauthorized	Сгорел bootstrap-токен	Выпустить новый
ModuleNotFoundError: PyQt6	venv не активирован	.venv\Scripts\Activate.ps1
ModuleNotFoundError: client	Запуск из D:\tracker\client, а не из D:\tracker	python -m client.main из корня
QObject::killTimer при закрытии	QTimer уничтожается не в том потоке	Косметика, не критично
17 часов работы за день	close_session ставил end = now	detect_abnormal_termination использует last_activity
pause_seconds > total_sec	Двойное вычитание паузы	Не вычитать в _analyze_session
Ключевые решения
PyQt6 + трей + QSS — зрелый GUI, системный трей, темы.

SQLite WAL — офлайн-first, транзакции, не блокирует читателей.

HMAC на каждой записи — целостность, офлайн-режим.

keyring для client_secret — нативное хранилище Windows, fallback через Fernet.

127.0.0.1 вместо localhost — обход IPv6-проблемы в Docker.

client/.env в приоритете — не подхватывает серверный .env.

Bound-функция _ для i18n — не теряет язык между запросами.

close_session_at(last_activity) — защита от «17 часов за день».

Retry с exponential backoff — устойчивость к временным сбоям сети.

Автозакрытие по idle (30 мин) — не копит «висящие» сессии.

Ссылки на код
запросить: client/main.py — MainWindow, трей, кнопки, обработчики

запросить: client/collector.py — CollectorWorker

запросить: client/activity_watcher.py — ActivityWatcher

запросить: client/sync.py — SyncWorker

запросить: client/db.py — SQLite, init_db, start_session, close_session_at, detect_abnormal_termination, auto_close_idle_session

запросить: client/registration.py — is_registered, register_with_token, ensure_registered

запросить: client/registration_dialog.py — диалог первого запуска

запросить: client/unclosed_dialog.py — диалог восстановления

запросить: client/reminder.py — ReminderService

запросить: client/reminder_settings.py — локальные настройки

запросить: client/config.py — load_config, get_server_url, get_language_code, get_theme_code

запросить: client/crypto.py — HMAC, canonical_json

запросить: client/http_client.py — httpx, pinning

запросить: client/autostart.py — set_autostart

запросить: client/updater.py — UpdateChecker, apply_update

запросить: client/themes.py — QSS light/dark

запросить: client/i18n.py — словарь RU/EN

запросить: client/settings_dialog.py — 3 вкладки

запросить: client/.env — конфиг клиента

запросить: client/requirements.txt — зависимости

Открытые вопросы / чего не хватает
нет данных: точный размер главного окна — ~500×280 px (из скриншота).

нет данных: полный список зависимостей в requirements.txt — нужно проверить.

нет данных: реализован ли retranslate главного окна — нет.

нет данных: работает ли клиент на Linux (кроме X11) — не подтверждено.

нет данных: есть ли поддержка macOS — не собирался.

не решено: нужен ли отдельный поток для UI (сейчас — главный поток).

не решено: как быть с несколькими мониторами (позиция окна).

не решено: нужна ли горячая клавиша Ctrl+Shift+S.

не решено: как показывать параллельную работу на двух ПК (тост раз в сессию).

не решено: нужен ли отдельный индикатор «идёт синхронизация» в трее.

не решено: где показывать «Отправить лог» — кнопка в меню трея или в настройках.

не решено: заменить ли httpx на aiohttp (сейчас async в SyncWorker).

Готово. Один файл выше. Следующий по индексу — 04_CLIENT\02_COLLECTOR.md.