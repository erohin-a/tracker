<!-- Часть 854 из 1409 -->
# --- 6.4. user_edit_form передаёт departments + department_id в form ---
*Хлебные крошки:* --- 6.4. user_edit_form передаёт departments + department_id в form ---

[◀ --- 6.3. Сохраняем department_id при создании + передаём departments при ошибке ---](853_6_3_Sohranyaem_department_id_pri_sozdanii_peredaem_departments_pri_oshibke.md) | [Оглавление](00_BCE_INDEX.md) | [--- 6.5. Приём department_id в POST /users/{id}/edit --- ▶](855_6_5_Priem_department_id_v_POST_users_id_edit.md)

---

# --- 6.4. user_edit_form передаёт departments + department_id в form ---
$old = @'
@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
def user_edit_form(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    _require_admin_role(request)
    user_obj = db.query(AdminUser).get(user_id)
    if not user_obj:
        raise HTTPException(404, "Пользователь не найден")
    return templates.TemplateResponse("user_form.html", {
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
    })
'@
$new = @'
@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
def user_edit_form(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    _require_admin_role(request)
    user_obj = db.query(AdminUser).get(user_id)
    if not user_obj:
        raise HTTPException(404, "Пользователь не найден")
    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
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
    })
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_edit_form передаёт departments" -ForegroundColor Green
}

