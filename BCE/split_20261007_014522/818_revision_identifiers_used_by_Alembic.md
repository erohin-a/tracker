<!-- Часть 818 из 1409 -->
# revision identifiers, used by Alembic
*Хлебные крошки:* revision identifiers, used by Alembic

[◀ Проверяем, что include_object применён в обоих configure()](817_Proveryaem_chto_include_object_primenen_v_oboih_configure.md) | [Оглавление](00_BCE_INDEX.md) | [revision identifiers, used by Alembic ▶](819_revision_identifiers_used_by_Alembic.md)

---

# revision identifiers, used by Alembic
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Apply this migration — what we do when upgrading the schema."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Rollback this migration — what we do when downgrading."""
    ${downgrades if downgrades else "pass"}
'@

[System.IO.File]::WriteAllText("D:\tracker\server\alembic\script.py.mako", $makoContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: script.py.mako переписан на английском" -ForegroundColor Green
________________________________________
Скрипт 4 — удалить .bak файл
.bak файл (76 КБ) — это старая, «грязная» версия ecb1e3f89300. Alembic его обычно игнорирует (расширение не .py), но лучше убрать, чтобы не путал.
powershell
$ErrorActionPreference = "Continue"
$bakPath = "D:\tracker\server\alembic\versions\ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py.bak"

if (Test-Path $bakPath) {
    Move-Item $bakPath "$env:TEMP\tracker_backup_$(Get-Date -Format yyyyMMdd_HHmmss).bak" -Force
    Write-Host "OK: .bak перемещён в $env:TEMP" -ForegroundColor Green
} else {
    Write-Host ".bak уже удалён" -ForegroundColor Yellow
}

Write-Host "`n=== Файлы в versions/ ===" -ForegroundColor Cyan
Get-ChildItem "D:\tracker\server\alembic\versions" | Format-Table Name, Length, LastWriteTime
Ожидаем: осталось ровно 4 файла .py + папка __pycache__ (если есть).
________________________________________
Скрипт 5 — быстрая проверка 939e3d0b6f4c (партиционирование)
Убеждаемся, что партиции действительно создаются в миграции.
powershell
$ErrorActionPreference = "Continue"
$path = "D:\tracker\server\alembic\versions\939e3d0b6f4c_partition_records_by_month.py"

Write-Host "=== Содержимое 939e3d0b6f4c ===" -ForegroundColor Cyan
Get-Content $path

Write-Host "`n=== Ключевые маркеры ===" -ForegroundColor Cyan
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
foreach ($m in @(
    "PARTITION BY RANGE",
    "PARTITION OF records",
    "records_2025",
    "records_2026",
    "records_2027",
    "records_default",
    "CREATE TABLE"
)) {
    if ($content.Contains($m)) {
        Write-Host "  ? $m" -ForegroundColor Green
    } else {
        Write-Host "  ? $m" -ForegroundColor Red
    }
}
Ожидаем: видны PARTITION BY RANGE и много PARTITION OF records. Если да — всё ок, сброс volume безопасен.
________________________________________
Скрипт 6 — сброс volume и подъём с нуля
Важно: это удалит всё — БД, партиции, зарегистрированные ПК. Раз данные тестовые — ок.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Останавливаем всё и удаляем volume ===" -ForegroundColor Cyan
docker compose down -v

Write-Host "`n=== Пересобираем образ (с учётом правок) ===" -ForegroundColor Cyan
docker compose build --no-cache api

Write-Host "`n=== Запускаем всё ===" -ForegroundColor Cyan
docker compose up -d
Start-Sleep -Seconds 25

Write-Host "`n=== Статус контейнеров ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи api (последние 40 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=40
Что ищем в логах:
text
tracker.server INFO Применение миграций Alembic...
alembic.runtime.migration INFO Running upgrade  -> 35d67a73f181, baseline
alembic.runtime.migration INFO Running upgrade 35d67a73f181 -> 939e3d0b6f4c, partition_records_by_month
alembic.runtime.migration INFO Running upgrade 939e3d0b6f4c -> ecb1e3f89300, add_schedules_roles...
alembic.runtime.migration INFO Running upgrade ecb1e3f89300 -> 2602b71902d4, add_employee_settings
tracker.server INFO Миграции Alembic успешно применены
Если увидим все 4 строки Running upgrade — победа.
________________________________________
Скрипт 7 — полная проверка БД
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== 1. Версия Alembic ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT * FROM alembic_version;"
Write-Host "Ожидаем: 2602b71902d4 (head)"

Write-Host "`n=== 2. Таблица employee_settings ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\d employee_settings"

Write-Host "`n=== 3. Таблица schedules (из ecb1e3f89300) ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\d schedules"

Write-Host "`n=== 4. Таблица admin_users ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\d admin_users"

Write-Host "`n=== 5. Партиции records (ДОЛЖНЫ БЫТЬ!) ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT tablename FROM pg_tables WHERE tablename LIKE 'records_%' AND tablename != 'records' ORDER BY tablename LIMIT 10;"

Write-Host "`n=== 6. Soft-delete колонки в records ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'records' AND column_name IN ('is_deleted', 'deleted_at', 'deleted_by');"

Write-Host "`n=== 7. Общее число таблиц ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname='public';"

Write-Host "`n=== 8. Endpoint /api/v1/client-config ===" -ForegroundColor Cyan
curl.exe -k -s "https://localhost/api/v1/client-config"
Что ожидаем:
Проверка	Ожидаемый результат
alembic_version	2602b71902d4
employee_settings	10 колонок (id, employee_id, reminder_* ? 4, end_of_day_* ? 2, updated_at, updated_by)
schedules	20 колонок
admin_users	11 колонок
Партиции records_*	? 5 строк (records_2025_01, records_2025_02, …)
Soft-delete в records	3 колонки
Всего таблиц	~25-30
/api/v1/client-config	JSON с 11 полями (включая reminder_* и end_of_day_*)
________________________________________
Порядок запуска
Запускай строго по порядку и пришли мне вывод после каждого:
Скрипт 1 — починка миграции 2602b71902d4 ? пришли Удалено операций и Осталось упоминаний.
Скрипт 2 — фикс env.py ? пришли include_object добавлен в N context.configure().
Скрипт 3 — .mako ? просто "OK".
Скрипт 4 — удаление .bak ? пришли список файлов в versions/.
Скрипт 5 — проверка 939e3d0b6f4c ? пришли маркеры ?/?.
Скрипт 6 — сброс volume + пересборка ? пришли логи API.
Скрипт 7 — полная проверка ? пришли выводы всех 8 блоков.
Не переходи к следующему, пока не подтвердил предыдущий. Особенно важно: если Скрипт 1 покажет records_*: 0 и employee_settings: 4 — только тогда идём дальше.
________________________________________
Что делаем после успешного запуска БД
Как только увидим 2602b71902d4 (head) и все проверки зелёные — продолжаем Спринт 5, часть A:
Этап 1 (следующее сообщение):
Патч /api/v1/client-config — читает X-Computer-Uid, находит employee_id, мержит глобальные дефолты + персональные из employee_settings.
Endpoint PUT /api/v1/client-settings — приём изменений от клиента (приоритет: сервер побеждает).
UI: страница /admin/employees/{id}/settings — форма с полями, где пусто = «как у всех».
Этап 2:
Клиентская часть A2: client/reminder.py (ActivityWatcher, ReminderDialog), патчи main.py, config.py.
Этап 3:
Возвращаемся к общему плану Спринта 2: роли (admin_users уже создана — надо довести до UI), API-ключи, планировщик, бэкапы, etc.
Запускай Скрипты 1?2?3?4?5 и присылай выводы. Не торопись с 6 (сброс volume) — сначала убедимся, что все патчи прошли корректно.
Пользователь запустил Скрипт 2 (фикс env.py), но получил неожиданный результат:
include_object добавлен в 1 context.configure() — а ожидалось 2.
Значит, в env.py только одна функция context.configure() содержит compare_type=True,. Второе может быть с другим отступом или без compare_type=True, вообще.
Также надо проверить: скрипт уже записал файл (после f.write). Значит, что-то уже пропатчено. Нужно проверить, что именно там сейчас.
Кстати, Сcript 1 (починка миграции) пользователь не запускал — он сразу перешёл к Скрипту 2. Это нормально, но надо проверить, что Скрипт 1 тоже сделан.
Давайте:
Посмотрим текущее состояние env.py.
Если только в одном configure — добавим во второй вручную.
Проблема: в env.py две функции context.configure() — в run_migrations_offline() и run_migrations_online(). В offline-версии я недавно писал:
python
context.configure(
    url=url,
    target_metadata=target_metadata,
    literal_binds=True,
    dialect_opts={"paramstyle": "named"},
    compare_type=True,   ? вот эта строка
)
А в online-версии:
python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,   ? вот эта строка
    include_schemas=False,
)
Возможно, в offline-версии compare_type=True, стоит с другим отступом, или за ним не идёт перевод строки. Или его нет.
Регекс r"^(\s*)compare_type=True,$" требует compare_type=True, на отдельной строке, начиная с пробелов. Если перед ним есть пробелы и после запятой сразу новый перевод строки — должно поймать. Но если, например, в offline-версии compare_type=True, стоит сразу после dialect_opts={...}, и regex ловит только последнее — хм, нет, regex ловит все совпадения, потому что используется re.sub без count.
Стоп. re.sub без count заменяет ВСЕ вхождения. Если только одна замена произошла, значит в env.py только одна строка точно соответствует ^(\s*)compare_type=True,$.
Возможно, в offline-версии этой строки нет вообще (я её писал в первой версии env.py, но потом при перезаписи мог убрать).
Давайте посмотрим на реальный env.py.
Также важно: файл уже записан. Значит, во все compare_type=True, добавлено include_object=include_object, — но их было 1.
Нужно:
Посмотреть текущий env.py.
Если в offline-функции нет compare_type=True, — добавить его вместе с include_object. Или добавить только include_object — для offline-режима это не критично, потому что offline не сравнивает схемы, а только пишет SQL.
Кстати, для offline-режима include_object не нужен. Он нужен только для online-режима (где autogenerate сравнивает). Так что даже если только в online — это нормально!
Но лучше добавить в оба для консистентности.
Дай посмотрю env.py.
________________________________________
План:
Показать текущий env.py.
Добавить во второй configure(), если нужно.
Проверить, что нигде нет SyntaxError.
Также напомнить про Скрипт 1 (починка миграции) — пользователь его не запускал.
И ещё важно: пользователь запустил Скрипт 2, но не Скрипт 1. По плану Скрипт 1 идёт первым. Надо напомнить.
Формат ответа:
Что видим — только одна замена.
Показать env.py — как есть.
Добавить второй include_object — если нужно.
Давай напишу простой скрипт для показа env.py.
?? В env.py только один context.configure() с compare_type=True,
Патч прошёл, но заменилось только одно место. Скорее всего, в run_migrations_offline() нет строки compare_type=True, — значит для offline-режима include_object и не нужен (в offline Alembic не сравнивает схему, а просто пишет SQL). Это не критично, но давай проверим.
________________________________________
Сначала — где мы в плане
Напомню: Скрипт 1 (починка миграции 2602b71902d4) ты не запускал. Мы сейчас сделали Скрипт 2. Ничего страшного, но потом не забудь вернуться к первому.
Важно: файл env.py уже изменён, второй прогон _fix_env.py ничего не сделает (там проверка if "def include_object" in content: SKIP).
________________________________________
Скрипт — показать текущее состояние env.py
Просто посмотрим, что сейчас в файле:
powershell
$ErrorActionPreference = "Continue"
$path = "D:\tracker\server\alembic\env.py"

Write-Host "=== env.py целиком ===" -ForegroundColor Cyan
Get-Content $path

Write-Host "`n=== Ключевые маркеры ===" -ForegroundColor Cyan
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

foreach ($m in @(
    "def include_object",
    "include_object=include_object",
    "compare_type=True",
    "def run_migrations_offline",
    "def run_migrations_online",
    "context.configure"
)) {
    $count = ([regex]::Matches($content, [regex]::Escape($m))).Count
    Write-Host "  $m : $count" -ForegroundColor $(if ($count -gt 0) { "Green" } else { "Red" })
}
Пришли мне вывод. Скорее всего увидим:
def include_object : 1 ?
include_object=include_object : 1 (только в online)
compare_type=True : 1
context.configure : 2 (offline + online)
Если так — это нормально, для offline-режима include_object не нужен. Оставляем как есть.
Но если окажется, что в online-версии include_object тоже нет — тогда допишем.
________________________________________
Что делаем дальше по плану
Ты пропустил Скрипт 1 (починка миграции). Давай вернёмся к нему — там как раз 30 секунд работы. Вот он ещё раз:
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

    if (stripped.startswith("op.create_table('records_") or
        stripped.startswith('op.create_table("records_')):
        skip_until_close = True
        continue

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

Размер файла после чистки: ~5.5 КБ

Осталось упоминаний в файле:
  'employee_settings': 4
  'records_2025_01': 0
  'records_2026_09': 0
  'records_default': 0
________________________________________
Порядок действий
Запусти диагностику env.py (скрипт выше) — пришли вывод.
Запусти Скрипт 1 (починка миграции) — пришли вывод.
После этого — Скрипт 3 (.mako), Скрипт 4 (удаление .bak), Скрипт 5 (проверка 939e3d0b6f4c).
Только потом Скрипт 6 (сброс volume).
Начнём с диагностики env.py — я по ней точно скажу, нужно ли добавлять include_object во второй context.configure().
Пользователь показал полный env.py. Всё правильно:
def include_object — 1 ?
include_object=include_object — 1 (только в online) ?
compare_type=True — 2 (в обоих)
def run_migrations_offline — 1 ?
def run_migrations_online — 1 ?
context.configure — 2 ?
Значит, всё в порядке. include_object не нужен в offline-режиме (там Alembic не сравнивает схему с БД, а просто пишет SQL). Так что предупреждение было ложным — просто мой шаблон искал compare_type=True, строго в конце строки, а в offline там ещё комментарий после запятой: compare_type=True, # otslezhivat.... Вот почему не заменилось.
Так что фикс env.py корректный, оставляем как есть.
Ещё замечаю: docstring env.py на латинице (Okruzhenie Alembic...), а комментарии в новом блоке — в крокозябрах. Значит, мой патч применился, но при записи файла кодировка где-то портится. Однако код при этом рабочий — это просто комментарии. Можно пофиксить, но не критично. Оставим на потом, когда будем переписывать env.py целиком.
Теперь идём по плану:
? Скрипт 2 (env.py) — готово
Скрипт 1 (починка миграции 2602b71902d4) — надо запустить (я его дал в прошлом сообщении, но пользователь запустил только env.py)
Скрипт 3 (.mako)
Скрипт 4 (удаление .bak)
Скрипт 5 (проверка 939e3d0b6f4c)
Скрипт 6 (сброс volume)
Скрипт 7 (проверка БД)
Давайте дам короткий ответ: подтверждаю, что env.py в порядке, и даю следующие шаги — чистку миграции + остальные.
Пользователь уже видел Скрипт 1 в прошлом сообщении. Но он его не запускал. Возможно, думал что сначала надо доделать с env.py. Скажу: env.py ок, переходим к Скрипту 1.
Формат ответа: коротко, чётко, по делу. Дам Скрипт 1 + Скрипты 3-5 одной пачкой, чтобы пользователь мог запустить по порядку. И обозначу, что после них — сброс volume.
? env.py в порядке — всё работает как надо
Разбор:
text
def include_object : 1                      ?
include_object=include_object : 1           ? (только в online — и это правильно)
compare_type=True : 2                       ? (в обоих configure)
def run_migrations_offline : 1              ?
def run_migrations_online : 1               ?
context.configure : 2                       ?
Почему только 1, а не 2: в offline-функции строка выглядит как compare_type=True, # otslezhivat... — с комментарием после запятой. Мой regex искал строго compare_type=True, в конце строки, поэтому не заменил. Но там и не нужно — offline-режим не сравнивает схему с БД, он просто генерирует SQL-скрипт. Так что всё корректно, оставляем как есть.
В .py файле docstring на латинице, а новый блок в крокозябрах — это косметика, на работу не влияет. Поправим когда будем переписывать env.py целиком (не сейчас).
________________________________________
Идём по плану. Запускай по очереди
Скрипт 1 — починка миграции 2602b71902d4 (ты его пропустил)
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

    if (stripped.startswith("op.create_table('records_") or
        stripped.startswith('op.create_table("records_')):
        skip_until_close = True
        continue

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
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_migration.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _fix_migration.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_migration.py
Ожидаем:
text
create_table: 37
drop_table: 37
drop_index: 111
create_index: 111
SYNTAX OK
Размер файла после чистки: ~5.5 КБ
'employee_settings': 4
'records_2025_01': 0
'records_2026_09': 0
'records_default': 0
________________________________________
Скрипт 3 — фикс .mako (английский шаблон)
powershell
$ErrorActionPreference = "Continue"

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

