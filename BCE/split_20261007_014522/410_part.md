<!-- Часть 410 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Records — идемпотентный ingest](409_Records_idempotentnyy_ingest.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](411_part.md)

---

# ============================================================

@app.post("/api/v1/records/batch", response_model=RecordBatchResponse)
def ingest_records(payload: RecordBatch, request: Request,
                   comp: Computer = Depends(get_computer),
                   db: Session = Depends(get_db)):
    secret = decrypt_secret(comp)

    # Какие из присланных session_uid известны (для этого ПК)
    session_uids = {r.session_uid for r in payload.records}
    known_sessions = {
        uid for (uid,) in db.query(WorkSession.session_uid)
        .filter(WorkSession.session_uid.in_(session_uids),
                WorkSession.computer_id == comp.id).all()
    }
    # Но также считаем «известными» сессии, привязанные к другому ПК —
    # их тоже примем (иначе клиент зациклится после перерегистрации).
    other_sessions = {
        uid for (uid,) in db.query(WorkSession.session_uid)
        .filter(WorkSession.session_uid.in_(session_uids)).all()
    }
    known_sessions |= other_sessions

    # --- Проверка подписи батча ---
    if payload.batch_signature is not None:
        batch_signable = {"records": [
            {"record_uid": r.record_uid, "session_uid": r.session_uid,
             "kind": r.kind, "data": r.data, "client_ts": r.client_ts,
             "signature": r.signature}
            for r in payload.records
        ]}
        if not verify_signature(secret, batch_signable, payload.batch_signature):
            raise HTTPException(400, "batch signature invalid")

    accepted: list[str] = []
    rejected: list[str] = []
    reasons: dict[str, str] = {}

    incoming_uids = [r.record_uid for r in payload.records]

    # --- Ищем дубликаты по ВСЕЙ таблице, а не только по этому ПК ---
    existing_uids = {
        uid for (uid,) in db.query(Record.record_uid)
        .filter(Record.record_uid.in_(incoming_uids)).all()
    }

    for rec in payload.records:
        signable = {
            "record_uid": rec.record_uid,
            "session_uid": rec.session_uid,
            "kind": rec.kind,
            "data": rec.data,
            "client_ts": rec.client_ts,
        }
        if not verify_signature(secret, signable, rec.signature):
            rejected.append(rec.record_uid)
            reasons[rec.record_uid] = "bad_signature"
            continue

        # Уже есть в БД (для любого ПК) — идемпотентно принимаем
        if rec.record_uid in existing_uids:
            accepted.append(rec.record_uid)
            continue

        if rec.session_uid not in known_sessions:
            rejected.append(rec.record_uid)
            reasons[rec.record_uid] = "unknown_session"
            continue

        try:
            db.add(Record(
                record_uid=rec.record_uid,
                session_uid=rec.session_uid,
                computer_id=comp.id,
                kind=rec.kind,
                data=json.dumps(rec.data, ensure_ascii=False),
                client_ts=rec.client_ts_dt,
                client_ip=request.client.host,
                signature=rec.signature,
            ))
            db.flush()
            accepted.append(rec.record_uid)
        except IntegrityError:
            # Кто-то успел вставить параллельно — считаем принято
            db.rollback()
            accepted.append(rec.record_uid)
            continue

    comp.last_seen_at = _now()

    if rejected:
        db.add(AuditLog(
            actor=f"computer:{comp.computer_uid}",
            entity="record", entity_id=",".join(rejected[:20]),
            action="reject_signature",
            new_value=json.dumps({"count": len(rejected), "reasons": reasons},
                                 ensure_ascii=False),
        ))

    db.commit()

    response_payload = {
        "accepted_uuids": accepted,
        "rejected_uuids": rejected,
        "reasons": reasons,
    }
    server_signature = compute_signature(secret, response_payload)

    return RecordBatchResponse(
        accepted_uuids=accepted, rejected_uuids=rejected, reasons=reasons,
        server_signature=server_signature,
    )


