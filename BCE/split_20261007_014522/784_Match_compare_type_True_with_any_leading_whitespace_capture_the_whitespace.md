<!-- Часть 784 из 1409 -->
# Match "compare_type=True," with any leading whitespace, capture the whitespace
*Хлебные крошки:* Match "compare_type=True," with any leading whitespace, capture the whitespace

[◀ Offline](783_Offline.md) | [Оглавление](00_BCE_INDEX.md) | [1. Добавляем функцию include_object после target_metadata ▶](785_1_Dobavlyaem_funktsiyu_include_object_posle_target_metadata.md)

---

# Match "compare_type=True," with any leading whitespace, capture the whitespace
pattern = re.compile(r"(\n\s*)(compare_type=True,)", re.MULTILINE)

def repl(m):
    indent = m.group(1)  # the newline + whitespace before
    line = m.group(2)   # compare_type=True,
    # Use same indent for the new line
    indent_str = indent[1:]  # remove the newline
    return f"{indent}{line}\n{indent_str}include_object=include_object,"

content = pattern.sub(repl, content)
This should work. But we should only patch context.configure() calls, not any other place where compare_type=True might appear. Since it only appears in context.configure, this is safe.
OK, let me finalize. I'll write the patcher carefully.
Actually — even simpler. Since we know env.py has exactly two occurrences (offline and online), just replace all:
python
content = content.replace("compare_type=True,", "compare_type=True,\n            include_object=include_object,")
But indentation would be wrong in offline (8 vs 12 spaces). Hmm.
Let me use the regex approach. Or — use a smarter replace that preserves indentation:
python
import re
content = re.sub(
    r"^(\s*)compare_type=True,$",
    r"\1compare_type=True,\n\1include_object=include_object,",
    content,
    flags=re.MULTILINE
)
This captures the leading whitespace and reuses it. Clean.
But wait — ^(\s*) will also match  (4 spaces) if compare_type is at 4-space indent. And \1 in the replacement will use the captured leading whitespace. This should work.
Yes, using this regex.
OK, writing the response now. Let me be concise but complete.
One more thing to mention — after this incident, the user should:
Not trust autogenerate blindly
Always inspect migrations before applying
Keep the env.py fix in place
Also — I want to note that the migration file has mojibake in the docstring/comments. I'll mention it but not critical.
Alright, final response time.
?? СТОП! Миграцию нельзя применять как есть — потеряешь все записи!
Я внимательно изучил файл 2602b71902d4_add_employee_settings.py, который сгенерировал Alembic. В нём кроме создания employee_settings есть катастрофа: он пытается удалить все партиционированные таблицы records_2025_01 … records_2027_12 и records_default — то есть все сырые записи об активности.
Что не так
В миграции есть вот такие строки (в обеих секциях — upgrade и downgrade):
text
op.drop_index('records_2025_05_computer_id_client_ts_idx', table_name='records_2025_05')
op.drop_index('records_2025_05_record_uid_client_ts_idx', table_name='records_2025_05')
op.drop_index('records_2025_05_session_uid_idx', table_name='records_2025_05')
op.drop_table('records_2025_05')
... и так для всех 36 партиций и records_default
Если применить как есть — потеряем все записи.
Почему так произошло
Мы используем PostgreSQL native partitioning — таблица records разбита на партиции records_2025_01, records_2026_09 и т.д.
PostgreSQL показывает эти партиции в information_schema как обычные таблицы. А SQLAlchemy про них ничего не знает — в Base.metadata есть только родительская records.
Alembic --autogenerate при сравнении видит: «В БД 36 таблиц records_*, которых нет в metadata — значит, их надо удалить». И генерирует drop_table.
Это классическая проблема Alembic + PostgreSQL partitioning. Лечится двумя шагами:
Сейчас — почистим эту миграцию вручную.
Навсегда — добавим фильтр в env.py, чтобы больше не повторялось.
________________________________________
Скрипт 1 — почистить миграцию
Удаляем все операции с records_* — оставляем только работу с employee_settings.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import re
import ast

PATH = r"D:\tracker\server\alembic\versions\2602b71902d4_add_employee_settings.py"

with open(PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
skip_until_close = False
skipped = {"create_table": 0, "drop_table": 0, "drop_index": 0, "create_index": 0}

for line in lines:
    if skip_until_close:
        if line.strip() == ")":
            skip_until_close = False
            skipped["create_table"] += 1
        continue

    stripped = line.strip()

    # Многострочные op.create_table('records_...' — пропускаем до закрывающей скобки
    if (stripped.startswith("op.create_table('records_") or
        stripped.startswith('op.create_table("records_')):
        skip_until_close = True
        continue

    # Однострочные drop_index / drop_table / create_index
    if (stripped.startswith("op.drop_index('records_") or
        stripped.startswith('op.drop_index("records_')):
        skipped["drop_index"] += 1
        continue
    if (stripped.startswith("op.drop_table('records_") or
        stripped.startswith('op.drop_table("records_')):
        skipped["drop_table"] += 1
        continue
    if (stripped.startswith("op.create_index('records_") or
        stripped.startswith('op.create_index("records_')):
        skipped["create_index"] += 1
        continue

    out.append(line)

new_content = "".join(out)
new_content = re.sub(r"\n\n\n+", "\n\n", new_content)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Удалено операций с партициями records_*:")
for k, v in skipped.items():
    print(f"  {k}: {v}")

try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

print("\nОсталось упоминаний в файле:")
for pattern in ["'employee_settings'", "'records_2025_01'", "'records_2026_09'", "'records_default'"]:
    print(f"  {pattern}: {new_content.count(pattern)}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_migration.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _fix_migration.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_migration.py
Что ожидаем:
text
Удалено операций с партициями records_*:
  create_table: 37    (36 партиций + records_default)
  drop_table: 37
  drop_index: 111     (по 3 индекса ? 37)
  create_index: 111
SYNTAX OK

Осталось упоминаний в файле:
  'employee_settings': 4     ? должно быть 4 (create/drop table + create/drop index)
  'records_2025_01': 0
  'records_2026_09': 0
  'records_default': 0
Если в «Осталось» у employee_settings — 4, а у records_* — 0, миграция чистая. Пришли мне этот вывод, я гляну финальный файл.
________________________________________
Скрипт 2 — фикс env.py, чтобы больше НИКОГДА такого не было
Добавляем include_object в Alembic — он говорит: «партиции records_* — не твои, не трогай».
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import re
import ast

ENV = r"D:\tracker\server\alembic\env.py"

with open(ENV, "r", encoding="utf-8") as f:
    content = f.read()

if "def include_object" in content:
    print("SKIP: include_object уже есть")
    raise SystemExit(0)

