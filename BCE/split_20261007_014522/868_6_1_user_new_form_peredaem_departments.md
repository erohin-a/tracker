<!-- Часть 868 из 1409 -->
# ---- 6.1: user_new_form — передаём departments ----
*Хлебные крошки:* ---- 6.1: user_new_form — передаём departments ----

[◀ ============================================================](867_part.md) | [Оглавление](00_BCE_INDEX.md) | [---- 6.2: user_new_submit — принимает department_id ---- ▶](869_6_2_user_new_submit_prinimaet_department_id.md)

---

# ---- 6.1: user_new_form — передаём departments ----
old = '''    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": None,
        "form": {"role": "viewer", "language": "ru"},
        "is_edit": False,
        "error": None,
    })'''
new = '''    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": None,
        "form": {"role": "viewer", "language": "ru"},
        "is_edit": False,
        "error": None,
        "departments": departments,
    })'''
if old in content:
    content = content.replace(old, new, 1)
    changes.append("user_new_form передаёт departments")
else:
    changes.append("SKIP: user_new_form (уже пропатчен или не найден)")

