<!-- Часть 347 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 3. main.py (клиент) — используем значение из БД](346_3_main_py_klient_ispolzuem_znachenie_iz_BD.md) | [Оглавление](00_BCE_INDEX.md) | [Employee: ▶](348_Employee.md)

---

# ============================================================
Write-Host "`n--- client/main.py ---" -ForegroundColor Cyan
$mainPath = "$clientDir\main.py"
$mainContent = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$oldCall = "            closed_uid = db.auto_close_idle_session(IDLE_CLOSE_MINUTES)"
$newCall = "            idle = db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)`n            closed_uid = db.auto_close_idle_session(idle)"

if ($mainContent.Contains($newCall)) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} elseif ($mainContent.Contains($oldCall)) {
    $mainContent = $mainContent.Replace($oldCall, $newCall)
    [System.IO.File]::WriteAllText($mainPath, $mainContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  main.py использует значение из БД" -ForegroundColor Green
} else {
    Write-Host "  ВНИМАНИЕ: не найден вызов auto_close_idle_session(IDLE_CLOSE_MINUTES)" -ForegroundColor Yellow
    Write-Host "  Откройте client/main.py и найдите вручную строку с auto_close_idle_session" -ForegroundColor Yellow
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"

Write-Host "`n=== Все патчи клиента применены ===" -ForegroundColor Cyan
________________________________________
Скрипт 5 — пересборка и проверка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

Write-Host "--- Пересборка Docker ---" -ForegroundColor Cyan
docker compose down
docker compose up -d --build

Start-Sleep -Seconds 25

Write-Host "`n--- Статус контейнеров ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Логи API (30 строк) ---" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`n--- Проверка endpoint ---" -ForegroundColor Cyan
curl.exe -k https://localhost/api/v1/client-config

Write-Host "`n`nГотово." -ForegroundColor Green
Write-Host "Откройте:" -ForegroundColor Green
Write-Host "  https://localhost/admin/settings       — настройка idle-порога" -ForegroundColor Green
Write-Host "  https://localhost/admin/reports        — новая форма отчёта" -ForegroundColor Green
Write-Host "`nПерезапустите клиент:" -ForegroundColor Green
Write-Host "  cd D:\tracker" -ForegroundColor Green
Write-Host "  client\.venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "  python -m client.main" -ForegroundColor Green
________________________________________
Как это работает
Настройка idle-порога
Открыть /admin/settings
Изменить число (например, на 60)
Сохранить
Клиенты подхватят значение максимум через 5 минут (после следующего цикла sync)
Если клиент офлайн — подхватит при следующем выходе на связь
«Отработано» vs «Эффективно»
Пример для одного дня:
Сессия	Старт	Конец	Эффективно
1	09:00	13:00	3:30 (обед, паузы)
2	14:00	18:00	3:30
Отработано = 18:00 ? 09:00 = 9:00:00 (от старта первой до конца последней)
Эффективно = 3:30 + 3:30 = 7:00:00 (сумма без пауз)
Топ программ с разбивкой
В таблице «Топ программ за период» под каждой программой есть треугольник ? Кто работал в «PyCharm» — N сотр. Кликните — раскроется таблица с ФИО, 1C ID, временем, клавиатурой и мышью по каждому сотруднику.
Экспорт CSV/XLSX
9 колонок: группа, день, сотрудник, 1C ID, компьютер, сессий, отработано, эффективно, аварийных.
Итоговая строка внизу.
________________________________________
Проверка
/admin/settings — открывается, поле заполнено 30, при сохранении всплывает зелёная плашка.
/admin/reports — новая форма с подсказкой про колонки.
Сформировать отчёт «Этот месяц», группировка «Рабочие дни ? Сотрудник».
В таблице: 1C ID, Отработано (span), Эффективно (зелёное).
В топе программ: развернуть любую ? разбивка по сотрудникам.
Экспорт XLSX — колонок 9.
Если что-то падает — пришлите:
powershell
docker compose logs api --tail=60
и Get-Content "$env:APPDATA\Tracker\client.log" -Tail 40 -Encoding UTF8.
отлично всё работает. В клиентской программе когда начинается работа отображается сессия с такого времени. Вот это время не соответствует текущему пускай отображается реальное. Что можно, нужно вынести на панель клиентскую? если что то стоящие давай добавим. В связи с появлением в админской части вкладки настройка давай туда уберем Часовой пояс Начало рабочего дня. Какие еще есть переменные в нашей программе которые мы можем вынести в настройку? давай выведем. В отчётах в .xlsx выводятся столбцы Отработано (сек) Эффективно (сек) Пускай выводятся сразу в формате время часы минуты секунды что бы программа сразу понимала Рабочий день Пускай выводятся сразу в формате дата день месяц год что бы программа сразу понимала В отчётах должна быть возможность выбрать нескольких сотрудников двух, трёх, десяти. А что делать с уволенными сотрудниками? Наверное их нужно убрать в отдельный список или как правильно по ним может понадобится информация? А если будет 100 сотрудников наверное стоит добавить отделы и также добавить для фильтра в отчёты. Давай попробуем реализовать всё это. А какие у тебя есть еще предложения?
The user wants a lot of changes. Let me break this down carefully:
Client time display fix - session start time shows wrong time (probably UTC instead of local). Need to display real local time.
Client panel improvements - what to display on client panel.
Move Timezone and Workday start to admin settings - so they're not per-report but global settings.
Other settings to move - identify all configurable variables.
Excel export:
"Отработано (сек)" and "Эффективно (сек)" ? format as HH:MM:SS time
"Рабочий день" ? format as DD.MM.YYYY
Multi-select employees - allow choosing multiple employees in reports.
Fired employees - separate list, soft delete, keep history.
Departments - add departments for 100+ employees, filter by department in reports.
Plus my own suggestions.
This is a huge chunk of work. Let me organize it as:
Part 1: Client time display fix
In client/main.py, the _short_dt function uses UTC time from DB. Need to convert to local time.
Part 2: Client panel
Add to client panel:
Current server status
Last sync time
Records pending
Current session duration (live)
Idle status indicator
Menu buttons
Part 3: Admin settings page
Add to AppSetting-based settings:
report_timezone
workday_start_hour
activity_gap_minutes
idle_close_minutes (already there)
Part 4: Excel export formats
In _report_to_table, convert:
Durations to HH:MM:SS strings (openpyxl can also format as time)
Dates to DD.MM.YYYY
Actually for openpyxl, we can set the cell format via number_format, but easier to just write strings.
Part 5: Multi-select employees
Change employee_id from single select to multi-select (checkbox list or <select multiple>). Parse as list.
Part 6: Fired employees
Add filter tabs: Active / Fired / All. Employee page shows only active by default.
Part 7: Departments
New model Department, Employee.department_id, filter in reports, page to manage departments.
This is going to be LONG. Let me structure this as a multi-part response. I should probably focus on giving complete PowerShell scripts as before.
Let me think about what order to do this:
Actually, given the scope, I think I should:
Acknowledge everything
Ask if user wants to proceed step by step OR all at once
Give suggestions
Start with the most critical/simplest first
Actually no, the user asked to do it all. Let me just do it, but split into clear scripts and give explanations.
Let me organize:
Server changes:
models.py: add Department, Employee.department_id, Employee.fired_at
web_admin.py: settings page gets new fields, reports multi-select, department filter, filters for fired employees, Excel formatting
Templates: settings, employees (with departments and fired tab), reports (multi-select), report_result
New page: /admin/departments
Client changes:
main.py: fix time display, add panel widgets
Let me be strategic. This is huge. I'll produce:
Script 1: Server models + new admin pages for departments & settings
Script 2: Server web_admin.py (reports with multi-select, departments, fired employees, Excel formatting)
Script 3: Templates (base, settings, employees, departments, reports, report_result)
Script 4: Client main.py (time fix + panel)
Let me plan carefully.
________________________________________
Server models.py
Add:
python
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

