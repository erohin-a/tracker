<!-- Часть 869 из 1409 -->
# ---- 6.2: user_new_submit — принимает department_id ----
*Хлебные крошки:* ---- 6.2: user_new_submit — принимает department_id ----

[◀ ---- 6.1: user_new_form — передаём departments ----](868_6_1_user_new_form_peredaem_departments.md) | [Оглавление](00_BCE_INDEX.md) | [---- 6.3: user_new_submit — обработка ошибки + сохранение ---- ▶](870_6_3_user_new_submit_obrabotka_oshibki_sohranenie.md)

---

# ---- 6.2: user_new_submit — принимает department_id ----
old = '''def user_new_submit(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    password: str = Form(...),
    password_confirm: str = Form(...),'''
new = '''def user_new_submit(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    department_id: str = Form(""),
    password: str = Form(...),
    password_confirm: str = Form(...),'''
if old in content:
    content = content.replace(old, new, 1)
    changes.append("user_new_submit принимает department_id")
else:
    changes.append("SKIP: user_new_submit signature")

