<!-- Часть 1062 из 1409 -->
# Заменяем оригинал
*Хлебные крошки:* Заменяем оригинал

[◀ Пишем во временный файл](1061_Pishem_vo_vremennyy_fayl.md) | [Оглавление](00_BCE_INDEX.md) | [Создаём временный файл с патчем через .NET (в другую папку!) ▶](1063_Sozdaem_vremennyy_fayl_s_patchem_cherez_NET_v_druguyu_papku.md)

---

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
