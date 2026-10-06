<!-- Часть 855 из 1409 -->
# --- 6.5. Приём department_id в POST /users/{id}/edit ---
*Хлебные крошки:* --- 6.5. Приём department_id в POST /users/{id}/edit ---

[◀ --- 6.4. user_edit_form передаёт departments + department_id в form ---](854_6_4_user_edit_form_peredaet_departments_department_id_v_form.md) | [Оглавление](00_BCE_INDEX.md) | [--- 6.6. Сохраняем department_id при редактировании --- ▶](856_6_6_Sohranyaem_department_id_pri_redaktirovanii.md)

---

# --- 6.5. Приём department_id в POST /users/{id}/edit ---
$old = @'
@router.post("/users/{user_id}/edit", response_class=HTMLResponse)
def user_edit_submit(
    user_id: int,
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
'@
$new = @'
@router.post("/users/{user_id}/edit", response_class=HTMLResponse)
def user_edit_submit(
    user_id: int,
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    department_id: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_edit_submit принимает department_id" -ForegroundColor Green
}

