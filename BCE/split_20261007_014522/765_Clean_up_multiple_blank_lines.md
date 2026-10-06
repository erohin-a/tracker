<!-- Часть 765 из 1409 -->
# Clean up multiple blank lines
*Хлебные крошки:* Clean up multiple blank lines

[◀ 4. Remove all single-line op.create_index('records_...', ...) calls](764_4_Remove_all_single_line_op_create_indexrecords_calls.md) | [Оглавление](00_BCE_INDEX.md) | [Collapse multiple blank lines ▶](766_Collapse_multiple_blank_lines.md)

---

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
