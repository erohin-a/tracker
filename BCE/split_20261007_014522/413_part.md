<!-- Часть 413 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Client config (то, что клиент подтягивает раз в 5 минут)](412_Client_config_to_chto_klient_podtyagivaet_raz_v_5_minut.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](414_part.md)

---

# ============================================================

@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    def getv(key, default, mn, mx):
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        try:
            return max(mn, min(mx, int(row.value))) if row else default
        except (ValueError, TypeError):
            return default

    return {
        "idle_close_minutes": getv("idle_close_minutes", 30, 5, 480),
        "sync_interval": getv("sync_interval", 30, 5, 3600),
        "batch_size": getv("batch_size", 200, 10, 1000),
        "active_window_interval": getv("active_window_interval", 5, 1, 60),
        "idle_threshold": getv("idle_threshold", 60, 10, 3600),
    }


