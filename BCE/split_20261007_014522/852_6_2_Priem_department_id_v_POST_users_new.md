<!-- Часть 852 из 1409 -->
# --- 6.2. Приём department_id в POST /users/new ---
*Хлебные крошки:* --- 6.2. Приём department_id в POST /users/new ---

[◀ --- 6.1. В user_new_form передаём список отделов ---](851_6_1_V_user_new_form_peredaem_spisok_otdelov.md) | [Оглавление](00_BCE_INDEX.md) | [--- 6.3. Сохраняем department_id при создании + передаём departments при ошибке --- ▶](853_6_3_Sohranyaem_department_id_pri_sozdanii_peredaem_departments_pri_oshibke.md)

---

# --- 6.2. Приём department_id в POST /users/new ---
$old = @'
@router.post("/users/new", response_class=HTMLResponse)
def user_new_submit(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
'@
$new = @'
@router.post("/users/new", response_class=HTMLResponse)
def user_new_submit(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(""),
    email: str = Form(""),
    role: str = Form("viewer"),
    language: str = Form("ru"),
    department_id: str = Form(""),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_new_submit принимает department_id" -ForegroundColor Green
}

