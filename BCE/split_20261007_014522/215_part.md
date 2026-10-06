<!-- Часть 215 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Аудит](214_Audit.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](216_part.md)

---

# ============================================================

@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    logs = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(200).all()
    return templates.TemplateResponse("audit.html", {
        "request": request, "logs": logs, "admin": request.session.get("admin"), "tz": tz,
    })
'@
[System.IO.File]::WriteAllText("$serverDir\web_admin.py", $web_admin_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  web_admin.py" -ForegroundColor Green

Write-Host "`n=== Скрипт 1 завершён ===" -ForegroundColor Cyan
После выполнения увидите:
text
OK  requirements.txt
OK  config.py
OK  web_admin.py

=== Скрипт 1 завершён ===
________________________________________
Скрипт 2 — HTML-шаблоны
Запустите вторым (тоже целиком):
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"
New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null

