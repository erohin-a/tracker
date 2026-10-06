<!-- Часть 870 из 1409 -->
# ---- 6.3: user_new_submit — обработка ошибки + сохранение ----
*Хлебные крошки:* ---- 6.3: user_new_submit — обработка ошибки + сохранение ----

[◀ ---- 6.2: user_new_submit — принимает department_id ----](869_6_2_user_new_submit_prinimaet_department_id.md) | [Оглавление](00_BCE_INDEX.md) | [---- 6.4: user_edit_form — передаём departments + form.department_id ---- ▶](871_6_4_user_edit_form_peredaem_departments_form_department_id.md)

---

# ---- 6.3: user_new_submit — обработка ошибки + сохранение ----
old = '''    if error:
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
    )'''
new = '''    dep_id = int(department_id) if department_id and department_id.isdigit() else None

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
    )'''
if old in content:
    content = content.replace(old, new, 1)
    changes.append("user_new_submit сохраняет department_id")
else:
    changes.append("SKIP: user_new_submit body")

