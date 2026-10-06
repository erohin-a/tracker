<!-- Часть 168 из 1409 -->
# ---------- Sessions ----------
*Хлебные крошки:* ---------- Sessions ----------

[◀ ---------- Register ----------](167_Register.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Records ---------- ▶](169_Records.md)

---

# ---------- Sessions ----------

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
        ws = WorkSession(
            session_uid=payload.session_uid,
            computer_id=comp.id,
            employee_id=comp.employee_id,           # ? наследуем от ПК
            session_start=start,
            session_end=end,
            abnormal_termination=payload.abnormal_termination,
            client_version=payload.client_version,
        )
        db.add(ws)
    else:
        if ws.computer_id != comp.id:
            raise HTTPException(409, "session_uid belongs to another computer")
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


