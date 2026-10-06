<!-- Часть 153 из 1409 -->
# ---------- Утилиты ----------
*Хлебные крошки:* ---------- Утилиты ----------

[◀ в __init__ после layout.addWidget(self.status):](152_v_init_posle_layout_addWidgetself_status.md) | [Оглавление](00_BCE_INDEX.md) | [Регистрируем фильтры Jinja ▶](154_Registriruem_filtry_Jinja.md)

---

# ---------- Утилиты ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_admin(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=401, detail="not authenticated")
    return request.session["admin"]


def _now():
    return datetime.now(timezone.utc)


def _hash_token(t: str) -> str:
    import hashlib
    return hashlib.sha256(t.encode()).hexdigest()


def _fmt_dt(dt):
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")


def _fmt_dur(seconds: int) -> str:
    if not seconds:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


