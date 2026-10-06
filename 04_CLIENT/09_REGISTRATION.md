# Регистрация
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\04_AUTH.md, 04_CLIENT\01_ARCHITECTURE.md, 04_CLIENT\06_SETTINGS_UI.md

## Назначение
Описать процесс регистрации ПК в «Трекере»: как клиент получает `client_secret`, где его хранит, как работает перерегистрация и что делать при сбоях. Это карта для администратора, который выдаёт ПК сотруднику, и для разработчика, который дорабатывает регистрацию.

## Содержание

### Что такое регистрация
- Первичная привязка нового ПК к серверу.
- Происходит **один раз** при первом запуске клиента.
- Требует **bootstrap-токен**, выпущенный администратором.
- В результате клиент получает два секрета:
  - `computer_uid` — UUID v4, идентификатор ПК.
  - `client_secret` — симметричный ключ для HMAC-подписи.
- `client_secret` хранится только на клиенте (в keyring) и на сервере в зашифрованном виде.

### Компоненты

| Компонент | Файл | Назначение |
|---|---|---|
| `RegistrationDialog` | `client/registration_dialog.py` | Диалог первого запуска (ввод bootstrap-токена) |
| `registration` | `client/registration.py` | Логика регистрации, keyring, fallback |
| `computers` | `server/models.py` | Таблица с зарегистрированными ПК |
| `bootstrap_tokens` | `server/models.py` | Одноразовые токены |
| `POST /api/v1/computers/register` | `server/main.py` | Эндпоинт регистрации |

### Функции `client/registration.py`

| Функция | Что делает |
|---|---|
| `is_registered()` | `True`, если есть `computer_uid` и `client_secret` |
| `register_with_token(token)` | Регистрирует ПК по bootstrap-токену |
| `ensure_registered()` | Проверяет и при необходимости регистрирует |
| `get_computer_uid()` | Возвращает `computer_uid` или `None` |

### Диалог `RegistrationDialog`
**Когда показывается:**
- При старте клиента, если `is_registered()` = `False`.
- При нажатии «Перерегистрировать» на вкладке «Регистрация».

**Элементы:**
- Заголовок: «Регистрация».
- Пояснение: что нужно ввести bootstrap-токен.
- Поле ввода `bootstrap_token` (QLineEdit).
- Кнопка «Зарегистрировать».
- Статус-строка (ошибка или успех).

**Логика:**
1. Пользователь вводит токен.
2. Клиент вызывает `register_with_token(token)`.
3. При успехе — диалог закрывается, клиент продолжает работу.
4. При ошибке — показывается статус (`401`, «токен истёк», «сеть недоступна»).

**Особенности:**
- Диалог **модальный** — нельзя закрыть без регистрации.
- В планах — кнопка «Отмена» для выхода из клиента.
- Строки **не переведены** (i18n не подключён).
- Если ПК уже зарегистрирован — диалог не показывается.

### Процесс регистрации

#### 1. Админ выпускает bootstrap-токен
- Через `/admin/tokens` → «Выпустить».
- Указывает TTL (по умолчанию 24 часа).
- Копирует токен (показывается **один раз**).
- Передаёт сотруднику по защищённому каналу.

#### 2. Сотрудник запускает клиент
- Первый запуск — `is_registered()` = `False`.
- Показывается `RegistrationDialog`.

#### 3. Клиент отправляет запрос
- `POST /api/v1/computers/register`.
- Тело:
```json
{
  "computer_uid": "uuid-v4",
  "hostname": "PC-BUH-01",
  "os_info": "Windows 10 Pro",
  "client_version": "1.0.0",
  "bootstrap_token": "xxxxx"
}
computer_uid генерируется клиентом (UUID v4), сохраняется в config.json.

4. Сервер проверяет токен
Хеширует токен (sha256).

Ищет в bootstrap_tokens по token_hash.

Проверяет:

used_at IS NULL (не использован).

expires_at > now() (не истёк).

Если всё ок — помечает used_at = now(), used_by_uid = computer_uid.

5. Сервер генерирует client_secret
secrets.token_urlsafe(48).

Шифрует Fernet (SECRET_ENCRYPTION_KEY).

Сохраняет в computers.client_secret_enc.

Устанавливает secret_version = 1.

6. Сервер возвращает client_secret
Ответ:

json
{
  "computer_uid": "uuid-v4",
  "client_secret": "yyyyy",
  "secret_version": 1
}
7. Клиент сохраняет секреты
computer_uid → config.json (%APPDATA%\Tracker\config.json).

client_secret → Windows keyring (или fallback).

Удаляет bootstrap.txt (если он был).

Закрывает диалог, продолжает работу.

Хранение client_secret
Основное: Windows keyring
Библиотека keyring.

Использует Windows Credential Manager.

Запись: keyring.set_password("tracker", "client_secret", value).

Чтение: keyring.get_password("tracker", "client_secret").

Плюсы:

Нативное хранилище Windows.

Защищено ОС.

Не требует файла с паролем.

Минусы:

Может не работать в некоторых окружениях.

Требует keyring в зависимостях.

Fallback: credentials.enc
Файл: %APPDATA%\Tracker\credentials.enc.

Шифрование: Fernet/DPAPI.

Используется, если keyring недоступен.

Формат: зашифрованный JSON с computer_uid и client_secret.

Когда используется fallback:

Keyring не установлен.

Keyring вернул ошибку.

Окружение не поддерживает keyring.

Хранение computer_uid
Всегда в config.json (%APPDATA%\Tracker\config.json).

Не шифруется (это не секрет).

Сохраняется при перерегистрации.

Перерегистрация
Когда нужна:

ПК переустановлен.

Сменился сотрудник.

Утёк client_secret.

ПК был отозван (revoke).

Процедура:

Админ: в /admin/computers находит ПК.

Нажимает «Разрешить перерегистрацию» — выпускает новый bootstrap-токен (TTL = 1 час).

Админ: передаёт токен сотруднику.

Сотрудник: на вкладке «Регистрация» вводит токен, нажимает «Перерегистрировать».

Клиент вызывает register_with_token(token).

Сервер:

Помечает старый client_secret_enc пустым.

Генерирует новый client_secret.

secret_version++.

Возвращает новый секрет.

Клиент сохраняет новый client_secret, computer_uid остаётся.

Важно:

При перерегистрации удаляется только client_secret, computer_uid сохраняется.

Старые сессии на сервере остаются привязанными к тому же ПК.

Если ПК был отозван — сначала revoke, потом перерегистрация.

Перерегистрация через re-registration-token
Роут: POST /api/v1/admin/computers/{uid}/re-registration-token.

Логика:

comp.is_active = False.

comp.client_secret_enc = "".

Создаётся новый bootstrap-токен с TTL = 1 час.

Токен возвращается админу (показывается один раз).

В UI:

Кнопка «Разрешить перерегистрацию» в /admin/computers.

Редирект на страницу с токеном в query-параметре.

Токен показывается один раз.

Отзыв ПК (revoke)
Роут: POST /api/v1/admin/computers/{uid}/revoke.

Логика:

comp.is_active = False.

Клиент при следующем запросе получает 401/403.

Клиент испускает auth_failed, синхронизация останавливается.

Для восстановления — перерегистрация.

Удаление ПК
Soft delete:

deleted_at = now(), is_active = False.

ПК в корзине, можно восстановить.

Hard delete:

POST /admin/computers/{id}/delete-forever.

Требует ввода hostname для подтверждения.

Удаляет computers, work_sessions, records, daily_stats.

С retry на FK-violation (3 попытки).

Обработка ошибок
Ошибка	Причина	Что видит сотрудник	Что делать
401 Invalid or expired bootstrap token	Токен использован или истёк	Сообщение об ошибке	Выпустить новый токен
400	Некорректные данные	Сообщение об ошибке	Проверить ввод
Сеть недоступна	Сервер офлайн	Ошибка соединения	Проверить сеть, повторить
SSL: CERTIFICATE_VERIFY_FAILED	Нет ca.pem	Ошибка SSL	Скопировать ca.pem в %APPDATA%\Tracker\
Hostname mismatch	Сертификат без SAN	Ошибка SSL	Перевыпустить сертификат
Keyring недоступен	Окружение	— (fallback срабатывает)	Ничего, используется credentials.enc
Что сотрудник НЕ видит
client_secret — не показывается в UI.

computer_uid — виден на вкладке «Регистрация».

bootstrap-токен — виден только при вводе.

Что видит администратор
В /admin/computers: hostname, UID, привязанный сотрудник, last_seen_at, статус.

В /admin/tokens: список токенов, использованные и активные.

В /admin/logins: история входов (для админки).

В audit_log: все операции с ПК.

Проблемы и решения
Проблема	Причина	Решение
401 Unauthorized	Токен сгорел	Выпустить новый
Токен не принимается	Введён с пробелами	Обрезать .strip()
Keyring не работает	Окружение	Fallback credentials.enc
credentials.enc не читается	Сменился SECRET_ENCRYPTION_KEY	Перерегистрация всех ПК
getaddrinfo failed	IPv6 vs IPv4	https://127.0.0.1 в client/.env
Регистрация не завершается	Сервер недоступен	Проверить сеть, повторить
computer_uid меняется	Переустановка	Ожидаемо, старые сессии остаются на старом ПК
Ротация client_secret
Когда:

Утёк.

Уволился сотрудник.

Плановая (обсуждалась, не реализована).

Процедура:

revoke ПК.

Выпустить новый bootstrap-токен.

Перерегистрировать ПК (см. выше).

Связь с .env
TRACKER_SERVER_URL — адрес сервера (по умолчанию https://127.0.0.1).

TRACKER_PIN — отпечаток сертификата (опционально).

TRACKER_VERSION — версия клиента (для регистрации).

TRACKER_CA_BUNDLE — путь к ca.pem.

Связь с сертификатом
При регистрации используется HTTPS.

Требуется ca.pem в %APPDATA%\Tracker\ca.pem.

Если сертификат самоподписанный — клиент должен ему доверять.

При смене сертификата — нужно обновить ca.pem (вручную или через UI, в планах).

Логи
text
2026-10-02 09:00:00 INFO tracker.registration Not registered, showing dialog
2026-10-02 09:00:15 INFO tracker.registration Registering with token...
2026-10-02 09:00:16 INFO tracker.registration Registration successful
2026-10-02 09:00:16 INFO tracker.registration client_secret saved to keyring
2026-10-02 09:00:16 INFO tracker.registration computer_uid saved to config.json
Проверка регистрации на сервере
SQL:

sql
SELECT id, computer_uid, hostname, is_active, registered_at, last_seen_at
FROM computers
WHERE computer_uid = 'uuid-v4';
Проверить, что ПК не отозван:

sql
SELECT is_active, deleted_at FROM computers WHERE computer_uid = 'uuid-v4';
Что НЕ реализовано
Retranslate RegistrationDialog — диалог на русском хардкодом.

Замена ca.pem через UI — обсуждалось, не реализовано.

Автоматическая перерегистрация при утере client_secret — нет.

Ротация client_secret по расписанию — нет.

Множественные ПК на одного сотрудника — не блокируется, но UI для управления нет.

UI для отзыва ПК — есть в /admin/computers, но не всё покрыто.

Ключевые решения
Bootstrap-токен — одноразовый. После использования сгорает.

client_secret хранится в keyring. Нативное хранилище Windows.

Fallback credentials.enc. Если keyring недоступен.

computer_uid сохраняется при перерегистрации. Меняется только секрет.

Регистрация — только через диалог. Никаких консольных команд.

client_secret не показывается в UI. Только сохраняется.

Fernet для шифрования на сервере. SECRET_ENCRYPTION_KEY — критичен.

401 при отозванном ПК. Синхронизация останавливается.

Retry при FK-violation при hard delete. Защита от race с клиентом.

Ссылки на код
запросить: client/registration.py — is_registered, register_with_token, ensure_registered, get_computer_uid

запросить: client/registration_dialog.py — RegistrationDialog

запросить: client/config.py — get_setting, set_setting, get_server_url

запросить: client/http_client.py — httpx, pinning, CA bundle

запросить: client/settings_dialog.py — RegistrationTab

запросить: server/main.py — POST /api/v1/computers/register

запросить: server/main.py — POST /api/v1/admin/computers/{uid}/revoke, POST /api/v1/admin/computers/{uid}/re-registration-token

запросить: server/models.py — Computer, BootstrapToken

запросить: server/config.py — FERNET, settings

запросить: server/web_admin.py — computers_re_registration_token, computer_revoke

запросить: server/templates/computers.html — UI для перерегистрации

Открытые вопросы / чего не хватает
нет данных: точная структура credentials.enc (JSON или Fernet-строка).

нет данных: реализован ли retry при регистрации — нет.

нет данных: показывается ли понятная ошибка при SSL: CERTIFICATE_VERIFY_FAILED — да, в логах.

нет данных: есть ли проверка os_info на сервере — да, сохраняется.

не решено: нужна ли кнопка «Отмена» в RegistrationDialog.

не решено: как быть с несколькими ПК на одного сотрудника (union в отчётах).

не решено: нужна ли автоматическая перерегистрация при утере client_secret.

не решено: как показывать статус revoked в клиенте — сейчас просто ошибка.

не решено: должен ли клиент сам удалять credentials.enc при перерегистрации.

не решено: нужна ли поддержка bootstrap.txt (сейчас читается из %APPDATA%\Tracker\bootstrap.txt).

не решено: retranslate диалога регистрации.

не решено: нужна ли возможность «отвязать ПК» без перерегистрации.

Готово. Один файл выше. Следующий по индексу — 05_SCP\01_OVERVIEW.md.