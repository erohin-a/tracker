<!-- Часть 821 из 1409 -->
# Проверка	Ожидаемое
*Хлебные крошки:* Проверка	Ожидаемое

[◀ Проверим ключевые строки](820_Proverim_klyuchevye_stroki.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](822_part.md)

---

#	Проверка	Ожидаемое
1	Alembic	2602b71902d4
2	Таблицы	computers, employees, departments, work_sessions, bootstrap_tokens, client_versions, audit_log, app_settings, calendar_days, schedules, admin_users, admin_logins, scheduled_tasks, task_runs, api_keys, daily_stats, backup_config, employee_settings + alembic_version
3	Партиции	37
4	employee_settings	10 колонок
5	schedules	есть
6	admin_users	есть
7	Soft-delete	3 колонки: is_deleted, deleted_at, deleted_by
8	JSON	11 полей, включая reminder_* и end_of_day_*
9	/admin/login	HTTP 200
________________________________________
Порядок
Проверка файла (первый скрипт) — пришли SYNTAX OK или трейсбек.
Если ОК — сброс volume (второй скрипт) — пришли логи.
Если миграции прошли — полная проверка (третий скрипт) — пришли 9 блоков.
Стоп-условие: если в логах Alembic упадёт на любой миграции — не повторяй down -v, пришли мне traceback. Разрулим за один шаг.
Запускай, жду выводы. Как только увидим 2602b71902d4 (head) и зелёные проверки — идём в Спринт 5, часть A, этап 2: патчим /api/v1/client-config под эффективные настройки для конкретного ПК, добавляем UI /admin/employees/{id}/settings, и endpoint PUT /api/v1/client-settings.
Отлично! Всё работает идеально:
? Alembic применил все 4 миграции на чистую БД
? version_num = 2602b71902d4 (head)
? 20 таблиц + 37 партиций records
? employee_settings создана со всеми полями
? schedules, admin_users из ecb1e3f89300 есть
? Soft-delete в records (3 колонки)
? /api/v1/client-config возвращает все 11 полей включая reminder_* и end_of_day_*
? Scheduler запущен — видим задачи:
cleanup_trash (cron=0 3 * * *, disabled)
create_future_partitions (cron=0 4 1 * *, enabled) ? критично
vacuum_analyze_hot_tables (cron=0 2 * * 0, disabled)
cleanup_old_admin_logins (cron=0 5 1 * *, disabled)
cleanup_old_task_runs (cron=30 5 * * 0, disabled)
aggregate_daily_stats (cron=0 1 * * *, enabled)
Пункт 9 — curl -k -s -o $null -w показал пустоту. Скорее всего потому что $null в PowerShell — это не то же, что /dev/null в bash. curl.exe использует NUL на Windows, или просто надо без -o. Но это мелочь. Проверю отдельно.
Также в логах видим, что у main.py уже есть:
init_tasks — загрузка дефолтных задач
scheduler — APScheduler запущен
Advisory lock 77777 — защита от race condition (только один воркер из нескольких запускает scheduler)
Это означает, что часть Спринта 1.2 (планировщик + задачи) уже реализована. И часть Спринта 2 (в admin_users) — модель есть, UI нет.
Теперь идём в Спринт 5, часть A, этап 2:
Патч /api/v1/client-config — читает X-Computer-Uid, находит employee_id, мержит глобальные дефолты + персональные из employee_settings
Endpoint PUT /api/v1/client-settings — приём изменений от клиента
UI: страница /admin/employees/{id}/settings
Начнём. По плану:
Сначала фиксим "мелочь" — проверка /admin/login
Потом патчим main.py (client-config)
Потом UI: страница settings сотрудника
Потом endpoint PUT client-settings
Разберём по шагам.
Что нужно понимать в архитектуре endpoint /api/v1/client-config:
Сейчас:
python
@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    # возвращает только глобальные настройки
Надо:
python
@app.get("/api/v1/client-config")
def get_client_config(request: Request, db: Session = Depends(get_db)):
    # 1. Читаем X-Computer-Uid из headers
    # 2. Если есть — находим Computer по computer_uid, потом employee_id
    # 3. Читаем employee_settings для этого employee_id (если есть)
    # 4. Мержим: global_defaults + overrides из employee_settings
    # 5. Возвращаем эффективные настройки
Но! Есть нюанс: endpoint /api/v1/client-config сейчас НЕ требует X-Computer-Uid. Клиент может его дёргать без авторизации. По плану надо сделать его опциональным — если UID есть, применяем персональные; если нет — только глобальные. Это ок для случаев:
Клиент ещё не зарегистрирован (до register) — получит глобальные
Клиент зарегистрирован — получит персональные
Дополнительные поля в employee_settings, которые надо вернуть:
reminder_enabled (bool)
reminder_threshold_minutes (int)
reminder_repeat_minutes (int)
reminder_max_per_day (int)
end_of_day_hour (int)
end_of_day_minute (int)
Каждое поле nullable — если NULL, берём глобальное значение.
Также нужно определиться — вернуть ли в ответе "source" (откуда взято каждое значение: global или personal). Это полезно для UI клиента — показать "это персональная настройка" или "это общая".
Для простоты пока не делаем. Просто возвращаем эффективные значения.
Что дальше — endpoint PUT /api/v1/client-settings:
python
@app.put("/api/v1/client-settings")
def update_client_settings(
    settings: ClientSettingsIn,  # Pydantic схема
    comp: Computer = Depends(get_computer),
    db: Session = Depends(get_db),
):
    # 1. Находим employee_id по comp
    # 2. Если нет employee_id — 400 ("ПК не привязан к сотруднику")
    # 3. Читаем employee_settings (или создаём)
    # 4. Обновляем поля, которые пришли
    # 5. Записываем в audit_log
    # 6. Возвращаем эффективные настройки
Приоритет при конфликте — server wins. То есть:
Если сервер менял настройки недавно (updated_at > N минут назад), отклоняем клиентские изменения
Иначе принимаем
Или проще: клиент отправляет изменение, сервер его пишет, но при следующем GET /client-config клиент получит именно то, что на сервере. То есть всегда server wins.
Дальше UI: страница /admin/employees/{id}/settings.
Что должно быть на странице:
Форма с полями reminder_, end_of_day_
Каждое поле: чекбокс "использовать персональное" + значение
Или проще: пустое поле = "как у всех", заполнено = "персональное"
Кнопка "Сбросить к общим"
Информация: глобальные значения для справки
Начнём по частям. Сначала — Схема и endpoint GET /client-config.
Разбиваю на скрипты:
Скрипт 1 — проверить admin/login (мелочь)
Скрипт 2 — Pydantic схема ClientSettingsIn (в schemas.py)
Скрипт 3 — Патч main.py: /api/v1/client-config с мержем персональных
Скрипт 4 — Патч main.py: PUT /api/v1/client-settings
Скрипт 5 — UI: страница /admin/employees/{id}/settings + форма в web_admin.py
Скрипт 6 — Шаблон employees/settings.html
Скрипт 7 — Пересборка и проверка
Начну. Учитывая объём, давай первые 2-3 скрипта в этом сообщении, потом следующие.
Также обратил внимание: в логах scheduler упоминается aggregate_daily_stats — но daily_stats в models.py мы делали. И create_future_partitions — это как раз server/tasks.py. Значит, часть работы из Спринта 1.2 и Спринта 5 (планировщик) уже сделана. Отлично.
Также init_tasks создаёт дефолтные задачи. Есть server/init_tasks.py или что-то подобное. И server/scheduler.py. И server/tasks.py. Не помню, что именно в них — но они работают.
Пойдём.
________________________________________
Кстати, я должен проверить — не сломана ли сейчас логика client-config после всех правок. Судя по выводу, endpoint работает, возвращает 11 полей. Хорошо.
Но! Проверю reminder_enabled в ответе:
text
"reminder_enabled":true
Boolean. Правильно.
И end_of_day_hour:19, end_of_day_minute:0 — тоже.
Значит, базовая инфраструктура для глобальных настроек УЖЕ работает. Теперь надо добавить мерж с персональными.
Начнём.
?? Полная победа! Всё применилось с нуля идеально
Разбор ключевых моментов
Alembic применил все 4 миграции:
text
Running upgrade  -> 35d67a73f181, baseline
Running upgrade 35d67a73f181 -> 939e3d0b6f4c, partition_records_by_month
Running upgrade 939e3d0b6f4c -> ecb1e3f89300, add_schedules_roles_scheduler_apikeys_dailystats_backup
Running upgrade ecb1e3f89300 -> 2602b71902d4, add_employee_settings
Проверки:
? version_num = 2602b71902d4 (head)
? 20 таблиц
? 37 партиций records — партиционирование работает
? employee_settings — 10 колонок, все на месте
? schedules, admin_users — из ecb1e3f89300
? Soft-delete колонки в records
? /api/v1/client-config — 11 полей, включая reminder_* и end_of_day_*
? Планировщик запущен — вижу 6 задач в логах:
create_future_partitions (enabled) — критично
aggregate_daily_stats (enabled)
Остальные 4 — disabled по умолчанию
Что уже сделано (оказывается, больше, чем я думал)
Судя по логам, уже реализовано:
server/init_tasks.py — дефолтные задачи
server/scheduler.py — APScheduler с advisory lock (защита от race между воркерами)
server/tasks.py — сами задачи (create_future_partitions на строке 116)
Глобальные настройки напоминания через AppSetting (работает /api/v1/client-config)
Значит, Спринт 1.2 (планировщик) частично готов. Мы в Спринте 5, часть A, этап 2.
Пункт 9 (/admin/login) в выводе пустой — но это мелочь. $null в PowerShell не то же, что /dev/null в bash. Проверим заодно.
________________________________________
Спринт 5, часть A, этап 2 — индивидуальные настройки
Что делаем
Схема Pydantic — ClientSettingsIn для приёма настроек от клиента.
Патч /api/v1/client-config — читает X-Computer-Uid, находит employee_id, мержит глобальные + персональные из employee_settings.
Endpoint PUT /api/v1/client-settings — приём изменений от клиента. Server wins.
UI: страница /admin/employees/{id}/settings — форма, где пусто = "как у всех".
Кнопка "Настройки напоминания" в карточке сотрудника — переход на эту страницу.
Клиент (этап 3, следующим сообщением) — client/reminder.py + интеграция.
Разбиваю на скрипты, чтобы ты не запутался.
________________________________________
Скрипт 1 — проверка /admin/login (мелочь, 5 секунд)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== /admin/login ===" -ForegroundColor Cyan
curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin/login"

Write-Host "`n=== /admin (должен быть 303 на логин) ===" -ForegroundColor Cyan
curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin"

Write-Host "`n=== /admin/settings ===" -ForegroundColor Cyan
curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin/settings"
Ожидаем: 200 для login, 303 или 200 для остальных.
________________________________________
Скрипт 2 — Pydantic схема ClientSettingsIn
Добавляем в server/schemas.py:
powershell
$ErrorActionPreference = "Continue"

$addition = @'


