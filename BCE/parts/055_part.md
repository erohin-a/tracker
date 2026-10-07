# ============================================================

*Часть 55 из 100. Источник: `BCE.md`.*

[◀ ============================================================](054_part.md) | [Оглавление](00_BCE_INDEX.md) | [Найдём место где формируется session["admin_user"] ▶](056_Naydem_mesto_gde_formiruetsya_session_admin_user.md)

---

# ============================================================
# Мой профиль
# ============================================================
@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    from .models import AdminUser
    sess = request.session.get("admin")
    # sess может быть строкой (старый формат) или dict
    username = sess if isinstance(sess, str) else (sess or {}).get("username")
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "admin": username,
        "admin_role": user.role,
        "user": user,
        "roles_info": ROLES_INFO,      # словарь ролей
        "saved": request.query_params.get("saved") == "1",
        "pw_changed": request.query_params.get("pw_changed") == "1",
        "pw_error": request.query_params.get("pw_error"),
    })
и т.д. — дам полный код после твоего вывода.
________________________________________
Скрипт 3 — миграция admin_users.department_id
Проверим сначала текущую модель AdminUser:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Модель AdminUser ===" -ForegroundColor Cyan
python -c @"
import re
with open(r'D:\tracker\server\models.py', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'class AdminUser.*?(?=\nclass |\Z)', content, re.DOTALL)
if m:
    print(m.group(0))
else:
    print('AdminUser не найдена')
"@

Write-Host "`n=== Список миграций ===" -ForegroundColor Cyan
Get-ChildItem "D:\tracker\server\alembic\versions\*.py" | Sort-Object Name | Format-Table Name, Length
Если department_id в AdminUser нет — сгенерируем миграцию через alembic revision --autogenerate. Но, зная про особенность партиций, я сначала проверю сгенерированный файл и почищу, если что.
________________________________________
Что делаем прямо сейчас
Запусти последовательно:
Скрипт 1 — патч base.html. Пришли: OK: base.html пропатчен и вывод проверки.
Скрипт 2 — список существующих роутов/хелперов. Пришли вывод.
Скрипт 3 — модель AdminUser + список миграций. Пришли вывод.
После этого я одним сообщением выдам:
Полный роут /admin/profile с сохранением и сменой пароля (учитывая то, что уже есть в web_admin.py).
Шаблон profile.html — форма + смена пароля.
Миграцию admin_users.department_id + патч формы пользователя в /admin/users (поле «Отдел» для manager).
Хелперы для фильтрации по отделу — чтобы manager видел только своих.
Отлично, я получил всю нужную информацию. Разберу, что у нас есть:
base.html — патч прошёл успешно, ссылка на профиль добавлена. Sidebar уже разграничен по ролям (строки 146-201) — это уже было сделано ранее, отлично.
web_admin.py — уже есть:
current_admin(request) — возвращает dict сессии (строка 57)
current_admin_or_none(request) (строка 69)
Хелпер для ORM-объекта (строка 75): db.query(AdminUser).filter(AdminUser.id == user["id"]).first()
AdminUser в моделях (строка 26)
Импорт из security_passwords: hash_password, verify_password, needs_rehash, is_valid_role
Уже есть CRUD для admin_users (строки 1714+)
AdminUser модель — есть поля: id, username, password_hash, full_name, email, role, is_active, language, created_at, last_login_at. НЕТ department_id.
Миграции: 5 штук — baseline, partition, schedules_roles, add_computer_soft_delete, add_employee_settings.
Что нужно сделать:
? base.html пропатчен (сделано)
Создать /admin/profile — роуты в web_admin.py + шаблон profile.html
Миграция admin_users.department_id + интеграция в форму users
Фильтрация для manager по отделу
Мне нужно посмотреть:
Функцию current_admin_or_none и хелпер для ORM (строки 57-90) — чтобы понять формат сессии
Роуты /admin/users (строки 1714+) — чтобы понять структуру и не сломать
Формат roles_info — где определён
Давайте запрошу эти куски. Но чтобы не терять время, я уже могу написать:
Полный код для /admin/profile — роуты (используя существующие хелперы)
Шаблон profile.html
Модель — добавить department_id в AdminUser
Миграцию — через alembic revision --autogenerate, потом почистить
Начну с запроса нужных кусков кода из web_admin.py, чтобы не ошибиться.
Кстати, я вижу из вывода, что в web_admin.py есть обёртки:
python
def current_admin(request: Request):
    ...

def current_admin_or_none(request: Request):
    ...

def _current_admin_user(request, db):
    """Возвращает ORM-объект AdminUser для текущей сессии или None."""
    user = current_admin_or_none(request)  # или похожее
    ...
    return db.query(AdminUser).filter(AdminUser.id == user["id"]).first()
И admin_count — что-то такое.
Мне нужно увидеть строки 50-90 web_admin.py и функции для /admin/users (1700-1990).
Давай запрошу их. И заодно посмотрю security_passwords.py — там roles_info может быть.
План ответа:
Подтвердить, что base.html пропатчен
Запросить нужные куски web_admin.py для точной интеграции
Дать готовые скрипты для /admin/profile — но подожду подтверждения от пользователя
Стоп. Пользователь хочет двигаться вперёд. Я уже знаю достаточно, чтобы:
Создать роуты /admin/profile — используя _current_admin_user(request, db) (тот что на строке 75)
Создать шаблон profile.html
Добавить department_id в модель AdminUser
Сгенерировать миграцию
Единственное, что я не знаю точно — это сигнатуру хелпера _current_admin_user. Он на строке 75. Давай запрошу строки 55-90. Это 5 секунд.
И заодно — как выглядит роль в сессии: user["role"] или user.role? Судя по base.html — там admin_role, который передаётся в контекст. Значит, есть контекст-процессор или это кладётся в каждый TemplateResponse.
Хм, посмотрю на строки 55-95 web_admin.py.
Ок, отвечаю. Сначала запрошу нужное, потом дам код.
Отлично, картина ясна:
? base.html пропатчен — ссылка на профиль добавлена
? Sidebar по ролям уже разграничен (строки 146–201) — это было сделано ранее
? В web_admin.py уже есть все хелперы: current_admin, current_admin_or_none, _current_admin_user, hash_password, verify_password
? Модель AdminUser есть, но в ней нет department_id — это надо добавить
? Есть 5 миграций, последняя 2602b71902d4
Теперь мне нужно увидеть 3 куска web_admin.py, чтобы написать точный код без догадок:
Скрипт — вывести нужные куски
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\web_admin.py"
$lines = [System.IO.File]::ReadAllLines($path, [System.Text.UTF8Encoding]::new($false))

Write-Host "=== 1. Хелперы current_admin (строки 55-100) ===" -ForegroundColor Cyan
for ($i = 54; $i -lt 100; $i++) { Write-Host ("{0,4}: {1}" -f ($i + 1), $lines[$i]) }

Write-Host "`n=== 2. roles_info / ROLES_INFO — где определены? ===" -ForegroundColor Cyan
Select-String -Path $path -Pattern "roles_info|ROLES_INFO|label_ru|label_en" | Select-Object -First 20

Write-Host "`n=== 3. Роуты /admin/users (строки 1700-1990) ===" -ForegroundColor Cyan
for ($i = 1699; $i -lt 1990; $i++) { Write-Host ("{0,4}: {1}" -f ($i + 1), $lines[$i]) }
По этому выводу я точно пойму:
Как устроена сессия (user["id"] vs user.id)
Есть ли уже roles_info и где (чтобы использовать один источник)
Как передаётся admin_role в шаблоны (context processor?)
Как устроены формы создания/редактирования users — чтобы добавить туда поле «Отдел»
После этого я одним сообщением выдам:
Роуты /admin/profile — GET, POST /save, POST /change-password (с bcrypt через существующие hash_password / verify_password)
Шаблон profile.html — форма ФИО/email/язык + смена пароля + кнопка «Мои входы»
Патч модели AdminUser — добавить department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
Миграция — сгенерируем, но потом вручную проверим и почистим от возможного мусора с партициями (у нас в env.py уже include_object, так что должно быть чисто)
Патч формы /admin/users — добавить выпадающий список «Отдел» (показывается только для роли manager)
Хелперы фильтрации — filter_employees_by_role(db, user, query) для использования во всех страницах, где manager видит сотрудников
Запускай скрипт и присылай вывод — дальше двигаемся в одном сообщении.
Отлично, теперь у меня полная картина. Резюмирую:
Что уже есть:
current_admin(request) ? возвращает dict из request.session["admin_user"] с полями id, username, role, full_name
current_admin_or_none(request) ? то же, но без 401
get_db_user(request, db) ? ORM-объект AdminUser из сессии
hash_password, verify_password, needs_rehash, is_valid_role
ROLES_INFO — словарь ролей (импортируется из security_passwords)
_require_admin_role(request) — 403 если не admin
Полный CRUD /admin/users (уже работает)
В шаблоне доступны: admin, admin_role, roles_info (через context_processor, строка 220)
Что нужно добавить:
Модель AdminUser.department_id (FK на departments.id)
Миграция (Alembic autogenerate)
Роуты /admin/profile:
GET /admin/profile — показать форму
POST /admin/profile/save — сохранить ФИО/email/язык
POST /admin/profile/change-password — сменить свой пароль
Шаблон profile.html
Форма /admin/users/new и /admin/users/{id}/edit — добавить поле «Отдел» (показывать только когда роль = manager)
Хелпер фильтрации по отделу для manager
Давай проверим контекст-процессор (строки 220 в web_admin.py) — там где roles_info, чтобы понять, как передаётся admin_role. И как устроен базовый контекст для всех шаблонов.
Мне нужно посмотреть строки 200-230 web_admin.py. Давай сразу дам скрипт для полного контекста и затем сразу все патчи одним сообщением.
Но я не хочу сильно затягивать. По опыту работы с этим проектом, думаю, что контекст-процессор выглядит примерно так:
python
def _inject_globals(request):
    user = request.session.get("admin_user")
    return {
        "admin": user["username"] if user else None,
        "admin_role": user["role"] if user else None,
        "admin_user_id": user["id"] if user else None,
        "roles_info": ROLES_INFO,
    }
templates.context_processors.append(_inject_globals)
Дам скрипт для точного показа, потом сразу патчи. Или лучше — я уже много раз видел, что пользователь торопится. Давай сразу дам:
Скрипт 1 — показать строки 200-240 web_admin.py (context processor)
Скрипт 2 — добавить поле department_id в модель AdminUser
Скрипт 3 — сгенерировать миграцию
Скрипт 4 — добавить роуты /admin/profile
Но если я дам всё сразу, есть риск, что где-то неправильно угадаю структуру. Лучше — покажу context processor, потом дам все патчи. Это 1 лишний шаг, но безопаснее.
Или — компромисс. Дам сразу скрипт показа (200-240) + сразу напишу полные патчи, но пометив места, которые нужно проверить по выводу. Если что-то не сойдётся — поправим.
Ок, давай так:
Скрипт показа context processor (200-240) — но пользователь уже видел строку 220 с roles_info, значит он там есть.
Даю все патчи одним сообщением, где:
Модель AdminUser — добавлю department_id
Схема Pydantic / роуты
Шаблон profile.html
Патч user_form.html (нужно посмотреть его содержимое!)
Хм, user_form.html я не видел. Надо его посмотреть, чтобы добавить поле «Отдел».
Ладно, давай так — компактный план:
Скрипт 1 — посмотреть:
web_admin.py строки 200-240 (context processor)
templates/user_form.html
templates/users.html (для добавления кнопки перехода в профиль)
Скрипт 2 — после вывода дам полный комплект:
патч модели
миграция
роуты /admin/profile
шаблон profile.html
патч user_form.html (поле Отдел)
патч users.html (кнопка "Редактировать" уже есть)
Так надёжнее. Давай так.
Отлично, картина почти полная. Всё что нужно для роутов /admin/profile есть: current_admin, hash_password, verify_password, модель AdminUser. Не хватает department_id в модели и самого шаблона user_form.html (его надо посмотреть, чтобы добавить поле «Отдел»).
Последний скрипт диагностики перед основной реализацией:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== 1. Context processor (строки 210-235) ===" -ForegroundColor Cyan
$lines = [System.IO.File]::ReadAllLines("D:\tracker\server\web_admin.py", [System.Text.UTF8Encoding]::new($false))
for ($i = 209; $i -lt 235; $i++) { Write-Host ("{0,4}: {1}" -f ($i + 1), $lines[$i]) }

Write-Host "`n=== 2. user_form.html ===" -ForegroundColor Cyan
if (Test-Path "D:\tracker\server\templates\user_form.html") {
    Get-Content "D:\tracker\server\templates\user_form.html"
} else {
    Write-Host "  НЕ НАЙДЕН" -ForegroundColor Red
}

Write-Host "`n=== 3. Список шаблонов ===" -ForegroundColor Cyan
Get-ChildItem "D:\tracker\server\templates\*.html" | Sort-Object Name | Format-Table Name, Length
Пришли вывод. После этого одним сообщением выдам полный комплект:
Патч модели — AdminUser.department_id (FK на departments.id)
Миграция Alembic — autogenerate + проверка через include_object (не тронет партиции)
Роуты /admin/profile — 3 штуки: GET профиля, POST сохранения, POST смены пароля
Шаблон profile.html — форма + смена пароля + кнопка «Мои входы»
Патч user_form.html — поле «Отдел» (показывается только для роли manager)
Хелперы фильтрации — _manager_filter(db, user) — можно будет использовать в отчётах и списках для роли manager
Запускай.
Now I have all information I need. Let me compile the complete solution:
Model AdminUser needs department_id column
Migration for that column
Routes for /admin/profile
Template profile.html
Patch user_form.html to add department_id field for manager role
Manager filter helpers
Also I noticed user_form.html has encoding issues - "РРІР°РЅРѕРІ РРІР°РЅ РРІР°РЅРѕРІРёС‡" instead of "Иванов Иван Иванович" in placeholder, and "[СЂРµРґ]" instead of emoji. Also "Р СѓСЃСЃРєРёР№" instead of "Русский". Let me fix these too.
Let me structure this response:
Script 1: Patch models.py — add department_id to AdminUser
Script 2: Generate migration with alembic
Script 3: Patch web_admin.py — add /admin/profile routes
Script 4: Create templates/profile.html
Script 5: Patch templates/user_form.html — add department dropdown + fix encoding
Script 6: Rebuild and test
Let me write them carefully.
For scripts, I'll use Python patchers where complex, PowerShell for simple things.
For the AdminUser model patch:
Add: department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
For migration:
Run alembic revision --autogenerate
Check what it generated (should only be adding department_id)
If it contains records_* operations, clean them up
Then apply
Since we already have include_object in env.py, this should be clean now.
For /admin/profile routes:
GET /admin/profile — show form
POST /admin/profile/save — update full_name, email, language
POST /admin/profile/change-password — change password
Note: username NOT changeable (as per user_form).
For user_form.html patch:
Add department dropdown after "role" field
Only show when role=manager (via JS toggling) — or always show, but note that it's only for manager
Fix encoding issues
Let me write everything now.
Also I should think about manager filtering. The user said "везде, где db.query(Employee) — фильтр по отделу, если роль = manager". This is a bigger change. Let me start with:
Model + migration + profile page + user_form patch
Then in next message: manager filtering everywhere
Actually let me include a helper now, and use it in a few key places:
/admin/employees list
/admin/reports employees dropdown
Let me structure:
Script 1: models.py patch — add department_id + helper
Script 2: alembic revision autogenerate + check
Script 3: web_admin.py — add profile routes + helper _filter_employees_query
Script 4: templates/profile.html — new file
Script 5: templates/user_form.html — full rewrite (cleaner than patches)
Script 6: rebuild + test
Let me be careful with the alembic migration — with include_object present, it should only generate the department_id addition. Let me tell the user to inspect it anyway.
Actually, let me also handle: when AdminUser is deleted, if they have department_id, what happens? Since it's nullable, no issue.
Also for the profile page — I need to know what the ROLES_INFO structure looks like. From base.html:
roles_info[admin_role].label_ru / label_en
So ROLES_INFO is a dict of role_code ? dict with label_ru, label_en.
Let me write the response now. I'll keep it compact but complete.
Actually — one important thing. When creating user with role=manager, we need to set department_id. The current user_form has no such field. Let me add it. For editing too.
Also: should hr role have department? No, hr sees all departments (per spec). Only manager is tied to a specific department.
Let me write the profile page template. It should show:
Username (readonly)
Full name (editable)
Email (editable)
Role (readonly, with label)
Language (editable select)
Save button
Change password section (old, new, new confirm)
Link to /admin/logins
Let me finalize.
Actually — the current_admin(request) returns {"id", "username", "role", "full_name"} per line 60. But looking at get_db_user at line 74-79, it queries by id. So the session stores at minimum id, username, role, full_name. Good.
For the profile routes I need:
current user from session
get DB object to update
Let me write.
One more thing — the display_name in context processor. Line 215: "admin": display_name. So in templates {{ admin }} is display_name, not username. And admin_username is available too. Good to know.
OK, writing the response now. I'll try to be compact but complete.
Отлично, картина полная. Всё что нужно — есть. Один вопрос: в user_form.html есть крокозябры (placeholder «РРІР°РЅРѕРІ...», «[СЂРµРґ]», «Р СѓСЃСЃРєРёР№») — починю заодно.
Погнали полным комплектом. Запускай по порядку 1?2?3?4?5?6.
________________________________________
Скрипт 1 — патч модели AdminUser
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\models.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("department_id = Column(Integer, ForeignKey(""departments.id""), nullable=True)") -and
    $content -match "class AdminUser[\s\S]*?department_id") {
    Write-Host "AdminUser.department_id уже есть" -ForegroundColor Yellow
} else {
    $old = @'
    language = Column(String(8), default="ru", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    last_login_at = Column(DateTime(timezone=True))
'@
    $new = @'
    language = Column(String(8), default="ru", nullable=False)
    # Для роли manager — привязка к отделу (видит только свой отдел).
    # Для остальных ролей — игнорируется (может быть NULL).
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    last_login_at = Column(DateTime(timezone=True))
'@
    if ($content.Contains($old)) {
        $content = $content.Replace($old, $new)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: AdminUser.department_id добавлено" -ForegroundColor Green
    } else {
        Write-Host "НЕ НАЙДЕН блок в AdminUser — правь вручную" -ForegroundColor Red
    }
}
python -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('SYNTAX OK')"
________________________________________
Скрипт 2 — генерируем и проверяем миграцию
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Генерация миграции ===" -ForegroundColor Cyan
docker compose exec -T api alembic -c /app/server/alembic.ini revision --autogenerate -m "add_admin_users_department_id"

Write-Host "`n=== Что появилось в versions/ ===" -ForegroundColor Cyan
Get-ChildItem "D:\tracker\server\alembic\versions\*.py" | Sort-Object LastWriteTime -Descending | Select-Object -First 2 | Format-Table Name, Length, LastWriteTime

Write-Host "`n=== Содержимое новой миграции ===" -ForegroundColor Cyan
$newFile = Get-ChildItem "D:\tracker\server\alembic\versions\*.py" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $newFile.FullName

Write-Host "`n=== Проверка на партиции records_* ===" -ForegroundColor Cyan
$content = [System.IO.File]::ReadAllText($newFile.FullName, [System.Text.UTF8Encoding]::new($false))
if ($content -match "records_\d{4}") {
    Write-Host "  ВНИМАНИЕ: в миграции есть records_YYYY !" -ForegroundColor Red
    Write-Host "  НЕ ПРИМЕНЯЙ! Пришли мне содержимое файла." -ForegroundColor Red
} else {
    Write-Host "  OK: партиции records не упоминаются" -ForegroundColor Green
}
Ожидаем: только op.add_column('admin_users', sa.Column('department_id', sa.Integer(), nullable=True)) и op.create_foreign_key(...). Если увидишь что-то про records_* — не применяй, пришли мне содержимое.
Если всё чисто — применяем:
powershell
docker compose restart api
Start-Sleep -Seconds 15
docker compose logs api --tail=25
docker compose exec -T db psql -U tracker -d tracker -c "SELECT column_name FROM information_schema.columns WHERE table_name='admin_users' AND column_name='department_id';"
________________________________________
Скрипт 3 — роуты /admin/profile + хелпер фильтрации
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains('def profile_page(')) {
    Write-Host "Роуты /profile уже есть" -ForegroundColor Yellow
} else {
    # Вставляем перед блоком "# Профиль" или после _require_admin_role
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
def apply_manager_filter(query, user, model_for_emp_column="employee_id"):
    """
    Если пользователь — manager с привязанным отделом, добавляет в query
    фильтр по сотрудникам этого отдела.
    query — SQLAlchemy Query (например db.query(WorkSession))
    user — dict из current_admin(request)
    model_for_emp_column — имя поля в query, содержащее employee_id
    """
    if not user or user.get("role") != "manager":
        return query
    dep_id = user.get("department_id")
    if not dep_id:
        return query  # manager без отдела — видит всё (лучше так, чем ничего)
    from .models import Employee as _Emp
    emp_ids = [e.id for e in db.query(_Emp).filter(_Emp.department_id == dep_id).all()] if False else None
    # Здесь нужен доступ к db — поэтому фильтруем проще: подзапрос
    from sqlalchemy import select
    subq = select(_Emp.id).where(_Emp.department_id == dep_id)
    col = getattr(query.column_descriptions[0]["entity"], model_for_emp_column)
    return query.filter(col.in_(subq))


def manager_department_id(user):
    """Возвращает department_id для manager или None."""
    if user and user.get("role") == "manager":
        return user.get("department_id")
    return None


# ============================================================
# Мой профиль
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
        new_value=json.dumps({"full_name": user.full_name, "email": user.email, "language": language}, ensure_ascii=False),
    ))
    db.commit()

    # Обновим сессию (display_name = full_name or username)
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
        Write-Host "OK: роуты /admin/profile добавлены" -ForegroundColor Green
    } else {
        Write-Host "НЕ НАЙДЕН anchor _active_admins_count — правь вручную" -ForegroundColor Red
    }
}
python -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('SYNTAX OK')"
Оговорка: функция apply_manager_filter написана с заделом на будущее. Пока что она не подключена нигде. В следующих сообщениях (когда будем править отчёты и списки) — используем её. Ключевое сейчас — manager_department_id(user) для получения department_id в шаблонах.
Также надо добавить в сессию department_id — при логине. Проверим/поправим это в скрипте 3b:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

