<!-- Часть 12 из 1409 -->
# 4.3. Папка `client/`
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 4. Полный список файлов с описанием / 4.3. Папка `client/`

[◀ 4.2. Папка `server/`](011_4_2_Papka_server.md) | [Оглавление](00_BCE_INDEX.md) | [5. Пошаговая установка с нуля ▶](013_5_Poshagovaya_ustanovka_s_nulya.md)

---

### 4.3. Папка `client/`

#### `client/requirements.txt`
PyQt6, httpx, pynput, keyring, psutil, python-dotenv, tenacity, cryptography, pywin32 (только на Windows).

#### `client/.env`
Настройки клиента:
```
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
```
**Опционально:** `TRACKER_INSECURE=1` — отключает проверку SSL (только dev).
**Опционально:** `TRACKER_CA_BUNDLE=путь` — путь к CA-сертификату.

#### `client/config.py`
Читает `.env` через `python-dotenv` (включая `override=True`). Определяет пути, интервалы, константы.

#### `client/crypto.py`
- `canonical_json` — **точно такая же**, как на сервере.
- `sign_payload` — HMAC-SHA256 с `client_secret` из keyring.
- `verify_payload` — проверка подписи от сервера.

#### `client/db.py`
Локальная SQLite. **Особенности:**
- WAL-режим, `busy_timeout=5000`, `journal_size_limit=64MB`.
- Отдельное соединение **на поток** (`threading.local`).
- `init_db` проверяет целостность, при повреждении — карантин.
- Миграция `_migrate` добавляет колонку `poisoned` в старые БД.
- `enforce_size_limit` удаляет синхронизированные записи при превышении 500 МБ.

#### `client/http_client.py`
`httpx.Client` с:
- `PinningTransport` — опциональная проверка отпечатка TLS-сертификата.
- Поддержка `TRACKER_INSECURE` (пропуск проверки SSL).
- Поддержка `TRACKER_CA_BUNDLE` (свой CA).

#### `client/registration.py`
- Хранит `computer_uid` и `client_secret` в **keyring**, fallback — в `credentials.enc` (Fernet/DPAPI).
- `ensure_registered()` — регистрирует ПК, если ещё не зарегистрирован.
- Читает bootstrap-токен из `%APPDATA%\Tracker\bootstrap.txt` или env.
- После успеха **удаляет bootstrap.txt**.

#### `client/collector.py`
`CollectorWorker(QObject)` в отдельном `QThread`:
- Слушает клавиатуру и мышь через `pynput`.
- Опрашивает активное окно каждые 5 секунд (`_get_active_window`).
- **Edge-triggered:** пишет `window` только при смене `(app, title)`.
- **Idle:** пишет `idle` один раз при переходе и `idle_end` при возврате (порог 60 сек).
- **Thread-safe:** счётчики под `threading.Lock`.
- **Wayland-детект:** по `XDG_SESSION_TYPE=wayland`.

#### `client/sync.py`
`SyncWorker(QObject)` в отдельном `QThread`:
- Каждые 30 секунд берёт непереданные записи и сессии.
- Отправляет сессии по одной, записи — пачкой (до 200).
- Проверяет подпись ответа сервера.
- **Различает** `bad_signature` (перманентно, в poisoned) и `unknown_session` (временно, повторить позже).
- Retry с exponential backoff при 5xx.
- При 401/403 — сигнал `auth_failed`, остановка sync.

#### `client/updater.py`
- `UpdateChecker` — в отдельном `QThread` проверяет `/api/v1/version` и (опционально) скачивает обновление.
- `apply_update` — запускает установщик, корректно выходит через `QApplication.quit()`.

#### `client/main.py`
**Точка входа.**
- Создаёт `QApplication`, `MainWindow`.
- Иконка в трее, скрытие окна вместо закрытия.
- Сигналы SIGTERM/SIGINT через `signal.set_wakeup_fd` + `QSocketNotifier`.
- `_start()` — регистрация, БД, запуск потоков.
- `_shutdown_workers()` — корректная остановка `CollectorWorker` и `SyncWorker` (с `QThread.quit()`).

#### `client/build.spec`
PyInstaller. **Ключевое:**
- `upx=False` (снижает ложные срабатывания антивирусов).
- `--onedir` (не `--onefile`).
- `hiddenimports` для `pynput`, `keyring`, `cryptography`.

#### `client/version_info.txt`
Метаданные PE-файла (компания, версия, copyright).

---

