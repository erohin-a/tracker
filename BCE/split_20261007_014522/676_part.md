<!-- Часть 676 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Переключение языка интерфейса](675_Pereklyuchenie_yazyka_interfeysa.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](677_part.md)

---

# ============================================================
@router.get("/set-lang/{code}")
def set_lang(code: str, request: Request):
    """
    Устанавливает язык админки через cookie.
    После переключения возвращает пользователя на ту же страницу,
    с которой пришёл (параметр next в query string).
    """
    from fastapi.responses import RedirectResponse as _RR
    if not is_valid_lang(code):
        code = DEFAULT_LANG
    next_url = request.query_params.get("next") or "/admin"
    # Не разрешаем редирект на внешние URL — только на наши
    if not next_url.startswith("/"):
        next_url = "/admin"
    resp = _RR(next_url, status_code=303)
    # Cookie на 1 год, доступна для всех страниц админки
    resp.set_cookie(
        "tracker_lang", code,
        max_age=365 * 24 * 3600,
        path="/",
        samesite="lax",
    )
    return resp


