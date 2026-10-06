<!-- Часть 597 из 1409 -->
# Добавляем alembic, если ещё нет
*Хлебные крошки:* Добавляем alembic, если ещё нет

[◀ Читаем текущее содержимое](596_Chitaem_tekuschee_soderzhimoe.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](598_part.md)

---

# Добавляем alembic, если ещё нет
if ($req -notmatch "alembic") {
    $req = $req.TrimEnd() + "`nalembic==1.13.2`n"
    [System.IO.File]::WriteAllText($reqPath, $req, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: alembic добавлен в requirements.txt" -ForegroundColor Green
} else {
    Write-Host "alembic уже есть — пропускаем" -ForegroundColor Yellow
}

Write-Host "`nТекущее содержимое requirements.txt:" -ForegroundColor Cyan
Get-Content $reqPath
Что должно быть в выводе:
text
fastapi==0.111.0
uvicorn[standard]==0.30.1
gunicorn==22.0.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
pydantic==2.7.4
pydantic-settings==2.3.0
cryptography==42.0.8
python-multipart==0.0.9
jinja2==3.1.4
itsdangerous==2.2.0
openpyxl==3.1.5
reportlab==4.2.2
tzdata==2024.1
alembic==1.13.2     ? новая строка
Запусти D1, пришли вывод — и сразу пойдём в E1 (серверный i18n-модуль). После E1–E5 я напомню, что мы делаем Alembic и куда возвращаемся.
Текущее содержимое requirements.txt: fastapi==0.111.0 uvicorn[standard]==0.30.1 gunicorn==22.0.0 sqlalchemy==2.0.30 psycopg2-binary==2.9.9 pydantic==2.7.4 pydantic-settings==2.3.0 cryptography==42.0.8 python-multipart==0.0.9 jinja2==3.1.4 itsdangerous==2.2.0 openpyxl==3.1.5 tzdata==2024.1 reportlab==4.2.2 alembic==1.13.2
User confirmed D1 works. Now we do E1-E5 — i18n infrastructure. Let me plan:
E1 — server/i18n.py — module with translations dict + t() function
E2 — client/i18n.py — same for client
E3 — hook into Jinja2 templates (web_admin.py)
E4 — language switcher in admin (cookie-based)
E5 — language switcher in client (.env + restart)
Let me be pragmatic. Since we're just adding infrastructure, we don't need to translate everything now. Just create the modules with initial minimal set of strings, hooks, and switcher.
Let me write E1 first.
Actually, let me structure this smartly:
E1: server/i18n.py — module
E2: hook in web_admin.py templates
E3: language switcher UI in base.html + endpoint in web_admin.py
E4: client/i18n.py — module
E5: client switcher in settings dialog (or just .env for now)
Let me start with E1 — server module.
Отлично, D1 готов
Начинаем блок E — инфраструктура i18n (RU/EN). Это 5 скриптов, дальше возвращаемся к Alembic.
План блока E:
E1 — серверный модуль server/i18n.py (словарь переводов + функция t())
E2 — хук в Jinja2 (чтобы в шаблонах работало {{ _("key") }})
E3 — переключатель языка в шапке админки (cookie)
E4 — клиентский модуль client/i18n.py
E5 — переключатель языка в клиенте
Строки будем пополнять постепенно. Сейчас закладываем ~30 базовых (меню, кнопки), дальше по ходу правок — добавляем.
________________________________________
Скрипт E1 — создаём server/i18n.py
powershell
powershell
$ErrorActionPreference = "Stop"
$i18nPath = "D:\tracker\server\i18n.py"

$i18nPy = @'
