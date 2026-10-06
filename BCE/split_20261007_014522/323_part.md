<!-- Часть 323 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Аудит](322_Audit.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](324_part.md)

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

Write-Host "`n--- Проверка синтаксиса ---" -ForegroundColor Cyan
python -c "import ast; ast.parse(open(r'$serverDir\models.py', encoding='utf-8').read()); ast.parse(open(r'$serverDir\web_admin.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — шаблоны (base, settings, reports, report_result)
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

