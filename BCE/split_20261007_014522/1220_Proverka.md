<!-- Часть 1220 из 1409 -->
# Проверка
*Хлебные крошки:* Проверка

[◀ Отрезаем всё от <script> после CDN до </script>](1219_Otrezaem_vse_ot_script_posle_CDN_do_script.md) | [Оглавление](00_BCE_INDEX.md) | [Трекер — учёт рабочего времени. Handoff-документ ▶](1221_Treker_uchet_rabochego_vremeni_Handoff_dokument.md)

---

# Проверка
$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
foreach ($m in @('durationSum', 'aggregatorTemplates', "'Отдел', 'Сотрудник'", 'pivotUI')) {
    if ($check.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}
Что ожидаем:
text
OK: JS-блок шаблона заменён (~4500 символов)
 OK: durationSum
 OK: aggregatorTemplates
 OK: 'Отдел', 'Сотрудник'
 OK: pivotUI
________________________________________
Скрипт 2 — Пересборка и проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
docker compose logs api --tail=15
После этого:
Открой https://localhost/admin/reports/pivot.
Жёстко обнови страницу: Ctrl+Shift+R (или Ctrl+F5) — сбросить кеш JS.
Через пару секунд должна отрендериться таблица с числами в формате HH:MM:SS.
________________________________________
Файл-handoff
Скопируй текст ниже в файл D:\tracker\HANDOFF.md (или любое удобное место). Это компактная, но полная сводка проекта. Прикладывай её в новый чат вместо огромного файла переписки.
markdown
