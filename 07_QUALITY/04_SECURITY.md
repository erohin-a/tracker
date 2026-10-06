# Безопасность
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\04_AUTH.md, 06_DEPLOY\02_NGINX_TLS.md, 04_CLIENT\09_REGISTRATION.md, 05_SCP\02_CERTIFICATES.md

## Назначение
Собрать в одном месте все аспекты безопасности «Трекера»: аутентификация, шифрование, TLS, секреты, защита от атак, приватность. Это справочник для администратора, отвечающего за безопасность, и для разработчика, который вносит изменения.

## Содержание

### Принципы безопасности
1. **Данные у вас.** Не вендор, не облако — ваш сервер.
2. **Минимум сбора.** Только счётчики активности, без содержимого.
3. **HMAC на каждой записи.** Целостность данных.
4. **Шифрование секретов.** Fernet для `client_secret`.
5. **Пароли — bcrypt.** Никогда не в открытом виде.
6. **TLS только 1.2/1.3.** HSTS включён.
7. **Ротация секретов.** Описана для всех ключей.
8. **Аудит всех действий.** `audit_log`, `admin_logins`.

---

### Аутентификация

#### Клиент → сервер: HMAC-SHA256
- **Что:** каждая запись и батч подписаны `client_secret`.
- **Canonical JSON:** `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`.
- **Защита от:** подмены данных, повторной отправки, MITM на уровне данных.
- **Не защищает от:** компрометации `client_secret`.
- **Ротация:** revoke ПК + перерегистрация.
- **Подробности:** `03_SERVER\04_AUTH.md`.

#### Bootstrap-токены
- **Что:** одноразовый токен для регистрации ПК.
- **Хранение:** хеш sha256 в `bootstrap_tokens.token_hash`.
- **TTL:** по умолчанию 24 часа, для перерегистрации — 1 час.
- **Защита от:** несанкционированной регистрации ПК.
- **Ротация:** одноразовые, сгорают после использования.

#### Сессии админки (cookie `tracker_admin`)
- **Что:** cookie с данными пользователя.
- **Хранилище:** SessionMiddleware (Starlette).
- **Флаги:** `httpOnly`, `samesite=lax`, `secure` (в проде).
- **Защита от:** XSS (httpOnly), CSRF (samesite).
- **Ротация:** смена `JWT_SECRET` → сброс всех сессий.

#### Admin API (`X-Admin-Token`)
- **Что:** заголовок с `ADMIN_API_KEY`.
- **Защита от:** несанкционированного доступа к админ API.
- **Ротация:** смена `ADMIN_API_KEY` в `.env`.

#### Пароли админов
- **Хеширование:** bcrypt (прямой, без passlib).
- **Требования:** ≥ 8 символов.
- **Защита от:** brute-force (медленный bcrypt), rainbow tables (соль).
- **Ротация:** через `/admin/users/{id}/reset-password` или SCP.

---

### Шифрование

#### `client_secret` на сервере
- **Что:** симметричный ключ ПК, зашифрован в БД.
- **Алгоритм:** Fernet (AES-128 CBC + HMAC-SHA256).
- **Ключ:** `SECRET_ENCRYPTION_KEY` из `.env`.
- **Почему Fernet:** обратимое шифрование, «защищённый от дурака» AES.
- **Ротация:** только при компрометации, с полной перерегистрацией.

#### `client_secret` на клиенте
- **Основное:** Windows keyring (Credential Manager).
- **Fallback:** `%APPDATA%\Tracker\credentials.enc` (Fernet/DPAPI).
- **Почему keyring:** нативное хранилище ОС.
- **Ротация:** revoke + перерегистрация.

#### Секреты в `.env`
| Секрет | Формат | Шифрование |
|---|---|---|
| `SECRET_ENCRYPTION_KEY` | Fernet-ключ (44 символа base64) | Не шифруется, хранится в `.env` |
| `JWT_SECRET` | URL-safe, 48+ байт | Не шифруется |
| `ADMIN_API_KEY` | URL-safe, 48+ байт | Не шифруется |

**Правила:**
- UTF-8 без BOM.
- Без пробелов вокруг `=`.
- В `.gitignore`.
- Не пересылать по открытым каналам.
- Хранить отдельно от бэкапа БД.

---

### TLS

#### Сертификаты
| Файл | Путь | Назначение |
|---|---|---|
| `fullchain.pem` | `D:\tracker\certs\fullchain.pem` | Публичный сертификат |
| `privkey.pem` | `D:\tracker\certs\privkey.pem` | Приватный ключ |
| `ca.pem` | `D:\tracker\client\ca.pem` | Копия для клиента |

#### Протоколы
- TLS 1.2 и TLS 1.3.
- TLS 1.0 и 1.1 — отключены.

#### HSTS
```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
2 года.

Браузер запоминает и требует HTTPS.

Certificate Pinning
Опционально через TRACKER_PIN в client/.env.

Зачем: защита от MITM с корпоративным прокси.

Минус: при смене сертификата все клиенты отвалятся.

Реализация: PinningTransport в client/http_client.py.

SAN (Subject Alternative Name)
Обязательно для современных клиентов.

Без SAN — Hostname mismatch.

Пример: -addext "subjectAltName=DNS:localhost,IP:127.0.0.1".

Ротация сертификата
Через SCP (05_SCP\02_CERTIFICATES.md).

Последствия: все клиенты отключатся, нужно раздать новый ca.pem.

Процедура: бэкап → генерация → копирование в client/ca.pem → перезапуск nginx.

Защита от атак
Атака	Защита	Реализовано
MITM	TLS + HMAC + Pinning	✅
Подмена данных	HMAC на каждой записи	✅
Повторная отправка (replay)	Идемпотентность по record_uid	✅
Brute-force паролей	bcrypt (медленный)	✅
XSS	httpOnly cookie	✅
CSRF	samesite=lax	✅
SQL-инъекции	SQLAlchemy ORM	✅
Clickjacking	Не реализовано	❌
MIME-sniffing	Не реализовано	❌
Rate limiting	Не реализовано	❌
IP-whitelist	Не реализовано	❌
2FA	Не реализовано	❌
Рекомендации (не реализованы)
X-Frame-Options: DENY — защита от clickjacking.

X-Content-Type-Options: nosniff — защита от MIME-sniffing.

Content-Security-Policy — ограничение источников.

Referrer-Policy — контроль referer.

Permissions-Policy — ограничение API браузера.

Rate limiting на /admin/login.

IP-whitelist для админки.

2FA (TOTP) для админов.

Секреты и их ротация
SECRET_ENCRYPTION_KEY
Где	D:\tracker\.env
Формат	Fernet-ключ, 44 символа base64
Назначение	Шифрование client_secret в БД
При смене	Все client_secret не расшифруются → перерегистрация всех ПК
Когда менять	Только при компрометации
Процедура	См. 03_SERVER\04_AUTH.md
JWT_SECRET
Где	D:\tracker\.env
Формат	URL-safe, 48+ байт
Назначение	Подпись cookie админки
При смене	Сессии админки сбросятся, перелогин
Когда менять	При утечке, раз в 6–12 мес
ADMIN_API_KEY
Где	D:\tracker\.env
Формат	URL-safe, 48+ байт
Назначение	Пароль admin + admin API
При смене	Перелогин админов
Когда менять	При утечке, при увольнении админа
client_secret
Где	keyring на ПК + computers.client_secret_enc
Формат	URL-safe, 48 символов
Назначение	HMAC-подпись
При смене	Revoke + перерегистрация одного ПК
Когда менять	При утечке
Bootstrap-токен
Где	bootstrap_tokens (хеш)
Формат	secrets.token_urlsafe(32)
Назначение	Регистрация ПК
При смене	Одноразовый, сгорает
Когда менять	При утечке — удалить из БД
TLS-приватный ключ
Где	D:\tracker\certs\privkey.pem
Формат	PEM
Назначение	TLS
При смене	Все клиенты отключатся
Когда менять	При компрометации, раз в 1–2 года
Генерация секретов
powershell
# SECRET_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# JWT_SECRET, ADMIN_API_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Bootstrap-токен (автоматически на сервере)
python -c "import secrets; print(secrets.token_urlsafe(32))"
Приватность и 152-ФЗ
Что собирается
Счётчики нажатий клавиатуры (без содержимого).

Клики и скролл мыши.

Имя приложения и заголовок окна (при смене).

Периоды простоя (idle).

Что НЕ собирается
Содержимое нажатий (COLLECT_KEYSTROKE_CHARS = False).

Скриншоты.

Пароли, тексты, URL.

Позиция курсора.

Требования 152-ФЗ
Письменное согласие сотрудников на обработку ПДн.

Приказ о введении мониторинга.

Уведомление Роскомнадзора об обработке ПДн.

Описание мер защиты (ст. 19 152-ФЗ).

Что уже сделано «в запас»
COLLECT_KEYSTROKE_CHARS = False.

Аудит всех действий админа.

Роли (admin/operator/hr/manager/viewer).

Soft delete для компьютеров и сессий.

Механизм delete-forever для полного удаления.

Что НЕ реализовано
Юридическое оформление (согласия, приказ, уведомление РКН).

Отчёт о мерах защиты.

Обработка запросов на удаление ПДн.

Аудит и логи
audit_log
Все значимые действия админов.

actor, entity, entity_id, action, old_value, new_value.

Не логируются отказы (403).

admin_logins
Каждая попытка входа (успех/отказ).

IP, User-Agent, причина отказа.

Логи сервера
docker compose logs api — ошибки, исключения.

Middleware для логирования 500 (рекомендуется).

Логи клиента
%APPDATA%\Tracker\client.log — ошибки синхронизации, регистрации.

Что НЕ реализовано (сводка)
Область	Что не реализовано	Приоритет
Заголовки безопасности	X-Frame-Options, CSP, Referrer-Policy, Permissions-Policy	P2
Rate limiting	На /admin/login	P2
IP-whitelist	Для админки	P3
2FA	TOTP для админов	P3
Подпись .exe	Authenticode	P1
Проверка SHA-256 .exe	При скачивании	P1
Шифрование бэкапов	152-ФЗ	P2
Vault/KMS	Для секретов	P3
Penetration testing	Аудит безопасности	P3
Логирование 403	Отказы в доступе	P2
Автоматическая ротация	Секретов	P3
Мониторинг сертификата	«Скоро истекает»	P2
Чек-лист безопасности
□ .env в .gitignore.
□ .env в UTF-8 без BOM.
□ SECRET_ENCRYPTION_KEY сгенерирован.
□ JWT_SECRET сгенерирован.
□ ADMIN_API_KEY сгенерирован.
□ TLS-сертификат с SAN.
□ HSTS включён.
□ TLS 1.2/1.3 только.
□ ca.pem на клиентах.
□ Pinning (опционально).
□ Пароль admin сменён с дефолтного.
□ Роли настроены.
□ Аудит работает.
□ Резервные копии делаются.
□ .env хранится отдельно от бэкапа БД.
□ 152-ФЗ оформлен (для прода).
□ Тесты на проникновение (P3).
Ключевые решения
HMAC на каждой записи. Целостность + офлайн.

Fernet для client_secret. Обратимое шифрование.

bcrypt для паролей. Прямой, без passlib.

TLS 1.2/1.3 + HSTS. Современный стандарт.

SAN обязателен. Без него — mismatch.

Pinning опционален. Для повышения безопасности.

SECRET_ENCRYPTION_KEY не ротируется. Только при компрометации.

Ротация ADMIN_API_KEY и JWT_SECRET — легко. Перелогин.

Bootstrap-токены одноразовые. Сгорают.

Скриншоты не собираются. Приватность + 152-ФЗ.

Содержимое нажатий не собирается. COLLECT_KEYSTROKE_CHARS = False.

Ссылки на код
запросить: server/security.py — HMAC, canonical_json

запросить: server/security_passwords.py — bcrypt, ROLES_INFO

запросить: server/config.py — settings, FERNET, проверка секретов

запросить: server/main.py — middleware, аутентификация API

запросить: server/web_admin.py — login, logout, setup, current_admin

запросить: client/crypto.py — HMAC

запросить: client/http_client.py — httpx, pinning

запросить: client/registration.py — keyring, fallback

запросить: server/nginx.conf — TLS, HSTS

запросить: certs/fullchain.pem, certs/privkey.pem — сертификаты

запросить: D:\tracker\.env — секреты

Открытые вопросы / чего не хватает
нет данных: реализованы ли заголовки безопасности (X-Frame-Options и др.) — нет.

нет данных: есть ли rate limiting — нет.

нет данных: есть ли IP-whitelist — нет.

нет данных: есть ли 2FA — нет.

нет данных: подписан ли .exe — нет.

нет данных: шифруются ли бэкапы — нет.

нет данных: используется ли Vault/KMS — нет.

не решено: нужны ли заголовки безопасности (P2).

не решено: нужен ли rate limiting на /admin/login (P2).

не решено: нужен ли IP-whitelist для админки (P3).

не решено: нужна ли 2FA для админов (P3).

не решено: подписывать ли .exe (P1).

не решено: проверять ли SHA-256 .exe (P1).

не решено: шифровать ли бэкапы (P2).

не решено: использовать ли Vault/KMS (P3).

не решено: логировать ли 403 в audit_log (P2).

не решено: нужна ли автоматическая ротация секретов (P3).

не решено: нужен ли мониторинг срока действия сертификата (P2).

не решено: как быть с 152-ФЗ — юридическое оформление.

не решено: нужен ли penetration testing (P3).

не решено: как хранить privkey.pem для прода (Vault, KMS).

не решено: нужна ли поддержка OAuth/SSO для админов.

Готово. Один файл выше. Следующий по индексу — 08_LEGAL\01_152FZ.md.