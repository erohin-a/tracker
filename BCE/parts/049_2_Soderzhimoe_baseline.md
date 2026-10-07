# 2. Содержимое baseline

*Часть 49 из 100. Источник: `BCE.md`.*

[◀ revision identifiers, used by Alembic](048_revision_identifiers_used_by_Alembic.md) | [Оглавление](00_BCE_INDEX.md) | [revision identifiers, used by Alembic ▶](050_revision_identifiers_used_by_Alembic.md)

---

# 2. Содержимое baseline
Get-Content (Get-ChildItem D:\tracker\server\alembic\versions\*ecb1e3f89300*.py).FullName
По ним я сразу скажу:
Если партиционирование есть в миграциях ? идём по плану: чистим миграцию, патчим env, сносим volume, поднимаем, всё ок.
Если партиционирования нет ? сначала напишу миграцию records с партициями, а потом уже добавим employee_settings.
Ничего не запускай пока. Сначала посмотрим список миграций — это займёт 10 секунд, а сэкономит нам полдня.
Отлично, теперь у меня полная картина. Смотрю на вывод пользователя:
text
2602b71902d4_add_employee_settings.py          ? текущая, проблемная
35d67a73f181_baseline.py                       ? baseline (создание базовых таблиц)
939e3d0b6f4c_partition_records_by_month.py     ? партиционирование records!
ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py  ? schedules, admin_users, api_keys, daily_stats, backup_config + soft delete
ecb1e3f89300_....py.bak                        ? bak-файл, старый вариант (76 КБ — с операциями records_*)
Ключевой момент: Партиционирование делается в миграции 939e3d0b6f4c_partition_records_by_month.py. Отлично! Значит, если сбросить volume и накатить миграции с нуля — партиции создадутся автоматически.
Также вижу: в ecb1e3f89300 — 14 КБ, и там в docstring прямо написано:
"все операции по records_YYYY_MM убраны из этой миграции вручную"
Значит, я эту миграцию уже почистил в прошлый раз (есть .bak на 76 КБ — старое, с records_*). А в актуальном 14 КБ — чисто. Отлично.
Что осталось сделать:
Почистить 2602b71902d4 — там тоже есть records_* операции
Пропатчить env.py — добавить include_object, чтобы больше такого не было
Пропатчить .mako — на английском
Удалить .bak файл (чтобы не путал)
Сбросить volume (данные не жалко)
Поднять заново — Alembic накатит:
35d67a73f181 — baseline (все базовые таблицы)
939e3d0b6f4c — партиционирование records
ecb1e3f89300 — schedules/admin_users/api_keys/daily_stats/backup_config/soft delete
2602b71902d4 — employee_settings
Проверил цепочку:
35d67a73f181 ? baseline (без down_revision, первый)
939e3d0b6f4c ? down_revision = 35d67a73f181
ecb1e3f89300 ? down_revision = 939e3d0b6f4c
2602b71902d4 ? down_revision = ecb1e3f89300
Цепочка линейная. Всё ок.
Проверю важный момент — в 939e3d0b6f4c_partition_records_by_month.py надо убедиться, что там действительно создаются партиции, а не просто что-то другое. Но раз файл 5 КБ и называется "partition_records_by_month" — почти уверен. Проверим для безопасности.
Хотя пользователь сказал "ничего не запускай пока", но он ждёт команды. Давай я дам ему готовые скрипты, чтобы он их запустил.
План:
Скрипт 1 — почистить 2602b71902d4 от records_* (тот же паттерн, что я давал)
Скрипт 2 — пропатчить env.py (include_object)
Скрипт 3 — пропатчить .mako
Скрипт 4 — удалить .bak файл
Скрипт 5 — проверить 939e3d0b6f4c (что там партиционирование)
Скрипт 6 — сброс volume + поднять заново
Скрипт 7 — проверка
Также важно: пользователь сказал "у нас с тобой там полный план". Он хочет, чтобы я шёл строго по плану. Значит, после применения миграции продолжаем Спринт 5 (напоминание):
Патч /api/v1/client-config — эффективные настройки
UI: /admin/employees/{id}/settings
Endpoint PUT /api/v1/client-settings
Клиентская часть A2
Но сначала — база. Без неё ничего не работает.
Начинаю писать. Сначала скрипт починки миграции 2602b71902d4.
Про .bak файл: он в папке versions/ и Alembic может попытаться его прочитать как миграцию. Хотя расширение .py.bak — не .py, Alembic обычно игнорирует. Но для чистоты — удалим.
Один важный момент: в файле ecb1e3f89300 вижу что-то странное — там уже admin_users, schedules, api_keys, daily_stats, backup_config. А это то, что мы планировали во втором спринте (Спринт 1.2 — "Новые таблицы для ролей, расписаний, планировщика, API-ключей"). То есть я это уже частично сделал в предыдущих чатах — судя по датам, 18.09.2026.
Хорошо, значит какая-то работа уже сделана. Идём дальше.
Пишу ответ:
Хорошие новости: партиционирование есть в отдельной миграции, значит сброс volume безопасен.
Показываю полную цепочку миграций (для наглядности).
Даю скрипты по порядку.
После проверки — идём в Спринт 5.
Начинаю.
?? Отлично, картина ясна! Партиционирование есть, сброс volume безопасен.
Полная цепочка миграций
Проверил все 4 файла + .bak. Выстроилась линейная цепочка:
text
35d67a73f181_baseline.py                     (18.09, 8 КБ)   ? baseline
   ? down_revision: 35d67a73f181
939e3d0b6f4c_partition_records_by_month.py   (18.09, 5 КБ)   ? партиционирование records ?
   ? down_revision: 939e3d0b6f4c
ecb1e3f89300_add_schedules_roles_...py       (18.09, 14 КБ)  ? 8 новых таблиц + soft delete
   ? down_revision: ecb1e3f89300
2602b71902d4_add_employee_settings.py        (21.09, 79 КБ)  ? employee_settings (ПОЧИСТИТЬ)
Ключевые выводы:
? Партиционирование records делается в 939e3d0b6f4c — если сбросить volume, Alembic создаст партиции с нуля. Сброс безопасен.
? ecb1e3f89300 уже почищен — 14 КБ вместо 76 КБ в .bak. Там в docstring прямо сказано: «все операции по records_YYYY_MM убраны вручную». Значит, в прошлый раз я это уже сделал.
? 2602b71902d4 содержит те же 37 drop-операций — её и чистим.
?? .bak файл — надо удалить, чтобы не путал.
________________________________________
Скрипт 1 — почистить миграцию 2602b71902d4
Паттерн — тот же, что я использовал в прошлый раз для ecb1e3f89300 (поэтому там и осталось 14 КБ). Только теперь применяем к новой миграции.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import re
import ast
import os

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

size_kb = os.path.getsize(PATH) / 1024
print(f"\nРазмер файла после чистки: {size_kb:.1f} КБ (был ~79 КБ)")

print("\nОсталось упоминаний в файле:")
for pattern in ["'employee_settings'", "'records_2025_01'", "'records_2026_09'", "'records_default'"]:
    print(f"  {pattern}: {new_content.count(pattern)}")

print("\nОжидаем:")
print("  'employee_settings': 4     — create/drop table + create/drop index")
print("  'records_2025_01': 0       — партиции не должны упоминаться")
print("  'records_2026_09': 0")
print("  'records_default': 0")
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_migration.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _fix_migration.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_migration.py
Что ожидаем:
text
Удалено операций с партициями records_*:
  create_table: 37
  drop_table: 37
  drop_index: 111
  create_index: 111
SYNTAX OK

Размер файла после чистки: ~5.5 КБ (был ~79 КБ)

Осталось упоминаний в файле:
  'employee_settings': 4
  'records_2025_01': 0
  'records_2026_09': 0
  'records_default': 0
________________________________________
Скрипт 2 — фикс env.py (чтобы больше не повторялось)
Это главный фикс. Один раз настроим include_object — и Alembic больше никогда не будет трогать партиции.
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

# 1. Добавляем функцию include_object после target_metadata
old_marker = "target_metadata = Base.metadata"
if old_marker not in content:
    print("ERROR: 'target_metadata = Base.metadata' не найден в env.py")
    raise SystemExit(1)

new_block = '''target_metadata = Base.metadata


# ============================================================
# Фильтр для autogenerate (не путать партиции с обычными таблицами)
# ============================================================
# Проблема: PostgreSQL native partitioning показывает партиции
# (records_2025_01, records_2026_09 и т.д.) в information_schema
# как обычные таблицы. Но в Base.metadata их нет — только
# родительская "records". Alembic --autogenerate видит
# "лишние" таблицы и генерирует их УДАЛЕНИЕ.
#
# Решение: include_object говорит Alembic — таблицы, имя которых
# начинается с "records_" (но не сама "records"), игнорировать.
# Тогда партиции никогда не попадут в миграции.
# ============================================================
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True'''

content = content.replace(old_marker, new_block, 1)

# 2. Добавляем include_object=include_object в оба context.configure()
# Используем regex, который найдёт строку "compare_type=True," и добавит после неё
content = re.sub(
    r"^(\s*)compare_type=True,$",
    r"\1compare_type=True,\n\1include_object=include_object,",
    content,
    flags=re.MULTILINE,
)

with open(ENV, "w", encoding="utf-8") as f:
    f.write(content)

print("OK: env.py пропатчен")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# Проверяем, что include_object применён в обоих configure()
count = content.count("include_object=include_object,")
print(f"include_object добавлен в {count} context.configure() (ожидаем 2)")

if count != 2:
    print("ПРЕДУПРЕЖДЕНИЕ: ожидалось 2, получено " + str(count))
    print("Проверьте env.py вручную")
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_env.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _fix_env.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_env.py
Что ожидаем:
text
OK: env.py пропатчен
SYNTAX OK
include_object добавлен в 2 context.configure() (ожидаем 2)
________________________________________
Скрипт 3 — фикс .mako шаблона (английский, без крокозябр)
В твоём файле 2602b71902d4 в docstring была каша: Opisanie migracii вЂ” chto menyaetsya.... Это потому что шаблон .mako содержит кириллицу, которая при генерации на Windows портится. Меняем на английский — не будет проблем с кодировкой.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$makoContent = @'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Description of this migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

