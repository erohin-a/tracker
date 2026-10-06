<!-- Часть 820 из 1409 -->
# Проверим ключевые строки
*Хлебные крошки:* Проверим ключевые строки

[◀ revision identifiers, used by Alembic](819_revision_identifiers_used_by_Alembic.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка	Ожидаемое ▶](821_Proverka_Ozhidaemoe.md)

---

# Проверим ключевые строки
print()
print('op.execute вызовов:', content.count('op.execute('))
print('CREATE INDEX:', content.count('CREATE INDEX'))
print('PARTITION OF records:', content.count('PARTITION OF records'))
"@
Ожидаем:
text
SYNTAX OK
op.execute вызовов: 11
CREATE INDEX: 3
PARTITION OF records: 2
Если увидим SYNTAX OK — всё в порядке, идём на сброс.
________________________________________
Скрипт — сброс volume и полный подъём
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Сброс volume (данные тестовые, не жалко) ===" -ForegroundColor Cyan
docker compose down -v

Write-Host "`n=== Пересборка образа API ===" -ForegroundColor Cyan
docker compose build --no-cache api

Write-Host "`n=== Подъём ===" -ForegroundColor Cyan
docker compose up -d
Start-Sleep -Seconds 30

Write-Host "`n=== Статус ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи API (последние 50 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=50
Что ищем в логах:
text
tracker.server INFO Применение миграций Alembic...
alembic.runtime.migration INFO Running upgrade  -> 35d67a73f181, baseline
alembic.runtime.migration INFO Running upgrade 35d67a73f181 -> 939e3d0b6f4c, partition_records_by_month
alembic.runtime.migration INFO Running upgrade 939e3d0b6f4c -> ecb1e3f89300, add_schedules_roles...
alembic.runtime.migration INFO Running upgrade ecb1e3f89300 -> 2602b71902d4, add_employee_settings
tracker.server INFO Миграции Alembic успешно применены
Все 4 строки Running upgrade должны быть. Если Alembic упадёт на 939e3d0b6f4c (например, SyntaxError или cannot create partition) — пришли мне traceback, разрулим.
________________________________________
Скрипт — полная проверка после подъёма
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== 1. Версия Alembic ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT * FROM alembic_version;"

Write-Host "`n=== 2. Все таблицы ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename NOT LIKE 'records_%' ORDER BY tablename;"

Write-Host "`n=== 3. Партиции records (должно быть 37) ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) AS partitions FROM pg_tables WHERE tablename LIKE 'records_%' AND tablename != 'records';"

Write-Host "`n=== 4. employee_settings ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\d employee_settings"

Write-Host "`n=== 5. schedules ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\d schedules" | Select-Object -First 15

Write-Host "`n=== 6. admin_users ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\d admin_users" | Select-Object -First 15

Write-Host "`n=== 7. Soft-delete в records ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT column_name FROM information_schema.columns WHERE table_name='records' AND column_name LIKE 'deleted%' OR (table_name='records' AND column_name='is_deleted');"

Write-Host "`n=== 8. /api/v1/client-config ===" -ForegroundColor Cyan
curl.exe -k -s "https://localhost/api/v1/client-config"

Write-Host "`n=== 9. /admin/login доступен? ===" -ForegroundColor Cyan
curl.exe -k -s -o $null -w "HTTP %{http_code}`n" "https://localhost/admin/login"
Что ожидаем:
