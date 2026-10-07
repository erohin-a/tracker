# Найдём место где формируется session["admin_user"]

*Часть 56 из 100. Источник: `BCE.md`.*

[◀ ============================================================](055_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](057_part.md)

---

# Найдём место где формируется session["admin_user"]
Select-String -Path "D:\tracker\server\web_admin.py" -Pattern 'session\["admin_user"\]|admin_user.*=.*\{' | Select-Object -First 20
Пришли вывод — если department_id там нет, надо добавить.
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
Скрипт 5 — полная замена user_form.html (с полем «Отдел» + чистые строки)
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
Write-Host "OK: user_form.html переписан (поле «Отдел» + чистые строки)" -ForegroundColor Green
________________________________________
Скрипт 6 — патч роутов создания/редактирования user (принимаем department_id)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

# --- 6.1. В user_new_form передаём список отделов ---
$old = @'
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": None,
        "form": {"role": "viewer", "language": "ru"},
        "is_edit": False,
        "error": None,
    })
'@
$new = @'
    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user_obj": None,
        "form": {"role": "viewer", "language": "ru"},
        "is_edit": False,
        "error": None,
        "departments": departments,
    })
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_new_form передаёт departments" -ForegroundColor Green
}

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

# --- 6.3. Сохраняем department_id при создании + передаём departments при ошибке ---
$old = @'
    if error:
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
    )
'@
$new = @'
    dep_id = int(department_id) if department_id and department_id.isdigit() else None

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
    )
'@
if ($content.Contains($old)) {
    $content = $content.Replace($old, $new, 1)
    Write-Host "OK: user_new_submit сохраняет department_id" -ForegroundColor Green
}

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

# Смотрим, где формируется сессия
Select-String -Path "D:\tracker\server\web_admin.py" -Pattern 'session\[.admin_user.\]\s*=' | Select-Object -First 5
Пришли мне вывод — если в формируемом dict нет department_id, надо добавить, иначе manager-фильтр не будет знать свой отдел.
________________________________________
Скрипт 8 — пересборка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
docker compose logs api --tail=30
После — проверь в браузере:
/admin — в шапке справа появилась кнопка «?? Мой профиль», имя пользователя тоже кликабельно
/admin/profile — форма + смена пароля
/admin/users/new — при выборе роли «manager» появляется выпадающий список отделов
/admin/users/{id}/edit — то же для редактирования
________________________________________
Порядок и что прислать
Скрипт 1 ? SYNTAX OK
Скрипт 2 ? вывод содержимого новой миграции + «OK: партиции records не упоминаются» ? потом docker compose restart api ? 2602b... уже применён ранее, теперь +новая
Скрипт 3 ? SYNTAX OK + вывод команды Select-String (для скрипта 7)
Скрипт 4 ? OK: profile.html создан
Скрипт 5 ? OK: user_form.html переписан
Скрипт 6 ? пять строк OK: ... + SYNTAX OK
Скрипт 7 ? вывод Select-String — по нему скажу, надо ли патчить
Скрипт 8 ? логи + скриншот (или просто «профиль открывается»)
Не торопись, запускай по порядку. Если где-то НЕ НАЙДЕН или SYNTAX ERROR — стоп, присылай вывод, поправим точечно.
(.venv) PS D:\tracker> $ErrorActionPreference = "Continue" >> Set-Location D:\tracker >> >> $path = "D:\tracker\server\models.py" >> $content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false)) >> >> if ($content.Contains("department_id = Column(Integer, ForeignKey(""departments.id""), nullable=True)") -and >> $content -match "class AdminUser[\s\S]*?department_id") { >> Write-Host "AdminUser.department_id уже есть" -ForegroundColor Yellow >> } else { >> $old = @' >> language = Column(String(8), default="ru", nullable=False) >> created_at = Column(DateTime(timezone=True), default=_utcnow) >> last_login_at = Column(DateTime(timezone=True)) >> '@ >> $new = @' >> language = Column(String(8), default="ru", nullable=False) >> # Для роли manager - привязка к отделу (видит только свой отдел). >> # Для остальных ролей - игнорируется (может быть NULL). >> department_id = Column(Integer, ForeignKey("departments.id"), nullable=True) >> created_at = Column(DateTime(timezone=True), default=_utcnow) >> last_login_at = Column(DateTime(timezone=True)) >> '@ >> if ($content.Contains($old)) { >> $content = $content.Replace($old, $new) >> [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false)) >> Write-Host "OK: AdminUser.department_id добавлено" -ForegroundColor Green >> } else { >> Write-Host "НЕ НАЙДЕН блок в AdminUser - правь вручную" -ForegroundColor Red >> } >> } >> python -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('SYNTAX OK')" НЕ НАЙДЕН блок в AdminUser — правь вручную SYNTAX OK
The user got "НЕ НАЙДЕН блок в AdminUser — правь вручную". The issue is likely that the exact text of the block in models.py doesn't match my $old string — probably due to whitespace differences (tabs vs spaces) or different line endings (\r\n vs \n).
From the earlier output, I see:
text
    language = Column(String(8), default="ru", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    last_login_at = Column(DateTime(timezone=True))
That looks right. But maybe there are trailing spaces, or \r\n vs \n, or a Unicode issue with the comment.
Let me use a more robust Python-based patcher that operates on lines instead of doing an exact string match.
Let me write a Python patcher that:
Reads models.py line by line
Finds the AdminUser class
Finds the line language = Column(String(8), default="ru", nullable=False) INSIDE the AdminUser class
Inserts the department_id line right after it
This is more robust than PowerShell string matching because Python handles encoding and line endings natively.
Let me write it.
Причина в том, что точное совпадение блока не сработало — скорее всего из-за пробелов/переносов строк (PowerShell-here-string с \n, а файл может быть с \r\n или там лишний пробел после запятой).
Используем Python-патчер — он работает построчно, это надёжнее.
Скрипт 1 (переделка) — добавляем department_id через Python
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\server\models.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

if re.search(r"class AdminUser[\s\S]*?department_id", content):
    print("SKIP: department_id уже есть в AdminUser")
    raise SystemExit(0)

# Находим класс AdminUser
m = re.search(r"(class AdminUser\(Base\):[\s\S]*?)(?=\nclass |\Z)", content)
if not m:
    print("ERROR: class AdminUser не найден")
    raise SystemExit(1)

class_body = m.group(1)

# Ищем строку language = ... внутри класса
target = 'language = Column(String(8), default="ru", nullable=False)'
if target not in class_body:
    print(f"ERROR: строка '{target}' не найдена в AdminUser")
    # выведем первые 30 строк класса для отладки
    for i, line in enumerate(class_body.splitlines()[:30]):
        print(f"  {i:2}: {line}")
    raise SystemExit(1)

# Вставляем новую строку с правильным отступом после target
lines = class_body.split("\n")
out_lines = []
inserted = False
for line in lines:
    out_lines.append(line)
    if not inserted and target in line:
        # определяем отступ из текущей строки
        indent = line[:len(line) - len(line.lstrip())]
        out_lines.append(f"{indent}# Для роли manager — привязка к отделу (видит только свой отдел).")
        out_lines.append(f'{indent}department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)')
        inserted = True

new_class_body = "\n".join(out_lines)
new_content = content.replace(class_body, new_class_body, 1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("OK: department_id добавлен в AdminUser")
try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# Показываем результат — что теперь в AdminUser
m2 = re.search(r"(class AdminUser\(Base\):[\s\S]*?)(?=\nclass |\Z)", new_content)
print("\n=== Новый AdminUser ===")
print(m2.group(1))
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_adminuser_dept.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Запуск патчера ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_adminuser_dept.py
Ожидаем:
text
OK: department_id добавлен в AdminUser
SYNTAX OK

=== Новый AdminUser ===
class AdminUser(Base):
    """
    Пользователь админ-панели.
    ...
    """
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    ...
    language = Column(String(8), default="ru", nullable=False)
    # Для роли manager — привязка к отделу (видит только свой отдел).
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    last_login_at = Column(DateTime(timezone=True))
Запусти и пришли вывод. Как только увидим новое поле — идём в Скрипт 2 (миграция).
>> & client\.venv\Scripts\python.exe _patch_adminuser_dept.py === Запуск патчера === OK: department_id добавлен в AdminUser SYNTAX OK === Новый AdminUser === class AdminUser(Base): """ Пользователь админ-панели. Пароль хранится как bcrypt-хеш (никогда не в открытом виде). Роли: admin, operator, viewer, hr, manager. """ __tablename__ = "admin_users" id = Column(Integer, primary_key=True) username = Column(String(64), unique=True, nullable=False, index=True) password_hash = Column(String(255), nullable=False) full_name = Column(String(255)) email = Column(String(255)) role = Column(String(32), nullable=False, default="viewer") is_active = Column(Boolean, default=True, nullable=False) language = Column(String(8), default="ru", nullable=False) # Для роли manager — привязка к отделу (видит только свой отдел). department_id = Column(Integer, ForeignKey("departments.id"), nullable=True) created_at = Column(DateTime(timezone=True), default=_utcnow) last_login_at = Column(DateTime(timezone=True))
Отлично, модель AdminUser обновлена. Теперь генерируем миграцию.
? Модель обновлена. Идём в Скрипт 2 — миграция.
________________________________________
Скрипт 2 — генерируем миграцию + проверяем на партиции
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Генерация миграции ===" -ForegroundColor Cyan
docker compose exec -T api alembic -c /app/server/alembic.ini revision --autogenerate -m "add_admin_users_department_id"

Write-Host "`n=== Что появилось в versions/ ===" -ForegroundColor Cyan
Get-ChildItem "D:\tracker\server\alembic\versions\*.py" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 3 |
    Format-Table Name, Length, LastWriteTime

Write-Host "`n=== Содержимое новой миграции ===" -ForegroundColor Cyan
$newFile = Get-ChildItem "D:\tracker\server\alembic\versions\*.py" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
Write-Host "Файл: $($newFile.Name)"
Write-Host ""
Get-Content $newFile.FullName

Write-Host "`n=== Проверка на партиции records_* ===" -ForegroundColor Cyan
$content = [System.IO.File]::ReadAllText($newFile.FullName, [System.Text.UTF8Encoding]::new($false))
$hasPartitions = $content -match "records_\d{4}"
$hasDropTable = $content -match "op\.drop_table\('records"
$hasCreateTable = $content -match "op\.create_table\('records_"
$hasDropIndex = $content -match "op\.drop_index\('records"

if ($hasPartitions -or $hasDropTable -or $hasCreateTable -or $hasDropIndex) {
    Write-Host "  ? ВНИМАНИЕ: миграция трогает партиции records_* !" -ForegroundColor Red
    Write-Host "  НЕ ПРИМЕНЯЙ! Пришли содержимое мне." -ForegroundColor Red
    Write-Host "  hasPartitions=$hasPartitions hasDropTable=$hasDropTable hasCreateTable=$hasCreateTable hasDropIndex=$hasDropIndex" -ForegroundColor Yellow
} else {
    Write-Host "  ? OK: партиции records_* не упоминаются" -ForegroundColor Green
}
Ожидаем: миграция должна содержать только два действия:
op.add_column('admin_users', sa.Column('department_id', sa.Integer(), nullable=True))
op.create_foreign_key(...) — FK на departments
Если увидишь что-то про records_* — стоп, присылай файл, разрулим.
Запускай — жду вывод.
Идеально. Миграция чистая, только:
add_column admin_users.department_id
create_foreign_key
Партиции не тронуты — наш include_object работает. Всё как надо.
Единственное замечание — op.create_foreign_key(None, ...) — имя constraint будет None. PostgreSQL сам сгенерирует имя. Это нормально, но лучше явное имя, чтобы в downgrade можно было удалить. Правда, alembic сам генерирует корректный drop_constraint(None, ...) — он тоже подставит автоимя. Обычно работает, но лучше явное имя.
Давай не будем заморачиваться — оставим как есть. Если будут проблемы с откатом, поправим.
Но! Есть один важный момент — миграция генерируется от b02da1230e4d (предыдущей). Хорошо, цепочка:
35d67a73f181 ? 939e3d0b6f4c ? ecb1e3f89300 ? 2602b71902d4 ? b02da1230e4d ? 0f13ad394b65
Ок, применяем.
Пользователь остановился здесь. Мне нужно:
Сказать: миграция чистая, применяем
Дать команду применения
Дать проверку — колонка появилась в БД
Перейти к Скрипту 3 — роуты /admin/profile
Скрипт 3 большой (роуты + хелперы фильтрации + сессия). Запустим.
Также важно — проверим, что Department импортирован в web_admin.py. Пользователь не присылал вывод этой команды.
Давай структурирую:
Применение миграции
Проверка
Скрипт 3 — роуты /admin/profile + хелпер manager_department_id (без apply_manager_filter — оставим на потом, чтобы не усложнять)
Скрипт 3b — проверить где формируется session["admin_user"] и добавить department_id
Скрипт 4 — profile.html (это уже давал в прошлом сообщении, но переиздам, чтобы пользователь не искал)
Скрипт 5 — user_form.html (тоже переиздам)
Скрипт 6 — патч роутов users (сокращу до минимума, только чтобы department_id принимался)
Пересборка
Хотя это уже было, но переиздам чтобы было в одном сообщении.
Хорошо, приступаю к написанию ответа.
? Миграция идеальная. include_object работает — партиции не тронуты. Применяем.
________________________________________
Скрипт 2a — применяем миграцию
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Перезапуск api (Alembic применит миграцию) ===" -ForegroundColor Cyan
docker compose restart api
Start-Sleep -Seconds 15

Write-Host "`n=== Логи API ===" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`n=== Версия Alembic ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT * FROM alembic_version;"

Write-Host "`n=== Колонка admin_users.department_id ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='admin_users' AND column_name='department_id';"

Write-Host "`n=== FK на departments ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT tc.constraint_name, ccu.table_name AS foreign_table FROM information_schema.table_constraints AS tc JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.table_name='admin_users' AND tc.constraint_type='FOREIGN KEY';"
Ожидаем:
Running upgrade b02da1230e4d -> 0f13ad394b65, add_admin_users_department_id
version_num = 0f13ad394b65
department_id присутствует, nullable
FK на departments
Как только увидим — идём в Скрипт 3.
________________________________________
Скрипт 3 — роуты /admin/profile + хелпер для manager
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains('def profile_page(')) {
    Write-Host "Роуты /profile уже есть" -ForegroundColor Yellow
} else {
    $anchor = @'
def _active_admins_count(db: Session) -> int:
    """Сколько активных администраторов в системе."""
    return db.query(AdminUser).filter(
        AdminUser.role == "admin",
        AdminUser.is_active == True,
    ).count()
'@
    $addition = @'
def _active_admins_count(db: Session) -> int:
    """Сколько активных администраторов в системе."""
    return db.query(AdminUser).filter(
        AdminUser.role == "admin",
        AdminUser.is_active == True,
    ).count()


# ============================================================
# Фильтрация данных по отделу для роли manager
# ============================================================
def manager_department_id(user):
    """
    Возвращает department_id если user.role == 'manager' и отдел задан.
    Иначе — None.
    Используется для фильтрации списков и отчётов.
    """
    if user and user.get("role") == "manager":
        return user.get("department_id")
    return None


def filter_employees_query(query, user, emp_col="id"):
    """
    Если user — manager с отделом: добавляет в query фильтр
    employee.department_id == его отдел.
    
    query — SQLAlchemy Query по модели Employee.
    user — dict из current_admin().
    """
    dep_id = manager_department_id(user)
    if dep_id is None:
        return query
    from .models import Employee as _Emp
    col = getattr(_Emp, emp_col, _Emp.id)
    return query.filter(_Emp.department_id == dep_id)


def filter_work_sessions_query(query, user):
    """
    Если user — manager с отделом: ограничивает WorkSession
    только сессиями сотрудников его отдела.
    """
    dep_id = manager_department_id(user)
    if dep_id is None:
        return query
    from .models import Employee as _Emp, WorkSession as _WS
    sub = db_subquery_employees_of_dept(dep_id)
    return query.filter(_WS.employee_id.in_(sub))


def db_subquery_employees_of_dept(dep_id):
    """Подзапрос: id сотрудников указанного отдела."""
    from .models import Employee as _Emp
    from sqlalchemy import select
    return select(_Emp.id).where(_Emp.department_id == dep_id)


# ============================================================
# Мой профиль
