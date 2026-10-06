<!-- Часть 374 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Bootstrap-токены](373_Bootstrap_tokeny.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](375_part.md)

---

# ============================================================

@router.get("/tokens", response_class=HTMLResponse)
def tokens_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    tokens = db.query(BootstrapToken).order_by(desc(BootstrapToken.id)).limit(50).all()
    return templates.TemplateResponse("tokens.html", {
        "request": request, "tokens": tokens,
        "admin": request.session.get("admin"),
        "new_token": request.query_params.get("new_token"), "tz": tz,
    })


@router.post("/tokens/issue")
def tokens_issue(ttl_hours: int = Form(24), issued_by: str = Form("admin"),
                 db: Session = Depends(get_db), _=Depends(current_admin)):
    ttl_hours = max(1, min(ttl_hours, 24 * 30))
    raw = secrets.token_urlsafe(32)
    db.add(BootstrapToken(token_hash=_hash_token(raw), issued_by=issued_by,
                          expires_at=_now() + timedelta(hours=ttl_hours)))
    db.add(AuditLog(actor="admin", entity="bootstrap_token", action="issue",
                    new_value=json.dumps({"ttl_hours": ttl_hours, "issued_by": issued_by})))
    db.commit()
    return RedirectResponse(f"/admin/tokens?new_token={raw}", status_code=303)


