<!-- Часть 856 из 1409 -->
# --- 6.6. Сохраняем department_id при редактировании ---
*Хлебные крошки:* --- 6.6. Сохраняем department_id при редактировании ---

[◀ --- 6.5. Приём department_id в POST /users/{id}/edit ---](855_6_5_Priem_department_id_v_POST_users_id_edit.md) | [Оглавление](00_BCE_INDEX.md) | [Смотрим, где формируется сессия ▶](857_Smotrim_gde_formiruetsya_sessiya.md)

---

# --- 6.6. Сохраняем department_id при редактировании ---
$old = @'
    old_role = user_obj.role
    user_obj.full_name = full_name.strip() or None
    user_obj.email = email.strip() or None
    user_obj.role = role
    user_obj.language = language
'@
$new = @'
    old_role = user_obj.role
    dep_id = int(department_id) if department_id and department_id.isdigit() else None
    user_obj.full_name = full_name.strip() or None
    user_obj.email = email.strip() or None
    user_obj.role = role
    user_obj.language = language
    user_obj.department_id = dep_id if role == "manager" else None
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_edit_submit сохраняет department_id" -ForegroundColor Green
}

[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
python -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('SYNTAX OK')"
Проверка Department импортирована в web_admin.py:
powershell
Select-String -Path "D:\tracker\server\web_admin.py" -Pattern "Department" | Select-Object -First 5
Если её нет в импортах — добавлю отдельным мини-скриптом.
________________________________________
Скрипт 7 — добавить department_id в сессию при логине
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

