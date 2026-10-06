<!-- Часть 1174 из 1409 -->
# Показываем функцию close_stale_sessions — первые 30 строк
*Хлебные крошки:* Показываем функцию close_stale_sessions — первые 30 строк

[◀ Ищем внутри функции close_stale_sessions строку с неполным импортом](1173_Ischem_vnutri_funktsii_close_stale_sessions_stroku_s_nepolnym_importom.md) | [Оглавление](00_BCE_INDEX.md) | [plus something for Record ▶](1175_plus_something_for_Record.md)

---

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
