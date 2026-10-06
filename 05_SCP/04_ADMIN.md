# Администрирование (SCP AdminTab)
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 05_SCP\01_OVERVIEW.md, 03_SERVER\04_AUTH.md, 09_OPS\01_RUNBOOK.md

## Назначение
Описать вкладку «Администрирование» (AdminTab) в SCP: что она должна делать, что уже реализовано, какие ручные процедуры можно выполнять сейчас и какие риски. Это карта для администратора сервера и для разработчика, который дорабатывает SCP.

## Содержание

### Что такое AdminTab
- Третья вкладка в SCP (`control/gui.py`).
- **Назначение:** операции уровня сервера, связанные с секретами и доступом.
- **Текущее состояние:** заглушка с текстом «⏳ Вкладка в разработке».
- **Не реализована**, но запланирована.

### Планируемые функции

| # | Функция | Приоритет | Риск |
|---|---|---|---|
| 1 | Сброс пароля веб-админа | P1 | Низкий |
| 2 | Смена `ADMIN_API_KEY` | P1 | Средний (перелогин) |
| 3 | Смена `JWT_SECRET` | P2 | Низкий (сброс сессий) |
| 4 | Смена `SECRET_ENCRYPTION_KEY` | P3 | **Критичный** (перерегистрация всех ПК) |
| 5 | Просмотр размера БД и количества записей | P2 | Нет |
| 6 | Диагностика (healthcheck, версия API) | P2 | Нет |
| 7 | Просмотр `audit_log` за 24 часа | P3 | Нет |

### 1. Сброс пароля веб-админа

**Зачем:**
- Админ забыл пароль.
- Подозрение на компрометацию.
- Плановая ротация.

**Планируемая логика:**
1. Кнопка «Сбросить пароль веб-админа».
2. Диалог: выбор пользователя из `admin_users` (или сброс для `admin`).
3. Генерация нового случайного пароля (`secrets.token_urlsafe(16)`).
4. Хеширование bcrypt.
5. `UPDATE admin_users SET password_hash = ? WHERE id = ?`.
6. Запись в `audit_log`.
7. Показ нового пароля один раз (скопировать в буфер).

**Ручная процедура (сейчас):**
1. Сгенерировать новый пароль:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(16))"
Сгенерировать bcrypt-хеш:

python
import bcrypt
password = "новый_пароль"
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hash)
Обновить в БД:

sql
UPDATE admin_users SET password_hash = '<hash>' WHERE username = 'admin';
Проверить вход: https://localhost/admin/login.

Альтернатива через существующий UI:

Если админ ещё может войти — /admin/users/{id}/reset-password.

Если админ заблокирован — только через SQL.

2. Смена ADMIN_API_KEY
Что это: пароль для входа admin + токен для /api/v1/admin/*.

Где хранится: D:\tracker\.env → ADMIN_API_KEY=....

Когда менять:

Утёк в чат/документ.

Уволился сотрудник, знавший ключ.

Плановая ротация (раз в 6–12 мес).

Ручная процедура:

Сгенерировать новый ключ:

powershell
python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(48))"
Открыть D:\tracker\.env, заменить строку ADMIN_API_KEY=....

Важно: UTF-8 без BOM, без пробелов вокруг =.

Перезапустить сервер:

powershell
cd D:\tracker
docker compose down
docker compose up -d --build
Проверить вход:

text
https://localhost/admin/login
Логин: admin
Пароль: новый ADMIN_API_KEY
Проверить admin API:

powershell
curl.exe -k -H "X-Admin-Token: новый_ключ" https://localhost/api/v1/admin/...
Что НЕ затрагивается: клиенты (они используют client_secret, не ADMIN_API_KEY).

Последствия: все текущие сессии админки инвалидируются, нужен перелогин.

Планируемая логика в AdminTab:

Кнопка «Сгенерировать новый ADMIN_API_KEY».

Автоматическое обновление .env.

docker compose down && docker compose up -d --build через subprocess.

Показ нового ключа.

3. Смена JWT_SECRET
Что это: секрет для подписи cookie админки (tracker_admin).

Где хранится: D:\tracker\.env → JWT_SECRET=....

Когда менять:

Утёк.

Плановая ротация.

Ручная процедура:

Сгенерировать:

powershell
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(48))"
Заменить в .env.

docker compose down && docker compose up -d --build.

Последствия: все сессии админки сбросятся, нужен перелогин. Клиенты не затронуты.

Планируемая логика в AdminTab:

Кнопка «Сменить JWT_SECRET».

Генерация + запись в .env + перезапуск.

4. Смена SECRET_ENCRYPTION_KEY
Что это: Fernet-ключ для шифрования client_secret в computers.client_secret_enc.

Где хранится: D:\tracker\.env → SECRET_ENCRYPTION_KEY=....

⚠ Опасно. Смена ключа ломает расшифровку всех client_secret. Все ПК получат bad_signature и перестанут синхронизироваться.

Когда менять:

Утечка ключа.

Компрометация сервера.

Не для плановой ротации.

Ручная процедура (с полной перерегистрацией):

Сгенерировать новый ключ:

powershell
python -c "from cryptography.fernet import Fernet; print('SECRET_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
Заменить в .env.

docker compose down && docker compose up -d --build.

Отозвать все ПК в /admin/computers (revoke).

Выпустить новые bootstrap-токены.

На каждом ПК удалить %APPDATA%\Tracker\credentials.enc и keyring-запись.

Перерегистрировать каждый ПК.

Последствия: все ПК нужно перерегистрировать. Простой в работе.

Планируемая логика в AdminTab:

Кнопка «Сменить SECRET_ENCRYPTION_KEY» с двойным подтверждением.

Предупреждение о полной перерегистрации.

Вероятно, не будет реализована — слишком опасно. Оставить только в инструкции.

5. Просмотр размера БД и количества записей
Зачем: контроль роста БД, оценка необходимости retention.

Планируемые метрики:

Метрика	SQL
Размер pgdata	docker volume inspect tracker_pgdata
Размер records	SELECT pg_size_pretty(pg_total_relation_size('records'));
Количество records	SELECT COUNT(*) FROM records;
Количество work_sessions	SELECT COUNT(*) FROM work_sessions;
Количество computers	SELECT COUNT(*) FROM computers;
Количество employees	SELECT COUNT(*) FROM employees;
Размер audit_log	SELECT pg_size_pretty(pg_total_relation_size('audit_log'));
Ручная проверка:

powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT pg_size_pretty(pg_total_relation_size('records'));"
6. Диагностика
Планируемые проверки:

Проверка	Как
Docker контейнеры запущены	docker compose ps
API отвечает	curl.exe -k https://localhost/api/v1/version
БД доступна	docker compose exec -T db psql -U tracker -d tracker -c "SELECT 1;"
nginx работает	docker compose logs nginx --tail=10
Планировщик работает	docker compose logs api --tail=50 | Select-String "scheduler"
Последние ошибки API	docker compose logs api --tail=100 | Select-String "Error|Traceback"
Ручная проверка: см. 09_OPS\01_RUNBOOK.md.

7. Просмотр audit_log за 24 часа
Зачем: быстрая проверка, что происходило на сервере.

Планируемая логика:

SQL-запрос к audit_log с фильтром created_at >= now() - interval '24 hours'.

Вывод в UI (таблица).

Ручная проверка:

sql
SELECT created_at, actor, entity, entity_id, action
FROM audit_log
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY id DESC;
Другие ручные процедуры администрирования
Перезапуск API без rebuild
Для правок HTML достаточно: docker compose restart api.

Для правок Python нужен rebuild: docker compose down && docker compose up -d --build.

Просмотр логов в реальном времени
powershell
docker compose logs -f api
Восстановление из бэкапа
Остановить сервер: docker compose down.

Восстановить: Get-Content backup.sql | docker compose exec -T db psql -U tracker -d tracker.

Запустить: docker compose up -d --build.

Сброс БД (ОПАСНО)
powershell
docker compose down -v  # удаляет volume pgdata
docker compose up -d --build
Внимание: все данные пропадут. Перед этим — бэкап.

Диагностика проблем
Симптом	Причина	Решение
Cannot connect to Docker daemon	Docker Desktop не запущен	Запустить Docker Desktop
api в Restarting	Ошибка Python / миграции	docker compose logs api --tail=100
nginx не поднимается	Ошибка сертификата / порт занят	docker compose logs nginx --tail=50, netstat -ano | findstr :443
db unhealthy	Volume повреждён	docker compose logs db --tail=50
Клиент «офлайн»	Сервер не отвечает	curl.exe -k https://localhost/api/v1/version
getaddrinfo failed	IPv6 vs IPv4	https://127.0.0.1 в client/.env
500 на отчётах	Ошибка в web_admin.py	docker compose logs api --tail=100
Volume pgdata удалён	Выполнили docker compose down -v	Восстановить из бэкапа
Порт 80 занят Windows	HTTP.sys (IIS/WinRM)	Использовать только 443
Быстрая диагностика за 30 секунд
powershell
cd D:\tracker
docker info | Select-String "Server Version"     # 1. Docker запущен
docker compose ps                                 # 2. Контейнеры живы
curl.exe -k https://localhost/api/v1/version      # 3. API отвечает
docker compose exec -T db psql -U tracker -d tracker -c "\dt"  # 4. БД видит таблицы
docker compose logs api --tail=30                 # 5. Последние ошибки
Что НЕ делает AdminTab
Не управляет сотрудниками/отделами (веб-админка).

Не строит отчёты (веб-админка).

Не редактирует настройки приложения (веб-админка).

Не работает по сети — только локально на сервере.

Не удаляет данные (кроме явного сброса).

Что НЕ реализовано
AdminTab в SCP — заглушка.

Кнопка «Сбросить пароль веб-админа» — не реализована.

Кнопка «Сменить ADMIN_API_KEY» — не реализована.

Кнопка «Сменить JWT_SECRET» — не реализована.

Кнопка «Сменить SECRET_ENCRYPTION_KEY» — не реализована (и, вероятно, не будет).

Просмотр размера БД — не реализован.

Диагностика — не реализована.

Просмотр audit_log — не реализован.

Ключевые решения
AdminTab — для операций уровня сервера. Не для контента.

Ротация секретов — через .env + перезапуск. Не через UI (пока).

Смена SECRET_ENCRYPTION_KEY — только при компрометации. Не плановая.

Смена ADMIN_API_KEY — легко. Перелогин админов.

Смена JWT_SECRET — легко. Сброс сессий админки.

Просмотр размера БД — через SQL. Не критично для UI.

Диагностика — через docker compose logs. Стандартные команды.

Все действия — логировать в audit_log. Если реализуем.

Не удалять данные через SCP. Только через веб-админку.

Ссылки на код
запросить: control/gui.py — AdminTab (заглушка)

запросить: server/config.py — settings.admin_api_key, settings.jwt_secret, settings.secret_encryption_key, FERNET

запросить: server/security_passwords.py — hash_password, verify_password

запросить: server/models.py — AdminUser, AuditLog

запросить: server/web_admin.py — /admin/users/{id}/reset-password (веб-версия)

запросить: D:\tracker\.env — секреты

запросить: docker-compose.yml — для docker compose команд

Открытые вопросы / чего не хватает
нет данных: будет ли AdminTab реализован в ближайшее время — в планах (P1).

нет данных: есть ли защита от случайной смены SECRET_ENCRYPTION_KEY — нет.

нет данных: логируется ли смена секретов в audit_log — нет.

нет данных: какой формат у credentials.enc — JSON, зашифрованный Fernet.

не решено: делать ли кнопку «Сменить SECRET_ENCRYPTION_KEY» вообще.

не решено: нужна ли автопроверка «сертификат истекает» с алертом.

не решено: как быть с ротацией секретов по расписанию.

не решено: нужна ли 2FA для админов.

не решено: должен ли AdminTab уметь работать с удалённым сервером (SSH).

не решено: нужна ли интеграция с Vault/KMS.

не решено: логировать ли действия AdminTab в audit_log.

не решено: нужна ли кнопка «Перезапустить API без rebuild».

не решено: должен ли AdminTab показывать статус планировщика.

не решено: нужен ли экспорт audit_log в CSV.

не решено: должен ли AdminTab показывать список активных сессий админки.

не решено: где хранить privkey.pem для прода (Vault, KMS).

Готово. Один файл выше. Следующий по индексу — 06_DEPLOY\01_DOCKER.md.