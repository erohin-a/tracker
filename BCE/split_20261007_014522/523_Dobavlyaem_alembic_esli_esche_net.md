<!-- Часть 523 из 1409 -->
# Добавляем alembic, если ещё нет
*Хлебные крошки:* Добавляем alembic, если ещё нет

[◀ /app должен быть в sys.path](522_app_dolzhen_byt_v_sys_path.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](524_part.md)

---

# Добавляем alembic, если ещё нет
if ($req -notmatch "alembic") {
    $req = $req.TrimEnd() + "`nalembic==1.13.2`n"
    [System.IO.File]::WriteAllText($reqPath, $req, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: alembic добавлен в requirements.txt" -ForegroundColor Green
} else {
    Write-Host "alembic уже есть" -ForegroundColor Yellow
}
Get-Content $reqPath
________________________________________
Скрипт D2 — создаём server/alembic.ini
powershell
powershell
$ErrorActionPreference = "Stop"
$alembicIni = "D:\tracker\server\alembic.ini"

$iniContent = @'
