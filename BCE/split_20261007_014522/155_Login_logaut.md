<!-- Часть 155 из 1409 -->
# ---------- Логин / логаут ----------
*Хлебные крошки:* ---------- Логин / логаут ----------

[◀ Регистрируем фильтры Jinja](154_Registriruem_filtry_Jinja.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Дашборд ---------- ▶](156_Dashbord.md)

---

# ---------- Логин / логаут ----------

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("admin"):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    ok_user = secrets.compare_digest(username, settings.admin_login)
    ok_pass = secrets.compare_digest(password, settings.admin_api_key)
    if ok_user and ok_pass:
        request.session["admin"] = username
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Неверный логин или ключ"},
        status_code=401,
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


