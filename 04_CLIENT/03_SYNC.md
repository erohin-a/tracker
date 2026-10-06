# Синхронизация
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 04_CLIENT\04_LOCAL_DB.md, 03_SERVER\02_API.md, 04_CLIENT\09_REGISTRATION.md

## Назначение
Описать, как клиент отправляет данные на сервер: сессии, записи, heartbeat, конфиг. Что происходит при ошибках, как работает retry, что видит пользователь. Это карта для разработчика, который дорабатывает синхронизацию, и для администратора, который разбирается с «клиент не отправляет».

## Содержание

### Общая схема
SQLite (локальная) Сервер
┌─────────────────┐ ┌──────────────────┐
│ sessions │─── POST ────▶│ /api/v1/sessions │
│ (unsynced) │ └──────────────────┘
├─────────────────┤
│ records │─── POST ────▶ /api/v1/records/batch
│ (unsynced) │ (батчи до 200)
├─────────────────┤
│ meta │─── POST ────▶ /api/v1/heartbeat
│ │ (раз в 3 мин)
└─────────────────┘
◀── GET ──── /api/v1/client-config
(раз в 5 мин)

text

### Компоненты

#### `SyncWorker`
- Наследник `QObject`, живёт в отдельном потоке.
- Основной цикл: **раз в 30 секунд** (`SYNC_INTERVAL`).
- Работает всегда, пока клиент запущен (независимо от сессии).
- Отправляет: сессии → записи → heartbeat → client-config.

#### `ReminderService`
- Отдельный цикл — опрос `client-config` раз в 5 минут.
- Не пересекается с `SyncWorker`.

### Что синхронизируется

#### 1. Сессии (`POST /api/v1/sessions`)
- **Что:** записи из таблицы `sessions`, где `synced = 0`.
- **Как:** **по одной** — каждая сессия отдельным запросом.
- **Когда:** при следующем цикле после появления новой или обновлённой сессии.
- **Что отправляется:**
```json
{
  "session_uid": "uuid-v4",
  "session_start": "2026-10-02T09:00:00+00:00",
  "session_end": "2026-10-02T17:00:00+00:00",
  "abnormal_termination": false,
  "client_version": "1.0.0"
}
После успеха: mark_session_synced(uid) — synced = 1 в SQLite.

Особенности:

Открытая сессия (session_end = NULL) отправляется тоже — сервер её примет.

При обновлении сессии (например, пришёл session_end) — synced сбрасывается в 0, отправляется заново.

Идемпотентность: session_uid уникален, повторная отправка обновляет.

409 при «чужом ПК»: сервер возвращает 200 OK, клиент считает успехом.

2. Записи (POST /api/v1/records/batch)
Что: записи из records, где synced = 0 AND poisoned = 0.

Как: батчами до 200 (BATCH_SIZE).

Когда: при следующем цикле, если есть unsynced-записи.

Порядок: ORDER BY client_ts ASC — сначала старые.

Что отправляется:

json
{
  "records": [
    {
      "record_uid": "uuid-v4",
      "session_uid": "uuid-v4",
      "kind": "activity",
      "data": {"keys": 5, "clicks": 3, "scroll": 1},
      "client_ts": "2026-10-02T09:05:00+00:00",
      "signature": "hmac-sha256-hex"
    }
  ],
  "batch_signature": "hmac-sha256-hex"
}
Ответ:

json
{
  "accepted_uuids": ["uuid-1", "uuid-2"],
  "rejected_uuids": ["uuid-3"],
  "reasons": {"uuid-3": "duplicate"},
  "server_signature": "hmac-sha256-hex"
}
После ответа:

accepted_uuids → synced = 1.

rejected_uuids → synced = 1, poisoned = 1 (permanent reject).

Ничего не осталось — цикл завершён.

3. Heartbeat (POST /api/v1/heartbeat)
Что: пустой запрос {}.

Как: раз в 3 минуты (независимо от цикла синхронизации).

Зачем: сервер обновляет computers.last_seen_at. Дашборд показывает онлайн-статус.

Если сервер недоступен: просто пропускается, попытка через 3 минуты.

4. Client-config (GET /api/v1/client-config)
Что: эффективные настройки для ПК.

Как: раз в 5 минут (в ReminderService).

Зачем: клиент подтягивает глобальные + персональные настройки:

reminder_enabled, reminder_threshold_minutes, reminder_repeat_minutes, reminder_max_per_day.

end_of_day_hour, end_of_day_minute.

Мерж: сервер отдаёт уже слитые значения (source_reminder, source_end_of_day).

5. Версия клиента (GET /api/v1/version)
Что: проверка новой версии.

Как: периодически (в updater.py).

Зачем: автообновление (публикация версий — не реализована, P0).

HMAC-подпись
Canonical JSON:

python
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
Подпись записи:

text
signature = HMAC-SHA256(client_secret, canonical_json({
    record_uid, session_uid, kind, data, client_ts
}))
Подпись батча:

text
batch_signature = HMAC-SHA256(client_secret, canonical_json({
    records: [...]
}))
Проверка на сервере:

Сервер расшифровывает client_secret_enc через Fernet.

Считает HMAC и сравнивает через hmac.compare_digest.

При несовпадении — запись отклоняется и помечается poisoned.

Обработка ошибок и retry
Классификация ошибок:

Ситуация	Ответ сервера	Что делает клиент
Успех	200	Помечает synced
Bad signature	200 + rejected	Помечает synced=1, poisoned=1
Duplicate	200 + rejected	Помечает synced=1, poisoned=1
Unknown session	200 + rejected	Помечает synced=1, poisoned=1 (не повторяет)
401/403	401/403	auth_failed, остановка синхронизации
500	500	Retry с backoff
Сеть недоступна	httpx.HTTPError	Retry с backoff, server_down()
Timeout	httpx.TimeoutException	Retry
Retry:

Библиотека tenacity.

Exponential backoff (например, 1с, 2с, 4с, 8с…).

Максимум попыток — задаётся в конфиге.

Не ретраит 401/403 — это permanent.

Не ретраит bad_signature — запись уже poisoned.

auth_failed:

Сигнал auth_failed() — клиент останавливает синхронизацию.

В UI — сообщение «Требуется перерегистрация».

Причина: сгорел client_secret, ПК отозван (revoke).

Действие админа: выпустить новый bootstrap-токен, перерегистрировать ПК.

Сигналы PyQt
SyncWorker испускает сигналы для UI:

Сигнал	Когда	Что показывает UI
synced(int)	После успешной отправки батча	«Синхронизировано N записей»
connected()	После успешного запроса	«✓ онлайн»
error(str)	При ошибке	Показать сообщение
server_down()	Сервер недоступен	«⚠ офлайн»
auth_failed()	401/403	«Требуется перерегистрация»
UI-индикация
Панель информации в главном окне:

Сервер: «✓ онлайн» / «⚠ офлайн».

Последняя синхронизация: DD.MM HH:MM:SS.

Записей в очереди: число unsynced.

Иконка в трее:

🟢 зелёный — сессия активна, сервер доступен.

🟡 жёлтый — пауза.

⚪ серый — нет сессии.

🔴 красный — нет связи с сервером.

Немедленная синхронизация
trigger():

Прерывает ожидание в цикле и запускает синхронизацию немедленно.

Вызывается:

при закрытии сессии («Конец работы»);

при старте клиента;

после изменения настроек.

Офлайн-режим
Как работает:

Клиент работает без сети — данные копятся в SQLite.

SyncWorker пытается отправить, получает server_down().

Retry с backoff.

При появлении связи — синхронизация возобновляется.

Данные не теряются.

Ограничение: enforce_size_limit — при превышении 500 МБ удаляются самые старые синхронизированные записи.

Порядок синхронизации
Сессии — сначала, чтобы сервер знал о них до приёма records.

Records — батчами.

Heartbeat — раз в 3 минуты, отдельно.

Client-config — раз в 5 минут, в другом потоке.

Известные проблемы и решения
Проблема	Причина	Решение
getaddrinfo failed	IPv6 vs IPv4	https://127.0.0.1 в client/.env
SSL: CERTIFICATE_VERIFY_FAILED	Нет ca.pem	Скопировать в %APPDATA%\Tracker\ca.pem
401 Unauthorized	Сгорел токен / ПК отозван	auth_failed, перерегистрация
500 на batch	Дубликаты record_uid	Ищем по всей таблице, IntegrityError обрабатываем
409 на sessions	Сессия принадлежит другому ПК	Возвращаем 200, клиент считает успехом
Спам retry при 401	Ретраил permanent-ошибку	Различать 401/403 — не ретраить
JSON decode error	PowerShell съел кавычки в .env	Использовать WriteAllText с UTF8Encoding(false)
Клиент «висит» на синхронизации	Долгий запрос без timeout	httpx.Timeout(30.0)
Логи
%APPDATA%\Tracker\client.log:

text
2026-10-02 09:05:00 INFO tracker.sync Sync started
2026-10-02 09:05:01 INFO tracker.sync Sessions sent: 1
2026-10-02 09:05:02 INFO tracker.sync Records sent: 50 accepted, 0 rejected
2026-10-02 09:05:02 INFO tracker.sync Sync completed
2026-10-02 09:05:30 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed
2026-10-02 09:08:00 INFO tracker.sync Heartbeat OK
Проверка:

powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 50 -Encoding UTF8
Ключевые решения
Сессии по одной, records батчами. Сессий мало, записей много.

HMAC на каждой записи и на батче. Двойная защита.

200 OK для «чужих» сессий. Не воюем, не блокируем.

poisoned для permanent reject. Больше не отправляем.

Retry с backoff для временных сбоев. Не ретраим 401/403.

auth_failed останавливает синхронизацию. Требуется перерегистрация.

Heartbeat раз в 3 минуты. Баланс трафика и точности онлайна.

Client-config раз в 5 минут. Быстрое применение изменений.

trigger() для немедленной отправки. При закрытии сессии, старте.

Офлайн-first. Данные копятся, отправляются при появлении связи.

Ссылки на код
запросить: client/sync.py — SyncWorker, все сигналы, trigger()

запросить: client/db.py — fetch_unsynced, fetch_unsynced_sessions, apply_sync_result, mark_session_synced

запросить: client/crypto.py — sign_payload, canonical_json

запросить: client/http_client.py — httpx, pinning, timeout, get_client

запросить: client/config.py — SYNC_INTERVAL, BATCH_SIZE, SERVER_URL

запросить: client/main.py — обработка сигналов synced, connected, error, server_down, auth_failed

запросить: client/reminder.py — ReminderService, опрос client-config

запросить: server/main.py — /api/v1/sessions, /api/v1/records/batch, /api/v1/heartbeat, /api/v1/client-config

запросить: server/security.py — проверка HMAC

Открытые вопросы / чего не хватает
нет данных: точное значение backoff и количество попыток retry.

нет данных: таймаут httpx — 30 сек или другой.

нет данных: что происходит при одновременном trigger() и цикле — блокировка?

нет данных: есть ли метрика «время последней успешной синхронизации» в SQLite meta — да, last_sync.

не решено: как быть с большими сессиями (например, 8 часов) — отправляем всё сразу?

не решено: нужно ли сжимать батчи (gzip).

не решено: как обрабатывать «полу-успех» — часть записей accepted, часть rejected.

не решено: нужен ли отдельный цикл для отправки «срочных» записей (например, при закрытии сессии).

не решено: должен ли heartbeat идти через тот же httpx-клиент или отдельный.

не решено: как быть с 500 на batch — ретраить весь батч или по одной записи.

Готово. Один файл выше. Следующий по индексу — 04_CLIENT\04_LOCAL_DB.md.