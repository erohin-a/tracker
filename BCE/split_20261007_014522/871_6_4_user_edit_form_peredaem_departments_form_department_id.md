<!-- Часть 871 из 1409 -->
# ---- 6.4: user_edit_form — передаём departments + form.department_id ----
*Хлебные крошки:* ---- 6.4: user_edit_form — передаём departments + form.department_id ----

[◀ ---- 6.3: user_new_submit — обработка ошибки + сохранение ----](870_6_3_user_new_submit_obrabotka_oshibki_sohranenie.md) | [Оглавление](00_BCE_INDEX.md) | [---- 6.5: user_edit_submit — принимает department_id ---- ▶](872_6_5_user_edit_submit_prinimaet_department_id.md)

---

# ---- 6.4: user_edit_form — передаём departments + form.department_id ----
old = '''    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": user_obj,
        "form": {
            "username": user_obj.username,
            "full_name": user_obj.full_name or "",
            "email": user_obj.email or "",
            "role": user_obj.role,
            "language": user_obj.language,
        },
        "is_edit": True,
        "error": None,
    })'''
new = '''    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": user_obj,
        "form": {
            "username": user_obj.username,
            "full_name": user_obj.full_name or "",
            "email": user_obj.email or "",
            "role": user_obj.role,
            "language": user_obj.language,
            "department_id": user_obj.department_id,
        },
        "is_edit": True,
        "error": None,
        "departments": departments,
    })'''
if old in content:
    content = content.replace(old, new, 1)
    changes.append("user_edit_form передаёт departments")
else:
    changes.append("SKIP: user_edit_form")

