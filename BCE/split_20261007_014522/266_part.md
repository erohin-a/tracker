<!-- Часть 266 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Аудит](265_Audit.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](267_Proverka_sintaksisa.md)

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

