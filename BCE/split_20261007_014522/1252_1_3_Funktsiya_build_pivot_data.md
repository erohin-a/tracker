<!-- Часть 1252 из 1409 -->
# 1.3 Функция _build_pivot_data
*Хлебные крошки:* 1.3 Функция _build_pivot_data

[◀ 1.2 Эндпоинт pivot-data](1251_1_2_Endpoint_pivot_data.md) | [Оглавление](00_BCE_INDEX.md) | [Print line numbers with content for inspection ▶](1253_Print_line_numbers_with_content_for_inspection.md)

---

# 1.3 Функция _build_pivot_data
c, n = re.subn(
    r'\ndef _build_pivot_data\([^\)]*\)[^\n]*\n(?:[^\n]*\n)*?(?=\n\n(?:def |@router\.|# =)|\Z)',
    '\n',
    c, count=1
)
print(f"  _build_pivot_data function removed: {n}")

p.write_text(c, encoding="utf-8")
print(f"OK web_admin.py: {orig} -> {len(c)}")
Hmm, the regex (?:[^\n]*\n)*? is greedy/non-greedy. Non-greedy with (?=...) should work but regex backtracking with [^\n]* can be slow. Better to use (?:.*\n)*? with DOTALL not needed.

Let me test in my head for _build_pivot_data:

Pattern: \ndef _build_pivot_data\([^\)]*\)[^\n]*\n(?:[^\n]*\n)*?(?=\n\n(?:def |@router\.|# =)|\Z)

Actually the \n\n in lookahead means end at blank line + def. But if function has blank lines inside, non-greedy will stop at first \n\n that's followed by def/@router/#=. Good.

But wait, (?:[^\n]*\n)*? — this matches any line. Non-greedy. When it sees \n\n followed by def, it stops. This should work.

But there's a risk: what if there's a blank line inside the function followed by a nested def? Unlikely in this case.

Actually let me simplify: I'll use an approach that reads lines and finds boundaries. That's cleaner and more predictable.

Actually, let me be pragmatic. This is getting too complex without seeing the actual file. Let me:

Ask user to run a script that dumps specific sections of web_admin.py to a text file

I'll write the patcher based on that

The extraction script:

python
from pathlib import Path
p = Path(r"D:\tracker\server\web_admin.py")
lines = p.read_text(encoding="utf-8").splitlines()
