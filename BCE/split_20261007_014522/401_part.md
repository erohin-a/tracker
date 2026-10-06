<!-- Часть 401 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Admin API](400_Admin_API.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](402_part.md)

---

# ============================================================

@app.post("/api/v1/admin/bootstrap-tokens",
          dependencies=[Depends(require_admin)])
def issue_bootstrap_token(ttl_hours: int = 24, issued_by: str = "admin",
                          db: Session = Depends(get_db)):
    ttl_hours = max(1, min(ttl_hours, 24 * 30))
    raw = secrets.token_urlsafe(32)
    db.add(BootstrapToken(
        token_hash=_hash_token(raw),
        issued_by=issued_by,
        expires_at=_now() + timedelta(hours=ttl_hours),
    ))
    db.commit()
    return {"token": raw, "expires_in_hours": ttl_hours}


@app.post("/api/v1/admin/computers/{computer_uid}/revoke",
          dependencies=[Depends(require_admin)])
def revoke_computer(computer_uid: str, db: Session = Depends(get_db)):
    comp = (db.query(Computer)
            .filter(Computer.computer_uid == computer_uid).first())
    if not comp:
        raise HTTPException(404, "not found")
    comp.is_active = False
    db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp.id),
                    action="revoke",
                    old_value=json.dumps({"uid": computer_uid}, ensure_ascii=False)))
    db.commit()
    return {"status": "revoked"}


