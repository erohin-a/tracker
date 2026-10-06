<!-- Часть 857 из 1409 -->
# Смотрим, где формируется сессия
*Хлебные крошки:* Смотрим, где формируется сессия

[◀ --- 6.6. Сохраняем department_id при редактировании ---](856_6_6_Sohranyaem_department_id_pri_redaktirovanii.md) | [Оглавление](00_BCE_INDEX.md) | [Находим класс AdminUser ▶](858_Nahodim_klass_AdminUser.md)

---

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

