<!-- Часть 867 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Мой профиль](866_Moy_profil.md) | [Оглавление](00_BCE_INDEX.md) | [---- 6.1: user_new_form — передаём departments ---- ▶](868_6_1_user_new_form_peredaem_departments.md)

---

# ============================================================
@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    sess = current_admin(request)
    user = db.query(AdminUser).filter(AdminUser.id == sess["id"]).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_obj": user,
        "roles_info": ROLES_INFO,
        "saved": request.query_params.get("saved") == "1",
        "pw_changed": request.query_params.get("pw_changed") == "1",
        "pw_error": request.query_params.get("pw_error"),
    })


@router.post("/profile/save")
def profile_save(
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    language: str = Form("ru"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    sess = current_admin(request)
    user = db.query(AdminUser).filter(AdminUser.id == sess["id"]).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if language not in ("ru", "en"):
        language = "ru"

    user.full_name = full_name.strip() or None
    user.email = email.strip() or None
    user.language = language

    db.add(AuditLog(
        actor=user.username,
        entity="admin_user",
        entity_id=str(user.id),
        action="profile_update",
        new_value=json.dumps(
            {"full_name": user.full_name, "email": user.email, "language": language},
            ensure_ascii=False,
        ),
    ))
    db.commit()

    # Обновляем сессию, чтобы display_name сразу подтянул новое ФИО
    sess["full_name"] = user.full_name or ""
    sess["language"] = language
    request.session["admin_user"] = sess

    return RedirectResponse("/admin/profile?saved=1", status_code=303)


@router.post("/profile/change-password")
def profile_change_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    sess = current_admin(request)
    user = db.query(AdminUser).filter(AdminUser.id == sess["id"]).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    if not verify_password(old_password, user.password_hash):
        return RedirectResponse("/admin/profile?pw_error=wrong", status_code=303)
    if len(new_password) < 8:
        return RedirectResponse("/admin/profile?pw_error=short", status_code=303)
    if new_password != new_password_confirm:
        return RedirectResponse("/admin/profile?pw_error=mismatch", status_code=303)

    user.password_hash = hash_password(new_password)
    db.add(AuditLog(
        actor=user.username,
        entity="admin_user",
        entity_id=str(user.id),
        action="profile_change_password",
    ))
    db.commit()

    log.info("User %s changed own password", user.username)
    return RedirectResponse("/admin/profile?pw_changed=1", status_code=303)
'@
    if ($content.Contains($anchor)) {
        $content = $content.Replace($anchor, $addition)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: роуты /admin/profile + хелперы фильтрации добавлены" -ForegroundColor Green
    } else {
        Write-Host "НЕ НАЙДЕН anchor _active_admins_count" -ForegroundColor Red
    }
}
python -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('SYNTAX OK')"
________________________________________
Скрипт 3b — проверка сессии (где формируется admin_user)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Где формируется session['admin_user'] ===" -ForegroundColor Cyan
Select-String -Path "D:\tracker\server\web_admin.py" -Pattern 'session\["admin_user"\]\s*=' -Context 0,8
Пришли вывод — если в dict нет department_id, я дам мини-патч.
Также проверь, что Department импортирован:
powershell
Select-String -Path "D:\tracker\server\web_admin.py" -Pattern "Department" | Select-Object -First 3
________________________________________
Скрипт 4 — шаблон profile.html
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\profile.html"
$content = @'
{% extends "base.html" %}
{% block title %}{{ _("profile.title") }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-7">

    <h3 class="mb-1">{{ _("profile.title") }}</h3>
    <p class="text-muted small mb-4">{{ _("profile.hint") }}</p>

    {% if saved %}
    <div class="alert alert-success py-2">? {{ _("profile.saved") }}</div>
    {% endif %}
    {% if pw_changed %}
    <div class="alert alert-success py-2">? {{ _("profile.pw_changed") }}</div>
    {% endif %}
    {% if pw_error %}
    <div class="alert alert-danger py-2">
      {% if pw_error == 'wrong' %}{{ _("profile.pw_wrong") }}
      {% elif pw_error == 'short' %}{{ _("profile.pw_too_short") }}
      {% elif pw_error == 'mismatch' %}{{ _("profile.pw_mismatch") }}
      {% else %}Ошибка{% endif %}
    </div>
    {% endif %}

    {# ---------- Форма 1: личные данные ---------- #}
    <div class="card mb-3">
      <div class="card-header">{{ _("profile.save") }}</div>
      <div class="card-body">
        <form method="post" action="/admin/profile/save">

          <div class="mb-3">
            <label class="form-label">{{ _("profile.username") }}</label>
            <input class="form-control" value="{{ user_obj.username }}" readonly disabled>
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("profile.role") }}</label>
            <input class="form-control" readonly disabled
                   value="{% if current_lang == 'ru' %}{{ roles_info[user_obj.role].label_ru }}{% else %}{{ roles_info[user_obj.role].label_en }}{% endif %}">
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("profile.full_name") }}</label>
            <input class="form-control" name="full_name"
                   value="{{ user_obj.full_name or '' }}" maxlength="255">
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("profile.email") }}</label>
            <input class="form-control" type="email" name="email"
                   value="{{ user_obj.email or '' }}" maxlength="255">
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("profile.language") }}</label>
            <select name="language" class="form-select">
              <option value="ru" {% if user_obj.language == 'ru' %}selected{% endif %}>Русский</option>
              <option value="en" {% if user_obj.language == 'en' %}selected{% endif %}>English</option>
            </select>
          </div>

          <div class="d-flex gap-2">
            <button class="btn btn-primary">{{ _("profile.save") }}</button>
            <a class="btn btn-outline-secondary" href="/admin">{{ _("btn.cancel") }}</a>
          </div>
        </form>
      </div>
    </div>

    {# ---------- Форма 2: смена пароля ---------- #}
    <div class="card mb-3">
      <div class="card-header">{{ _("profile.change_pw") }}</div>
      <div class="card-body">
        <form method="post" action="/admin/profile/change-password">

          <div class="mb-3">
            <label class="form-label">{{ _("profile.old_pw") }}</label>
            <input class="form-control" type="password" name="old_password" required autocomplete="current-password">
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("profile.new_pw") }}</label>
            <input class="form-control" type="password" name="new_password" required minlength="8" autocomplete="new-password">
            <div class="form-text">{{ _("profile.pw_too_short") }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("profile.new_pw2") }}</label>
            <input class="form-control" type="password" name="new_password_confirm" required minlength="8" autocomplete="new-password">
          </div>

          <button class="btn btn-warning">{{ _("profile.change_pw") }}</button>
        </form>
      </div>
    </div>

    <div class="mt-3">
      <a class="btn btn-outline-info" href="/admin/logins">?? {{ _("profile.my_logins") }}</a>
    </div>

  </div>
</div>
{% endblock %}
'@
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: profile.html создан" -ForegroundColor Green
________________________________________
Скрипт 5 — переписать user_form.html (поле «Отдел» + чистые строки)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\user_form.html"
$content = @'
{% extends "base.html" %}
{% block title %}{{ _("user_form.edit_title") if is_edit else _("user_form.new_title") }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-7">
    <h3 class="mb-3">
      {% if is_edit %}
        ?? {{ _("user_form.edit_title") }}: <code>{{ user_obj.username }}</code>
      {% else %}
        ? {{ _("user_form.new_title") }}
      {% endif %}
    </h3>

    {% if error %}
    <div class="alert alert-danger py-2">{{ error }}</div>
    {% endif %}

    <div class="card">
      <div class="card-body">
        <form method="post"
              action="{% if is_edit %}/admin/users/{{ user_obj.id }}/edit{% else %}/admin/users/new{% endif %}">

          <div class="mb-3">
            <label class="form-label">{{ _("users.username") }}</label>
            {% if is_edit %}
            <input class="form-control" value="{{ user_obj.username }}" readonly disabled>
            <div class="form-text">{{ _("user_form.username_readonly") }}</div>
            {% else %}
            <input class="form-control" name="username" required
                   pattern="[a-zA-Z0-9._\-]+" minlength="3"
                   value="{{ form.username or '' }}"
                   placeholder="operator1">
            <div class="form-text">{{ _("setup.username_hint") }}</div>
            {% endif %}
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("users.full_name") }}</label>
            <input class="form-control" name="full_name"
                   value="{{ form.full_name or '' }}"
                   placeholder="Иванов Иван Иванович">
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("users.email") }}</label>
            <input class="form-control" type="email" name="email"
                   value="{{ form.email or '' }}">
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("users.role") }}</label>
            <select name="role" class="form-select" required id="roleSelect">
              {% for role_code in ['admin', 'operator', 'hr', 'manager', 'viewer'] %}
              <option value="{{ role_code }}"
                      {% if form.role == role_code %}selected{% endif %}>
                {% if current_lang == 'ru' %}
                  {{ roles_info[role_code].label_ru }} — {{ roles_info[role_code].description_ru }}
                {% else %}
                  {{ roles_info[role_code].label_en }} — {{ roles_info[role_code].description_en }}
                {% endif %}
              </option>
              {% endfor %}
            </select>
            <div class="form-text">{{ _("user_form.role_hint") }}</div>
          </div>

          <div class="mb-3" id="departmentBlock" style="display:none">
            <label class="form-label">
              Отдел <span class="hint" title="Для роли «Руководитель отдела» — какие сотрудники попадут в отчёты этого пользователя.">?</span>
            </label>
            <select name="department_id" class="form-select">
              <option value="">— без отдела —</option>
              {% for d in departments %}
              <option value="{{ d.id }}" {% if form.department_id == d.id %}selected{% endif %}>{{ d.name }}</option>
              {% endfor %}
            </select>
            <div class="form-text">Менеджер видит данные только своего отдела.</div>
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("users.language") }}</label>
            <select name="language" class="form-select">
              <option value="ru" {% if form.language == 'ru' %}selected{% endif %}>Русский</option>
              <option value="en" {% if form.language == 'en' %}selected{% endif %}>English</option>
            </select>
          </div>

          {% if not is_edit %}
          <hr>
          <div class="mb-3">
            <label class="form-label">{{ _("user_form.password") }}</label>
            <input class="form-control" type="password" name="password" required minlength="8">
            <div class="form-text">{{ _("user_form.password_hint") }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label">{{ _("user_form.password_confirm") }}</label>
            <input class="form-control" type="password" name="password_confirm" required minlength="8">
          </div>
          {% endif %}

          <div class="d-flex gap-2">
            <button class="btn btn-primary">{{ _("users.save") }}</button>
            <a class="btn btn-outline-secondary" href="/admin/users">{{ _("users.cancel") }}</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<script>
  function toggleDepartment() {
    var sel = document.getElementById('roleSelect');
    var block = document.getElementById('departmentBlock');
    if (!sel || !block) return;
    block.style.display = (sel.value === 'manager') ? '' : 'none';
  }
  document.getElementById('roleSelect')?.addEventListener('change', toggleDepartment);
  document.addEventListener('DOMContentLoaded', toggleDepartment);
</script>
{% endblock %}
'@
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: user_form.html переписан" -ForegroundColor Green
________________________________________
Скрипт 6 — патч роутов users (приём department_id)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

changes = []

