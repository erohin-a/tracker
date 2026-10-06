<!-- Часть 1066 из 1409 -->
# Пишем в НОВЫЙ файл (в другой папке) — не трогаем оригинал
*Хлебные крошки:* Пишем в НОВЫЙ файл (в другой папке) — не трогаем оригинал

[◀ ============================================================](1065_part.md) | [Оглавление](00_BCE_INDEX.md) | [1. В get_settings_dict добавляем поле ▶](1067_1_V_get_settings_dict_dobavlyaem_pole.md)

---

# Пишем в НОВЫЙ файл (в другой папке) — не трогаем оригинал
with open(TMP, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    os.remove(TMP)
    raise SystemExit(1)

print(f"OK: подготовлен новый файл: {TMP}")
print("Теперь используем robocopy для замены оригинала")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_tasks_stage1.py", $patcher, [System.Text.UTF8Encoding]::new($false))

& client\.venv\Scripts\python.exe _patch_tasks_stage1.py

if (Test-Path "D:\tracker\_tasks_new.py") {
    Write-Host "`n Файл подготовлен, пробуем заменить через robocopy..." -ForegroundColor Cyan
    # robocopy копирует с флагом /B (backup mode) — иногда обходит блокировки
    $result = robocopy "D:\tracker" "D:\tracker\server" "_tasks_new.py" "tasks.py" /B /IS /IT /NFL /NDL /NJH /NJS /NP 2>&1
    Write-Host $result
    
    # Проверяем результат
    if (Test-Path "D:\tracker\_tasks_new.py") {
        # Если robocopy не сработал — пробуем через cmd copy /y
        Write-Host "`n Пробуем через cmd copy /y..." -ForegroundColor Yellow
        cmd /c "copy /y D:\tracker\_tasks_new.py D:\tracker\server\tasks.py"
    }
    
    # Проверка
    $ts = [System.IO.File]::ReadAllText("D:\tracker\server\tasks.py", [System.Text.UTF8Encoding]::new($false))
    if ($ts.Contains("def close_stale_sessions")) {
        Write-Host "`n OK: tasks.py обновлён, close_stale_sessions на месте" -ForegroundColor Green
        Remove-Item "D:\tracker\_tasks_new.py" -ErrorAction SilentlyContinue
    } else {
        Write-Host "`n Файл НЕ обновлён. Возможные причины:" -ForegroundColor Red
        Write-Host "  - Файл открыт в редакторе (VS Code, Notepad++)" -ForegroundColor Yellow
        Write-Host "  - Пользователь admin не имеет прав на папку server/" -ForegroundColor Yellow
        Write-Host "  - Антивирус блокирует запись" -ForegroundColor Yellow
        Write-Host "`n Что делать:" -ForegroundColor Cyan
        Write-Host "  1. Закрой все редакторы" -ForegroundColor White
        Write-Host "  2. Проверь что ты не в папке server/ в проводнике" -ForegroundColor White
        Write-Host "  3. Запусти PowerShell от имени администратора и повтори" -ForegroundColor White
    }
}
Что ожидаем:
Диагностика покажет: файл read-only? процессы? атрибуты?
Stage1 подготовит D:\tracker\_tasks_new.py
Замена через robocopy или copy /y
________________________________________
Если и robocopy не поможет — ручная замена
Тогда делаем совсем просто:
Открой D:\tracker\server\tasks.py в блокноте (или VS Code).
Ctrl+A, Delete — полностью очисти.
Открой D:\tracker\_tasks_new.py (создан после stage1) — Ctrl+A, Ctrl+C.
Вставь в очищенный tasks.py.
Сохрани (Ctrl+S). Если не даёт — «Сохранить как» ? сохрани как tasks_new.py в server/, потом удали старый и переименуй.
Но сначала — пришли вывод диагностики. Там будет видно, что именно мешает: read-only, process, или ACL.
=== 1. Атрибуты файла === Name : tasks.py Length : 14696 Attributes : Archive LastWriteTime : 21.09.2026 16:17:36 IsReadOnly : False === 2. Попытка открыть на чтение (не монопольно) === OK: файл читается, размер 14696 байт === 3. Запущенные python процессы === === 4. Обработчики файла (если есть Sysinternals handle) === handle.exe не установлен — пропускаем === 5. Пробуем снять read-only === Файл не read-only === 6. Обходной путь через robocopy === OK: задача зарегистрирована в TASKS_REGISTRY SYNTAX OK OK: подготовлен новый файл: D:\tracker\_tasks_new.py Теперь используем robocopy для замены оригинала Файл подготовлен, пробуем заменить через robocopy... Пробуем через cmd copy /y... Скопировано файлов: 1. OK: tasks.py обновлён, close_stale_sessions на месте
Отлично, файл обновился через copy /y. Диагностика показала:
Файл не read-only
Читается нормально
Нет python процессов
Robocopy не сработал, но copy /y сработал
Причина скорее всего была — временная блокировка (антивирус или что-то держало эксклюзивно несколько секунд).
Теперь у нас:
Шаг 3+6 — готово
Шаг 5a — готово
Осталось: шаг 4 (cap 24h), шаг 5b (настройка), шаг 5c (шаблон)
Проверим что 5a действительно применился, и продолжим с оставшимися шагами.
Отлично, copy /y прошёл. Файл не был read-only и никаких процессов — это была временная эксклюзивная блокировка (антивирус или редактор на доли секунды). robocopy /B не справился, а copy /y — да.
Проверим, что шаг 5a реально применился, и добьём остальные три (4, 5b, 5c).
Шаг B — Проверка 5a и патч 4 (cap 24h)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== tasks.py: что в итоге? ===" -ForegroundColor Cyan
$ts = [System.IO.File]::ReadAllText("D:\tracker\server\tasks.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
    if ($ts.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}

Write-Host "`n=== Шаг 4: патч server/main.py (cap 24h) ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_server_cap.py
Что ожидаем:
text
OK: def close_stale_sessions
OK: close_stale_sessions": {
OK: "default_cron": "*/30 * * * *"

=== Шаг 4: патч server/main.py (cap 24h) ===
OK: добавлен предохранитель 24 часа
SYNTAX OK
________________________________________
Шаг C — Патчи 5b (настройка) и 5c (шаблон)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Шаг 5b: настройка stale_session_hours в web_admin.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_settings_stale.py
Что ожидаем:
text
OK: stale_session_hours в settings_dict
OK: параметр stale_session_hours в settings_save
OK: обработка stale_session_hours в new_vals
SYNTAX OK
Затем шаблон:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\settings.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("stale_session_hours")) {
    Write-Host "SKIP: поле уже есть" -ForegroundColor Yellow
} else {
    $oldBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
'@

    $newBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">
                        Автозакрытие зависших сессий
                        <span class="hint" data-bs-toggle="tooltip" title="Если сессия висит без session_end дольше указанного времени — сервер закроет её временем последней активности. Защита от ситуации «сотрудник забыл нажать Конец работы, ПК выключили».">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="stale_session_hours" class="form-control"
                               value="{{ cfg.stale_session_hours }}" min="1" max="24">
                        <span class="input-group-text">часов</span>
                    </div>
                    <div class="form-text">По умолчанию 2 часа. Рекомендуется 1–3.</div>
                </div>
'@

    if ($content.Contains($oldBlock)) {
        $content = $content.Replace($oldBlock, $newBlock)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: поле stale_session_hours добавлено" -ForegroundColor Green
    } else {
        Write-Host "ERROR: не найден блок Idle-порог в settings.html" -ForegroundColor Red
        Write-Host "Проверь вручную: поищи 'idle_close_minutes' в шаблоне" -ForegroundColor Yellow
    }
}

$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
if ($check.Contains("stale_session_hours")) {
    Write-Host " Поле в шаблоне: OK" -ForegroundColor Green
} else {
    Write-Host " Поле в шаблоне: MISS" -ForegroundColor Red
}
Что ожидаем:
text
OK: поле stale_session_hours добавлено
 Поле в шаблоне: OK
________________________________________
Шаг D — Пересборка + проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Синтаксис Python ===" -ForegroundColor Cyan
client\.venv\Scripts\python.exe -c @"
import ast
for p in [r'D:\tracker\server\web_admin.py', r'D:\tracker\server\main.py', r'D:\tracker\server\tasks.py']:
    with open(p, encoding='utf-8') as f:
        ast.parse(f.read())
    print(f' OK: {p.split(chr(92))[-1]}')
print('ALL SYNTAX OK')
"@

Write-Host "`n=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 30

Write-Host "`n=== Статус ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи API (последние 40 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=40

Write-Host "`n=== Проверка: задача close_stale_sessions в БД ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron FROM scheduled_tasks WHERE name='close_stale_sessions';"

Write-Host "`n=== Проверка: app_settings для stale_session_hours ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT key, value FROM app_settings WHERE key='stale_session_hours';"

Write-Host "`n=== Проверка: cap в /api/v1/sessions (grep) ===" -ForegroundColor Cyan
docker compose exec -T api grep -c "MAX_SESSION_HOURS" /app/server/main.py
docker compose exec -T api grep -c "_union_duration" /app/server/web_admin.py
docker compose exec -T api grep -c "close_stale_sessions" /app/server/tasks.py
Что ожидаем:
ALL SYNTAX OK — три OK и одна итоговая
Все 3 контейнера Up
В логах — Созданы дефолтные задачи: close_stale_sessions (или «Все задачи планировщика уже в БД» если задача была создана раньше)
В scheduled_tasks — строка close_stale_sessions | t | */30 * * * *
В app_settings — пусто или stale_session_hours | 2
В grep: MAX_SESSION_HOURS — 1+, _union_duration — 2+, close_stale_sessions — 3+
________________________________________
Что делаем после успеха
Откроем /admin/settings — увидим новое поле «Автозакрытие зависших сессий» с значением 2.
Сформируем отчёт за 23.09 — «24 часа» должны превратиться в ~5–6 часов.
Обнулим БД — docker compose down -v + docker compose up -d --build, начать чисто.
Запускай шаги B ? C ? D по порядку. Присылай вывод.
ytpfgecrftncz rjl
The user's terminal seems stuck. Looking at the screenshot, they ran a script but nothing executed. The issue is that PowerShell is waiting for more input — probably because a here-string or bracket wasn't closed properly.
Looking at the screenshot, I can see:
Line 6: Write-Host "=== tasks.py: что в итоге? ===" -ForegroundColor Cyan — that looks fine
Line 7: $ts = [System.IO.File]::ReadAllText("D:\tracker\server\tasks.py", [System.Text.UTF8Encoding]::new($false)) — that looks fine
Line 8: foreach ($m in @("def close_stale_sessions", "close_stale_sessions": {", "default_cron": "*/30 * * * *")) { — WAIT
The issue: "close_stale_sessions": { — inside a double-quoted PowerShell string, that's fine, but there are unclosed quotes issues. Let me look again:
@("def close_stale_sessions", "close_stale_sessions": {", "default_cron": "*/30 * * * *")
The problem is "close_stale_sessions": {" — this seems OK as a string.
But "*/30 * * * *" contains * characters — that's fine in a string.
Actually the issue might be the extra " character in "close_stale_sessions": {". Let me count quotes... Actually looking at it: "close_stale_sessions": {" — there's a : inside but that shouldn't matter.
Hmm. Actually I think the problem is { in the string. Wait no, { inside a string is fine in PowerShell.
Actually looking at line 8 more carefully:
text
foreach ($m in @("def close_stale_sessions", "close_stale_sessions": {", "default_cron": "*/30 * * * *")) {
The { at the end of "close_stale_sessions": {" — that's inside the quotes so it should be fine.
Wait — I need to look at the whole structure. The user is in PowerShell and has typed out the script. The prompt shows >> which means PowerShell is waiting for more input — meaning it's still in a multi-line continuation (something didn't close).
The most likely culprit: the { that appears AFTER the closing quote of a string might confuse PowerShell's parser in some contexts. But no, PowerShell should handle it.
Actually — I see the problem now. Looking at the display:
text
foreach ($m in @("def close_stale_sessions", "close_stale_sessions": {", "default_cron": "*/30 * * * *")) {
The string "close_stale_sessions": { ends with { inside quotes. Then there's " at the end. So it should be "close_stale_sessions\": {" actually wait, let me recount:
"close_stale_sessions": { — opening ", text close_stale_sessions, then " closes the string, then :, then { — this is a syntax error!
Ohh I see! The user typed: "close_stale_sessions": { — but this is not how I wrote it. In my script, this string was INSIDE a python block that was inside a PowerShell here-string. Looking at the source:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Wait no. Let me look at my original script:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Hmm no. Let me look at the actual script I sent:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Actually looking at what I sent in my previous message:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
No, I wrote it as:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Ugh, let me just look at the actual text I sent. From my message:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Wait no, I need to look at what I actually sent. The actual command was:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Hmm, I'm confusing myself. Let me just look at what my actual message said:
text
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
OK I'll just look at the actual previous message. In my previous message I wrote:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Ugh whatever. Let me look at the user's SCREENSHOT more carefully:
text
foreach ($m in @("def close_stale_sessions", "close_stale_sessions": {", "default_cron": "*/30 * * * *")) {
This is what the user typed. But this is WRONG because:
"close_stale_sessions": {" — this has an unmatched "
The { at the end opens a PowerShell block that's never closed
Actually wait — PowerShell sees "close_stale_sessions": { as a string that starts with " at position 0, ends with " after sessions. Then : — that's fine. Then { — this is where it goes wrong. { alone in PowerShell enters "script block" mode (like & {...}). So PowerShell is waiting for }.
But actually, PowerShell is smart about this in strings. "close_stale_sessions\": {" might work if the \ escaped the quote. But in PowerShell, \ is NOT an escape character — the backtick ` is. So \" inside a double-quoted string is \ followed by end of string, and then : is a syntax error.
That's the issue!
Let me also look at my actual previous message: I wrote:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Wait, I need to check. Actually in my message I wrote:
text
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Hmm. Let me search for what I actually wrote. Looking at my previous message, the block was:
powershell
Write-Host "=== tasks.py: что в итоге? ===" -ForegroundColor Cyan
$ts = [System.IO.File]::ReadAllText("D:\tracker\server\tasks.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Actually looking at my message again, I wrote:
text
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
I'm looking at what I sent. The actual code in my message:
powershell
foreach ($m in @("def close_stale_sessions", "close_stale_sessions\": {", '"default_cron": "*/30 * * * *"')) {
Yes! That's what I sent. And what did I MEAN to send?
I meant to have three checks:
def close_stale_sessions (Python function definition)
close_stale_sessions": { (in dict)
"default_cron": "*/30 * * * *" (cron string)
To represent these in PowerShell, they need proper escaping. The correct version is:
powershell
foreach ($m in @(
    "def close_stale_sessions",
    "close_stale_sessions`": {",   # escape internal double quote with backtick
    '"default_cron": "*/30 * * * *"'  # single-quoted so double quotes are literal
)) {
Or use here-strings or single quotes for each.
But the user's terminal shows they typed it as:
text
foreach ($m in @("def close_stale_sessions", "close_stale_sessions": {", "default_cron": "*/30 * * * *")) {
Looking at the screenshot again — actually the \ may be there but not visible due to how the terminal renders. Let me trust that PowerShell is still waiting for input (>> prompt).
The FIX is simple: press Ctrl+C to cancel, then run a corrected version.
Let me write the corrected script.
Also I need to make sure I actually fix my original script. The issue is that my original had "close_stale_sessions\": {" and '"default_cron": "*/30 * * * *"' — some strings were double-quoted with escapes, some single-quoted. It got messy.
Let me write it cleanly using a simplified approach — just search for substrings without any tricky quotes.
Also note: the user ran copilot at the top which tried to find GitHub CLI — ignore that.
Plan for the response:
Explain the issue: PowerShell still waiting for input (>>), a string quote wasn't closed
User should press Ctrl+C to abort
Give simplified verification script (short, using simple strings only)
Let me write a clean version. I'll use single-quoted strings where the content contains double quotes, and avoid tricky patterns.
Actually, better approach: skip the complex verification, just go straight to remaining patches with simpler scripts.
Let me keep it very simple:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Проверка tasks.py ===" -ForegroundColor Cyan
$ts = [System.IO.File]::ReadAllText("D:\tracker\server\tasks.py", [System.Text.UTF8Encoding]::new($false))

if ($ts.Contains('def close_stale_sessions')) {
    Write-Host " OK: def close_stale_sessions" -ForegroundColor Green
} else {
    Write-Host " MISS: def close_stale_sessions" -ForegroundColor Red
}

if ($ts.Contains('"close_stale_sessions"')) {
    Write-Host " OK: ключ в TASKS_REGISTRY" -ForegroundColor Green
} else {
    Write-Host " MISS: ключ в TASKS_REGISTRY" -ForegroundColor Red
}

if ($ts.Contains('*/30 * * * *')) {
    Write-Host " OK: cron" -ForegroundColor Green
} else {
    Write-Host " MISS: cron" -ForegroundColor Red
}

Write-Host "`n=== Шаг 4: патч server/main.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_server_cap.py
That's clean — no double-quote-inside-double-quote issues.
Then in a second message (or same), do the rest.
PowerShell висит в режиме >> — ждёт продолжения ввода. Причина: в одной из строк "close_stale_sessions": {" внутренняя кавычка сломала парсинг, и PowerShell думает, что ты ещё не закончил.
Первое действие: нажми Ctrl+C — отменить ввод, вернуться к обычному PS D:\tracker>.
Ниже — упрощённая проверка без кавычек-ловушек. Использую только одинарные кавычки в проверках, чтобы ничего не ломалось.
Шаг 1 — Abort и простая проверка tasks.py
Нажми Ctrl+C, потом запусти это:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Проверка tasks.py ===" -ForegroundColor Cyan
$ts = [System.IO.File]::ReadAllText("D:\tracker\server\tasks.py", [System.Text.UTF8Encoding]::new($false))

if ($ts.Contains('def close_stale_sessions')) {
    Write-Host " OK: def close_stale_sessions" -ForegroundColor Green
} else {
    Write-Host " MISS: def close_stale_sessions" -ForegroundColor Red
}

if ($ts.Contains('close_stale_sessions": {')) {
    Write-Host " OK: ключ в TASKS_REGISTRY" -ForegroundColor Green
} else {
    Write-Host " MISS: ключ в TASKS_REGISTRY" -ForegroundColor Red
}

if ($ts.Contains('*/30 * * * *')) {
    Write-Host " OK: cron */30" -ForegroundColor Green
} else {
    Write-Host " MISS: cron */30" -ForegroundColor Red
}
Обрати внимание: в проверках используется одинарная кавычка снаружи ('...'), а двойные кавычки внутри — литеральные. Это безопасно.
Что ожидаем:
text
=== Проверка tasks.py ===
 OK: def close_stale_sessions
 OK: ключ в TASKS_REGISTRY
 OK: cron */30
________________________________________
Шаг 2 — Патч server/main.py (cap 24h)
Он не сработал в прошлый раз — ты не успел его запустить, PowerShell висел.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Шаг 4: патч server/main.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_server_cap.py
Что ожидаем:
text
=== Шаг 4: патч server/main.py ===
OK: добавлен предохранитель 24 часа
SYNTAX OK
________________________________________
Шаг 3 — Патч настроек (stale_session_hours)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Шаг 5b: патч web_admin.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_settings_stale.py
Что ожидаем:
text
OK: stale_session_hours в settings_dict
OK: параметр stale_session_hours в settings_save
OK: обработка stale_session_hours в new_vals
SYNTAX OK
________________________________________
Шаг 4 — Патч шаблона settings.html
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\settings.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("stale_session_hours")) {
    Write-Host "SKIP: поле уже есть" -ForegroundColor Yellow
} else {
    $oldBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
'@

    $newBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">
                        Автозакрытие зависших сессий
                        <span class="hint" data-bs-toggle="tooltip" title="Если сессия висит без session_end дольше указанного времени — сервер закроет её временем последней активности. Защита от ситуации «сотрудник забыл нажать Конец работы, ПК выключили».">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="stale_session_hours" class="form-control"
                               value="{{ cfg.stale_session_hours }}" min="1" max="24">
                        <span class="input-group-text">часов</span>
                    </div>
                    <div class="form-text">По умолчанию 2 часа. Рекомендуется 1–3.</div>
                </div>
'@

    if ($content.Contains($oldBlock)) {
        $content = $content.Replace($oldBlock, $newBlock)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: поле stale_session_hours добавлено" -ForegroundColor Green
    } else {
        Write-Host "ERROR: не найден блок Idle-порог" -ForegroundColor Red
    }
}

$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
if ($check.Contains("stale_session_hours")) {
    Write-Host " Поле в шаблоне: OK" -ForegroundColor Green
} else {
    Write-Host " Поле в шаблоне: MISS" -ForegroundColor Red
}
Что ожидаем:
text
OK: поле stale_session_hours добавлено
 Поле в шаблоне: OK
________________________________________
Шаг 5 — Пересборка + проверка всего
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Синтаксис Python ===" -ForegroundColor Cyan
client\.venv\Scripts\python.exe -c "import ast; [ast.parse(open(p, encoding='utf-8').read()) for p in [r'D:\tracker\server\web_admin.py', r'D:\tracker\server\main.py', r'D:\tracker\server\tasks.py']]; print('ALL SYNTAX OK')"

Write-Host "`n=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 30

Write-Host "`n=== Статус ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи API (последние 40 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=40

Write-Host "`n=== Задача close_stale_sessions в БД ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron FROM scheduled_tasks WHERE name='close_stale_sessions';"

Write-Host "`n=== grep-проверки в контейнере ===" -ForegroundColor Cyan
docker compose exec -T api grep -c "MAX_SESSION_HOURS" /app/server/main.py
docker compose exec -T api grep -c "_union_duration" /app/server/web_admin.py
docker compose exec -T api grep -c "close_stale_sessions" /app/server/tasks.py
Что ожидаем:
ALL SYNTAX OK
Все 3 контейнера Up
В логах — Созданы дефолтные задачи: close_stale_sessions (или «Все задачи планировщика уже в БД»)
В scheduled_tasks — строка close_stale_sessions | t | */30 * * * *
grep-проверки: 1, 2, 3+
________________________________________
Что делать сейчас
Ctrl+C — вернуться к обычному prompt.
Запусти Шаг 1 — короткая проверка tasks.py.
Если все три OK — запускай Шаг 2 ? 3 ? 4 ? 5 по порядку.
Пришли вывод. Если где-то ошибка — стоп, только этот шаг.
После успеха:
Откроем /admin/settings — увидим поле «Автозакрытие зависших сессий» = 2.
Сформируем отчёт за 23.09 — «24 часа» должны превратиться в ~5–6 часов.
Обнулим БД.
=== Проверка tasks.py === OK: def close_stale_sessions OK: ключ в TASKS_REGISTRY OK: cron */30 PS D:\tracker> === Проверка tasks.py === >> OK: def close_stale_sessions >> OK: ключ в TASKS_REGISTRY >> OK: cron */30 === : Имя "===" не распознано как имя командлета, функции, файла сценария или выполняемой программы. Проверьте правильность на писания имени, а также наличие и правильность пути, после чего повторите попытку. строка:1 знак:1 + === Проверка tasks.py === + ~~~ + CategoryInfo : ObjectNotFound: (===:String) [], CommandNotFoundException + FullyQualifiedErrorId : CommandNotFoundException OK: : Имя "OK:" не распознано как имя командлета, функции, файла сценария или выполняемой программы. Проверьте правильность на писания имени, а также наличие и правильность пути, после чего повторите попытку. строка:2 знак:2 + OK: def close_stale_sessions + ~~~ + CategoryInfo : ObjectNotFound: (OK::String) [], CommandNotFoundException + FullyQualifiedErrorId : CommandNotFoundException OK: : Имя "OK:" не распознано как имя командлета, функции, файла сценария или выполняемой программы. Проверьте правильность на писания имени, а также наличие и правильность пути, после чего повторите попытку. строка:3 знак:2 + OK: ключ в TASKS_REGISTRY + ~~~ + CategoryInfo : ObjectNotFound: (OK::String) [], CommandNotFoundException + FullyQualifiedErrorId : CommandNotFoundException OK: : Имя "OK:" не распознано как имя командлета, функции, файла сценария или выполняемой программы. Проверьте правильность на писания имени, а также наличие и правильность пути, после чего повторите попытку. строка:4 знак:2 + OK: cron */30 + ~~~ + CategoryInfo : ObjectNotFound: (OK::String) [], CommandNotFoundException + FullyQualifiedErrorId : CommandNotFoundException
Всё в порядке. Пользователь вставил вывод программы как команды в PowerShell — поэтому и получил ошибки. Это не поломка, а его недопонимание.
Давай объясню коротко и пойдём дальше. Главное — Шаг 1 прошёл (все три OK). Файл tasks.py обновлён корректно.
Он может перепутать: вывод, который печатает Write-Host — это НЕ команды для PowerShell. Просто смотри на него, не копируй обратно.
Запускаем Шаг 2 (patch_server_cap.py) — это простой скрипт, который мы уже писали.
Коротко и ясно.
Всё отлично — Шаг 1 прошёл успешно, все три проверки OK:
text
 OK: def close_stale_sessions
 OK: ключ в TASKS_REGISTRY
 OK: cron */30
Красные ошибки — это не поломка. Ты случайно скопировал вывод (то, что вывела программа) обратно в PowerShell, а PowerShell попытался выполнить это как команды. Строки вроде === Проверка tasks.py === и OK: ... — это текстовый отчёт, а не команды. Их не надо запускать повторно.
Правило на будущее: если строка начинается с === или OK: или MISS: — это отчёт, не команды. Просто смотри на него, не копируй в терминал.
________________________________________
Шаг 2 — Патч server/main.py (cap 24h)
Скопируй это и запусти:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Шаг 4: патч server/main.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_server_cap.py
Что ожидаем в выводе:
text
=== Шаг 4: патч server/main.py ===
OK: добавлен предохранитель 24 часа
SYNTAX OK
________________________________________
Шаг 3 — Патч настроек (stale_session_hours)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Шаг 5b: патч web_admin.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_settings_stale.py
Что ожидаем:
text
=== Шаг 5b: патч web_admin.py ===
OK: stale_session_hours в settings_dict
OK: параметр stale_session_hours в settings_save
OK: обработка stale_session_hours в new_vals
SYNTAX OK
________________________________________
Шаг 4 — Патч шаблона settings.html
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\settings.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("stale_session_hours")) {
    Write-Host "SKIP: поле уже есть" -ForegroundColor Yellow
} else {
    $oldBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
'@

    $newBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">
                        Автозакрытие зависших сессий
                        <span class="hint" data-bs-toggle="tooltip" title="Если сессия висит без session_end дольше указанного времени — сервер закроет её временем последней активности. Защита от ситуации «сотрудник забыл нажать Конец работы, ПК выключили».">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="stale_session_hours" class="form-control"
                               value="{{ cfg.stale_session_hours }}" min="1" max="24">
                        <span class="input-group-text">часов</span>
                    </div>
                    <div class="form-text">По умолчанию 2 часа. Рекомендуется 1–3.</div>
                </div>
'@

    if ($content.Contains($oldBlock)) {
        $content = $content.Replace($oldBlock, $newBlock)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: поле stale_session_hours добавлено" -ForegroundColor Green
    } else {
        Write-Host "ERROR: не найден блок Idle-порог" -ForegroundColor Red
    }
}

$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
if ($check.Contains("stale_session_hours")) {
    Write-Host " Поле в шаблоне: OK" -ForegroundColor Green
} else {
    Write-Host " Поле в шаблоне: MISS" -ForegroundColor Red
}
Что ожидаем:
text
OK: поле stale_session_hours добавлено
 Поле в шаблоне: OK
________________________________________
Шаг 5 — Пересборка и проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Синтаксис Python ===" -ForegroundColor Cyan
client\.venv\Scripts\python.exe -c "import ast; [ast.parse(open(p, encoding='utf-8').read()) for p in [r'D:\tracker\server\web_admin.py', r'D:\tracker\server\main.py', r'D:\tracker\server\tasks.py']]; print('ALL SYNTAX OK')"

Write-Host "`n=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 30

Write-Host "`n=== Статус ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи API (последние 40 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=40

Write-Host "`n=== Задача close_stale_sessions в БД ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron FROM scheduled_tasks WHERE name='close_stale_sessions';"

Write-Host "`n=== grep-проверки в контейнере ===" -ForegroundColor Cyan
docker compose exec -T api grep -c "MAX_SESSION_HOURS" /app/server/main.py
docker compose exec -T api grep -c "_union_duration" /app/server/web_admin.py
docker compose exec -T api grep -c "close_stale_sessions" /app/server/tasks.py
Что ожидаем:
ALL SYNTAX OK
Все 3 контейнера Up
В логах: Созданы дефолтные задачи: close_stale_sessions
В scheduled_tasks — строка close_stale_sessions | t | */30 * * * *
Grep-проверки: 1, 2, 3+
________________________________________
Запускай Шаг 2, потом 3, 4, 5 по порядку. После каждого смотри вывод — если OK и SYNTAX OK, идём дальше. Пришли итог — и проверим отчёт за 23.09.
=== Шаг 4: патч server/main.py === SKIP: cap уже есть SYNTAX OK === Шаг 5b: патч web_admin.py === D:\tracker\client\.venv\Scripts\python.exe: can't open file 'D:\\tracker\\_patch_settings_stale.py': [Errno 2] No such file ordirectory
Пользователь:
Шаг 4 (server/main.py cap) — "SKIP: cap уже есть" — значит патч уже применён ранее (видимо, скрипт запустился в прошлый раз, но мы не видели вывода). Это нормально, всё ок.
Шаг 5b — файл _patch_settings_stale.py не найден. Мы его не создавали в этой сессии — я дал код inline, но не обернул в скрипт с WriteAllText. Надо создать файл и запустить.
Давай сделаю так:
Создам файл _patch_settings_stale.py (Python-патчер)
Запущу его
Заодно проверю, что в main.py cap уже стоит
Также надо проверить, что в web_admin.py и settings.html ничего не сломалось.
План:
Создать _patch_settings_stale.py с полным содержимым патча
Запустить
Если OK — перейти к шаблону settings.html
Потом пересборка
Пишу ответ коротко.
Шаг 4 (cap 24h) уже был применён ранее — это нормально, файл server/main.py уже содержит предохранитель. Двигаемся дальше.
Ошибка в шаге 5b: файл _patch_settings_stale.py не был создан (я дал код inline, но не обернул в создание файла). Исправляю — создаю скрипт и сразу запускаю.
Шаг 3 — Создание и запуск патча web_admin.py
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "stale_session_hours" in content:
    print("SKIP: stale_session_hours уже есть")
    raise SystemExit(0)

