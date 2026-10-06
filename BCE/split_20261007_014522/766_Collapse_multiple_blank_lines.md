<!-- Часть 766 из 1409 -->
# Collapse multiple blank lines
*Хлебные крошки:* Collapse multiple blank lines

[◀ Clean up multiple blank lines](765_Clean_up_multiple_blank_lines.md) | [Оглавление](00_BCE_INDEX.md) | [Collapse triple+ newlines to double ▶](767_Collapse_triple_newlines_to_double.md)

---

# Collapse multiple blank lines
new_content = re.sub(r"\n\n\n+", "\n\n", new_content)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)
This is cleaner. Let me finalize.
Also, I should add a permanent fix to env.py to exclude records_* tables from autogenerate. Alembic has include_object hook:
python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False  # Skip partition tables
    return True
And in context.configure(...), add include_object=include_object.
Let me also mention the mojibake issue with the .mako template. The Russian text "Opisanie migracii вЂ” chto menyaetsya i zachem." is a garbled version of "Описание миграции — что меняется и зачем." — this happens because the template was saved with the wrong encoding. The .mako file itself is probably UTF-8, but somewhere during generation the encoding got lost. Actually looking more carefully, this looks like the migration was generated on a Windows system where the console default encoding (cp1251?) got applied to the .mako template's Cyrillic characters.
The fix: change the .mako template to use English comments only, to avoid the issue entirely.
Or fix the encoding — but honestly, simpler to just use English in .mako.
Let me structure the response:
Diagnosis of the problem with the migration
Explain WHY (partition tables vs. SQLAlchemy metadata)
Script 1: Fix the migration file (remove spurious operations)
Script 2: Fix env.py to prevent this in the future (add include_object filter)
Script 3: Fix the .mako template to English comments
Script 4: Apply the migration
Verify
Let me write this cleanly.
Actually the user asked in Russian, so I should respond in Russian.
Also, I should keep in mind that this is Sprint 5, and we're in the middle of:
Part A1 (server settings for reminder) — partially done
We were supposed to do A2 (client side)
And the user is now implementing per-employee settings
So the context is: we're adding employee_settings table via Alembic, but the auto-generated migration is dangerous.
Let me write the response.
Response structure:
Часть 1. Диагноз — миграция опасна
Объяснение: автогенерация увидела партиции records_* как «лишние таблицы» и хочет их удалить
Почему: SQLAlchemy не знает про PostgreSQL partitioning
Что будет если применить как есть — все записи потеряются
Часть 2. Спасаем миграцию
Python-патчер, который удалит лишнее
Часть 3. Применяем миграцию
docker compose restart api (или upgrade head)
Часть 4. Фикс на будущее
env.py — добавить include_object, чтобы больше такого не было
.mako — перевести на английский (или UTF-8 с BOM)
.gitignore — игнорировать мусорные миграции, если такие будут
Let me write the patcher carefully.
Actually — wait, I need to double-check the regex. In the given migration, the block starts with:
text
    op.create_table('records_2027_06',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    ...
    sa.Column('deleted_by', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['computer_id'], ['computers.id'], name='records_computer_id_fkey'),
    sa.PrimaryKeyConstraint('id', 'client_ts', name='records_2027_06_pkey')
    )
The closing line is ) (4 spaces + )).
But the FK constraint line starts with sa.ForeignKeyConstraint — 4 spaces.
And the last line before ) is sa.PrimaryKeyConstraint(...) — 4 spaces.
So my line-by-line approach: I check line.strip() == ")" to detect the end. This works because the closing line's .strip() is just ).
Let me also handle the case where the create_table might end with ) but the closing might be inside a different structure. Actually all Alembic-generated create_table blocks end with a line that's just ) (4 spaces + close paren). So this should be safe.
But wait — if it's a nested structure, my logic might break. Let me use a more robust state machine that tracks indentation:
Actually, simpler approach: when I see op.create_table('records_, I skip lines until I see a line whose strip is ) AND the next line doesn't start with sa.. Hmm, that's fragile.
Or even simpler: skip until the depth returns to 0. Let me count parentheses:
python
skip_depth = 0
for line in lines:
    if skip_depth > 0:
        skip_depth += line.count("(") - line.count(")")
        continue
    if stripped.startswith("op.create_table('records_"):
        skip_depth = line.count("(") - line.count(")")
        if skip_depth <= 0:
            # Single-line, already done
            continue
        continue
    ...
Hmm, this gets complicated because line counting parentheses across multi-line strings.
Let me just use the simpler approach: skip until I see a line whose .strip() equals ).
Actually one more consideration — the FK constraint line contains ['computers.id'] with brackets [ and ], not ( and ). So that's fine, no ) in that line except within sa.ForeignKeyConstraint(...) which opens and closes on the same line — net 0.
Wait no — sa.ForeignKeyConstraint(['computer_id'], ['computers.id'], name='records_computer_id_fkey'), — the ( and ) are balanced. Good.
sa.PrimaryKeyConstraint('id', 'client_ts', name='records_2027_06_pkey') — balanced.
So counting parens per line and skipping until we go back to 0 should work:
python
skip_depth = 0
for line in lines:
    if skip_depth > 0:
        skip_depth += line.count("(") - line.count(")")
        continue
    stripped = line.strip()
    if stripped.startswith("op.create_table('records_"):
        skip_depth = line.count("(") - line.count(")")
        continue
    ...
Hmm but the first line op.create_table('records_2027_06', has 1 ( and 0 ) ? depth 1. Then subsequent lines have balanced parens ? depth stays 1. Final ) ? depth goes to 0.
Yeah, this works. Let me use this.
Actually even simpler — since the closing is always a line whose strip is ), let me use that:
python
skip_until_close = False
for line in lines:
    if skip_until_close:
        if line.strip() == ")":
            skip_until_close = False
        continue
    stripped = line.strip()
    if stripped.startswith("op.create_table('records_"):
        skip_until_close = True
        continue
    ...
This is cleanest. Let me go with this.
But wait — what if the create_table block's closing is not exactly ) but ) (with 4 spaces)? .strip() removes whitespace, so .strip() == ")" works.
What if there's a comment after the closing? Like ) # end? Looking at the generated file — no, Alembic generates clean ).
OK, going with this approach.
Let me write the full response now.
Один момент — important. The user's last command was to view the migration file. They haven't applied it yet. So we're at a good point to prevent disaster.
Also — I should note that the file was already written to disk with the mojibake in the docstring. That's not critical (it's just a comment), but we'll fix the template for future.
Let me also remember — the migration file was created, but not applied. The database still has the old schema (no employee_settings). So we need to:
Fix the migration file
Apply it
Also — I should note that the file naming is 2602b71902d4_add_employee_settings.py — the revision ID is 2602b71902d4.
Now writing.
I should also mention this is going to be a big issue going forward — every time we autogenerate, we'll get partition drops. So the env.py fix is essential.
Let me write it all.
Стоп — важно! Я вижу в миграции что-то интересное. Смотрю на downgrade:
text
op.create_table('records_2027_06',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    ...
    sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('deleted_by', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['computer_id'], ['computers.id'], name='records_computer_id_fkey'),
    sa.PrimaryKeyConstraint('id', 'client_ts', name='records_2027_06_pkey')
)
Interesting — the downgrade table has is_deleted, deleted_at, deleted_by columns! These columns were NOT in the original records table. So SQLAlchemy is picking up the CURRENT state of these partition tables from the DB, not from our metadata. Because we added those columns at some point via ALTER TABLE, but they might not be in the SQLAlchemy model? Wait — actually we did add is_deleted etc. via Alembic (in the previous Sprint we added soft delete). So the metadata should have them.
Hmm, but the autogenerate is treating each partition as a separate table because PostgreSQL exposes them that way in information_schema. And it's matching each partition's columns to... nothing in metadata. So it wants to drop them.
Actually, looking at the CREATE in downgrade — it recreates the partitions with all their current columns. So SQLAlchemy correctly detects they exist and their columns. Since records_2027_06 is not in Base.metadata, it wants to drop it. In downgrade, it recreates what was there before.
This is a fundamental problem with partitioned tables + Alembic autogenerate.
The fix in env.py is critical: include_object must return False for any table starting with records_ (except the parent records).
Or more precisely: skip any table that is a partition. How to detect? The PostgreSQL pg_class.relispartition column, or simply by name pattern. Name pattern is fine — all our partitions are records_YYYY_MM or records_default.
The parent table records is also in metadata. The partition tables are reflected from DB.
So:
python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_"):
        return False
    return True
This skips any table whose name starts with records_.
Now, another issue — if we later add a NEW column to the records parent table, SQLAlchemy would want to add it only to the parent. But PostgreSQL partitions inherit columns from parent automatically. So this should be fine.
Actually — hmm, for partitioned tables in PostgreSQL, when you ALTER TABLE parent ADD COLUMN, PostgreSQL automatically adds it to all partitions. But Alembic will only emit ALTER for the parent table, so it should work.
Alright, let me also handle the include_object for column-level checks:
python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True
Good.
Now let me also think about the .mako template. The template says:
text
"""${message}
...
Описание миграции — что меняется и зачем.
"""
The .mako file was saved by our PowerShell script with [System.Text.UTF8Encoding]::new($false) — UTF-8 without BOM. That should be fine. But the output shows mojibake. So the issue is that Alembic on Windows reads the .mako template and writes it with the system default encoding (cp1251), not UTF-8.
Actually, looking at the pattern of mojibake: Описание миграции — что меняется и зачем became Opisanie migracii вЂ” chto menyaetsya i zachem. This looks like UTF-8 bytes being interpreted as cp1252. The word "Описание" (Cyrillic) became "Opisanie" (Latin) — that's NOT a simple encoding issue, that's a transliteration!
Wait no, looking more carefully:
"Opisanie migracii" — is this a transliteration of "Описание миграции"?
"вЂ”" — this is UTF-8 em-dash (вЂ”) — that's UTF-8 bytes being read as cp1252
"chto menyaetsya i zachem" — transliteration of "что меняется и зачем"
So it seems like part of the text got transliterated and part got encoded wrong. Very strange. This suggests the .mako template was already mangled when we saved it.
Oh! I see. When we created the .mako file via PowerShell here-string with Cyrillic, and PowerShell saved it with UTF-8, but the WRITE of Alembic's output file used the OS default codepage...
Actually the simplest explanation: the .mako file itself is fine (UTF-8 with Cyrillic), but when Alembic runs the .mako to generate the migration, Python's file writing uses locale.getpreferredencoding() which on Russian Windows is cp1251. So the Cyrillic in the template gets written with cp1251 encoding, but the output file is then read as UTF-8 by us, showing mojibake.
Or the .mako file got saved wrong. Either way — easiest fix is to make the .mako template use pure ASCII/English.
Let me do that.
Alright, writing the response now.
Response outline:
?? СТОП — миграцию нельзя применять как есть!
Диагноз: автогенератор увидел партиции records_* как «лишние» и хочет их удалить. Если применить — потеряем все сырые записи.
Объяснение почему (кратко).
Что делаем:
Скрипт — почистим миграцию (удалим операции с records_*)
Скрипт — фикс env.py, чтобы больше не повторялось
Скрипт — фикс .mako (на английском)
Перезапуск и применение
Скрипт 1 — починка миграции
(here goes the Python patcher)
Скрипт 2 — фикс env.py
(include_object hook)
Скрипт 3 — .mako на английском
(full replacement)
Скрипт 4 — применение
(docker compose restart api)
Let me finalize the Python patcher code.
python
import re
import ast

PATH = r"D:\tracker\server\alembic\versions\2602b71902d4_add_employee_settings.py"

with open(PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
skip_until_close = False
skipped_counts = {
    "create_table": 0,
    "drop_table": 0,
    "drop_index": 0,
    "create_index": 0,
}

for line in lines:
    if skip_until_close:
        if line.strip() == ")":
            skip_until_close = False
            skipped_counts["create_table"] += 1
        continue
    
    stripped = line.strip()
    
    # Multi-line op.create_table('records_...' 
    if (stripped.startswith("op.create_table('records_") or 
        stripped.startswith('op.create_table("records_')):
        skip_until_close = True
        continue
    
    # Single-line removals
    if (stripped.startswith("op.drop_index('records_") or 
        stripped.startswith('op.drop_index("records_')):
        skipped_counts["drop_index"] += 1
        continue
    if (stripped.startswith("op.drop_table('records_") or 
        stripped.startswith('op.drop_table("records_')):
        skipped_counts["drop_table"] += 1
        continue
    if (stripped.startswith("op.create_index('records_") or 
        stripped.startswith('op.create_index("records_')):
        skipped_counts["create_index"] += 1
        continue
    
    out.append(line)

new_content = "".join(out)
