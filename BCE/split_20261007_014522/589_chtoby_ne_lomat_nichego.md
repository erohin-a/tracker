<!-- Часть 589 из 1409 -->
# чтобы не ломать ничего.
*Хлебные крошки:* чтобы не ломать ничего.

[◀ 3) Убираем импорт init_db (он больше не нужен) — но оставляем саму функцию в database.py,](588_3_Ubiraem_import_init_db_on_bolshe_ne_nuzhen_no_ostavlyaem_samu_funktsiyu_v_data.md) | [Оглавление](00_BCE_INDEX.md) | [Должно быть "Did not find any relations" — БД пустая ▶](590_Dolzhno_byt_Did_not_find_any_relations_BD_pustaya.md)

---

#    чтобы не ломать ничего.
if ($content -match "from \.database import SessionLocal, init_db") {
    $content = $content.Replace(
        "from .database import SessionLocal, init_db",
        "from .database import SessionLocal  # init_db больше не используется (заменён Alembic)"
    )
    Write-Host "OK: убран импорт init_db" -ForegroundColor Green
}

[System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('SYNTAX OK')"
________________________________________
Скрипт D6 — сброс volume и первый запуск (без миграций)
На этом шаге мы поднимем контейнеры, но миграций ещё нет. FastAPI стартует, попытается применить Alembic — и упадёт, потому что нет baseline-миграции. Это нормально — мы сейчас её сгенерируем.
powershell
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

Write-Host "`n=== Останавливаем и удаляем всё ===" -ForegroundColor Cyan
docker compose down -v    # -v удаляет volume pgdata (все данные)

Write-Host "`n=== Пересобираем образ с Alembic ===" -ForegroundColor Cyan
docker compose build --no-cache api

Write-Host "`n=== Запускаем только db, чтобы подготовить её к генерации миграций ===" -ForegroundColor Cyan
docker compose up -d db
Start-Sleep -Seconds 8

Write-Host "`n=== Проверка: БД пустая ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\dt"
