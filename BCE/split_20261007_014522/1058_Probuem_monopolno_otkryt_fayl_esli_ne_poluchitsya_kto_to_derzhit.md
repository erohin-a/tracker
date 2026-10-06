<!-- Часть 1058 из 1409 -->
# Пробуем монопольно открыть файл — если не получится, кто-то держит
*Хлебные крошки:* Пробуем монопольно открыть файл — если не получится, кто-то держит

[◀ Проверка](1057_Proverka.md) | [Оглавление](00_BCE_INDEX.md) | [7. Автозакрытие зависших сессий ▶](1059_7_Avtozakrytie_zavisshih_sessiy.md)

---

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
