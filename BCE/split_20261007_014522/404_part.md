<!-- Часть 404 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Register](403_Register.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](405_part.md)

---

# ============================================================

@app.post("/api/v1/computers/register", response_model=RegisterResponse)
def register_computer(payload: RegisterRequest, request: Request,
                      db: Session = Depends(get_db)):
    now = _now()
    stmt = (
        update(BootstrapToken)
        .where(BootstrapToken.token_hash == _hash_token(payload.bootstrap_token),
               BootstrapToken.used_at.is_(None),
               BootstrapToken.expires_at > now)
        .values(used_at=now, used_by_uid=payload.computer_uid)
        .returning(BootstrapToken.id, BootstrapToken.issued_by)
    )
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(401, "Invalid or expired bootstrap token")

    _, issued_by = row

    existing = (db.query(Computer)
                .filter(Computer.computer_uid == payload.computer_uid).first())
    if existing and existing.is_active:
        raise HTTPException(409, "computer_uid already registered; ask admin to revoke")

    client_secret = secrets.token_urlsafe(48)
    secret_enc = FERNET.encrypt(client_secret.encode()).decode()

    try:
        if existing:
            existing.client_secret_enc = secret_enc
            existing.secret_version = (existing.secret_version or 1) + 1
            existing.hostname = payload.hostname
            existing.os_info = payload.os_info
            existing.client_version = payload.client_version
            existing.is_active = True
            comp = existing
        else:
            comp = Computer(
                computer_uid=payload.computer_uid,
                hostname=payload.hostname,
                os_info=payload.os_info,
                client_version=payload.client_version,
                client_secret_enc=secret_enc,
                secret_version=1,
            )
            db.add(comp)
            db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "computer_uid already registered (race)")

    db.add(AuditLog(
        actor=issued_by or "system",
        entity="computer", entity_id=str(comp.id), action="register",
        new_value=json.dumps(
            {"uid": payload.computer_uid, "hostname": payload.hostname,
             "secret_version": comp.secret_version},
            ensure_ascii=False),
    ))
    db.commit()
    log.info("Registered uid=%s ip=%s", payload.computer_uid, request.client.host)

    return RegisterResponse(computer_uid=payload.computer_uid,
                            client_secret=client_secret,
                            secret_version=comp.secret_version)


