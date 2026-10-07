# Проверка

*Часть 73 из 100. Источник: `BCE.md`.*

[◀ full_duration = от первой до последней РЕАЛЬНОЙ активности](072_full_duration_ot_pervoy_do_posledney_REALNOY_aktivnosti.md) | [Оглавление](00_BCE_INDEX.md) | [Пишем в НОВЫЙ файл (в другой папке) — не трогаем оригинал ▶](074_Pishem_v_NOVYY_fayl_v_drugoy_papke_ne_trogaem_original.md)

---

# Проверка
$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
if ($check.Contains("stale_session_hours")) {
    Write-Host " Поле в шаблоне: OK" -ForegroundColor Green
} else {
    Write-Host " Поле в шаблоне: MISS" -ForegroundColor Red
}
Что ожидаем:
text
OK: поле stale_session_hours добавлено
 Поле в шаблоне: OK
________________________________________
Пересборка сервера
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Проверка синтаксиса ===" -ForegroundColor Cyan
client\.venv\Scripts\python.exe -c "import ast; ast.parse(open(r'D:\tracker\server\web_admin.py', encoding='utf-8').read()); ast.parse(open(r'D:\tracker\server\main.py', encoding='utf-8').read()); ast.parse(open(r'D:\tracker\server\tasks.py', encoding='utf-8').read()); print('ALL SYNTAX OK')"

Write-Host "`n=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25

Write-Host "`n=== Статус ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи API (последние 30 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`n=== Проверка что задача зарегистрирована ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron FROM scheduled_tasks WHERE name='close_stale_sessions';"

Write-Host "`n=== Проверка что настройка есть ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT key, value FROM app_settings WHERE key='stale_session_hours';"
Что ожидаем:
ALL SYNTAX OK
все 3 контейнера Up
в логах — Scheduler запущен в этом воркере
в scheduled_tasks — строка close_stale_sessions | t | */30 * * * *
в app_settings — пусто или stale_session_hours | 2 (если сохранял)
________________________________________
Что делаем дальше
Запускай по порядку:
Шаг 3+6 — патч отчётов. Ожидаем 3 OK + SYNTAX OK.
Шаг 4 — предохранитель. Ожидаем 1 OK + SYNTAX OK.
Шаг 5a — новая задача. Ожидаем OK + SYNTAX OK.
Шаг 5b — настройка. Ожидаем 3 OK + SYNTAX OK.
Шаг 5c — шаблон. Ожидаем OK + проверка.
Пересборка. Ожидаем статус Up и всё чисто.
Присылай вывод. Если где-то ERROR — стоп, пришли только этот шаг, поправим.
После этого:
Откроем /admin/settings и убедимся, что поле «Автозакрытие зависших сессий» появилось.
Сформируем отчёт за 23.09 и увидим, что 24 часа превратились в ~5-6.
Обнулим БД (docker compose down -v) для чистой работы.
>> & client\.venv\Scripts\python.exe _patch_tasks_stale.py === Патч tasks.py === OK: задача зарегистрирована в TASKS_REGISTRY Traceback (most recent call last): File "D:\tracker\_patch_tasks_stale.py", line 133, in <module> with open(PATH, "w", encoding="utf-8") as f: ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ PermissionError: [Errno 13] Permission denied: 'D:\\tracker\\server\\tasks.py'
Пользователь запустил патчи. Шаг 3+6 — OK. Шаг 5a (tasks.py) упал с PermissionError — файл занят. Скорее всего контейнер api его держит, или что-то ещё.
PermissionError на tasks.py — наиболее вероятная причина: файл открыт в редакторе (VS Code, Notepad++) или занят процессом. Также может быть — контейнер Docker смонтирован и файл read-only (но у нас не mount, у нас копируется при сборке).
Проверим и перезапустим. Также нужно проверить, что предыдущие шаги (4, 5b, 5c) выполнены — но пользователь показывает только вывод для 3+6 и 5a. Скорее всего он не успел/не показал остальные.
Дам диагностику + обходной путь: закрыть VS Code / редакторы, сохранить через временный файл, или использовать os.replace.
Также важно: после шага 3+6 надо пересобрать api, но перед этим надо доделать 4, 5a, 5b, 5c.
План ответа:
Причина — файл занят (VS Code / проводник / другое).
Диагностика — какие процессы держат файл (можно через PowerShell).
Обходной путь: если VS Code открыт — закрыть; или копировать через временный файл + os.replace.
Продолжить с шага 4, 5b, 5c.
Пересборка.
Дам скрипт-обходной путь, который пишет во временный файл и заменяет через os.replace — это работает даже если файл залочен на чтение/запись в другом процессе (но не всегда на Windows).
На Windows os.replace может не сработать, если файл открыт в другом процессе с эксклюзивной блокировкой. Проверим.
Также лучше сначала сохранить то, что уже сделано (шаг 3+6 прошёл), и не терять. Второй запуск 5a должен пойти.
Стратегия: сначала повторим 5a — возможно, был временный лок от антивируса. Если упадёт снова — попросим закрыть VS Code.
Ошибка PermissionError: [Errno 13] Permission denied на server/tasks.py — файл кем-то занят. Скорее всего, он открыт в редакторе (VS Code, Notepad++, PyCharm) или в проводнике залочен проводником/антивирусом.
Шаги 3+6 прошли — это отлично. Не теряем их результат.
Сначала — закрыть всё, что может держать файл:
Закрой VS Code / PyCharm / Notepad++, если открыт tasks.py или папка server/.
Закрой окно проводника Windows, если открыта папка D:\tracker\server.
Подожди 3 секунды (антивирус может проверять файл).
Теперь диагностика и повтор.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Кто держит tasks.py ===" -ForegroundColor Cyan
# Пробуем монопольно открыть файл — если не получится, кто-то держит
try {
    $fs = [System.IO.File]::Open("D:\tracker\server\tasks.py", 'Open', 'ReadWrite', 'None')
    $fs.Close()
    Write-Host " OK: файл свободен" -ForegroundColor Green
} catch {
    Write-Host " ЗАНЯТ: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host " Ищем процессы, держащие файл (нужен handle.exe или PowerShell 7)..." -ForegroundColor Yellow
    Write-Host " Если найдёшь — закрой вручную. Чаще всего это:" -ForegroundColor Yellow
    Write-Host "   - code.exe (VS Code)" -ForegroundColor Yellow
    Write-Host "   - notepad++.exe" -ForegroundColor Yellow
    Write-Host "   - explorer.exe (открыта папка в проводнике)" -ForegroundColor Yellow
    Write-Host "   - python.exe / pythonw.exe (запущенный клиент)" -ForegroundColor Yellow
}

Write-Host "`n=== Проверка: шаг 3+6 уже в web_admin.py? ===" -ForegroundColor Cyan
$wa = [System.IO.File]::ReadAllText("D:\tracker\server\web_admin.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("_union_duration", "activity_start_local", "activity_end_local")) {
    if ($wa.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}

Write-Host "`n=== tasks.py — есть ли close_stale_sessions? ===" -ForegroundColor Cyan
$ts = [System.IO.File]::ReadAllText("D:\tracker\server\tasks.py", [System.Text.UTF8Encoding]::new($false))
if ($ts.Contains("def close_stale_sessions")) {
    Write-Host " Уже есть (патч применился до ошибки записи?)" -ForegroundColor Yellow
} else {
    Write-Host " НЕТ — надо будет пропатчить" -ForegroundColor Yellow
}
Что ожидаем:
Если файл свободен ? OK: файл свободен
Шаг 3+6 — 3 маркера OK
close_stale_sessions — либо есть, либо нет
________________________________________
Если файл занят — быстрый обходной путь
Скрипт ниже пишет патч во временный файл, а потом делает Move-Item -Force (перезапись с заменой). На Windows это может сработать, даже если файл залочен не эксклюзивно (например, VS Code держит его как read+write but not exclusive).
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import os

PATH = r"D:\tracker\server\tasks.py"
TMP = PATH + ".tmp_patch"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "def close_stale_sessions" in content:
    print("SKIP: close_stale_sessions уже есть")
    raise SystemExit(0)

marker = "# ============================================================\n# Карта задач: имя в scheduler"

new_func = '''# ============================================================
# 7. Автозакрытие зависших сессий
# ============================================================
def close_stale_sessions(db: Session) -> str:
    """
    Закрывает сессии, которые клиент так и не закрыл.

    Сценарий: сотрудник ушёл домой, забыл нажать «Конец работы»,
    ПК выключили или клиент упал. Сессия висит в БД с session_end = NULL.
    Такая сессия портит отчёты (был случай: 17 часов за один день).

    Логика:
      1. Читаем настройку stale_session_hours (по умолчанию 2 часа).
      2. Ищем сессии, где session_end IS NULL
         и session_start < NOW() - stale_session_hours.
      3. Закрываем каждую:
         - session_end = MAX(client_ts) из records (последняя активность)
         - если записей нет — session_end = session_start
         - abnormal_termination = True
      4. Пишем в audit_log.

    Запускается каждые 30 минут (cron */30 * * * *).
    """
    from .models import AppSetting as _AppSetting, Record as _Record

    row = db.query(_AppSetting).filter(
        _AppSetting.key == "stale_session_hours"
    ).first()
    try:
        stale_hours = max(1, min(24, int(row.value))) if row else 2
    except (ValueError, TypeError):
        stale_hours = 2

    cutoff = _now() - timedelta(hours=stale_hours)

    stale = (
        db.query(WorkSession)
        .filter(
            WorkSession.session_end.is_(None),
            WorkSession.session_start < cutoff,
        )
        .all()
    )

    if not stale:
        return f"Зависших сессий нет (порог {stale_hours}ч)"

    closed = 0
    for ws in stale:
        last_record_ts = (
            db.query(_Record.client_ts)
            .filter(_Record.session_uid == ws.session_uid)
            .order_by(_Record.client_ts.desc())
            .limit(1)
            .scalar()
        )

        if last_record_ts is not None:
            end_ts = last_record_ts
        else:
            end_ts = ws.session_start

        ws.session_end = end_ts
        ws.abnormal_termination = True
        closed += 1

        db.add(AuditLog(
            actor="scheduler:close_stale_sessions",
            entity="work_session",
            entity_id=ws.session_uid,
            action="auto_close_stale",
            new_value=(
                f"start={ws.session_start.isoformat()}, "
                f"end={end_ts.isoformat() if end_ts else 'None'}, "
                f"threshold={stale_hours}h"
            ),
        ))

    db.commit()
    log.warning(
        "close_stale_sessions: закрыто %d сессий (порог %dч)",
        closed, stale_hours,
    )
    return f"Закрыто зависших сессий: {closed} (порог {stale_hours}ч)"


'''

if marker not in content:
    print("ERROR: маркер TASKS_REGISTRY не найден")
    raise SystemExit(1)

content = content.replace(marker, new_func + marker, 1)

old_reg = '''    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

new_reg = '''    "close_stale_sessions": {
        "func": close_stale_sessions,
        "label_ru": "Автозакрытие зависших сессий",
        "label_en": "Auto-close stale sessions",
        "desc_ru": "Закрывает сессии без активности дольше N часов (настраивается в /admin/settings).",
        "desc_en": "Closes sessions without activity for N hours.",
        "default_cron": "*/30 * * * *",
        "default_enabled": True,
    },
    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

if old_reg in content:
    content = content.replace(old_reg, new_reg, 1)
    print("OK: задача зарегистрирована в TASKS_REGISTRY")
else:
    print("WARN: не найден блок aggregate_daily_stats")

# Пишем во временный файл
with open(TMP, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    os.remove(TMP)
    raise SystemExit(1)

# Заменяем оригинал
try:
    os.replace(TMP, PATH)
    print("OK: tasks.py перезаписан")
except OSError as e:
    print(f"ERROR replace: {e}")
    print(f"Временный файл оставлен: {TMP}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_tasks_stale.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Повторный патч tasks.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_tasks_stale.py
________________________________________
Что делать сейчас
Запусти сначала диагностику — она короткая, покажет, занят ли файл и что уже прошло.
Если файл свободен — просто повтори патч 5a (первую версию скрипта), он должен пройти.
Если файл занят — закрой все редакторы / проводник и запусти обходной вариант выше.
Пришли вывод диагностики — по нему пойму, что происходит.
Что уже точно есть (шаг 3+6) — не потерялось, проверка покажет.
>> } === Кто держит tasks.py === ЗАНЯТ: Исключение при вызове "Open" с "4" аргументами: "Отказано в доступе по пути "D:\tracker\server\tasks.py"." Ищем процессы, держащие файл (нужен handle.exe или PowerShell 7)... Если найдёшь — закрой вручную. Чаще всего это: - code.exe (VS Code) - notepad++.exe - explorer.exe (открыта папка в проводнике) - python.exe / pythonw.exe (запущенный клиент) === Проверка: шаг 3+6 уже в web_admin.py? === OK: _union_duration OK: activity_start_local OK: activity_end_local === tasks.py — есть ли close_stale_sessions? === НЕТ — надо будет пропатчить
Файл занят. Шаг 3+6 прошёл — web_admin.py содержит все маркеры. Теперь надо разобраться, кто держит tasks.py.
"Отказано в доступе по пути" — это может быть не блокировка процесса (share violation), а именно permission denied — то есть ACL/права файла. Возможно:
Файл открыт в редакторе с блокировкой записи
Файл имеет read-only атрибут
Антивирус блокирует
Файл принадлежит другой учётной записи
Проверим атрибуты файла и попробуем разные подходы:
Снять read-only
Скопировать через robocopy/copy с force
Проверить владельца через Get-Acl
Давай дам диагностику + несколько способов обхода.
Главное — сначала понять реальную причину. "Отказано в доступе" в .NET File.Open с FileShare.None — это именно про блокировку. Если бы был read-only, было бы "Access to the path is denied" при записи, но Open для ReadWrite может открыться.
Хм. Попробуем через обычный PowerShell Get-ItemProperty для атрибутов + попробуем открыть на чтение без монопольного доступа.
План:
Диагностика: атрибуты, ACL, попытка открыть с разными share-режимами
Если read-only ? снять атрибут
Если процесс держит ? найти его
Обходной путь: записать через robocopy или через cmd copy /y
Дам один скрипт с несколькими проверками и обходной путь через robocopy (он часто проходит там, где прямая запись падает).
Также важно — проверить, не запущен ли где-то в фоне python.exe клиента (мы его недавно запускали). Клиент импортирует server.main, но не должен держать файлы сервера в рабочей папке. Хотя... python -m client.main не трогает server/.
Хотя, возможно, у пользователя ещё остались запущенные процессы отладки. Проверим через Get-Process python.
Пишу диагностику + обходной путь.
"Отказано в доступе" — это не обычная блокировка. Три возможных причины:
Файл помечен как read-only (атрибут)
Процесс держит эксклюзивный lock (VS Code, антивирус, python.exe)
Проблема с ACL (правами) на файле
Диагностика ниже покажет, что именно. Плюс дам обходной путь через robocopy — он часто проходит там, где прямая запись падает.
Шаг A — Диагностика и обходной путь
Запусти целиком:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== 1. Атрибуты файла ===" -ForegroundColor Cyan
$item = Get-Item "D:\tracker\server\tasks.py" -Force
$item | Format-List Name, Length, Attributes, LastWriteTime, IsReadOnly

Write-Host "`n=== 2. Попытка открыть на чтение (не монопольно) ===" -ForegroundColor Cyan
try {
    $fs = [System.IO.File]::Open("D:\tracker\server\tasks.py", 'Open', 'Read', 'ReadWrite')
    $len = $fs.Length
    $fs.Close()
    Write-Host " OK: файл читается, размер $len байт" -ForegroundColor Green
} catch {
    Write-Host " ОШИБКА чтения: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 3. Запущенные python процессы ===" -ForegroundColor Cyan
Get-Process python*, pythonw* -ErrorAction SilentlyContinue |
    Select-Object Id, ProcessName, Path, StartTime |
    Format-Table -AutoSize

Write-Host "`n=== 4. Обработчики файла (если есть Sysinternals handle) ===" -ForegroundColor Cyan
if (Get-Command handle.exe -ErrorAction SilentlyContinue) {
    handle.exe "D:\tracker\server\tasks.py"
} else {
    Write-Host " handle.exe не установлен — пропускаем" -ForegroundColor Yellow
}

Write-Host "`n=== 5. Пробуем снять read-only ===" -ForegroundColor Cyan
if ($item.IsReadOnly) {
    try {
        Set-ItemProperty -Path "D:\tracker\server\tasks.py" -Name IsReadOnly -Value $false
        Write-Host " OK: read-only снят" -ForegroundColor Green
    } catch {
        Write-Host " ОШИБКА снятия read-only: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host " Файл не read-only" -ForegroundColor Yellow
}

Write-Host "`n=== 6. Обходной путь через robocopy ===" -ForegroundColor Cyan
# Создаём временный файл с патчем через .NET (в другую папку!)
$patcher = @'
import ast
import os

PATH = r"D:\tracker\server\tasks.py"
TMP = r"D:\tracker\_tasks_new.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "def close_stale_sessions" in content:
    print("SKIP: close_stale_sessions уже есть")
    raise SystemExit(0)

marker = "# ============================================================\n# Карта задач: имя в scheduler"

new_func = '''# ============================================================
# 7. Автозакрытие зависших сессий
# ============================================================
def close_stale_sessions(db: Session) -> str:
    """
    Закрывает сессии, которые клиент так и не закрыл.

    Сценарий: сотрудник ушёл домой, забыл нажать «Конец работы»,
    ПК выключили или клиент упал. Сессия висит в БД с session_end = NULL.
    Такая сессия портит отчёты (был случай: 17 часов за один день).

    Запускается каждые 30 минут (cron */30 * * * *).
    """
    from .models import AppSetting as _AppSetting, Record as _Record

    row = db.query(_AppSetting).filter(
        _AppSetting.key == "stale_session_hours"
    ).first()
    try:
        stale_hours = max(1, min(24, int(row.value))) if row else 2
    except (ValueError, TypeError):
        stale_hours = 2

    cutoff = _now() - timedelta(hours=stale_hours)

    stale = (
        db.query(WorkSession)
        .filter(
            WorkSession.session_end.is_(None),
            WorkSession.session_start < cutoff,
        )
        .all()
    )

    if not stale:
        return f"Зависших сессий нет (порог {stale_hours}ч)"

    closed = 0
    for ws in stale:
        last_record_ts = (
            db.query(_Record.client_ts)
            .filter(_Record.session_uid == ws.session_uid)
            .order_by(_Record.client_ts.desc())
            .limit(1)
            .scalar()
        )

        if last_record_ts is not None:
            end_ts = last_record_ts
        else:
            end_ts = ws.session_start

        ws.session_end = end_ts
        ws.abnormal_termination = True
        closed += 1

        db.add(AuditLog(
            actor="scheduler:close_stale_sessions",
            entity="work_session",
            entity_id=ws.session_uid,
            action="auto_close_stale",
            new_value=(
                f"start={ws.session_start.isoformat()}, "
                f"end={end_ts.isoformat() if end_ts else 'None'}, "
                f"threshold={stale_hours}h"
            ),
        ))

    db.commit()
    log.warning(
        "close_stale_sessions: закрыто %d сессий (порог %dч)",
        closed, stale_hours,
    )
    return f"Закрыто зависших сессий: {closed} (порог {stale_hours}ч)"


'''

if marker not in content:
    print("ERROR: маркер TASKS_REGISTRY не найден")
    raise SystemExit(1)

content = content.replace(marker, new_func + marker, 1)

old_reg = '''    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

new_reg = '''    "close_stale_sessions": {
        "func": close_stale_sessions,
        "label_ru": "Автозакрытие зависших сессий",
        "label_en": "Auto-close stale sessions",
        "desc_ru": "Закрывает сессии без активности дольше N часов (настраивается в /admin/settings).",
        "desc_en": "Closes sessions without activity for N hours.",
        "default_cron": "*/30 * * * *",
        "default_enabled": True,
    },
    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

if old_reg in content:
    content = content.replace(old_reg, new_reg, 1)
    print("OK: задача зарегистрирована в TASKS_REGISTRY")
else:
    print("WARN: не найден блок aggregate_daily_stats")

