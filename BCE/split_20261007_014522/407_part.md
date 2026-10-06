<!-- Часть 407 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Sessions — идемпотентный upsert](406_Sessions_idempotentnyy_upsert.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](408_part.md)

---

# ============================================================

@app.post("/api/v1/sessions")
def upsert_session(payload: SessionIn, comp: Computer = Depends(get_computer),
                   db: Session = Depends(get_db)):
    start = datetime.fromisoformat(payload.session_start.replace("Z", "+00:00"))
    end = (datetime.fromisoformat(payload.session_end.replace("Z", "+00:00"))
           if payload.session_end else None)

    if end is not None and end < start:
        raise HTTPException(422, "session_end < session_start")

    ws = (db.query(WorkSession)
          .filter(WorkSession.session_uid == payload.session_uid).first())

    if ws is None:
        # Новая сессия — создаём
        ws = WorkSession(
            session_uid=payload.session_uid,
            computer_id=comp.id,
            employee_id=comp.employee_id,
            session_start=start,
            session_end=end,
            abnormal_termination=payload.abnormal_termination,
            client_version=payload.client_version,
        )
        db.add(ws)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            # Кто-то успел создать раньше (race) — считаем ok
            return {"status": "ok", "note": "race"}
    else:
        # Сессия уже есть в БД
        if ws.computer_id != comp.id:
            # Сессия принадлежит другому компьютеру (например, после перерегистрации).
            # Не воюем — считаем «принято», чтобы клиент не ретраил бесконечно.
            log.info("Session %s belongs to another computer (have=%s, got=%s) — accept-as-is",
                     payload.session_uid, ws.computer_id, comp.id)
            comp.last_seen_at = _now()
            db.commit()
            return {"status": "ok", "note": "belongs_to_another_computer"}

        # Тот же ПК — обновляем конец/аварийность
        if end:
            ws.session_end = end
        if payload.abnormal_termination:
            ws.abnormal_termination = True

    if payload.abnormal_termination:
        db.add(AuditLog(actor=f"computer:{comp.computer_uid}",
                        entity="work_session", entity_id=payload.session_uid,
                        action="abnormal_termination"))

    comp.last_seen_at = _now()
    db.commit()
    return {"status": "ok"}


