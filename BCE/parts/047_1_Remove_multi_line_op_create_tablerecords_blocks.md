# 1. Remove multi-line op.create_table('records_...' blocks

*Часть 47 из 100. Источник: `BCE.md`.*

[◀ Identifikatory revizii (ispolzuyutsya Alembic dlya otslezhivaniya)](046_Identifikatory_revizii_ispolzuyutsya_Alembic_dlya_otslezhivaniya.md) | [Оглавление](00_BCE_INDEX.md) | [revision identifiers, used by Alembic ▶](048_revision_identifiers_used_by_Alembic.md)

---

# 1. Remove multi-line op.create_table('records_...' blocks
# Pattern: op.create_table('records_...' followed by any number of indented lines ending with `    )\n`
pattern_create = re.compile(
    r"\n    op\.create_table\('records_[^']*',.*?\n    \)\n",
    re.DOTALL
)
content = pattern_create.sub("\n", content)

# 2. Remove all single-line op.drop_index('records_...') calls
pattern_dropidx = re.compile(r"\n    op\.drop_index\('records_[^']*'.*?\)\n")
content = pattern_dropidx.sub("\n", content)

# 3. Remove all single-line op.drop_table('records_...') calls
pattern_droptbl = re.compile(r"\n    op\.drop_table\('records_[^']*'\)\n")
content = pattern_droptbl.sub("\n", content)

# 4. Remove all single-line op.create_index('records_...', ...) calls
pattern_createidx = re.compile(r"\n    op\.create_index\('records_[^']*'.*?\)\n")
content = pattern_createidx.sub("\n", content)

# Clean up multiple blank lines
content = re.sub(r"\n\n\n+", "\n\n", content)
Wait, but I need to be careful. The regex for create_table with DOTALL and non-greedy might match too much if there are multiple create_table calls. Let me use a more targeted approach:
Actually, the pattern \n op\.create_table\('records_[^']*',.*?\n \)\n with non-greedy .*? will match from op.create_table('records_... to the first \n )\n. Since the block only spans until that ), it should work.
But wait — in the downgrade block, there's also op.create_table('records_... — same pattern, will work.
Let me verify with a simpler approach — just check if it works and provide fallback.
Actually, let me just test with the specific patterns I see. Also I should handle the case where a create_table block ends with ) immediately followed by another line.
Let me write it as:
python
pattern_create = re.compile(
    r"    op\.create_table\('records_[^']*',\n(?:.*?\n)*?    \)\n",
    re.MULTILINE
)
Actually DOTALL isn't needed if I use (?:.*?\n)*? which matches lines. Let me use that.
Hmm, this is getting complicated. Let me use a line-by-line state machine approach instead. It's more robust:
python
import re

PATH = r"D:\tracker\server\alembic\versions\2602b71902d4_add_employee_settings.py"

with open(PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
skip_until_close = False

for line in lines:
    if skip_until_close:
        # Inside a multi-line create_table block for records_*
        if line.strip() == ")":
            skip_until_close = False
        continue
    
    # Check for multi-line op.create_table('records_...' or op.create_table(op.f('records_...
    stripped = line.strip()
    if stripped.startswith("op.create_table('records_") or stripped.startswith('op.create_table("records_'):
        skip_until_close = True
        continue
    
    # Single-line removals
    if stripped.startswith("op.drop_index('records_"):
        continue
    if stripped.startswith("op.drop_table('records_"):
        continue
    if stripped.startswith("op.create_index('records_"):
        continue
    if stripped.startswith('op.drop_index("records_'):
        continue
    if stripped.startswith('op.drop_table("records_'):
        continue
    if stripped.startswith('op.create_index("records_'):
        continue
    
    out.append(line)

new_content = "".join(out)
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
# Collapse triple+ newlines to double
new_content = re.sub(r"\n\n\n+", "\n\n", new_content)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Удалено операций:")
for k, v in skipped_counts.items():
    print(f"  {k}: {v}")

# Verify syntax
try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    exit(1)

# Verify remaining operations
remaining = []
for m in re.finditer(r"op\.(create_table|drop_table|create_index|drop_index)\(([^,)]+)", new_content):
    remaining.append(m.group(0)[:80])

print(f"\nОсталось операций: {len(remaining)}")
for r in remaining:
    print(f"  {r}")
Wait, the regex for remaining might not work well with nested parens. Let me simplify — just check specific strings:
python
print("\nПроверка содержимого:")
for pattern in [
    "'employee_settings'",
    "'records_2025_01'",
    "'records_2026_09'",
    "'records_default'",
]:
    count = new_content.count(pattern)
    print(f"  {pattern}: {count} раз")
Expected: employee_settings — appears 4 times (create_table + create_index + drop_index + drop_table), records_* — 0.
OK, let me finalize the response.
Actually one more thing — I should tell them that after this fix, when they apply the migration, only employee_settings will be created. That's the goal.
And for env.py fix, I'll give a Python patcher too.
Let me write it all now.
For env.py, the target function is run_migrations_online(). Inside, there's context.configure(...). I need to add include_object=include_object there, and define include_object above.
Actually, better: define it at module level near target_metadata = Base.metadata, and pass in both offline and online modes.
Let me write:
python
def include_object(object, name, type_, reflected, compare_to):
    """
    Фильтр для autogenerate.
    Исключаем партиционированные таблицы records_YYYY_MM и records_default —
    они не в metadata (это партиции PostgreSQL), и Alembic не должен
    пытаться их удалять или создавать.
    """
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True
Then in run_migrations_offline and run_migrations_online, add include_object=include_object to the context.configure(...) call.
The patcher:
python
ENV = r"D:\tracker\server\alembic\env.py"
with open(ENV, "r", encoding="utf-8") as f:
    content = f.read()

if "def include_object" in content:
    print("SKIP: already patched")
    exit(0)

# Add include_object after target_metadata
old = "target_metadata = Base.metadata"
new = '''target_metadata = Base.metadata


# ============================================================
# Фильтр для autogenerate
# ============================================================
# Исключаем партиционированные таблицы records_YYYY_MM и records_default.
# PostgreSQL показывает их в information_schema как обычные таблицы,
# но в Base.metadata их нет — только родительская "records".
# Без этого фильтра alembic revision --autogenerate пытается
# УДАЛИТЬ все партиции при генерации любой миграции.
# ============================================================
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True'''

content = content.replace(old, new, 1)

# Add include_object to context.configure in both offline and online
content = content.replace(
    "    context.configure(\n            url=url,\n            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True, # отслеживать изменения типов колонок\n        )",
    "    context.configure(\n            url=url,\n            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True,\n            include_object=include_object,\n        )"
)
Hmm, hardcoding the exact text to replace is fragile. Let me use a more robust approach — find compare_type=True in env.py and add include_object=include_object after it (only once per occurrence).
Actually, looking at my previous env.py:
python
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # отслеживать изменения типов колонок
    )
    ...

def run_migrations_online() -> None:
    connectable = engine_from_config(...)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=False,
        )
Both have compare_type=True,. So I can find all occurrences and add include_object=include_object, after each.
python
import re

# Find "compare_type=True," and add include_object after
content = re.sub(
    r"(compare_type=True,)",  # match
    r"\1\n            include_object=include_object,",
    content
)
But wait, in the offline case, indentation is 12 spaces for compare_type=True,? Let me check:
text
    context.configure(
        url=url,
        target_metadata=target_metadata,
        ...
        compare_type=True,  # отслеживать изменения типов колонок
    )
That's 8 spaces. And online:
text
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=False,
        )
That's 12 spaces.
So different indentations. The re.sub approach needs to preserve indentation... Actually since I'm inserting after and the resulting code will have same indentation as the matched line, let me just add a newline and same indent:
python
import re

def add_include_object(match):
    line = match.group(0)  # "compare_type=True,"
    # Detect indent by looking at the match position in the original
    # ... complex
Too complicated. Let me just do a straightforward .replace() with the exact strings.
Actually — since this is a one-time fix, let me be pragmatic:
python
# Online
content = content.replace(
    "            connection=connection,\n            target_metadata=target_metadata,\n            compare_type=True,",
    "            connection=connection,\n            target_metadata=target_metadata,\n            compare_type=True,\n            include_object=include_object,"
)

# Offline  
content = content.replace(
    "            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True,",
    "            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True,\n            include_object=include_object,"
)
Hmm, but I'm not 100% sure of the exact whitespace in the file. Let me use a regex that handles both:
python
import re

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

# 1. Добавляем функцию include_object после target_metadata
old_marker = "target_metadata = Base.metadata"
new_block = '''target_metadata = Base.metadata


# ============================================================
# Фильтр для autogenerate
# ============================================================
# Исключаем партиционированные таблицы records_YYYY_MM и records_default.
# PostgreSQL показывает их в information_schema как обычные таблицы,
# но в Base.metadata их нет — только родительская "records".
# Без этого фильтра alembic revision --autogenerate пытается
# УДАЛИТЬ все партиции при генерации любой миграции.
# ============================================================
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True'''

content = content.replace(old_marker, new_block, 1)

# 2. Добавляем include_object=include_object в оба context.configure(...)
# Используем regex, который сохраняет отступ
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
Скрипт 3 — фикс .mako шаблона (чтобы docstring не был в крокозябрах)
Заодно переведём шаблон миграций на английский — не будет проблем с кодировкой на Windows.
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

