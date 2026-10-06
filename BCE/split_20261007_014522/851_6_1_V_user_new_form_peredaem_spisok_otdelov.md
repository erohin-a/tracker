<!-- Часть 851 из 1409 -->
# --- 6.1. В user_new_form передаём список отделов ---
*Хлебные крошки:* --- 6.1. В user_new_form передаём список отделов ---

[◀ Найдём место где формируется session["admin_user"]](850_Naydem_mesto_gde_formiruetsya_session_admin_user.md) | [Оглавление](00_BCE_INDEX.md) | [--- 6.2. Приём department_id в POST /users/new --- ▶](852_6_2_Priem_department_id_v_POST_users_new.md)

---

# --- 6.1. В user_new_form передаём список отделов ---
$old = @'
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": None,
        "form": {"role": "viewer", "language": "ru"},
        "is_edit": False,
        "error": None,
    })
'@
$new = @'
    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": None,
        "form": {"role": "viewer", "language": "ru"},
        "is_edit": False,
        "error": None,
        "departments": departments,
    })
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_new_form передаёт departments" -ForegroundColor Green
}

