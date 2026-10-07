# Сколько минут без активности — порог авто-закрытия висящей сессии

*Часть 32 из 100. Источник: `BCE.md`.*

[◀ Heartbeat каждый цикл (30 секунд) — это ок, дёшево](031_Heartbeat_kazhdyy_tsikl_30_sekund_eto_ok_deshevo.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](033_part.md)

---

# Сколько минут без активности — порог авто-закрытия висящей сессии
IDLE_CLOSE_MINUTES = 30
'@
[System.IO.File]::WriteAllText($cfgPath, $config_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/config.py перезаписан" -ForegroundColor Green

python -c "import ast; ast.parse(open(r'$cfgPath', encoding='utf-8').read()); print('  SYNTAX OK')"

Write-Host "`n--- Что теперь читается из .env ---" -ForegroundColor Cyan
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -c @"
from client.config import SERVER_URL, BASE_DIR, _loaded_from if False else None
print('  SERVER_URL =', SERVER_URL)
print('  BASE_DIR   =', BASE_DIR)
"@
Ожидаемый вывод:
text
OK  client/config.py перезаписан
  SYNTAX OK

--- Что теперь читается из .env ---
  SERVER_URL = https://127.0.0.1
  BASE_DIR   = C:\Users\erohin\AppData\Roaming\Tracker
________________________________________
Перезапуск клиента
Закройте клиент (трей ? Выход). Затем:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

# Чистим лог, чтобы видеть только свежее
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

python -m client.main
Параллельно во втором окне:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки — обратите внимание на первые три:
text
tracker.config INFO Loaded .env from D:\tracker\client\.env        ? теперь правильно
tracker.http Using CA bundle: C:\Users\erohin\AppData\Roaming\Tracker\ca.pem
tracker.http Pinning DISABLED
tracker.sync SyncWorker started; server=https://127.0.0.1          ? правильный URL
tracker.sync Server reachable (HTTP 200)
httpx HTTP Request: POST https://127.0.0.1/api/v1/heartbeat "HTTP/1.1 200 OK"
На панели клиента — «? онлайн» зелёным.
________________________________________
Проверка
Через 30 секунд после запуска:
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at, NOW() - last_seen_at AS age FROM computers ORDER BY last_seen_at DESC LIMIT 5;"
age должен быть < 1 минуты — это heartbeat.
________________________________________
Что важно понять на будущее
При запуске клиента из корня проекта D:\tracker нельзя искать .env через Path.cwd() — там лежит серверный .env. Я это теперь исправил: клиент смотрит только:
client/.env (рядом с config.py)
%APPDATA%\Tracker\.env (если кто-то положит туда)
Порядок — сначала client/.env.
Если когда-то понадобится переопределить URL — просто править client/.env, и всё.
________________________________________
После того как «онлайн» появится
Проверьте:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 15 -Encoding UTF8
Не должно быть getaddrinfo failed и 500. Должны быть 200 OK.
Затем — скажите слово, и пришлю Подблок C:
Календарь рабочих/нерабочих дней — страница /admin/calendar, автозаполнение Сб/Вс как нерабочих на год вперёд, ручная правка
Подсветка в отчётах — рабочие/нерабочие/выходные дни разными цветами
PDF-отчёт — reportlab + кириллица
Запускайте, присылайте результат.
Этот ответ сгенерирован AI, только для справки.
OK client/config.py перезаписан SYNTAX OK --- Что теперь читается из .env --- File "<string>", line 1 from client.config import SERVER_URL, BASE_DIR, _loaded_from if False else None ^^ SyntaxError: invalid syntax
Пользователь получил ошибку из моей проверочной команды. Надо исправить одну строчку и дать простой скрипт проверки.
Проблема в моём скрипте-проверке — я написал бредовое выражение _loaded_from if False else None в импорте. Надо просто убрать этот кусок.
Главное: config.py перезаписан успешно. Осталось только проверить, что он реально читает SERVER_URL = https://127.0.0.1 и запустить клиент.
Дадим короткий фикс.
Ошибка в моей проверочной команде, файл config.py записан правильно
Скрипт с from client.config import ... — это была моя ошибка в синтаксисе проверки, а не в вашем config.py. Файл config.py уже перезаписан и корректен (SYNTAX OK — это подтверждает).
Забудьте про этот неудачный тест. Проверим иначе.
________________________________________
Простая проверка config.py (правильный синтаксис)
Запустите из папки D:\tracker:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
from client import config
print('  SERVER_URL    =', config.SERVER_URL)
print('  BASE_DIR      =', config.BASE_DIR)
print('  CLIENT_VERSION=', config.CLIENT_VERSION)
"@
Ожидаемый вывод:
text
  SERVER_URL    = https://127.0.0.1
  BASE_DIR      = C:\Users\erohin\AppData\Roaming\Tracker
  CLIENT_VERSION= 1.0.0
Если увидите SERVER_URL = https://127.0.0.1 — всё правильно, .env читается.
Если увидите https://tracker.example.com — значит .env не найден, будем разбираться.
________________________________________
Запуск клиента
Закройте старый клиент (трей ? Выход), затем:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

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

# Добавляем CalendarDay в models.py
$content = [System.IO.File]::ReadAllText($modelsPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("class CalendarDay")) {
    Write-Host "Модель CalendarDay уже есть" -ForegroundColor Yellow
} else {
    $addition = @'


class CalendarDay(Base):
    """Календарь рабочих/нерабочих дней.

    По умолчанию (если записи нет): Пн-Пт — рабочие, Сб-Вс — нерабочие.
    Если запись есть — используется её значение is_working.
    """
    __tablename__ = "calendar_days"

    day = Column(String(10), primary_key=True)   # ISO YYYY-MM-DD
    is_working = Column(Boolean, nullable=False, default=True)
    note = Column(String(255))
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
'@
    $content = $content + $addition
    [System.IO.File]::WriteAllText($modelsPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  CalendarDay добавлен в models.py" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$modelsPath', encoding='utf-8').read()); print('  SYNTAX OK')"

# Миграция БД
Write-Host "`n--- Миграция БД ---" -ForegroundColor Cyan
cd D:\tracker
docker compose up -d db
Start-Sleep -Seconds 5

docker compose exec -T db psql -U tracker -d tracker -c @"
CREATE TABLE IF NOT EXISTS calendar_days (
    day VARCHAR(10) PRIMARY KEY,
    is_working BOOLEAN NOT NULL DEFAULT TRUE,
    note VARCHAR(255),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"@

Write-Host "OK  таблица calendar_days" -ForegroundColor Green
________________________________________
Скрипт C2 — requirements.txt + шрифт для PDF
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

# --- requirements.txt: добавить reportlab ---
$reqPath = "$serverDir\requirements.txt"
$req = [System.IO.File]::ReadAllText($reqPath, [System.Text.UTF8Encoding]::new($false))

if ($req -notmatch "reportlab") {
    $req = $req.TrimEnd() + "`nreportlab==4.2.2`n"
    [System.IO.File]::WriteAllText($reqPath, $req, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  reportlab добавлен в requirements.txt" -ForegroundColor Green
} else {
    Write-Host "reportlab уже есть" -ForegroundColor Yellow
}

Get-Content $reqPath

# --- Скачиваем DejaVuSans.ttf для PDF ---
Write-Host "`n--- Шрифт для PDF ---" -ForegroundColor Cyan
$fontsDir = "$serverDir\fonts"
New-Item -ItemType Directory -Force -Path $fontsDir | Out-Null

$fontFile = "$fontsDir\DejaVuSans.ttf"
if (Test-Path $fontFile) {
    Write-Host "Шрифт уже есть: $fontFile" -ForegroundColor Yellow
} else {
    # Пробуем несколько источников
    $urls = @(
        "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
        "https://cdn.jsdelivr.net/gh/dejavu-fonts/dejavu-fonts@master/ttf/DejaVuSans.ttf"
    )
    $ok = $false
    foreach ($u in $urls) {
        try {
            Write-Host "  Пробуем: $u"
            Invoke-WebRequest -Uri $u -OutFile $fontFile -UseBasicParsing -ErrorAction Stop
            $ok = $true
            Write-Host "  OK  скачали из $u" -ForegroundColor Green
            break
        } catch {
            Write-Host "  не вышло: $_" -ForegroundColor Yellow
        }
    }

    if (-not $ok) {
        Write-Host "  Не удалось скачать DejaVuSans.ttf. Пробуем взять системный Arial…" -ForegroundColor Yellow
        $winFont = "$env:WINDIR\Fonts\arial.ttf"
        if (Test-Path $winFont) {
            Copy-Item $winFont $fontFile -Force
            Write-Host "  OK  скопирован $winFont ? $fontFile" -ForegroundColor Green
        } else {
            Write-Host "  ВНИМАНИЕ: шрифта нет. PDF будет с квадратиками." -ForegroundColor Red
        }
    }

    if (Test-Path $fontFile) {
        $size = (Get-Item $fontFile).Length
        Write-Host "  Размер: $size байт"
    }
}
________________________________________
Скрипт C3 — патч web_admin.py (календарь)
Добавляем функции и роуты календаря в существующий web_admin.py. Ничего не удаляем.
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("@router.get(\"/calendar\"")) {
    Write-Host "Календарь уже добавлен — пропускаем" -ForegroundColor Yellow
} else {
    # Импорт CalendarDay
    if ($content -notmatch "CalendarDay") {
        $content = $content.Replace(
            "    AppSetting, AuditLog, BootstrapToken, Computer, Department,",
            "    AppSetting, AuditLog, BootstrapToken, CalendarDay, Computer, Department,"
        )
    }

    # Добавляем блок календаря перед "Аудит"
    $calendarBlock = @'

# ============================================================
# Календарь рабочих/нерабочих дней
# ============================================================

def _get_calendar_map(db: Session, year: int) -> dict:
    """Возвращает {date_iso: is_working} для указанного года."""
    rows = db.query(CalendarDay).filter(
        CalendarDay.day.like(f"{year:04d}-%")
    ).all()
    return {r.day: r.is_working for r in rows}


def _is_working_day(db: Session, d: date) -> bool:
    """Рабочий ли день. Если записи нет — дефолт: Пн-Пт = рабочий."""
    row = db.query(CalendarDay).filter(CalendarDay.day == d.isoformat()).first()
    if row is not None:
        return row.is_working
    return d.weekday() < 5


def _day_type(db: Session, d: date) -> str:
    """Тип дня: 'working', 'weekend', 'holiday'."""
    row = db.query(CalendarDay).filter(CalendarDay.day == d.isoformat()).first()
    if row is not None:
        if not row.is_working:
            # Если это Сб/Вс и нерабочий — 'weekend', иначе 'holiday'
            if d.weekday() >= 5:
                return "weekend"
            return "holiday"
        return "working"
    if d.weekday() >= 5:
        return "weekend"
    return "working"


@router.get("/calendar", response_class=HTMLResponse)
def calendar_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    now = datetime.now()
    try:
        year = int(request.query_params.get("year", str(now.year)))
        year = max(2020, min(2100, year))
    except (ValueError, TypeError):
        year = now.year

    cal = _get_calendar_map(db, year)

    # Собираем 12 месяцев
    months = []
    for m in range(1, 13):
        first = date(year, m, 1)
        if m == 12:
            last = date(year, 12, 31)
        else:
            last = date(year, m + 1, 1) - timedelta(days=1)

        # Пн=0 ... Вс=6, но в отображении — Пн первый столбец
        # Находим первый понедельник (или нужный день месяца)
        days_in_month = (last - first).days + 1
        # weekday: Пн=0 … Вс=6
        start_offset = first.weekday()  # сколько пустых ячеек до 1-го числа

        cells = []
        for _ in range(start_offset):
            cells.append(None)
        for day_num in range(1, days_in_month + 1):
            d = date(year, m, day_num)
            iso = d.isoformat()
            is_working = cal.get(iso)
            if is_working is None:
                is_working = d.weekday() < 5
            cells.append({
                "date": d,
                "iso": iso,
                "is_working": is_working,
                "weekday": d.weekday(),
            })
        # Добиваем до конца недели
        while len(cells) % 7 != 0:
            cells.append(None)

        # Разбиваем на недели
        weeks = [cells[i:i+7] for i in range(0, len(cells), 7)]

        months.append({
            "num": m,
            "name": RU_MONTHS[m],
            "weeks": weeks,
        })

    # Итоги года
    total_days = (date(year, 12, 31) - date(year, 1, 1)).days + 1
    working_days = sum(
        1 for i in range(total_days)
        if _is_working_day(db, date(year, 1, 1) + timedelta(days=i))
    )

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "admin": request.session.get("admin"),
        "year": year,
        "months": months,
        "weekday_names": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "working_days": working_days,
        "total_days": total_days,
        "saved": request.query_params.get("saved") == "1",
        "years": list(range(now.year - 2, now.year + 3)),
    })


@router.post("/calendar/save")
async def calendar_save(request: Request,
                        db: Session = Depends(get_db), _=Depends(current_admin)):
    """Сохраняет отмеченные рабочие дни для указанного года."""
    form = await request.form()
    year = int(form.get("year", 0))
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")

    # Собираем: какие дни отмечены is_working
    checked_isos = set()
    for k, v in form.multi_items():
        # Имена чекбоксов: day_YYYY-MM-DD
        if k.startswith("day_") and k[4:].startswith(f"{year:04d}-"):
            checked_isos.add(k[4:])

    # Обходим все дни года и обновляем/создаём записи
    cur_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    while cur_date <= end_date:
        iso = cur_date.isoformat()
        is_working_default = cur_date.weekday() < 5
        is_working_new = iso in checked_isos

        row = db.query(CalendarDay).filter(CalendarDay.day == iso).first()

        # Оптимизация: если значение совпадает с дефолтом и записи нет — не создаём
        if row is None and is_working_new == is_working_default:
            cur_date += timedelta(days=1)
            continue

        if row is None:
            db.add(CalendarDay(day=iso, is_working=is_working_new))
        else:
            row.is_working = is_working_new

        cur_date += timedelta(days=1)

    db.add(AuditLog(actor="admin", entity="calendar", entity_id=str(year),
                    action="save"))
    db.commit()
    return RedirectResponse(f"/admin/calendar?year={year}&saved=1", status_code=303)


@router.post("/calendar/generate")
def calendar_generate(year: int = Form(...), db: Session = Depends(get_db),
                      _=Depends(current_admin)):
    """Заполняет год по дефолту: Сб/Вс нерабочие."""
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")
    cur = date(year, 1, 1)
    end = date(year, 12, 31)
    while cur <= end:
        iso = cur.isoformat()
        row = db.query(CalendarDay).filter(CalendarDay.day == iso).first()
        is_working = cur.weekday() < 5
        if row is None:
            db.add(CalendarDay(day=iso, is_working=is_working))
        else:
            row.is_working = is_working
        cur += timedelta(days=1)
    db.add(AuditLog(actor="admin", entity="calendar", entity_id=str(year),
                    action="generate"))
    db.commit()
    return RedirectResponse(f"/admin/calendar?year={year}&saved=1", status_code=303)


@router.post("/calendar/reset")
def calendar_reset(year: int = Form(...), db: Session = Depends(get_db),
                   _=Depends(current_admin)):
    """Удаляет все записи за год ? возвращаемся к дефолту."""
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")
    db.query(CalendarDay).filter(CalendarDay.day.like(f"{year:04d}-%")).delete(
        synchronize_session=False)
    db.add(AuditLog(actor="admin", entity="calendar", entity_id=str(year),
                    action="reset"))
    db.commit()
    return RedirectResponse(f"/admin/calendar?year={year}&saved=1", status_code=303)


# ============================================================
# Аудит
# ============================================================
'@

    # Находим маркер "# ============================================================\n# Аудит"
    $marker = @"
# ============================================================
# Аудит
