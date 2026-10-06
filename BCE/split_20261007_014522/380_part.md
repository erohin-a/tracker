<!-- Часть 380 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Аудит](379_Audit.md) | [Оглавление](00_BCE_INDEX.md) | [base.html — ссылка на Отделы ▶](381_base_html_ssylka_na_Otdely.md)

---

# ============================================================

@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    logs = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(200).all()
    return templates.TemplateResponse("audit.html", {
        "request": request, "logs": logs, "admin": request.session.get("admin"), "tz": tz,
    })
'@
[System.IO.File]::WriteAllText("$serverDir\web_admin.py", $web_admin_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  web_admin.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$serverDir\web_admin.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 3 — server/main.py: расширяем /api/v1/client-config
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$old = @'
@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    """Клиент подтягивает эту конфигурацию раз в 5 минут."""
    from .models import AppSetting as _AppSetting
    row = db.query(_AppSetting).filter(_AppSetting.key == "idle_close_minutes").first()
    try:
        idle = max(5, min(480, int(row.value))) if row else 30
    except (ValueError, TypeError):
        idle = 30
    return {"idle_close_minutes": idle}
'@

$new = @'
@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    """Клиент подтягивает эту конфигурацию раз в 5 минут."""
    from .models import AppSetting as _AppSetting

    def getv(key, default, mn, mx):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        try:
            return max(mn, min(mx, int(row.value))) if row else default
        except (ValueError, TypeError):
            return default

    return {
        "idle_close_minutes": getv("idle_close_minutes", 30, 5, 480),
        "sync_interval": getv("sync_interval", 30, 5, 3600),
        "batch_size": getv("batch_size", 200, 10, 1000),
        "active_window_interval": getv("active_window_interval", 5, 1, 60),
        "idle_threshold": getv("idle_threshold", 60, 10, 3600),
    }
'@

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  client-config расширен" -ForegroundColor Green
} else {
    Write-Host "  ВНИМАНИЕ: не найдена старая версия endpoint. Пропускаем." -ForegroundColor Yellow
}
python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"
________________________________________
Скрипт 4 — шаблоны: settings.html, departments.html, employees.html, reports.html, base.html
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"
New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null

