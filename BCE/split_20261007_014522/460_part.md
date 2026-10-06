<!-- Часть 460 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Heartbeat — клиент раз в 3 минуты говорит "я жив"](459_Heartbeat_klient_raz_v_3_minuty_govorit_ya_zhiv.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](461_part.md)

---

# ============================================================

@app.post("/api/v1/heartbeat")
def heartbeat(comp: Computer = Depends(get_computer),
              db: Session = Depends(get_db)):
    comp.last_seen_at = _now()
    db.commit()
    return {"status": "ok", "server_time": _now().isoformat()}


