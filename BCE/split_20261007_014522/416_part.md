<!-- Часть 416 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Version](415_Version.md) | [Оглавление](00_BCE_INDEX.md) | [В окне клиента — правый клик на трее ? Выход ▶](417_V_okne_klienta_pravyy_klik_na_tree_Vyhod.md)

---

# ============================================================

@app.get("/api/v1/version", response_model=VersionResponse)
def get_latest_version(current: str = "", db: Session = Depends(get_db)):
    latest = (db.query(ClientVersion)
              .order_by(ClientVersion.release_date.desc()).first())
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
    return VersionResponse(latest_version=latest.version,
                           download_url=latest.download_url,
                           mandatory=latest.mandatory,
                           release_notes=latest.release_notes)
'@
[System.IO.File]::WriteAllText("$serverDir\main.py", $main_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  server/main.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$serverDir\main.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — пересборка сервера
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25

docker compose ps
Write-Host "`n--- Логи API ---" -ForegroundColor Cyan
docker compose logs api --tail=40
________________________________________
Скрипт 3 — на клиенте чистим «застрявшие» сессии
На клиенте накопились старые сессии, которые никогда не отправятся (те, что дают 409). Раз сервер теперь отвечает 200 на 409 — они отправятся при следующем цикле. Но чтобы не ждать 30 секунд, перезапустите клиент.
powershell
