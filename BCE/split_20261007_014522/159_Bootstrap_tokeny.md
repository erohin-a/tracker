<!-- Часть 159 из 1409 -->
# ---------- Bootstrap-токены ----------
*Хлебные крошки:* ---------- Bootstrap-токены ----------

[◀ ---------- Компьютеры ----------](158_Kompyutery.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Отчёты ---------- ▶](160_Otchety.md)

---

# ---------- Bootstrap-токены ----------

@router.get("/tokens", response_class=HTMLResponse)
def tokens_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tokens = db.query(BootstrapToken).order_by(desc(BootstrapToken.id)).limit(50).all()
    return templates.TemplateResponse("tokens.html", {
        "request": request, "tokens": tokens,
        "admin": request.session.get("admin"),
        "new_token": request.query_params.get("new_token"),
    })


@router.post("/tokens/issue")
def tokens_issue(
    ttl_hours: int = Form(24),
    issued_by: str = Form("admin"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    ttl_hours = max(1, min(ttl_hours, 24 * 30))
    raw = secrets.token_urlsafe(32)
    db.add(BootstrapToken(
        token_hash=_hash_token(raw),
        issued_by=issued_by,
        expires_at=_now() + timedelta(hours=ttl_hours),
    ))
    db.add(AuditLog(actor="admin", entity="bootstrap_token", action="issue",
                    new_value=json.dumps({"ttl_hours": ttl_hours, "issued_by": issued_by})))
    db.commit()
    # показываем токен один раз через query param
    return RedirectResponse(f"/admin/tokens?new_token={raw}", status_code=303)


