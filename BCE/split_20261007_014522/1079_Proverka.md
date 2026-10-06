<!-- Часть 1079 из 1409 -->
# Проверка
*Хлебные крошки:* Проверка

[◀ и заменяем на 6 карточек. Используем простой якорь — строку с "Сессий"](1078_i_zamenyaem_na_6_kartochek_Ispolzuem_prostoy_yakor_stroku_s_Sessiy.md) | [Оглавление](00_BCE_INDEX.md) | [Ищем блок с totals в _build_report ▶](1080_Ischem_blok_s_totals_v_build_report.md)

---

# Проверка
$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
foreach ($m in @('worked_span_duration', 'break_duration', 'idle_duration')) {
    Write-Host (" {0}: {1}" -f $m, $(if ($check.Contains($m)) { "OK" } else { "MISS" })) -ForegroundColor $(if ($check.Contains($m)) { "Green" } else { "Red" })
}
Скрипт 3 — Добавить break_duration и idle_duration в бэкенд
Если в web_admin.py этих полей в report["totals"] нет — их надо добавить.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "break_duration" in content:
    print("SKIP: break_duration уже есть")
    raise SystemExit(0)

