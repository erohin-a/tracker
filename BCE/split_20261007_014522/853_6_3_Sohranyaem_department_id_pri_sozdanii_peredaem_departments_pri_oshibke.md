<!-- Часть 853 из 1409 -->
# --- 6.3. Сохраняем department_id при создании + передаём departments при ошибке ---
*Хлебные крошки:* --- 6.3. Сохраняем department_id при создании + передаём departments при ошибке ---

[◀ --- 6.2. Приём department_id в POST /users/new ---](852_6_2_Priem_department_id_v_POST_users_new.md) | [Оглавление](00_BCE_INDEX.md) | [--- 6.4. user_edit_form передаёт departments + department_id в form --- ▶](854_6_4_user_edit_form_peredaet_departments_department_id_v_form.md)

---

# --- 6.3. Сохраняем department_id при создании + передаём departments при ошибке ---
$old = @'
    if error:
        return templates.TemplateResponse("user_form.html", {
            "request": request,
            "user_obj": None,
            "form": {"username": username, "full_name": full_name, "email": email, "role": role, "language": language},
            "is_edit": False,
            "error": error,
        }, status_code=400)

    new_user = AdminUser(
        username=username,
        password_hash=hash_password(password),
        full_name=full_name or None,
        email=email or None,
        role=role,
        is_active=True,
        language=language,
    )
'@
$new = @'
    dep_id = int(department_id) if department_id and department_id.isdigit() else None

    if error:
        departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
        return templates.TemplateResponse("user_form.html", {
            "request": request,
            "user_obj": None,
            "form": {"username": username, "full_name": full_name, "email": email, "role": role, "language": language, "department_id": dep_id},
            "is_edit": False,
            "error": error,
            "departments": departments,
        }, status_code=400)

    new_user = AdminUser(
        username=username,
        password_hash=hash_password(password),
        full_name=full_name or None,
        email=email or None,
        role=role,
        is_active=True,
        language=language,
        department_id=dep_id if role == "manager" else None,
    )
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_new_submit сохраняет department_id" -ForegroundColor Green
}

