<!-- Часть 165 из 1409 -->
# --- Подключаем веб-админку /admin/* ---
*Хлебные крошки:* --- Подключаем веб-админку /admin/* ---

[◀ --- Сессионный middleware для веб-интерфейса администратора ---](164_Sessionnyy_middleware_dlya_veb_interfeysa_administratora.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Admin API ---------- ▶](166_Admin_API.md)

---

# --- Подключаем веб-админку /admin/* ---
app.include_router(admin_web_router)


def _now():
    return datetime.now(timezone.utc)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_computer(x_computer_uid: str = Header(...),
                 db: Session = Depends(get_db)) -> Computer:
    comp = (db.query(Computer)
            .filter(Computer.computer_uid == x_computer_uid).first())
    if not comp or not comp.is_active:
        raise HTTPException(401, "Unknown or inactive computer")
    return comp


def decrypt_secret(comp: Computer) -> str:
    return FERNET.decrypt(comp.client_secret_enc.encode()).decode()


def require_admin(x_admin_token: Optional[str] = Header(None)):
    if x_admin_token is None:
        raise HTTPException(401, "admin token required",
                            headers={"WWW-Authenticate": "ApiKey"})
    if not secrets.compare_digest(x_admin_token, settings.admin_api_key):
        raise HTTPException(403, "admin required")


def _hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


@app.on_event("startup")
def on_startup():
    init_db()


