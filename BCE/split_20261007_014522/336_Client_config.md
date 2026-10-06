<!-- Часть 336 из 1409 -->
# ---------- Client config ----------
*Хлебные крошки:* ---------- Client config ----------

[◀ ============================================================](335_part.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Version ---------- ▶](337_Version.md)

---

# ---------- Client config ----------

@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    """Клиент подтягивает эту конфигурацию раз в 5 минут."""
    from .models import AppSetting as _AppSetting
    row = db.query(_AppSetting).filter(_AppSetting.key == "idle_close_minutes").first()
    try:
        idle = max(5, min(480, int(row.value))) if row else 30
    except (ValueError, TypeError):
        idle = 30
    return {"idle_close_minutes": idle}


