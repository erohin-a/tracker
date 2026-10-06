# Аутентификация
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\02_API.md, 03_SERVER\03_MODELS.md, 01_PRODUCT\02_USER_ROLES.md

## Назначение
Описать все механизмы аутентификации в «Трекере»: HMAC клиента, bootstrap-токены, сессии админки, bcrypt, роли. Это эталон для разработчика и справочник для администратора по безопасности.

## Содержание

### Четыре механизма аутентификации

| Механизм | Кто использует | Что проверяет сервер |
|---|---|---|
| HMAC-SHA256 + `X-Computer-Uid` | Клиент на ПК | Подпись каждой записи/батча с `client_secret` |
| Bootstrap-токен | Новый ПК при первой регистрации | Хеш токена в `bootstrap_tokens` |
| Сессия в cookie `tracker_admin` | Веб-админка | Данные пользователя в `admin_users` |
| `X-Admin-Token` | Внешние вызовы админ API | Совпадение с `ADMIN_API_KEY` из `.env` |

### 1. HMAC-SHA256 (клиент → сервер)

**Назначение:** гарантировать целостность данных и подлинность источника. Работает в офлайн-режиме, не истекает.

**При регистрации:**
1. Клиент отправляет bootstrap-токен на `POST /api/v1/computers/register`.
2. Сервер генерирует `client_secret = secrets.token_urlsafe(48)`.
3. Шифрует Fernet, сохраняет в `computers.client_secret_enc`.
4. Возвращает `client_secret` клиенту — **один раз**.
5. Клиент сохраняет его в keyring Windows. Fallback — `credentials.enc` (Fernet/DPAPI).

**Canonical JSON:**
```python
def canonical_json(obj: Any) -> bytes:
    normalized = _validate(obj)
    return json.dumps(
        normalized, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
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

При несовпадении — запись помечается poisoned, клиент получает bad_signature.

Файлы: server/security.py, client/crypto.py (идентичны).

2. Bootstrap-токены
Назначение: одноразовая регистрация нового ПК без паролей.

Жизненный цикл:

Админ выпускает токен через /admin/tokens (или POST /api/v1/admin/bootstrap-tokens).

Сервер генерирует secrets.token_urlsafe(32).

Хеш (sha256) сохраняется в bootstrap_tokens.token_hash.

TTL — по умолчанию 24 часа (ttl_hours).

Клиент вводит токен при первом запуске.

Сервер проверяет хеш, TTL, used_at IS NULL.

При успехе — used_at = now(), used_by_uid = computer_uid.

Правила:

Токен показывается администратору один раз.

После использования — сгорает.

Если утёк, но не использован — истечёт сам или удаляется вручную.

Перерегистрация ПК:

POST /api/v1/admin/computers/{uid}/re-registration-token — выпускает новый токен с TTL = 1 час.

Клиент удаляет credentials.enc / keyring-запись и регистрируется заново.

3. Сессии админки (cookie tracker_admin)
Назначение: вход в веб-админку.

Хранилище:

SessionMiddleware (Starlette).

Cookie tracker_admin — подписана, httpOnly, samesite=lax, secure (в проде).

Процесс входа:

POST /admin/login с логином и паролем.

Поиск в admin_users по username.

Проверка пароля через bcrypt.checkpw.

Проверка is_active.

При успехе — request.session["admin_user"] = {id, username, role, full_name, department_id, language}.

Запись в admin_logins (успех или отказ).

last_login_at = now().

Проверка на каждом запросе:

current_admin(request) — возвращает dict или HTTPException(401).

current_admin_or_none(request) — для страниц, где вход не обязателен.

_require_admin_role(request) — для разделов только для admin.

Выход:

GET /admin/logout — request.session.clear() → редирект на login.

Первичная настройка (/admin/setup):

Доступна, только если admin_users пуста.

Создаёт первого администратора с ролью admin.

После — страница возвращает 403.

Первый вход без setup:

Логин admin, пароль ADMIN_API_KEY из .env — если таблица пуста.

4. X-Admin-Token (админ API)
Назначение: внешние вызовы /api/v1/admin/* без интерактивной сессии.

Запрос:

text
POST /api/v1/admin/computers/{uid}/revoke
X-Admin-Token: <ADMIN_API_KEY>
Проверка: сравнение с settings.admin_api_key.

Пароли: bcrypt
Библиотека: прямой bcrypt, без passlib.

Почему не passlib:

passlib выдаёт warnings на Python 3.11+ (использует устаревший crypt).

Нам нужны только hashpw и checkpw.

Меньше зависимостей — меньше проблем на Windows.

Функции (server/security_passwords.py):

python
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    if not password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False
Требования к паролю: ≥ 8 символов. Логин — ≥ 3 символов, только a-zA-Z0-9._-.

needs_rehash: всегда False (bcrypt без параметров — не требуется перехеширование).

Роли
Пять ролей (ROLES_INFO в security_passwords.py):

Код	RU	EN
admin	Администратор	Administrator
operator	Оператор	Operator
hr	Кадровик	HR
manager	Руководитель отдела	Manager
viewer	Наблюдатель	Viewer
Где хранятся: admin_users.role (String(32)).

Где проверяются:

В шаблонах — admin_role через context processor.

В роутах — _require_admin_role(request) — 403, если роль не admin.

В отчётах — manager_department_id(user) — фильтр по отделу для manager.

Защита от «последнего admin»:

_active_admins_count(db) — количество активных admin.

Нельзя удалить/деактивировать/понизить последнего активного admin.

Нельзя удалить/деактивировать самого себя.

Смена роли: через /admin/users/{id}/edit.

Секреты в .env
Секрет	Формат	Назначение	При смене
SECRET_ENCRYPTION_KEY	Fernet (44 символа base64)	Шифрование client_secret	Ломает все ПК → перерегистрация
JWT_SECRET	URL-safe, 48+ байт	Подпись cookie админки	Сброс сессий админки
ADMIN_API_KEY	URL-safe, 48+ байт	Пароль admin + admin API	Смена пароля + перелогин
Генерация:

powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_urlsafe(48))"
Файл .env: UTF-8 без BOM, без пробелов вокруг =. В .gitignore.

Хранение client_secret
На сервере:

computers.client_secret_enc — Fernet-шифрование.

Ключ — SECRET_ENCRYPTION_KEY из .env.

secret_version — версия секрета (для ротации отдельного ПК).

На клиенте:

Windows keyring (keyring.set_password("tracker", "client_secret", ...)).

Fallback — %APPDATA%\Tracker\credentials.enc (Fernet/DPAPI).

Удаление при перерегистрации: только client_secret, computer_uid сохраняется.

Ротация секретов
Секрет	Как часто	Последствия
ADMIN_API_KEY	Раз в 6–12 мес или при утечке	Перелогин админов
JWT_SECRET	Раз в 6–12 мес	Сброс сессий админки
SECRET_ENCRYPTION_KEY	Только при утечке	Перерегистрация всех ПК
client_secret (одного ПК)	При утечке	Revoke + перерегистрация этого ПК
Bootstrap-токен	Одноразовый	Сгорает после использования
TLS-сертификат	Раз в 1–2 года	Все клиенты отвалятся, пока не заменят ca.pem
Процедура ротации ADMIN_API_KEY:

Сгенерировать новый.

Заменить в .env.

docker compose down && docker compose up -d --build.

Проверить вход в админку.

Процедура ротации SECRET_ENCRYPTION_KEY:

Сгенерировать новый.

Заменить в .env.

docker compose down && docker compose up -d --build.

Отозвать все ПК, выпустить новые bootstrap-токены, перерегистрировать.

Если утёк client_secret
POST /api/v1/admin/computers/{uid}/revoke.

На ПК удалить credentials.enc и keyring-запись.

Выпустить новый bootstrap-токен.

Перерегистрировать ПК.

Аудит и логи
admin_logins — каждая попытка входа (успех/отказ, IP, User-Agent).

audit_log — все значимые действия админов (создание, редактирование, удаление).

Клиентские ошибки auth — в логах клиента (client.log) и в audit_log (при reject).

Ключевые решения
HMAC на каждой записи — целостность, офлайн-режим, нет истечения.

Bootstrap-токены — одноразовые — нельзя переиспользовать.

Сессия в cookie — просто и достаточно для админки.

bcrypt напрямую, без passlib — меньше зависимостей, нет warnings.

Fernet для client_secret — обратимое шифрование симметричного ключа.

5 ролей жёстко в коде — не в БД, проще поддержка.

Защита от последнего admin — нельзя остаться без администратора.

SECRET_ENCRYPTION_KEY не ротируется — только при компрометации.

Все timestamps — UTC — нет путаницы с часовыми поясами.

Ссылки на код
запросить: server/security.py — HMAC, canonical_json

запросить: server/security_passwords.py — bcrypt, ROLES_INFO, ROLE_ADMIN

запросить: server/config.py — settings, проверка секретов, FERNET

запросить: server/main.py — регистрация, проверка HMAC

запросить: server/web_admin.py — login, logout, setup, current_admin

запросить: server/models.py — AdminUser, AdminLogin, BootstrapToken, Computer

запросить: client/crypto.py — HMAC (идентичен серверному)

запросить: client/registration.py — keyring, register_with_token, ensure_registered

Открытые вопросы / чего не хватает
нет данных: точный TTL bootstrap-токена по умолчанию — 24 часа (проверено).

нет данных: есть ли rate limiting на /admin/login — не описан.

нет данных: логируется ли bad_signature в audit_log — да, как reject_signature.

не решено: нужна ли 2FA для админов.

не решено: использовать ли OAuth/SSO для входа.

не решено: нужен ли IP-whitelist для админки.

не решено: редирект 401 на /admin/login — не реализован (сейчас JSON).

не решено: нужна ли ротация client_secret по расписанию (не только при утечке).

не решено: где хранить client_secret на Linux-клиенте (keyring есть, но проверено ли).

не решено: должен ли HR видеть раздел «Пользователи» — сейчас нет.

Готово. Один файл выше. Следующий по индексу — 03_SERVER\05_TASKS.md.