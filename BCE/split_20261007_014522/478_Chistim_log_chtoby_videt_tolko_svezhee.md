<!-- Часть 478 из 1409 -->
# Чистим лог, чтобы видеть только свежее
*Хлебные крошки:* Чистим лог, чтобы видеть только свежее

[◀ Чистим лог, чтобы видеть только свежее](477_Chistim_log_chtoby_videt_tolko_svezhee.md) | [Оглавление](00_BCE_INDEX.md) | [Добавляем CalendarDay в models.py ▶](479_Dobavlyaem_CalendarDay_v_models_py.md)

---

# Чистим лог, чтобы видеть только свежее
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

python -m client.main
Параллельно во втором окне PowerShell:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Что важно увидеть:
text
tracker.config INFO Loaded .env from D:\tracker\client\.env        ? .env найден
tracker.http Using CA bundle: ...
tracker.http Pinning DISABLED
tracker.sync SyncWorker started; server=https://127.0.0.1          ? правильный URL
tracker.sync Server reachable (HTTP 200)
На панели клиента — ? онлайн зелёным.
________________________________________
Если снова «офлайн»
Пришлите мне одним сообщением:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 20 -Encoding UTF8
Этого достаточно — я увижу, читается ли .env (строка Loaded .env from ...) и какой URL используется.
________________________________________
Что мы починили
Корень проблемы: клиент запускался из D:\tracker (Path.cwd() = корень проекта), а в config.py первым в списке кандидатов был Path.cwd() / ".env". В корне лежит серверный .env — с SECRET_ENCRYPTION_KEY, ADMIN_API_KEY, но без TRACKER_SERVER_URL. Клиент читал его, не находил URL и падал в дефолт https://tracker.example.com ? getaddrinfo failed.
Что сделали: переписали config.py так, что приоритет — у client/.env (рядом с самим файлом), а .env в текущей директории больше не ищется.
________________________________________
Запускайте проверку выше, потом клиент. Пришлите лог — и переходим к Подблоку C (календарь + PDF).
Этот ответ сгенерирован AI, только для справки.
(.venv) PS D:\tracker> cd D:\tracker >> client\.venv\Scripts\Activate.ps1 >> python -m client.main (.venv) PS D:\tracker> Get-Content "$env:APPDATA\Tracker\client.log" -Tail 20 -Encoding UTF8 2026-09-17 22:57:52,761 INFO tracker.http Using CA bundle: C:\Users\erohin\AppData\Roaming\Tracker\ca.pem 2026-09-17 22:57:52,763 WARNING tracker.http Pinning DISABLED 2026-09-17 22:57:54,025 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/sessions "HTTP/1.1 200 OK" 2026-09-17 22:57:54,033 INFO httpx HTTP Request: GET https://127.0.0.1/api/v1/version?current=1.0.0 "HTTP/1.1 200 OK" 2026-09-17 22:57:54,052 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/sessions "HTTP/1.1 200 OK" 2026-09-17 22:57:54,178 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/records/batch "HTTP/1.1 200 OK" 2026-09-17 22:58:23,101 INFO tracker.main Work session started uid=6e49f707-657e-4bb4-95bb-6d6110551138 2026-09-17 22:58:23,149 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/sessions "HTTP/1.1 200 OK" 2026-09-17 22:58:23,171 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/records/batch "HTTP/1.1 200 OK" 2026-09-17 22:58:40,641 INFO tracker.main Work session stopped uid=6e49f707-657e-4bb4-95bb-6d6110551138 2026-09-17 22:58:40,678 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/sessions "HTTP/1.1 200 OK" 2026-09-17 22:58:40,702 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/records/batch "HTTP/1.1 200 OK" 2026-09-17 22:59:26,558 INFO tracker.main Work session started uid=792de187-fcc3-49ff-be9b-47a8fd4bfd2e 2026-09-17 22:59:26,605 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/sessions "HTTP/1.1 200 OK" 2026-09-17 22:59:26,626 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/records/batch "HTTP/1.1 200 OK" 2026-09-17 22:59:56,688 INFO httpx HTTP Request: POST https://127.0.0.1/api/v1/records/batch "HTTP/1.1 200 OK" Вроде всё ок давай приступим к следующей стадии
The user says everything is working now. They want to proceed to the next stage — Подблок C: calendar of working/non-working days + PDF report.
Let me plan this carefully:
Calendar of working/non-working days
New model CalendarDay with date, is_working, note
Migration SQL
Admin page /admin/calendar with year view, bulk generate
Auto-fill Saturdays/Sundays as non-working, plus the ability to toggle
Highlight in reports
PDF report
Add reportlab to requirements
Font with Cyrillic — need to ship DejaVuSans.ttf or use a system font
New render function _render_pdf
Button in reports form
Let me write all this out.
For the PDF, need to think about fonts. The cleanest approach:
Include DejaVuSans.ttf in the repo (server/fonts/DejaVuSans.ttf)
Or download from a known location
Or use system font via reportlab's TTFont with absolute path
The simplest that works: download DejaVuSans.ttf once and put it in the project. Let me include a script that downloads it.
Actually, a cleaner approach: use reportlab's built-in UnicodeCIDFont('Helvetica') — no, that doesn't work for Cyrillic. Need TTF.
Let me use a PowerShell script that downloads DejaVuSans.ttf from a reliable CDN into server/fonts/.
For the calendar:
Model: CalendarDay(date: Date, is_working: Bool, note: Text)
But wait — I'm using SQLAlchemy with models imported once. Need to add the model and ALTER/CREATE TABLE.
Let me structure the response:
Скрипт C1 — модели (CalendarDay) + миграция
Скрипт C2 — добавление зависимостей (reportlab + скачивание шрифта)
Скрипт C3 — патч web_admin.py (календарь + PDF)
Скрипт C4 — шаблон calendar.html
Скрипт C5 — патч report_result.html (подсветка нерабочих дней)
Скрипт C6 — патч reports.html (кнопка PDF)
Скрипт C7 — пересборка
That's a lot. Let me be careful and split logically.
Actually let me reconsider the model change. The user has already had troubles with migrations. Let me think about a simpler approach.
Approach for calendar:
Store only exceptions in a table — days that are working or non-working explicitly marked
Default rule: Sat+Sun = non-working, Mon-Fri = working
Admin can override specific dates
Actually simpler to store ALL days for the year when admin generates. But that's 365 rows per year. Not a big deal for PostgreSQL.
Let me go with: table calendar_days (date PRIMARY KEY, is_working, note).
Admin has page with a year selector
Button "Сгенерировать календарь на 2026" — creates entries for all 365 days with Sat/Sun = non-working, Mon-Fri = working
Admin can toggle individual days by clicking
Bulk-set all to working or non-working
Reports check calendar_days when deciding highlight
For reports, we add a day_type field in flat records:
working — рабочий
weekend — выходной (Сб/Вс по календарю)
holiday — нерабочий (праздник, помечен вручную)
Then in report_result.html colour-code.
I'll combine into fewer scripts to make it easier.
Let me write everything out.
For the PDF font — DejaVuSans is available at:
https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf
Or use system: C:\Windows\Fonts\arial.ttf (has Cyrillic)
Using system Arial on Windows is easiest and no download. But on Linux (Docker) Arial may not exist. Let me use a robust approach:
Try to find Arial on the system
If not found, download DejaVuSans.ttf on first run
Fallback to Helvetica if nothing works (broken Cyrillic but at least doesn't crash)
Actually, in the Docker container (python:3.11-slim), no fonts at all. So we MUST ship a TTF in the repo.
Simplest approach: put a PowerShell script that downloads DejaVuSans.ttf to server/fonts/DejaVuSans.ttf. That file gets copied into the Docker image via COPY server/ ./server/. Already working.
Let me write the download script.
DejaVuSans.ttf reliable URL:
https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip
But that's a zip. Simpler:
https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf
Or from another source. Let me use the GitHub raw URL.
Actually, let's use a more stable CDN. https://cdn.jsdelivr.net/gh/dejavu-fonts/dejavu-fonts@master/ttf/DejaVuSans.ttf — that should work.
Hmm, jsdelivr path syntax may need work. Let me use the raw.githubusercontent.com approach and hope it works. If not, user can manually download.
Fallback: on Windows, use Arial from C:\Windows\Fonts\arial.ttf.
OK let me write it.
I'll break the response into logically grouped scripts:
Скрипт C1: модели + миграция БД
Скрипт C2: requirements + шрифт
Скрипт C3: web_admin.py (полная замена с новыми функциями)
Скрипт C4: шаблоны — calendar.html + reports.html + report_result.html
Скрипт C5: пересборка
Given web_admin.py is already huge, replacing it entirely again is risky. Let me try to do patches where possible.
Actually, since we've already replaced web_admin.py multiple times, let me just do it again — it's the safest way to ensure consistency.
Let me be pragmatic and write. This will be long.
Actually — let me split this response into TWO:
This response: Calendar (модель, миграция, страница, подсветка в отчётах)
Next response: PDF-отчёт
Because PDF needs font download and its own dependencies, and it's cleaner to test each part.
Actually, no — user said "приступим к следующей стадии". Let me give them the full Подблок C in one go but grouped so they can test in stages.
Hmm, actually the message is already going to be very long. Let me be smart about it:
Скрипт C1: модель + миграция + requirements (reportlab) + скачивание шрифта
Скрипт C2: web_admin.py (полная замена — включает и календарь, и PDF)
Скрипт C3: календарь шаблон
Скрипт C4: отчет result — подсветка + PDF кнопка
Скрипт C5: пересборка
Let me write. Final answer will be long but complete.
Wait, actually I realize I should check if web_admin.py has a way to add the calendar route without replacing the whole file. Given it's already been replaced a few times and I know the structure, let me just write a complete new version — that's the most reliable.
OK writing now.
For the PDF, I need to think about what to include:
Header with period, employee(s), department(s)
Table with rows matching the current grouping
Totals at the bottom
Footer with generation time
Let me use reportlab's Table for that.
For calendar, need:
/admin/calendar?year=2026 — full year view with 12 months grid
Each day cell shows: day number, background color (working = white, weekend = yellow, holiday = red), checkbox to toggle
Bulk actions: "Сделать все будни рабочими", "Сделать все выходные нерабочими", "Сбросить к дефолту"
Note field per day (optional) — skip for now, keep it simple
Save on click (AJAX would be nice, but let's use form POST for simplicity)
Simpler approach: one form per month, submit button. That's more code but simpler UI.
Even simpler: store just exceptions in DB. Default rules:
Sat, Sun ? non-working
Mon-Fri ? working
If admin marks a specific day ? that override is stored
Wait, but I want to support "marked holidays" which requires storing specific days anyway. Let me just store all days that admin explicitly marked. Reports will use: if day in DB ? use DB value, else ? default (Sat/Sun = non-working).
Hmm, but then "bunch of holidays" would require many entries. That's fine.
Actually simplest for admin: generate the full year with defaults. Then admin can toggle individual days.
Let me do:
"Сгенерировать календарь на год" — creates 365 entries with default values
Table shows each day with a checkbox "рабочий"
Admin changes checkboxes and clicks "Сохранить" per month
Actually, saving 365 checkboxes per save is fine.
OK let me write it.
Given length constraints, I'll make the calendar UI compact — one month per row of the page, each month is a form.
Let me finalize the design:
/admin/calendar?year=2026
Top: year selector, "Сгенерировать на год" button, "Сбросить год" button
12 month cards, each with:
Grid 7 columns (Пн-Вс), 6 rows
Each cell: day number, checkbox is_working, color by type
Button "Сохранить месяц"
Actually, saving per month is a bit weird. Let me save everything at once: one big form, button "Сохранить всё" at the bottom.
Or even better — for simplicity, no separate save: each checkbox is a form of its own. Too many requests.
Compromise: one form per year, button at bottom "Сохранить весь год". On submit, form sends day_2026-01-01=on for all checked working days. Server updates them all in one go.
That's clean. Let me go with that.
Actually even simpler: each day has hidden input with date and checkbox is_working. On save, iterate all form fields.
Let me write.
OK enough planning, writing the answer now.
Note: I should keep the answer focused. Let me structure:
Короткое вступление
Скрипт C1 — модель + миграция + requirements
Скрипт C2 — скачать шрифт
Скрипт C3 — web_admin.py (полная замена)
Скрипт C4 — calendar.html
Скрипт C5 — report_result.html + reports.html
Скрипт C6 — пересборка
Проверка
That's 6+ scripts. Long but complete.
For report_result.html I'll add day_type badge. For reports.html I'll add PDF option in the format select.
Let me write.
Actually wait — I want to minimize risk. The user's had a LOT of iterations. Let me split into two responses:
Этот ответ: Календарь (модель, миграция, страница, подсветка в отчётах)
Следующий: PDF
That reduces the risk of a bug breaking everything.
Hmm, but user wants "следующая стадия". Let me just give calendar first, PDF after testing. I'll say that clearly.
Actually, let me include requirements change in one script, then calendar, then note that PDF будет в следующем. That's cleaner.
Let me be decisive: give calendar now, PDF next. Explain why.
OK writing.
Подблок C — часть 1: Календарь рабочих/нерабочих дней
PDF-отчёт отдам следующим сообщением — сначала проверим календарь и подсветку. Так безопаснее: если что-то упадёт, легче локализовать.
Что делаем
Таблица calendar_days — какие дни рабочие, какие нет
Страница /admin/calendar — просмотр года по месяцам, чекбоксы, массовые действия
Подсветка в отчётах — рабочие/выходные/праздники разными цветами
Чекбокс в Настройках «Учитывать нерабочие дни»
Логика:
По умолчанию: Пн–Пт рабочие, Сб–Вс нерабочие
Админ может переопределить любой день (например, 1 мая сделать нерабочим, или субботу сделать рабочей)
В отчётах дни подсвечиваются: рабочий — нейтрально, суббота/воскресенье — жёлтый, помеченный нерабочий — красный
________________________________________
Скрипт C1 — модель + миграция БД
powershell
$ErrorActionPreference = "Stop"
$modelsPath = "D:\tracker\server\models.py"

