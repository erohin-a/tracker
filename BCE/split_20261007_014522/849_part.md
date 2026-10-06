<!-- Часть 849 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Мой профиль](848_Moy_profil.md) | [Оглавление](00_BCE_INDEX.md) | [Найдём место где формируется session["admin_user"] ▶](850_Naydem_mesto_gde_formiruetsya_session_admin_user.md)

---

# ============================================================
@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    sess = current_admin(request)
    user = db.query(AdminUser).filter(AdminUser.id == sess["id"]).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_obj": user,
        "roles_info": ROLES_INFO,
        "saved": request.query_params.get("saved") == "1",
        "pw_changed": request.query_params.get("pw_changed") == "1",
        "pw_error": request.query_params.get("pw_error"),
    })


@router.post("/profile/save")
def profile_save(
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    language: str = Form("ru"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    sess = current_admin(request)
    user = db.query(AdminUser).filter(AdminUser.id == sess["id"]).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if language not in ("ru", "en"):
        language = "ru"

    user.full_name = full_name.strip() or None
    user.email = email.strip() or None
    user.language = language

    db.add(AuditLog(
        actor=user.username,
        entity="admin_user",
        entity_id=str(user.id),
        action="profile_update",
        new_value=json.dumps({"full_name": user.full_name, "email": user.email, "language": language}, ensure_ascii=False),
    ))
    db.commit()

    # Обновим сессию (display_name = full_name or username)
    sess["full_name"] = user.full_name or ""
    sess["language"] = language
    request.session["admin_user"] = sess

    return RedirectResponse("/admin/profile?saved=1", status_code=303)


@router.post("/profile/change-password")
def profile_change_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    sess = current_admin(request)
    user = db.query(AdminUser).filter(AdminUser.id == sess["id"]).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    if not verify_password(old_password, user.password_hash):
        return RedirectResponse("/admin/profile?pw_error=wrong", status_code=303)
    if len(new_password) < 8:
        return RedirectResponse("/admin/profile?pw_error=short", status_code=303)
    if new_password != new_password_confirm:
        return RedirectResponse("/admin/profile?pw_error=mismatch", status_code=303)

    user.password_hash = hash_password(new_password)
    db.add(AuditLog(
        actor=user.username,
        entity="admin_user",
        entity_id=str(user.id),
        action="profile_change_password",
    ))
    db.commit()

    log.info("User %s changed own password", user.username)
    return RedirectResponse("/admin/profile?pw_changed=1", status_code=303)
'@
    if ($content.Contains($anchor)) {
        $content = $content.Replace($anchor, $addition)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: роуты /admin/profile добавлены" -ForegroundColor Green
    } else {
        Write-Host "НЕ НАЙДЕН anchor _active_admins_count — правь вручную" -ForegroundColor Red
    }
}
python -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('SYNTAX OK')"
Оговорка: функция apply_manager_filter написана с заделом на будущее. Пока что она не подключена нигде. В следующих сообщениях (когда будем править отчёты и списки) — используем её. Ключевое сейчас — manager_department_id(user) для получения department_id в шаблонах.
Также надо добавить в сессию department_id — при логине. Проверим/поправим это в скрипте 3b:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

