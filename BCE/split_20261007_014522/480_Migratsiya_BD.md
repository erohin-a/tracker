<!-- Часть 480 из 1409 -->
# Миграция БД
*Хлебные крошки:* Миграция БД

[◀ Добавляем CalendarDay в models.py](479_Dobavlyaem_CalendarDay_v_models_py.md) | [Оглавление](00_BCE_INDEX.md) | [--- requirements.txt: добавить reportlab --- ▶](481_requirements_txt_dobavit_reportlab.md)

---

# Миграция БД
Write-Host "`n--- Миграция БД ---" -ForegroundColor Cyan
cd D:\tracker
docker compose up -d db
Start-Sleep -Seconds 5

docker compose exec -T db psql -U tracker -d tracker -c @"
CREATE TABLE IF NOT EXISTS calendar_days (
    day VARCHAR(10) PRIMARY KEY,
    is_working BOOLEAN NOT NULL DEFAULT TRUE,
    note VARCHAR(255),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"@

Write-Host "OK  таблица calendar_days" -ForegroundColor Green
________________________________________
Скрипт C2 — requirements.txt + шрифт для PDF
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

