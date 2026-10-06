<!-- Часть 725 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Переключение языка интерфейса](724_Pereklyuchenie_yazyka_interfeysa.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](726_part.md)

---

# ============================================================
@router.get("/set-lang/{code}")
def set_lang(code: str, request: Request):
    """
    Устанавливает язык админки через cookie.
    После переключения возвращает пользователя на ту же страницу.
    """
    from fastapi.responses import RedirectResponse as _RR
    if not is_valid_lang(code):
        code = DEFAULT_LANG
    next_url = request.query_params.get("next") or "/admin"
    if not next_url.startswith("/"):
        next_url = "/admin"
    resp = _RR(next_url, status_code=303)
    resp.set_cookie(
        "tracker_lang", code,
        max_age=365 * 24 * 3600,
        path="/",
        samesite="lax",
    )
    return resp


