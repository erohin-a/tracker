# Что	Оценка

*Часть 87 из 100. Источник: `BCE.md`.*

[◀ Ищем блок с return в _build_report (тот, что уже пропатчен)](086_Ischem_blok_s_return_v_build_report_tot_chto_uzhe_propatchen.md) | [Оглавление](00_BCE_INDEX.md) | [Найдём все функции экспорта отчёта ▶](088_Naydem_vse_funktsii_eksporta_otcheta.md)

---

#	Что	Оценка
25	Тесты pytest на критичные пути	1-2 дня
26	152-ФЗ: согласия, приказ, уведомление РКН, меры защиты (ст. 19)	не разработка
27	Партиционирование других hot-таблиц (daily_stats, records архивы)	1 день
28	Мониторинг Prometheus + Grafana	1 день
29	Аудит действий пользователя — сейчас только админа	1 день
30	Оптимизация SQL-запросов отчётов при 500k+ записей	1-2 дня
________________________________________
3. Что именно надо починить сейчас (детально)
3.1. XLSX/CSV/PDF — старые колонки
Сейчас экспорт делает _report_to_table в web_admin.py и в report_result.html. Там ещё старые колонки (Отработано / С трекером / Эффективно / Пауза), а мы добавили Интенсивная и переопределили Паузу.
Нужно привести _report_to_table к новому формату:
python
headers = [
    "Группа", "Рабочий день", "Сотрудник", "1C ID", "Отдел", "Компьютер",
    "Сессий", "Отработано", "С трекером", "Интенсивная", "Эффективно", "Пауза",
]
Плюс — в XLSX ячейки длительностей должны быть в формате [HH]:MM:SS (или строками в часах-минутах-секундах), а даты — как DD.MM.YYYY.
3.2. Кнопка «Вчера» в отчётах
В reports.html функция setYesterday() сейчас не обновляет date_to. Надо, чтобы обе даты ставились на вчера. Я уже давал этот фикс в прошлом чате — он, скорее всего, не применился.
3.3. Cookie админки и 401
Сейчас при истечении cookie API возвращает JSON {"detail":"not authenticated"}, а браузер показывает это как текст. Нужно:
Добавить в web_admin.py декоратор/зависимость current_admin_or_redirect, которая на невалидную сессию делает RedirectResponse("/admin/login").
Или — перехватывать 401 на уровне middleware.
Это важно, чтобы админ не пугался «голого» JSON при отвале сессии.
3.4. Установщик Inno Setup
У тебя уже есть client/build.spec (PyInstaller). Нужен ещё:
installer.iss — скрипт Inno Setup.
Экран запроса bootstrap-токена при установке.
Копирование ca.pem в %APPDATA%\Tracker\ca.pem.
Ярлык в Startup или запись в реестр.
Кнопка «Собрать .exe» в SCP (BuildTab), которая вызывает pyinstaller и ISCC.exe.
3.5. Публикация версий клиента через UI
Без этого автообновление (updater.py) будет пустым:
Форма в админке: загрузка .exe, версия, обязательность, notes.
Запись в таблицу client_versions.
Клиент проверяет /api/v1/version и, если есть новая версия, предлагает обновиться.
3.6. Замена ca.pem через UI (клиент)
Логика:
Кнопка «Загрузить ca.pem из файла» на вкладке «Регистрация».
Показать пользователю отпечаток (SHA-256) загружаемого сертификата.
Сравнение с TRACKER_PIN (если задан) или просто подтверждение.
Сохранение в %APPDATA%\Tracker\ca.pem, инвалидация httpx.Client.
При ошибке SSL — автооткат к предыдущему.
3.7. Клиентский i18n и темы — доделать
Полностью перевести главное окно и SettingsDialog.
Реализовать retranslateUi() для всех виджетов, чтобы язык переключался без перезапуска.
Расширить тёмную QSS на все элементы (таблицы, трей, диалоги, тосты).
Тёмный titlebar — опционально через DwmSetWindowAttribute.
3.8. Импорт/экспорт сотрудников
XLSX-файл с колонками:
text
ФИО | 1C ID | Отдел | График | Статус | ПК
Функции:
Экспорт всех сотрудников.
Импорт: добавление новых, обновление существующих по 1C ID, деактивация отсутствующих.
Предпросмотр «будет создано: N, обновлено: M, деактивировано: K».
3.9. Индивидуальные графики работы
Сейчас есть только один график — «Стандартный 9-18». Нужно:
CRUD графиков (страница /admin/schedules).
Привязка: отдел ? график, сотрудник ? график.
Отчёт «Опоздания/переработки» на базе графиков.
________________________________________
4. Мой план на ближайшие 2-3 сессии чата
Сессия 1 (следующая)
Фикс close_stale_sessions — 5 мин.
Кнопка «Вчера» + cookie-редирект — 30 мин.
XLSX/CSV/PDF — новые колонки — 2-3 часа.
Сессия 2
Установщик Inno Setup + BuildTab в SCP.
Публикация версий через UI.
Сессия 3
Замена ca.pem через UI.
i18n + темы клиента до конца.
Сессия 4+
Импорт/экспорт сотрудников.
Индивидуальные графики.
Опоздания/переработки.
________________________________________
5. Что важно понимать по проекту
Из файла видно, что функционально система готова на ~85-90%. Сервер, админка, клиент, отчёты, роли, партиционирование, планировщик — всё это работает. Оставшиеся 10-15% — это:
Упаковка (установщик клиента, публикация версий).
Полировка (отчёты в XLSX/PDF, i18n, темы).
Эксплуатация (бэкапы, алерты, мониторинг).
Юридическое (152-ФЗ).
Новые фичи (Live, графики, отчёты по программам, импорт сотрудников) — это уже «после того как основное заработает стабильно».
По количеству часов: до «можно отдать одному сотруднику» — примерно 15-20 часов работы. До «можно отдать 50 сотрудникам в компании» — примерно 40-50 часов (включая установщик, бэкапы, алерты, документацию).
________________________________________
6. Про контроль окончания чата
Я понял замечание. Впредь буду следить за длиной контекста. Если увижу, что мы близко к лимиту, сразу предложу собрать компактную handoff-сводку (что сделано, что осталось, ключевые файлы и команды), чтобы ты мог скопировать её в новый чат и продолжить без потерь.
Сейчас контекст ещё есть, можно продолжать. Начнём с фикса tasks.py, потом — XLSX/CSV, потом — установщик.
ручками вставлять проблемно давай через команды
User wants the fix via PowerShell command instead of manual editing. Let me provide a command that patches tasks.py to add the missing imports.
The file D:\tracker\server\tasks.py needs the import line changed. Let me write a safe PowerShell script.
Понял, давай через скрипт. Ниже — безопасный патчер, который сам найдёт нужную строку и добавит недостающие импорты.
Скрипт — фикс close_stale_sessions в tasks.py
Скопируй блок целиком в PowerShell (в папке D:\tracker) и нажми Enter:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\tasks.py")
content = PATH.read_text(encoding="utf-8")

# Ищем внутри функции close_stale_sessions строку с неполным импортом
old = "from .models import AppSetting as _AppSetting, Record as _Record"

new = (
    "from .models import (\n"
    "        AppSetting as _AppSetting,\n"
    "        Record as _Record,\n"
    "        WorkSession,\n"
    "        AuditLog,\n"
    "    )"
)

if new in content:
    print("SKIP: импорт уже расширен")
elif old in content:
    content = content.replace(old, new, 1)
    PATH.write_text(content, encoding="utf-8")
    print("OK: импорт WorkSession и AuditLog добавлен")
else:
    print("WARN: строка с импортом не найдена — ищу альтернативу")
    # Альтернатива: возможно строка уже другая
    m = re.search(r"from \.models import [^\n]*AppSetting[^\n]*\n", content)
    if m:
        print("Найдено:", m.group(0).strip())
        print("Проверь вручную и пришли эту строку")
    else:
        print("Модели вообще не импортируются — надо смотреть файл целиком")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# Показываем функцию close_stale_sessions — первые 30 строк
m = re.search(r"def close_stale_sessions.*?(?=\ndef |\Z)", content, re.DOTALL)
if m:
    print()
    print("=== close_stale_sessions (первые 30 строк) ===")
    for i, line in enumerate(m.group(0).split("\n")[:30], 1):
        print(f"{i:3} {line}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_tasks_imports.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Запуск патчера ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_tasks_imports.py
Что должно быть в выводе
Один из трёх вариантов:
Вариант 1 — удачно:
text
OK: импорт WorkSession и AuditLog добавлен
SYNTAX OK
=== close_stale_sessions (первые 30 строк) ===
...
Вариант 2 — уже пропатчено:
text
SKIP: импорт уже расширен
SYNTAX OK
...
Вариант 3 — не нашли строку:
text
WARN: строка с импортом не найдена — ищу альтернативу
Найдено: from .models import ...
Проверь вручную и пришли эту строку
Пришли мне вывод в любом случае. Если вариант 3 — покажу строку, которую надо заменить вручную (одна строка, не блок).
После патча — пересборка
powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose logs api --tail=20
Через 30 минут проверь /admin/scheduler — в истории запусков должна появиться зелёная строка close_stale_sessions | успех. Если снова ошибка — пришли traceback из логов, поправлю точечно.
Запускай и покажи вывод.
>> & client\.venv\Scripts\python.exe _fix_tasks_imports.py === Запуск патчера === OK: импорт WorkSession и AuditLog добавлен SYNTAX ERROR: invalid syntax (<unknown>, line 265) начал работать через Visual Studio Code смотри нашу переписку
The user ran the patcher. It says "OK: импорт WorkSession и AuditLog добавлен" but then "SYNTAX ERROR: invalid syntax (<unknown>, line 265)".
So the patcher replaced the import but the syntax error appeared. Wait — the patcher does ast.parse(content) AFTER writing to file. So it wrote the file first, then tried to parse. The parse failed at line 265.
This means: the file was modified, but there's now a syntax error somewhere. Actually no — if the file already had a syntax error before, replacing the import string wouldn't cause it. Unless the replacement broke something.
Wait — the original line was:
python
from .models import AppSetting as _AppSetting, Record as _Record
This is INSIDE the function, so it's indented. My replacement is:
python
from .models import (
        AppSetting as _AppSetting,
        Record as _Record,
        WorkSession,
        AuditLog,
    )
But I don't know the original indentation. If the original was indented by 4 spaces, my new lines with 8 spaces would still work because the parenthesis continues. But my first line from .models import ( has NO indentation. So if the original was indented, my replacement breaks indentation.
Actually — I need to look at what the user showed us. In the very first message, the tasks.py structure was:
python
def close_stale_sessions(db: Session) -> str:
    ...
    from .models import AppSetting as _AppSetting, Record as _Record
    row = db.query(_AppSetting).filter(...)
So the import WAS indented (4 spaces inside the function). My replacement starts with from .models import ( at column 0 — that breaks the indentation.
That's the syntax error on line 265.
OK, so I need to fix this. The user needs to:
Revert the bad write OR fix the indentation
Since the file is now written with bad content, we need to fix it. Best approach: write a patcher that opens the file, finds the block I inserted, and re-writes it with proper indentation.
But I don't know exactly what got written. Let me think.
The original string I replaced was exactly:
text
from .models import AppSetting as _AppSetting, Record as _Record
This was ONCE in the file (probably).
After replacement, the file has:
text
from .models import (
        AppSetting as _AppSetting,
        Record as _Record,
        WorkSession,
        AuditLog,
    )
But at position where from .models import AppSetting... used to be — which was indented.
So inside the function, it now looks like:
python
    ...
    # (4 spaces indent)
from .models import (
        AppSetting as _AppSetting,
        ...
    )
Wait — actually .replace() replaces the exact string. So if the original was from .models import AppSetting... (with 4 leading spaces preserved as part of the line but not part of the search string), then after replacement:
python
    from .models import (
        AppSetting as _AppSetting,
        Record as _Record,
        WorkSession,
        AuditLog,
    )
Hmm actually — the search string was just from .models import AppSetting... without leading whitespace. So the leading 4 spaces stay, then from .models import ( gets inserted at that position. That's actually fine — the indentation stays.
Let me re-read my replacement string:
python
new = (
    "from .models import (\n"
    "        AppSetting as _AppSetting,\n"
    "        Record as _Record,\n"
    "        WorkSession,\n"
    "        AuditLog,\n"
    "    )"
)
So the replacement is:
text
from .models import (
        AppSetting as _AppSetting,
        Record as _Record,
        WorkSession,
        AuditLog,
    )
If the original line was from .models import AppSetting as _AppSetting, Record as _Record (4 spaces indent), after .replace() it becomes:
text
    from .models import (
        AppSetting as _AppSetting,
        Record as _Record,
        WorkSession,
        AuditLog,
    )
That's syntactically valid Python.
BUT — the error is at line 265. So maybe the replacement happened at a wrong location (e.g., inside a docstring or a comment).
Or — actually, looking more carefully. The user said "from .models import AppSetting as _AppSetting, Record as _Record" was the line I described. But maybe it appeared multiple times? Or maybe the actual line was different.
Or — maybe the file already had a syntax error at line 265 BEFORE my patch, and the patch didn't cause it.
Let me check the user's earlier evidence. From the previous "Планировщик задач.pdf":
text
NameError: name 'WorkSession' is not defined
Then later:
text
NameError: name 'AuditLog' is not defined
The error changed — meaning the user had already patched something manually between these two errors. They added WorkSession somewhere. But AuditLog still missing. So the import in the file might be:
python
from .models import WorkSession  # added manually
# plus something for Record
Actually maybe the file is a mess now. Let me approach this differently:
Give the user a script that shows what's on line 265, and around the import in close_stale_sessions.
Then we can fix precisely.
The user also said "начал работать через Visual Studio Code смотри нашу переписку" — meaning they can now look at the file directly. So it's easier.
Let me ask them to:
Open D:\tracker\server\tasks.py in VS Code.
Go to line 265.
Show me what's around there.
Or — better — give a script that prints:
lines 255-275 (around the error)
the full close_stale_sessions function
Then I can fix precisely.
Actually, the simplest fix: the patcher already wrote the file. So the file has the replacement + whatever syntax error was already there. Let me ask user to:
Open VS Code, file D:\tracker\server\tasks.py.
Look at line 265 and around.
Send me screenshot OR use a diagnostic script.
Let me give a diagnostic script that prints those lines.
Let me also ask them to run:
python
python -c "import ast; ast.parse(open(r'D:\tracker\server\tasks.py', encoding='utf-8').read())"
This gives the error with line number.
Then a script that prints lines 250-280.
Let me write it.
Патч записался, но задел синтаксис — ошибка на строке 265. Скорее всего, оригинальный импорт был внутри функции с отступом, а я подставил блок с другим отступом, и теперь Python ругается.
Давай сначала посмотрим, что там в файле. Запусти этот диагностический скрипт:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$diag = @'
from pathlib import Path
import ast

PATH = Path(r"D:\tracker\server\tasks.py")
lines = PATH.read_text(encoding="utf-8").splitlines()

# 1. Показываем строки 250-285 (где ошибка)
print("=== Строки 250-285 ===")
for i in range(249, min(285, len(lines))):
    print(f"{i+1:4} | {lines[i]}")

print()
print("=== Все строки с 'from .models import' ===")
for i, line in enumerate(lines, 1):
    if "from .models import" in line:
        # Печатаем строку и 5 следующих
        for j in range(i - 1, min(i + 6, len(lines))):
            print(f"{j+1:4} | {lines[j]}")
        print("---")

# 2. Пробуем распарсить
content = "\n".join(lines)
try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: line={e.lineno}, msg={e.msg}")
    print(f"Текст: {e.text}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_diag_tasks.py", $diag, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _diag_tasks.py
Что ожидаем увидеть
Скрипт покажет:
Строки 250–285 — там, где сейчас ошибка.
Все места, где есть from .models import — их может быть несколько.
Точное сообщение об ошибке с указанием строки.
Пришли мне вывод целиком. По нему я:
Пойму, где именно кривой отступ.
Дам точный патч, который заменит проблемный блок на корректный.
Проверю, что все нужные модели (WorkSession, AuditLog) импортированы.
Если у тебя теперь есть VS Code — можешь просто открыть D:\tracker\server\tasks.py, перейти на строку 265 (Ctrl+G ? 265) и прислать мне скриншот 10 строк до и 10 строк после. Это тоже сработает.
Now I can see the exact problem. Line 265 has ), WorkSession — the trailing , WorkSession is the leftover from my bad patch. The import block is already correct (lines 260-264 have all 4 models). The problem is just the extra , WorkSession at line 265.
Let me give a precise fix: replace ), WorkSession with ).
Let me write a Python patcher that fixes this.
Actually the cleanest way: read the file, replace the exact string ), WorkSession\n with )\n. Then check syntax.
Let me also verify the rest of the file looks fine — no other issues visible. The task itself references WorkSession, AuditLog, _Record, _AppSetting — all now imported.
Let me write a simple PowerShell script.
Всё видно: на строке 265 остался «хвост» от моего неудачного патча — ), WorkSession. Импорт на строках 260–264 уже правильный, надо просто убрать этот хвост.
Скрипт — точный фикс строки 265
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
from pathlib import Path

PATH = Path(r"D:\tracker\server\tasks.py")
lines = PATH.read_text(encoding="utf-8").splitlines()

# Ищем строку с хвостом ), WorkSession
bad = "    ), WorkSession"
good = "    )"

found = False
for i, line in enumerate(lines):
    if line.rstrip() == bad:
        lines[i] = good
        found = True
        print(f"OK: строка {i+1} исправлена: '{bad}' -> '{good}'")
        break

if not found:
    print("WARN: строка '    ), WorkSession' не найдена")
    # Ищем любые строки, содержащие '), WorkSession'
    for i, line in enumerate(lines, 1):
        if "WorkSession" in line and ")" in line and "from" not in line and "import" not in line:
            print(f"  строка {i}: {line}")

if found:
    PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    content = "\n".join(lines)
    try:
        ast.parse(content)
        print("SYNTAX OK")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: line={e.lineno}, msg={e.msg}")
        print(f"Текст: {e.text}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_line265.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Фикс строки 265 ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_line265.py
Что ожидаем
text
OK: строка 265 исправлена: '    ), WorkSession' -> '    )'
SYNTAX OK
После фикса
Проверь ещё раз диагностикой:
powershell
& client\.venv\Scripts\python.exe _diag_tasks.py
Должно быть SYNTAX OK и никаких следов ), WorkSession.
Пересобери и перезапусти:
powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose logs api --tail=20
Через 30 минут проверь /admin/scheduler. Должна появиться зелёная строка close_stale_sessions | успех.
Запускай, пришли вывод.
>> & client\.venv\Scripts\python.exe _fix_line265.py === Фикс строки 265 === OK: строка 265 исправлена: ' ), WorkSession' -> ' )' SYNTAX OK (.venv) PS D:\tracker> & client\.venv\Scripts\python.exe _diag_tasks.py === Строки 250-285 === 250 | def close_stale_sessions(db: Session) -> str: 251 | """ 252 | Закрывает сессии, которые клиент так и не закрыл. 253 | 254 | Сценарий: сотрудник ушёл домой, забыл нажать «Конец работы», 255 | ПК выключили или клиент упал. Сессия висит в БД с session_end = NULL. 256 | Такая сессия портит отчёты (был случай: 17 часов за один день). 257 | 258 | Запускается каждые 30 минут (cron */30 * * * *). 259 | """ 260 | from .models import ( 261 | AppSetting as _AppSetting, 262 | Record as _Record, 263 | WorkSession, 264 | AuditLog, 265 | ) 266 | 267 | row = db.query(_AppSetting).filter( 268 | _AppSetting.key == "stale_session_hours" 269 | ).first() 270 | try: 271 | stale_hours = max(1, min(24, int(row.value))) if row else 2 272 | except (ValueError, TypeError): 273 | stale_hours = 2 274 | 275 | cutoff = _now() - timedelta(hours=stale_hours) 276 | 277 | stale = ( 278 | db.query(WorkSession) 279 | .filter( 280 | WorkSession.session_end.is_(None), 281 | WorkSession.session_start < cutoff, 282 | ) 283 | .all() 284 | ) 285 | === Все строки с 'from .models import' === 217 | from .models import AppSetting as _AppSetting 218 | 219 | def _get(key: str, default: str) -> str: 220 | row = db.query(_AppSetting).filter(_AppSetting.key == key).first() 221 | return row.value if row else default 222 | 223 | tz_name = _get("report_timezone", "Europe/Moscow") --- 260 | from .models import ( 261 | AppSetting as _AppSetting, 262 | Record as _Record, 263 | WorkSession, 264 | AuditLog, 265 | ) 266 | --- SYNTAX OK нажал принудительный запуск скриншот во вложении
Скриншот показывает, что задача всё ещё падает с NameError: name 'AuditLog' is not defined. Хотя синтаксис OK и импорт вроде бы на месте.
Причина — Python видит импорт внутри функции, но ошибка всё равно возникает. Это происходит, потому что в файле есть проблема с областью видимости: AuditLog используется в другой функции, где он не импортирован, ИЛИ старая версия файла в контейнере (не пересобралась).
Смотрим внимательно:
Строки 260-265 — импорт внутри close_stale_sessions.
Но что если AuditLog используется не внутри close_stale_sessions, а в aggregate_daily_stats или другой функции?
Или: контейнер не пересобрался, и в нём старая версия файла.
Скриншот показывает: последний запуск 25.09.2026 21:20 — ошибка NameError: name 'AuditLog' is not defined. До этого 20:54 — та же ошибка.
Значит, docker compose up -d --build не пересобрал образ, или пользователь ещё не пересобирал после фикса строки 265.
Стоп — судя по выводу, скрипт _fix_line265.py прошёл, потом _diag_tasks.py показал SYNTAX OK. Но пользователь пишет "нажал принудительный запуск скриншот во вложении" — и на скриншоте всё ещё ошибка AuditLog.
Это значит: контейнер всё ещё работает со старой версией tasks.py, потому что не было docker compose up -d --build после фикса.
Нужно:
Пересобрать образ.
Или, если контейнер запущен и файл tasks.py не примонтирован — пересборка обязательна.
Также обратим внимание: в close_stale_sessions импорт теперь правильный. Но NameError: name 'AuditLog' is not defined на строке 21:20 — это уже после фикса строки 265? Смотрю: пользователь запустил фикс, потом diag, потом "нажал принудительный запуск". Если он не пересобрал контейнер, то запуск идёт по старой версии в контейнере.
Даю команду на пересборку.
Также — обратим внимание, что в PowerShell после _fix_line265.py и _diag_tasks.py пользователь не выполнил docker compose down && up -d --build. Обязательно надо это сделать.
Кроме того — возможно, надо проверить, что в контейнере действительно новая версия файла. Дам команду проверки и пересборки.
Синтаксис починен, но задача всё ещё падает с NameError: AuditLog. Причина одна: контейнер не пересобран — он всё ещё работает со старой версией tasks.py, которая загружена в образ при последней сборке. Правки на хосте без --build не доходят.
Проверим и пересоберём.
Шаг 1 — проверить, что в контейнере старая версия
powershell
Set-Location D:\tracker
Write-Host "=== Что в контейнере сейчас ===" -ForegroundColor Cyan
docker compose exec -T api grep -n "WorkSession" /app/server/tasks.py | Select-Object -First 5
Write-Host ""
docker compose exec -T api grep -n "AuditLog" /app/server/tasks.py | Select-Object -First 5
Если увидишь старую строку from .models import AppSetting as _AppSetting, Record as _Record — это точно старая версия.
Шаг 2 — пересобрать образ с новым кодом
powershell
Set-Location D:\tracker
Write-Host "=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
Write-Host ""
Write-Host "=== Проверка, что новая версия в контейнере ===" -ForegroundColor Cyan
docker compose exec -T api grep -n "WorkSession," /app/server/tasks.py
docker compose exec -T api grep -n "AuditLog," /app/server/tasks.py
Ожидаем:
Все три контейнера Up.
В grep увидим строки WorkSession, и AuditLog, — значит, новая версия внутри.
Шаг 3 — принудительно запустить задачу
Через веб-интерфейс /admin/scheduler нажми «Запуск» у задачи close_stale_sessions. Или через консоль:
powershell
docker compose exec -T api python -c @"
from server.database import SessionLocal
from server import tasks
db = SessionLocal()
try:
    result = tasks.close_stale_sessions(db)
    print('OK:', result)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
"@
Если увидишь OK: Зависших сессий нет или OK: Закрыто зависших сессий: N — победа.
Если снова NameError — значит, в контейнере всё ещё старая версия, и надо смотреть, почему docker compose up -d --build не подхватывает изменения.
Шаг 4 — если и после пересборки ошибка
Тогда проверим содержимое контейнера целиком:
powershell
docker compose exec -T api cat /app/server/tasks.py | Select-String -Pattern "from .models import" -Context 0,8
Это покажет реальный импорт в контейнере. Если он не совпадает с тем, что на хосте — значит, Docker не пересобирает образ (например, из-за кэша слоёв или потому что файл tasks.py в .dockerignore).
Начни с шага 1 и 2. Пришли вывод grep из шага 1 (что в контейнере до пересборки) и вывод команды из шага 3 (запуск задачи).
переходим к следующим шогам
Пользователь показал скриншот — задача close_stale_sessions теперь работает успешно:
#66 (25.09.2026 21:40) — успех, "Зависших сессий нет (порог 2ч)"
#65 (25.09.2026 21:30) — успех, "Зависших сессий нет (порог 2ч)"
Значит пересборка прошла, задача работает. Отлично.
Теперь переходим к следующим шагам. По моему плану приоритетов:
Приоритет 1 — закончить отчёты:
? close_stale_sessions — сделано
XLSX/CSV/PDF — новые колонки (Интенсивная, переопределённая Пауза)
Кнопка «Вчера» — ставит только date_from
Cookie админки: 401 ? редирект на /login
Начну с пункта 2 (XLSX/CSV/PDF) — это самое важное для отчётов, потому что при выгрузке данные сейчас неполные.
Смотрю на скриншот отчёта из предыдущего сообщения — там видно:
В таблице есть колонки: Рабочий день | Сотрудник | 1C ID | Отдел | Сессий | Отработано | С трекером | Интенсивная | Эффективно | Пауза
Раскрытие сессии показывает: Начало | Конец | Отработано | Интенсивная | Эффективно | Пауза | Авар.
Раскрытие программ показывает: Программа | Время | Клавиатура | Мышь
Всё это уже есть в HTML. Но при экспорте в XLSX/CSV/PDF — там ещё старые колонки (Отработано / С трекером / Эффективно, без Интенсивной и переопределённой Паузы).
Мне нужно посмотреть текущий _report_to_table в web_admin.py, чтобы понять, что там сейчас. И _render_csv, _render_xlsx, _render_pdf.
Давай сначала диагностику — покажу текущее содержимое этих функций.
Актуальный план:
Диагностика: посмотреть _report_to_table, _render_csv, _render_xlsx, _render_pdf в web_admin.py
Дать патч с новыми колонками
Проверить на живом отчёте
Также надо не забыть про:
Кнопка «Вчера» в reports.html
Cookie 401 ? редирект
Начну с диагностики — покажу функции.
Формат ответа:
Подтверждение что фикс сработал
Диагностический скрипт
Просьба прислать вывод
Пусть будет компактно.
Отлично, задача close_stale_sessions теперь работает — в истории видно два успешных запуска подряд (#65 и #66). Баг закрыт.
Переходим к следующим шагам. По приоритету — доделать экспорт отчётов (XLSX/CSV/PDF), потом кнопка «Вчера» и редирект на логин.
Что делаем
Экспорт в XLSX/CSV/PDF сейчас использует старые колонки — без «Интенсивной» и с прежней формулой «Паузы». Надо привести к тому, что видно в HTML-версии отчёта:
Рабочий день / Месяц / Сотрудник / 1C ID / Отдел / Компьютер
Сессий
Отработано (span)
С трекером (union)
Интенсивная ? новое
Эффективно
Пауза ? переопределена как pause_seconds + (Отработано ? С трекером)
Чтобы не гадать с текущим кодом, сначала посмотрим, что сейчас в _report_to_table и функциях экспорта.
Диагностика — что сейчас в web_admin.py
Скопируй блок целиком в PowerShell и запусти:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$diag = @'
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\web_admin.py")
content = PATH.read_text(encoding="utf-8")

