<!-- Часть 872 из 1409 -->
# ---- 6.5: user_edit_submit — принимает department_id ----
*Хлебные крошки:* ---- 6.5: user_edit_submit — принимает department_id ----

[◀ ---- 6.4: user_edit_form — передаём departments + form.department_id ----](871_6_4_user_edit_form_peredaem_departments_form_department_id.md) | [Оглавление](00_BCE_INDEX.md) | [---- 6.6: user_edit_submit — сохраняем department_id ---- ▶](873_6_6_user_edit_submit_sohranyaem_department_id.md)

---

# ---- 6.5: user_edit_submit — принимает department_id ----
old = '''def user_edit_submit(
    user_id: int,
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    db: Session = Depends(get_db),'''
new = '''def user_edit_submit(
    user_id: int,
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    department_id: str = Form(""),
    db: Session = Depends(get_db),'''
if old in content:
    content = content.replace(old, new, 1)
    changes.append("user_edit_submit принимает department_id")
else:
    changes.append("SKIP: user_edit_submit signature")

