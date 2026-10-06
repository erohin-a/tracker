<!-- Часть 164 из 1409 -->
# --- Сессионный middleware для веб-интерфейса администратора ---
*Хлебные крошки:* --- Сессионный middleware для веб-интерфейса администратора ---

[◀ Логи api](163_Logi_api.md) | [Оглавление](00_BCE_INDEX.md) | [--- Подключаем веб-админку /admin/* --- ▶](165_Podklyuchaem_veb_adminku_admin.md)

---

# --- Сессионный middleware для веб-интерфейса администратора ---
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret or settings.jwt_secret,
    session_cookie="tracker_admin",
    max_age=8 * 3600,
    same_site="lax",
    https_only=settings.web_secure_cookie,
)

