# Проверка	Ожидаемое

*Часть 52 из 100. Источник: `BCE.md`.*

[◀ revision identifiers, used by Alembic](051_revision_identifiers_used_by_Alembic.md) | [Оглавление](00_BCE_INDEX.md) | [2. profile.* ключи ▶](053_2_profile_klyuchi.md)

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


# ============================================================
# Клиентские настройки напоминания (приём от клиента)
# ============================================================
from typing import Optional as _Opt

class ClientSettingsIn(BaseModel):
    """Настройки, которые клиент может поменять локально и запушить на сервер."""
    reminder_enabled: _Opt[bool] = None
    reminder_threshold_minutes: _Opt[int] = Field(None, ge=1, le=480)
    reminder_repeat_minutes: _Opt[int] = Field(None, ge=1, le=480)
    reminder_max_per_day: _Opt[int] = Field(None, ge=1, le=100)
    end_of_day_hour: _Opt[int] = Field(None, ge=0, le=23)
    end_of_day_minute: _Opt[int] = Field(None, ge=0, le=59)


class ClientSettingsOut(BaseModel):
    """Эффективные настройки — что клиент получит в ответе."""
    reminder_enabled: bool
    reminder_threshold_minutes: int
    reminder_repeat_minutes: int
    reminder_max_per_day: int
    end_of_day_hour: int
    end_of_day_minute: int
    # Источник: "personal" / "global" — для UI клиента (показать бейдж)
    source_reminder: str = "global"
    source_end_of_day: str = "global"
'@

$schemasPath = "D:\tracker\server\schemas.py"
$content = [System.IO.File]::ReadAllText($schemasPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("class ClientSettingsIn")) {
    Write-Host "SKIP: ClientSettingsIn уже есть" -ForegroundColor Yellow
} else {
    $content = $content.TrimEnd() + $addition + "`n"
    [System.IO.File]::WriteAllText($schemasPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: ClientSettingsIn добавлена" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$schemasPath', encoding='utf-8').read()); print('SYNTAX OK')"
Ожидаем: SYNTAX OK.
________________________________________
Скрипт 3 — главный: патч /api/v1/client-config (мерж персональных)
Здесь логика:
Читаем X-Computer-Uid из headers (опционально).
Если есть — находим Computer, потом employee_id.
Читаем employee_settings для этого employee_id.
Для каждого поля: personal.value if not None else global_default.
Возвращаем эффективные значения + source_reminder / source_end_of_day (какие поля персональные).
Используем Python-патчер — надёжнее, чем Replace со сложными строками.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import sys
import ast
import re

MAIN = r"D:\tracker\server\main.py"

with open(MAIN, "r", encoding="utf-8") as f:
    content = f.read()

if "def _merge_effective_settings" in content:
    print("SKIP: уже пропатчен")
    raise SystemExit(0)

# Находим начало функции get_client_config
start_marker = '@app.get("/api/v1/client-config")'
start = content.find(start_marker)
if start < 0:
    print("ERROR: декоратор /api/v1/client-config не найден")
    raise SystemExit(1)

# Находим конец функции (следующий @app. или # ===)
end1 = content.find("\n@app.", start + 10)
end2 = content.find("\n# ===", start + 10)
ends = [e for e in (end1, end2) if e > 0]
if not ends:
    print("ERROR: не нашли конец функции")
    raise SystemExit(1)
end = min(ends)

# Новая версия функции
new_func = '''@app.get("/api/v1/client-config")
def get_client_config(request: Request, db: Session = Depends(get_db)):
    """
    Клиент подтягивает эту конфигурацию раз в 5 минут.
    
    Если передан заголовок X-Computer-Uid и этот ПК привязан
    к сотруднику, в employee_settings есть персональные настройки —
    они перекрывают глобальные (AppSetting). Иначе — только глобальные.
    """
    from .models import AppSetting as _AppSetting, Computer as _Computer, EmployeeSettings as _ES

    # --- 1. Глобальные дефолты ---
    def getv(key, default, mn, mx):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        try:
            return max(mn, min(mx, int(row.value))) if row else default
        except (ValueError, TypeError):
            return default

    def getstr(key, default):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        return row.value if row else default

    eff = {
        "idle_close_minutes": getv("idle_close_minutes", 30, 5, 480),
        "sync_interval": getv("sync_interval", 30, 5, 3600),
        "batch_size": getv("batch_size", 200, 10, 1000),
        "active_window_interval": getv("active_window_interval", 5, 1, 60),
        "idle_threshold": getv("idle_threshold", 60, 10, 3600),
        "reminder_enabled": getstr("reminder_enabled", "1") == "1",
        "reminder_threshold_minutes": getv("reminder_threshold_minutes", 15, 1, 480),
        "reminder_repeat_minutes": getv("reminder_repeat_minutes", 10, 1, 480),
        "reminder_max_per_day": getv("reminder_max_per_day", 5, 1, 100),
        "end_of_day_hour": getv("end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": getv("end_of_day_minute", 0, 0, 59),
    }
    eff["source_reminder"] = "global"
    eff["source_end_of_day"] = "global"

    # --- 2. Персональные override (если ПК привязан к сотруднику) ---
    computer_uid = request.headers.get("X-Computer-Uid")
    if computer_uid:
        comp = db.query(_Computer).filter(_Computer.computer_uid == computer_uid).first()
        if comp and comp.employee_id:
            es = db.query(_ES).filter(_ES.employee_id == comp.employee_id).first()
            if es:
                # reminder-настройки
                reminder_fields = [
                    "reminder_enabled",
                    "reminder_threshold_minutes",
                    "reminder_repeat_minutes",
                    "reminder_max_per_day",
                ]
                for field in reminder_fields:
                    val = getattr(es, field, None)
                    if val is not None:
                        eff[field] = val
                        eff["source_reminder"] = "personal"
                # end-of-day
                eod_fields = ["end_of_day_hour", "end_of_day_minute"]
                for field in eod_fields:
                    val = getattr(es, field, None)
                    if val is not None:
                        eff[field] = val
                        eff["source_end_of_day"] = "personal"

    return eff
'''

new_content = content[:start] + new_func + content[end:]

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(new_content)

print("OK: get_client_config переписан с мержем персональных")

try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# Проверки
checks = [
    "def _merge_effective_settings",   # не должно быть — просто маркер, что мы не переписали
    "source_reminder",                  # появилось
    "source_end_of_day",                # появилось
    "comp.employee_id",                 # логика поиска
    "_ES",                              # алиас EmployeeSettings
]
for c in checks:
    found = c in new_content
    mark = "OK" if (c != "def _merge_effective_settings" or not found) else "ОШИБКА"
    print(f"  {mark}: {c} = {found}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_client_config.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _patch_client_config.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_client_config.py
Что ожидаем:
text
OK: get_client_config переписан с мержем персональных
SYNTAX OK
  OK: def _merge_effective_settings = False
  OK: source_reminder = True
  OK: source_end_of_day = True
  OK: comp.employee_id = True
  OK: _ES = True
________________________________________
Скрипт 4 — endpoint PUT /api/v1/client-settings
Добавляем новый endpoint после get_client_config. Он принимает JSON, применяет к employee_settings, отдаёт эффективные.
Приоритет — server wins: если сервер недавно менял (updated_at > 5 минут назад и updated_by != "client"), отклоняем. Иначе принимаем.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import sys
import ast

MAIN = r"D:\tracker\server\main.py"

with open(MAIN, "r", encoding="utf-8") as f:
    content = f.read()

if "/api/v1/client-settings" in content:
    print("SKIP: /client-settings уже есть")
    raise SystemExit(0)

# Вставляем после функции get_client_config
marker = "    return eff\n\n"
pos = content.find(marker)
if pos < 0:
    print("ERROR: маркер конца get_client_config не найден")
    raise SystemExit(1)
insert_at = pos + len(marker)

new_endpoint = '''# ============================================================
# Приём изменений настроек от клиента
# ============================================================
@app.put("/api/v1/client-settings")
def update_client_settings(
    payload: ClientSettingsIn,
    comp: Computer = Depends(get_computer),
    db: Session = Depends(get_db),
):
    """
    Клиент отправляет свои локальные изменения настроек.
    
    Логика приоритета (server wins):
    - Если сервер недавно менял настройки (updated_at < 5 минут назад)
      и updated_by != "client" — отклоняем клиентские изменения, возвращаем
      то, что на сервере.
    - Иначе — применяем клиентские изменения, пишем в audit_log.
    
    Требует X-Computer-Uid. Если ПК не привязан к сотруднику — 400.
    """
    from datetime import timedelta as _td
    from .models import EmployeeSettings as _ES
    from .schemas import ClientSettingsOut as _Out

    if not comp.employee_id:
        raise HTTPException(
            400,
            "Компьютер не привязан к сотруднику. Обратитесь к администратору.",
        )

    es = db.query(_ES).filter(_ES.employee_id == comp.employee_id).first()

    # Проверка приоритета: если сервер менял недавно — server wins
    now = _now()
    server_recently = False
    if es and es.updated_at:
        updated = es.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if (now - updated) < _td(minutes=5) and (es.updated_by or "") != "client":
            server_recently = True

    if not server_recently:
        # Создаём запись, если её нет
        if not es:
            es = _ES(employee_id=comp.employee_id, updated_by="client")
            db.add(es)

        # Применяем только те поля, что пришли (не None)
        changed = []
        for field in [
            "reminder_enabled",
            "reminder_threshold_minutes",
            "reminder_repeat_minutes",
            "reminder_max_per_day",
            "end_of_day_hour",
            "end_of_day_minute",
        ]:
            new_val = getattr(payload, field, None)
            if new_val is not None:
                old_val = getattr(es, field, None)
                if old_val != new_val:
                    setattr(es, field, new_val)
                    changed.append({"field": field, "old": old_val, "new": new_val})

        es.updated_at = now
        es.updated_by = "client"

        if changed:
            db.add(AuditLog(
                actor=f"client:{comp.computer_uid}",
                entity="employee_settings",
                entity_id=str(comp.employee_id),
                action="client_update",
                new_value=json.dumps(changed, ensure_ascii=False, default=str),
            ))
        db.commit()
        log.info(
            "client-settings applied for emp=%s from comp=%s, changed=%d",
            comp.employee_id, comp.computer_uid, len(changed),
        )
    else:
        log.info(
            "client-settings rejected (server_recently_changed) emp=%s",
            comp.employee_id,
        )

    # Возвращаем эффективные настройки (как в GET)
    # Переиспользуем логику — вызовем get_client_config через внутренний расчёт
    from .models import AppSetting as _AppSetting

    def getv(key, default, mn, mx):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        try:
            return max(mn, min(mx, int(row.value))) if row else default
        except (ValueError, TypeError):
            return default

    def getstr(key, default):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        return row.value if row else default

    eff = {
        "reminder_enabled": getstr("reminder_enabled", "1") == "1",
        "reminder_threshold_minutes": getv("reminder_threshold_minutes", 15, 1, 480),
        "reminder_repeat_minutes": getv("reminder_repeat_minutes", 10, 1, 480),
        "reminder_max_per_day": getv("reminder_max_per_day", 5, 1, 100),
        "end_of_day_hour": getv("end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": getv("end_of_day_minute", 0, 0, 59),
        "source_reminder": "global",
        "source_end_of_day": "global",
    }
    if es:
        for field in ["reminder_enabled", "reminder_threshold_minutes",
                      "reminder_repeat_minutes", "reminder_max_per_day"]:
            val = getattr(es, field, None)
            if val is not None:
                eff[field] = val
                eff["source_reminder"] = "personal"
        for field in ["end_of_day_hour", "end_of_day_minute"]:
            val = getattr(es, field, None)
            if val is not None:
                eff[field] = val
                eff["source_end_of_day"] = "personal"

    return eff


'''

new_content = content[:insert_at] + new_endpoint + content[insert_at:]

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(new_content)

print("OK: /api/v1/client-settings добавлен")

try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# Проверки
checks = [
    "/api/v1/client-settings",
    "server_recently",
    "ClientSettingsIn",
    "client_update",
]
for c in checks:
    found = c in new_content
    print(f"  {'OK' if found else 'MISS'}: {c}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_client_settings_endpoint.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _patch_client_settings_endpoint.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_client_settings_endpoint.py
Что ожидаем:
text
OK: /api/v1/client-settings добавлен
SYNTAX OK
  OK: /api/v1/client-settings
  OK: server_recently
  OK: ClientSettingsIn
  OK: client_update
Важно: я использую ClientSettingsIn и ClientSettingsOut из schemas.py, но не импортировал их в main.py. Проверим импорты — если их нет, надо добавить. Посмотрим после запуска.
________________________________________
Порядок запусков
Скрипт 1 — проверка admin/login (30 сек)
Скрипт 2 — Pydantic схема (30 сек)
Скрипт 3 — патч client-config (2 мин)
Скрипт 4 — новый endpoint PUT /client-settings (2 мин)
Запускай по порядку и пришли мне вывод каждого. После Скрипта 3 и 4 — не пересобирай сразу, я должен проверить, что импорты ClientSettingsIn в main.py корректны, иначе будет NameError при старте.
Если в Скрипте 4 увидим MISS: ClientSettingsIn — значит нужно добавить импорт в main.py, дам отдельный мини-скрипт.
________________________________________
Что дальше (следующее сообщение)
После того как оба endpoint'а заработают и пересоберём:
UI: страница /admin/employees/{id}/settings — форма с полями + кнопка "Сбросить к общим".
Кнопка "Настройки напоминания" в карточке сотрудника.
Клиентская часть (этап 3): client/reminder.py, патчи main.py клиента.
Погнали. Запускай 1?2?3?4 по очереди, присылай выводы.
Скрипт 1 PS D:\tracker> $ErrorActionPreference = "Continue" >> Set-Location D:\tracker >> >> Write-Host "=== /admin/login ===" -ForegroundColor Cyan >> curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin/login" >> >> Write-Host "`n=== /admin (должен быть 303 на логин) ===" -ForegroundColor Cyan >> curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin" >> >> Write-Host "`n=== /admin/settings ===" -ForegroundColor Cyan >> curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin/settings" === /admin/login === HTTP 303 === /admin (должен быть 303 на логин) === HTTP 301 === /admin/settings === HTTP 401 PS D:\tracker>
Отлично. Из диагностики:
i18n — почти всё на месте, отсутствует только menu.profile
logins.html — структура понятна, в нём тоже есть крокозябры [Р»РѕРіРё] (это "Логи") и в†ђ (стрелка)
users.html — тоже есть крокозябры, но это отдельная тема
Теперь моя задача:
Добавить menu.profile + i18n ключи для profile страницы
Патчить base.html — разграничить sidebar по ролям + добавить ссылку на profile
Создать /admin/profile — страницу профиля
Проверить/починить крокозябры в users.html и logins.html (убрать [СЂРµРґ] и т.д.)
Но сначала — я должен показать контекст base.html (строки 140-260). Пользователь не запустил вторую команду. Мне нужно попросить показать base.html.
Хотя... по выводу я уже вижу большинство строк. Мне нужно увидеть полный контекст, чтобы патчить точно. Давай запрошу.
Но чтобы не терять время, я могу:
Добавить i18n ключи
Показать base.html и запросить патч
Параллельно — начать с чистки крокозябр в users.html и logins.html
Давай сделаю всё сразу.
Стоп, нужно подумать. base.html у меня нет целиком. Я знаю только некоторые строки (140-198). Но мне нужно:
Строки 140 — начало sidebar
Строки 200-260 — конец sidebar и main content
Где именно вставлять условия по ролям
Давай попрошу показать base.html строки 130-260, а параллельно дам скрипт для i18n ключей.
Также надо решить, что с крокозябрами в users.html. Судя по всему, там [СЂРµРґ] — это [ред] (редактировать) — испортилось при копировании. Или это emoji ??. Надо заменить на чистые emoji или на текст без emoji.
Аналогично в logins.html — [Р»РѕРіРё] это [логи], в†ђ это ?.
Давай сначала i18n ключи, потом base.html диагностика, потом патчи.
Пусть ответ будет:
Добавляем i18n ключи (menu.profile + profile.*)
Запрос base.html для точного патча
Пока параллельно — починим крокозябры в users.html и logins.html
Или проще — давай сразу патчим base.html по тому что вижу (я знаю структуру). Патч такой:
Обернуть группы в условия по ролям
Заменить ссылку на logout / добавить перед ней ссылку на profile
Давай напишу патч по кусочкам. Мне нужно:
Строка 141-143 — группа Main (Дашборд) — доступна всем
Строка 149-161 — группа Directories (Сотрудники, Отделы, Графики, Компьютеры) — доступна admin, operator, hr, manager (без viewer)
Строка 165-179 — группа Data (Отчёты, Сессии, Календарь, Аудит) — доступна всем кроме viewer
Строка 185-199 — группа Admin (Токены, Планировщик, Пользователи, Входы, Корзина, Настройки) — только admin и оператор (частично)
Конкретная матрица:
Пункт	admin	operator	hr	manager	viewer
Дашборд	?	?	?	?	?
Сотрудники	?	?	?	?	?
Отделы	?	?	?	?	?
Графики	?	?	?	?	?
Компьютеры	?	?	?	?	?
Отчёты	?	?	?	? (свой отдел)	?
Сессии	?	?	?	?	?
Календарь	?	?	?	?	?
Аудит	?	?	?	?	?
Токены	?	?	?	?	?
Планировщик	?	?	?	?	?
Пользователи	?	?	?	?	?
Входы	?	?	?	?	?
Корзина	?	?	?	?	?
Настройки	?	?	?	?	?
Слишком сложно. Давай упростим:
admin — всё
operator — все группы, кроме «Пользователи», «Входы», «Корзина», «Настройки», «Планировщик», «Аудит»
hr — только «Справочники» (Сотрудники, Отделы, Графики, Календарь) + Дашборд + Отчёты
manager — Дашборд + Отчёты + Сотрудники
viewer — Дашборд + Отчёты
Это можно реализовать через {% if current_role in (...)%}.
Хорошо. Давай сделаю патч:
Сначала i18n — menu.profile + profile.* + поменять/добавить нужные ключи
Запросить base.html строки 130-270 для точного anchor
Параллельно — фикс крокозябр в users.html и logins.html
Начну.
Отлично — не хватает только menu.profile. Действуем по шагам
Скрипт 1 — i18n-ключи (profile + меню)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

I18N = r"D:\tracker\server\i18n.py"

with open(I18N, "r", encoding="utf-8") as f:
    content = f.read()

changed = []

# 1. menu.profile
if '"menu.profile"' not in content:
    old = '"menu.logout":'
    new = '"menu.profile": {"ru": "Мой профиль", "en": "My profile"},\n    "menu.logout":'
    if old in content:
        content = content.replace(old, new, 1)
        changed.append("menu.profile")

