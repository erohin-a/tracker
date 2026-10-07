# Ищет все упоминания "pivot" и "pdf" в проекте, чтобы аккуратно удалить функционал.

*Часть 96 из 100. Источник: `BCE.md`.*

[◀ 2. Структура проекта](095_2_Struktura_proekta.md) | [Оглавление](00_BCE_INDEX.md) | [Делает бэкапы всех правленых файлов в D:\tracker\_backup_remove_pivot_pdf\<дата_время>\ ▶](097_Delaet_bekapy_vseh_pravlenyh_faylov_v_D_tracker_backup_remove_pivot_pd.md)

---

# Ищет все упоминания "pivot" и "pdf" в проекте, чтобы аккуратно удалить функционал.
import os
import re

ROOT = r"D:\tracker"
SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules", "dist", "build", ".idea", ".vscode"}
PATTERNS = [re.compile(r"pivot", re.IGNORECASE), re.compile(r"\bpdf\b", re.IGNORECASE)]
EXTS = {".py", ".html", ".js", ".md", ".txt", ".json", ".ini", ".bat", ".ps1", ".css", ".yml", ".yaml", ".env"}

hits = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in EXTS:
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            for p in PATTERNS:
                if p.search(line):
                    hits.setdefault(path, []).append((i, line.rstrip()))
                    break

for path, items in sorted(hits.items()):
    rel = os.path.relpath(path, ROOT)
    print(f"\n=== {rel} ({len(items)} hits) ===")
    for i, line in items[:25]:
        print(f"  {i}: {line[:200]}")
    if len(items) > 25:
        print(f"  ... и ещё {len(items) - 25}")

print(f"\nВсего файлов с упоминаниями: {len(hits)}")
Запусти:

powershell
cd D:\tracker
python tools\find_pivot_pdf.py
Что мне нужно от тебя
Пришли весь вывод этого скрипта. Дальше я:

Составлю точный список файлов и строк на удаление.

Дам Python-патчер, который:

уберёт роуты /admin/reports/pivot и /admin/api/pivot-data;

удалит шаблон reports_pivot.html (или вынесет в _unused/);

уберёт пункт «Pivot» из меню;

уберёт PDF-ветку из экспорта отчётов (оставит CSV/XLSX);

уберёт ссылки на PivotTable.js из base.html.

Проверим: docker compose down && docker compose up -d --build, откроем отчёты, убедимся, что CSV/XLSX работают, а pivot/PDF в меню больше нет.

Обновлю в KB файлы 02_METRICS\03_PIVOT.md и 02_METRICS\04_EXPORTS.md, а также HANDOFF.md (убираем пункты про pivot и PDF) — и напомню про update_site.bat.

Жду вывод скрипта.

The user wants to remove pivot and PDF. Let me create a Python patcher that removes both features cleanly.

Key files to modify:

server/web_admin.py - remove pivot route, pivot API endpoint, _build_pivot_data function, PDF rendering code, PDF branch in export

server/templates/reports_pivot.html - delete file (or move to _unused)

server/templates/reports.html - remove PDF option from dropdown

server/templates/report_result.html - remove PDF button

server/i18n.py - remove PDF translation keys

docs\_sidebar.md - remove Pivot link

Also need to check the templates/base.html for pivot link in navigation - it wasn't in the grep results, but let me search.

Wait, the grep shows reports_pivot.html has 54 hits and the menu link isn't shown in base.html. Let me check - probably in docs\03_SERVER\09_TEMPLATES.md it says "Данные: Отчёты, Pivot, Сессии, Календарь, Аудит" - so pivot link is somewhere. Let me be safe and search within templates directory.

Actually, let me focus on what I know for sure:

web_admin.py has pivot route at 1205, _build_pivot_data at 1832, pivot endpoint at 2033, PDF at 2124 (if fmt == "pdf"), PDF render at 4645

reports.html has PDF option at 92

report_result.html has PDF button at 321-324

i18n.py has btn.download_pdf and btn.download_pdf_full

Let me write a patcher. I need to be careful about Python patchers with here-strings >30 lines — user said use Python patchers.

Let me look at how the code structure is. From the grep:

Line 1205: @router.get("/reports/pivot"...)

Line 1222: return templates.TemplateResponse("reports_pivot.html"...)

Line 1832: def _build_pivot_data(...)

Line 2033: @router.post("/api/pivot-data")

Line 2034: def pivot_data(

Line 2057: rows = _build_pivot_data(...)

Line 2124: if fmt == "pdf":

Line 4645: # PDF-рендер отчёта

I need to see the actual code around these lines to write a proper patcher. But I should just write a patcher that:

Finds the pivot route (from @router.get("/reports/pivot" to the end of the function)

Finds _build_pivot_data function (from def _build_pivot_data to next def)

Finds the pivot-data endpoint (from @router.post("/api/pivot-data" to next @router or def)

Removes PDF branch in export

Removes PDF rendering function

Let me write a careful patcher. I'll use regex-based removal.

Actually, given the complexity, maybe I should give the user a patcher script that:

Reads web_admin.py

Removes specific code blocks by markers

Writes back

But I need to know the exact structure. Let me ask the user to first show me the sections of web_admin.py around those lines, OR write a patcher that works with regex and prints warnings if markers not found.

Actually, better approach: write a patcher that uses regex to find and remove blocks. Use anchors like:

Route pivot: @router.get("/reports/pivot" until the next @router. decorator

Function _build_pivot_data: def _build_pivot_data until \n\ndef or \n\n@router

API endpoint: @router.post("/api/pivot-data" until next @router.

PDF branch: if fmt == "pdf": ... this is tricky, need to know how it's structured

PDF render section: # PDF-рендер отчёта until next major marker

Hmm, this is risky. Let me propose a two-step approach:

First, user runs a script that extracts the relevant sections to a text file

Then I write the patcher based on that

OR, simpler: I write a patcher that does the removal and prints what it removed + warnings. If something doesn't match, it prints and doesn't crash.

Let me go with that. I'll write it as a Python script with clear markers.

Let me draft the patcher. I need to be careful about:

Removing function/blocks with proper boundaries

Not breaking the file

Plan for web_admin.py:

Remove from @router.get("/reports/pivot" up to (but not including) the next @router. decorator

Remove _build_pivot_data function: from def _build_pivot_data up to \n\n@router or \n\ndef at same indent level

Remove @router.post("/api/pivot-data") route to next @router.

PDF branch: if fmt == "pdf": — need to know indentation and structure. Common pattern:

python
if fmt == "pdf":
    ...
    return ...
followed by elif or next block.

PDF rendering function _render_pdf or similar

Let me write the patcher with multiple regexes, each of which prints SUCCESS or WARN.

Actually, let me ask the user to first dump the relevant sections:

web_admin.py lines 1200-1240 (pivot route)

web_admin.py lines 1820-1870 (_build_pivot_data)

web_admin.py lines 2025-2080 (pivot endpoint)

web_admin.py lines 2110-2140 (PDF branch)

web_admin.py lines 4640-4890 (PDF render)

Then I can write exact patchers.

Hmm, but that's a lot of back-and-forth. Let me just write a robust patcher that uses markers.

Actually the safest approach: use the markers I see in the file. Let me write a patcher.

For web_admin.py:

python
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\web_admin.py")
content = PATH.read_text(encoding="utf-8")
original_len = len(content)

# 1. Удаляем роут pivot-страницы
# Ищем от `@router.get("/reports/pivot"` до следующего @router. на верхнем уровне
content, n1 = re.subn(
    r'\n@router\.get\("/reports/pivot"[^\n]*\n(?:.*?\n)*?(?=@router\.)',
    '\n',
    content,
    count=1,
)

# 2. Удаляем эндпоинт pivot-data
content, n2 = re.subn(
    r'\n@router\.post\("/api/pivot-data"\)\n(?:.*?\n)*?(?=@router\.)',
    '\n',
    content,
    count=1,
)

# 3. Удаляем функцию _build_pivot_data
content, n3 = re.subn(
    r'\ndef _build_pivot_data\(.*?(?=\n\n(?:def |@router|# =))',
    '',
    content,
    count=1,
    flags=re.DOTALL,
)

# 4. PDF: удаляем ветку if fmt == "pdf"
# Осторожно — нужно посмотреть структуру
# ...

PATH.write_text(content, encoding="utf-8")
print(f"OK: web_admin.py {original_len} -> {len(content)}")
This is getting messy. Let me take a different approach.

Simplest robust approach:

Back up the file

For each route/function, use start/end markers and remove between them

Print what was removed

Let me write it more carefully. Actually let me look at the file to understand structure. I'll ask the user to run a small extraction script.

OK here's my decision: ask user to run a script that dumps the relevant sections. Then I write an exact patcher. This is the most reliable with a non-programmer user.

Actually, let me try one more thing: write a patcher that works with these anchors:

Find line with @router.get("/reports/pivot" → find end at next line starting with @router. (exactly, no leading space)

Find line with def _build_pivot_data → find end at next line starting with def or @router.

Find line with @router.post("/api/pivot-data") → find end at next @router.

Find if fmt == "pdf": → find end at next if fmt or elif fmt at same indent or next # === section

The tricky part is PDF. Let me look for hints in the grep:

Line 2124: if fmt == "pdf": — this is within the generate_report route

Line 4645: # PDF-рендер отчёта — this is a section for _render_pdf

Line 4883: buf, media_type="application/pdf", — this is the return statement

Line 4885: f"attachment; filename=report_{date_from}_{date_to}.pdf"

So the structure is probably:

text
@router.post("/reports/generate")  # or similar
def generate_report(...):
    ...
    if fmt == "html": ...
    elif fmt == "xlsx": ...
    elif fmt == "csv": ...
    elif fmt == "pdf":
        ...
    
    # or
    if fmt == "pdf":
        return _render_pdf(...)
Let me write a two-step approach: first a diagnostic script that shows me the exact context, then the patcher.

Actually let me just write a comprehensive patcher that's resilient:

python
# remove_pivot_pdf.py
import re
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP_DIR = ROOT / "_backup_remove_pivot_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def backup(path):
    rel = path.relative_to(ROOT)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)

# ============================================================
# 1. server/web_admin.py
# ============================================================
p = ROOT / "server" / "web_admin.py"
backup(p)
c = p.read_text(encoding="utf-8")
orig = len(c)

# 1.1 Роут pivot-страницы
c, n = re.subn(
    r'\n@router\.get\("/reports/pivot"[^\n]*\n(?:[^\n]*\n)*?(?=@router\.|\Z)',
    '\n',
    c, count=1
)
print(f"  reports/pivot route removed: {n}")

# 1.2 Эндпоинт pivot-data
c, n = re.subn(
    r'\n@router\.post\("/api/pivot-data"\)\n(?:[^\n]*\n)*?(?=@router\.|\Z)',
    '\n',
    c, count=1
)
print(f"  api/pivot-data endpoint removed: {n}")

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
# Print line numbers with content for inspection
# Sections around: 1205, 1832, 2033, 2124, 4645, 4885
ranges = [(1195, 1240), (1820, 1880), (2025, 2080), (2110, 2150), (4630, 4900)]
out = Path(r"D:\tracker\_inspect_web_admin.txt")
with out.open("w", encoding="utf-8") as f:
    for a, b in ranges:
        f.write(f"\n=== lines {a}..{b} ===\n")
        for i in range(max(0, a-1), min(len(lines), b)):
            f.write(f"{i+1:5}: {lines[i]}\n")
print(f"OK: {out}")
Then user pastes the content. That's a lot to paste though.

Alternative: ask user to just run a smarter patcher that I write now. If it fails, we try again.

OK let me just go with the patcher and make it print warnings. User is non-programmer, but running one script is fine. If something fails, we iterate.

Let me write it carefully. I'll write the patcher as a Python file that:

Backs up everything to _backup_remove_pivot_pdf/

Removes pivot route, endpoint, function from web_admin.py (with clear markers printed)

Removes PDF branch

Removes PDF rendering section

Removes PDF option from reports.html

Removes PDF button from report_result.html

Removes PDF keys from i18n.py

Renames reports_pivot.html to _unused_reports_pivot.html

Removes Pivot line from _sidebar.md

Let me write it.

For the PDF rendering section starting at line 4645 # PDF-рендер отчёта: it's likely delimited by a big comment box like:

text
# ============================================================
# PDF-рендер отчёта
# ============================================================
So I can remove from that box to the next # ====... section.

For the PDF branch if fmt == "pdf" at 2124 — let me assume it's:

python
    if fmt == "pdf":
        ...
        return ...
or

python
    elif fmt == "pdf":
        ...
        return ...
I'll match \n (el)?if fmt == "pdf":\n(?: .*\n|\n)*? and stop at next if fmt or elif fmt at same indent, or end of function.

Actually this is really fragile. Let me ask the user to run an inspection script first that outputs the relevant sections, then I'll write the patcher.

Decision: two-phase.

Send inspection script.

After user runs it and pastes output, send patcher.

Let me write the inspection script compactly.

Actually, I want to minimize round trips. Let me just write a patcher with regex, and if it fails on some parts, it prints "WARN" and I fix those specifically.

Let me write it now.

python
# D:\tracker\tools\remove_pivot_pdf.py
"""Удаляет pivot и PDF из проекта «Трекер»."""
import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP = ROOT / "_backup_remove_pivot_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")

def backup(path: Path):
    rel = path.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)

def remove_block(text, pattern, name, flags=re.DOTALL):
    new, n = re.subn(pattern, "", text, count=1, flags=flags)
    if n:
        print(f"  [OK] {name}: удалено {len(text)-len(new)} симв.")
    else:
        print(f"  [WARN] {name}: не найдено")
    return new

# ============================================================
# 1. web_admin.py
# ============================================================
print("\n=== server/web_admin.py ===")
p = ROOT / "server" / "web_admin.py"
backup(p)
c = p.read_text(encoding="utf-8")
orig = len(c)

# 1.1 pivot-страница: @router.get("/reports/pivot" ... до следующего @router.
c = remove_block(
    c,
    r'@router\.get\("/reports/pivot".*?(?=\n@router\.)',
    "роут /reports/pivot",
)

# 1.2 pivot-data: @router.post("/api/pivot-data") ... до следующего @router.
c = remove_block(
    c,
    r'@router\.post\("/api/pivot-data"\).*?(?=\n@router\.)',
    "эндпоинт /api/pivot-data",
)

# 1.3 _build_pivot_data ... до следующего \ndef или \n@router или \n# ===
c = remove_block(
    c,
    r'\ndef _build_pivot_data\(.*?(?=\n(?:def |@router\.|# =))',
    "функция _build_pivot_data",
)

# 1.4 PDF-ветка: 'if fmt == "pdf":' или 'elif fmt == "pdf":'
# Убираем от строки с проверкой до следующего if/elif fmt или return/конца
c = remove_block(
    c,
    r'\n    (?:el)?if fmt == "pdf":\n(?:        .*\n|\n)*?(?=\n    (?:el)?if fmt|\n    return|\n\n@router|\n\n# =)',
    "ветка if fmt == \"pdf\"",
)

# 1.5 PDF-рендер: секция '# PDF-рендер отчёта' до следующего '# ===' блока
c = remove_block(
    c,
    r'\n# =+\n# PDF-рендер отчёта\n# =+\n.*?(?=\n# =+\n# |\Z)',
    "секция PDF-рендер",
)

# 1.6 импорт reportlab, если есть
c, n = re.subn(r'\n(?:from reportlab[^\n]*\n|import reportlab[^\n]*\n)', '\n', c)
print(f"  [i] удалено импортов reportlab: {n}")

p.write_text(c, encoding="utf-8")
print(f"OK web_admin.py: {orig} -> {len(c)}")

# ============================================================
# 2. reports.html — убрать опцию PDF
# ============================================================
print("\n=== server/templates/reports.html ===")
p = ROOT / "server" / "templates" / "reports.html"
if p.exists():
    backup(p)
    c = p.read_text(encoding="utf-8")
    c, n = re.subn(r'\s*<option value="pdf">PDF</option>', '', c)
    p.write_text(c, encoding="utf-8")
    print(f"  [{'OK' if n else 'WARN'}] опция PDF: {n}")
else:
    print("  [skip] нет файла")

# ============================================================
# 3. report_result.html — убрать кнопку PDF
# ============================================================
print("\n=== server/templates/report_result.html ===")
p = ROOT / "server" / "templates" / "report_result.html"
if p.exists():
    backup(p)
    c = p.read_text(encoding="utf-8")
    # Убираем form с fmt=pdf
    c, n1 = re.subn(
        r'\s*<form[^>]*>\s*<input type="hidden" name="fmt" value="pdf">.*?</form>',
        '',
        c, flags=re.DOTALL,
    )
    if n1 == 0:
        # Fallback: просто удалить кнопку и hidden
        c, n2 = re.subn(r'\s*<input type="hidden" name="fmt" value="pdf">', '', c)
        c, n3 = re.subn(r'\s*<button[^>]*>📄 Скачать PDF</button>', '', c)
        print(f"  [i] fallback: hidden={n2}, button={n3}")
    else:
        print(f"  [OK] форма PDF: {n1}")
    p.write_text(c, encoding="utf-8")
else:
    print("  [skip] нет файла")

# ============================================================
# 4. i18n.py — убрать ключи PDF
# ============================================================
print("\n=== server/i18n.py ===")
p = ROOT / "server" / "i18n.py"
if p.exists():
    backup(p)
    c = p.read_text(encoding="utf-8")
    c, n = re.subn(
        r'\n\s*"btn\.download_pdf(?:_full)?":\s*\{[^\}]*\},?',
        '',
        c,
    )
    p.write_text(c, encoding="utf-8")
    print(f"  [{'OK' if n else 'WARN'}] ключей PDF: {n}")
else:
    print("  [skip] нет файла")

# ============================================================
# 5. reports_pivot.html — перенести в _unused
# ============================================================
print("\n=== server/templates/reports_pivot.html ===")
p = ROOT / "server" / "templates" / "reports_pivot.html"
if p.exists():
    backup(p)
    dst = ROOT / "server" / "templates" / "_unused_reports_pivot.html.txt"
    p.rename(dst)
    print(f"  [OK] переименован в {dst.name}")
else:
    print("  [skip] нет файла")

# ============================================================
# 6. docs\_sidebar.md — убрать Pivot
# ============================================================
print("\n=== docs/_sidebar.md ===")
p = ROOT / "docs" / "_sidebar.md"
if p.exists():
    backup(p)
    c = p.read_text(encoding="utf-8")
    c, n = re.subn(r'\s*-\s*\[Pivot-таблица\]\([^\)]*\)\n?', '\n', c)
    p.write_text(c, encoding="utf-8")
    print(f"  [{'OK' if n else 'WARN'}] Pivot в сайдбаре: {n}")
else:
    print("  [skip] нет файла")

print(f"\nВсе бэкапы: {BACKUP}")
print("Готово. Дальше: docker compose down && docker compose up -d --build")
Hmm wait, the regex r'\n@router\.get\("/reports/pivot".*?(?=\n@router\.)' with DOTALL — .*? matches everything including newlines. (?=\n@router\.) requires \n followed by @router. at start of line. Good.

But issue: .*? with DOTALL can match newlines. Fine.

For 1.4 PDF branch, the regex \n (?:el)?if fmt == "pdf": — this matches exactly 4 spaces indent. Then \n(?: .*\n|\n)*? matches lines starting with 8 spaces or blank lines. Lookahead (?=\n (?:el)?if fmt|\n return|\n\n@router|\n\n# =).

Hmm, but the \n return might occur inside the if block. Actually return inside the if block would be at 8 spaces indent, so \n return. Then after block ends at 4 spaces, next is \n (blank + 4 spaces) which would match \n (?:el)?if fmt. But what if next statement is \n return ...? Then the block ends. That's probably fine to also end at — but wait, if the PDF branch ends with a return and the whole function ends after it... Actually no, HTML/CSV/XLSX come first probably.

This is really fuzzy. Let me be more conservative. Actually, the safest is: keep PDF functionality in backend (it's harmless), just remove the UI options. User just doesn't want to use it.

Actually the user said "PDF-экспорт тоже удаляем" - remove it. So backend cleanup is desired too.

OK let me not overthink. Let me write the patcher and accept that some parts may need iterative fixes.

Actually, let me also handle the case where 1.4 fails. If it fails, the PDF branch remains but is unreachable (since UI doesn't call it). Not great but not fatal.

Let me also think about the PDF-рендер section 4645. Looking at grep: line 4645 says # PDF-рендер отчёта. And around line 4883 is the return statement. So the section goes from ~4640 to ~4890.

I'll match from # =+\n# PDF-рендер отчёта\n# =+\n to the next \n# =+\n# or end of file. That should be safe if the file uses that section divider pattern.

Let me finalize the patcher. I'll write it now.

One more consideration: _report_row_to_list might be used only by PDF? Let me check the grep: line 11466 says # 1. _report_row_to_list — добавляем 3 колонки и pivot-колонки. So _report_row_to_list is used for Excel/HTML too, not just PDF. Keep it.

Also _pdf_table_data and _render_pdf — these are in the PDF-рендер section, removed with section.

Let me also check if there's an import of _build_pivot_data or something. Probably not.

Also check PROJECT_SNAPSHOT_...txt — it's a snapshot file, not code. Skip.

Also, the user's HANDOFF.md mentions these — we'll update KB after code is fixed.

OK let me write it. And I'll also address the update to HANDOFF.md etc. later.

Let me also add: after removing the pivot route from web_admin.py, there might be an import of reports_pivot.html or template listing — no, templates are loaded by name.

Let me also check if base.html has a link to pivot page. The grep didn't find pivot in base.html, so probably the menu is elsewhere. Actually docs\03_SERVER\09_TEMPLATES.md says "Данные: Отчёты, Pivot, Сессии, Календарь, Аудит" so there's a navigation somewhere. Let me search more broadly... The grep results don't show any other .html file (only report_result.html, reports.html, reports_pivot.html). So maybe the pivot link is inside reports.html as a tab? Let me handle it — add a rule to reports.html removing <a href="/admin/reports/pivot">... links.

Actually, let me look again... the grep output for reports.html shows only 1 hit (option value="pdf"). So the pivot link is NOT in reports.html.

Hmm, where is it? Maybe in base.html via an {% if %} block, or it was dynamically generated. Let me add a rule: search for reports/pivot in ALL templates.

Actually, simplest: after the patcher, run a grep again and fix manually if anything remains.

Let me write it.

Also — one important thing: the reports.html option for PDF, when removed, might leave the default fmt as pdf if it was selected. Let me also check that html/csv/xlsx options remain.

OK writing the final script now.

Let me reconsider the regex for the pivot route. Line 1205: @router.get("/reports/pivot", response_class=HTMLResponse). The route function ends before the next @router. — that's line 1225 or so (since return is at 1222). So from 1205 to ~1225. Lookahead (?=\n@router\.) works.

But wait, what if there's another decorator after? Like @router.get("/reports/pivot") then @router.get("/other") immediately? Then non-greedy .*? stops at first \n@router.. But between them, the whole function body of pivot_page would be included. Good.

OK. Let me also handle: after removing the pivot route, there might be a blank line issue. I'll add \n cleanup at the end.

Let me write the final patcher.

Actually one thing: the section divider comment. Looking at HANDOFF.md's content for PDF-рендер:

text
# ============================================================
# PDF-рендер отчёта
And the surrounding context probably:

text
# ============================================================
# PDF-рендер отчёта
# ============================================================
...code...

# ============================================================
# Что-то ещё
# ============================================================
So regex r'\n# =+\n# PDF-рендер отчёта\n# =+\n.*?(?=\n# =+\n# |\Z)' should work.

But what if # PDF-рендер отчёта doesn't have a closing # === line right before the code? Let me just match from \n# PDF-рендер отчёта\n to the next \n# ==== section or end.

I'll use: r'\n# =+\n# PDF-рендер отчёта\n# =+\n.*?(?=\n# =+\n# |\Z)'

Actually maybe there's not a # === right before it. From the grep: "marker = '# ============================================================\n# PDF-рендер отчёта'". So the marker is # ===\n# PDF-рендер отчёта. So yes there's a # === before it.

OK final. Let me write.

I'll write the file content and give instructions. Let me keep it under 30 lines per here-string... no wait, I'll use a Python file. User said to use Python patchers. So write the file via here-string or however. Actually user writes the .py file via editor or notepad.

Let me give the user the script as a code block that they paste into D:\tracker\tools\remove_pivot_pdf.py.

Actually the script is long. Let me split into logical chunks or just provide it all. It's fine to be long since it's a saved file, not a here-string.

Let me write it. I'll use the Python patcher approach.

Actually, on reflection, I realize I should keep it simpler. Let me split into:

Part 1: code cleanup (web_admin.py, templates, i18n, sidebar)
Part 2: KB updates (docs)

For Part 1: use remove_block by regex with verbose output.

Let me write it.

One more consideration for the regex on the PDF branch. Actually, let me use a more targeted approach. Let me look for the pattern in web_admin.py where the report generation ends with:

text
    if fmt == "pdf":
        ...
        return StreamingResponse(
            buf, media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.pdf"},
        )
The signature: return StreamingResponse(\n buf, media_type="application/pdf", is at line 4883. So PDF branch's return might be at 4883-4885 area... but that's in the PDF render section. Hmm.

Wait, line 2124 if fmt == "pdf": and line 4883 buf, media_type="application/pdf" are far apart. So the PDF render function is at 4645-4890, and the branch at 2124 probably calls it:

python
if fmt == "pdf":
    return _render_report_pdf(db, rows, ...)  # calls function
Or maybe the branch at 2124 IS at the top of a function that renders, and the actual PDF rendering happens in the same block down to 4885? No, that doesn't make sense.

Let me guess: there's a route like @router.post("/reports/generate") with a big if/elif chain (html/xlsx/csv/pdf) around line 2124, and separately there's a def _render_report_pdf(...) at ~4645. So the branch at 2124 is like:

python
    if fmt == "pdf":
        return _render_report_pdf(...)
    elif fmt == "xlsx":
        ...
So the PDF branch at 2124 is small (a few lines). Then the function definition _render_report_pdf at 4645 is a separate block.

OK, for the branch I'll use:

text
r'\n    if fmt == "pdf":\n(?:        .*\n)+?(?=\n    (?:el)?if |\n    return |\n\n)'
Let me just try it. If it fails, user reports WARN and we fix.

Alternatively, since I'm uncertain, let me NOT try to remove the PDF branch automatically. Just remove the UI option (reports.html + report_result.html) — user won't trigger PDF anymore. And remove the PDF rendering section (which is dead code). The branch in web_admin.py can stay and just be dead code.

Hmm, but user said "удаляем". Let me try to remove it and if it fails just leave dead code (harmless).

OK writing now.

Let me use a simpler approach for the whole thing: search for specific strings and see structure, then decide. No, let me just write the patcher.

FINAL: I'll write the patcher with reasonable regexes, with verbose output, that also prints the modified file size and skips if markers not found. User runs it, sees output, pastes back, I fix if needed.

Let me write it now, being careful about escaping.

Also I should ask user to make sure Docker is stopped or at least that no Python is holding the files. On Windows, python files aren't locked. OK.

Final script:

python
# D:\tracker\tools\remove_pivot_pdf.py
"""Удаляет pivot и PDF-экспорт из проекта «Трекер»."""
import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP = ROOT / "_backup_remove_pivot_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path):
    rel = path.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)

def rm_block(text, pattern, label, flags=re.DOTALL):
    new, n = re.subn(pattern, "", text, count=1, flags=flags)
    if n:
        print(f"  [OK]   {label}: -{len(text)-len(new)} симв.")
    else:
        print(f"  [WARN] {label}: не найдено")
    return new

# ============================================================
# 1. web_admin.py
# ============================================================
print("\n=== server/web_admin.py ===")
p = ROOT / "server" / "web_admin.py"
backup(p)
c = p.read_text(encoding="utf-8")
orig = len(c)

c = rm_block(c, r'@router\.get\("/reports/pivot".*?(?=\n@router\.)', "роут /reports/pivot")
c = rm_block(c, r'@router\.post\("/api/pivot-data"\).*?(?=\n@router\.)', "эндпоинт /api/pivot-data")
c = rm_block(c, r'\ndef _build_pivot_data\(.*?(?=\n(?:def |@router\.|# =))', "функция _build_pivot_data")

# PDF-ветка (короткая, если fmt == "pdf")
c = rm_block(
    c,
    r'\n    (?:el)?if fmt == "pdf":\n(?:        .*\n|\n)+?(?=\n    (?:el)?if fmt|\n\n# |\n@router\.)',
    'ветка if fmt == "pdf"',
)

# Большая секция PDF-рендер
c = rm_block(
    c,
    r'\n# =+\n# PDF-рендер отчёта\n# =+\n.*?(?=\n# =+\n# |\Z)',
    "секция PDF-рендер",
)

# Импорты reportlab
c, n = re.subn(r'\n(?:from reportlab[^\n]*|import reportlab[^\n]*)\n', '\n', c)
print(f"  [i]    импортов reportlab: {n}")

c = re.sub(r'\n{4,}', '\n\n\n', c)  # убрать лишние пустые строки
p.write_text(c, encoding="utf-8")
print(f"OK web_admin.py: {orig} -> {len(c)}")

# ============================================================
# 2. reports.html — убрать опцию PDF
# ============================================================
print("\n=== server/templates/reports.html ===")
p = ROOT / "server" / "templates" / "reports.html"
backup(p)
c = p.read_text(encoding="utf-8")
c, n = re.subn(r'\s*<option value="pdf">PDF</option>', '', c)
p.write_text(c, encoding="utf-8")
print(f"  [{'OK' if n else 'WARN'}] опция PDF: {n}")

# ============================================================
# 3. report_result.html — убрать кнопку PDF
# ============================================================
print("\n=== server/templates/report_result.html ===")
p = ROOT / "server" / "templates" / "report_result.html"
backup(p)
c = p.read_text(encoding="utf-8")

# Ищем форму с input fmt=pdf и кнопку рядом
c2, n1 = re.subn(
    r'\s*<form[^>]*>\s*<input type="hidden" name="fmt" value="pdf"\s*/?>\s*<button[^>]*>[^<]*PDF[^<]*</button>\s*</form>',
    '', c, flags=re.DOTALL,
)
if n1:
    c = c2
    print(f"  [OK] форма PDF удалена: {n1}")
else:
    c, n2 = re.subn(r'\s*<input type="hidden" name="fmt" value="pdf"\s*/?>', '', c)
    c, n3 = re.subn(r'\s*<button[^>]*>[^<]*PDF[^<]*</button>', '', c)
    print(f"  [i] fallback: hidden={n2}, button={n3}")
p.write_text(c, encoding="utf-8")

# ============================================================
# 4. i18n.py — ключи PDF
# ============================================================
print("\n=== server/i18n.py ===")
p = ROOT / "server" / "i18n.py"
backup(p)
c = p.read_text(encoding="utf-8")
c, n = re.subn(r'\n\s*"btn\.download_pdf(?:_full)?":\s*\{[^}]*\},?', '', c)
p.write_text(c, encoding="utf-8")
print(f"  [{'OK' if n else 'WARN'}] ключей PDF: {n}")

# ============================================================
# 5. reports_pivot.html — переименовать
# ============================================================
print("\n=== server/templates/reports_pivot.html ===")
p = ROOT / "server" / "templates" / "reports_pivot.html"
backup(p)
dst = p.with_name("_unused_reports_pivot.html.txt")
if dst.exists():
    dst.unlink()
p.rename(dst)
print(f"  [OK] {p.name} -> {dst.name}")

# ============================================================
# 6. docs/_sidebar.md — убрать Pivot
# ============================================================
print("\n=== docs/_sidebar.md ===")
p = ROOT / "docs" / "_sidebar.md"
if p.exists():
    backup(p)
    c = p.read_text(encoding="utf-8")
    c, n = re.subn(r'\s*-\s*\[[^\]]*Pivot[^\]]*\]\([^)]*\)', '', c)
    p.write_text(c, encoding="utf-8")
    print(f"  [{'OK' if n else 'WARN'}] строк в сайдбаре: {n}")

print(f"\nБэкапы: {BACKUP}")
print("Следующий шаг: docker compose down && docker compose up -d --build")
Wait, there's an issue with [^}]* inside i18n regex — the dict values are {"ru": "...", "en": "..."}. So [^}]* matches up to the first }. Good.

But { in "btn.download_pdf": {"ru":...} — I have \{ escaped. Good.

The \s* at the start — combined with ,? at the end, might remove wrong amount of whitespace. Let me use \n\s*... to require at least one newline before.

OK. Now let me also think: after this, need to also check server/templates/base.html or wherever the pivot link lives. Since grep didn't find pivot there, maybe it's inside reports.html as a link. Let me add a check:

Actually, since grep already scanned and found nothing in base.html, we're fine.

But wait — the grep did NOT include .html in SKIP_DIRS? No, it only had .venv, venv, __pycache__, .git, node_modules, dist, build, .idea, .vscode. Templates are scanned. So base.html was scanned. No hits. Good.

So the pivot link — where is it? Let me search the grep output more carefully... reports_pivot.html (54 hits) — that's the page itself. web_admin.py (16 hits) — backend. _sidebar.md (1 hit). Docs. That's it. So where does user click to go to /admin/reports/pivot?

Maybe it's generated dynamically? Or maybe it's in reports.html near the top? The grep for reports.html shows only 1 hit, and it's the <option value="pdf">. So there's no link to pivot in reports.html.

Hmm, maybe there's a tab bar in base.html or in reports.html around line 1-90 that has a link. Let me trust the grep — it found nothing.

Or maybe the pivot link is in a template file we haven't seen, like a _tabs.html or _nav.html include. But grep scans all files, so it would have found it. Unless the file is .jinja or has some other extension.

Or maybe the user reaches pivot page by direct URL. That's possible.

OK, no additional cleanup needed for menu.

Let me finalize the script. I'll also add a step to print all remaining "pivot"/"pdf" hits in the code files so we can verify.

Actually the code already exists — I can ask user to re-run find_pivot_pdf.py after. Let me just remind.

OK. Write it up.

Wait, one more: what if _report_row_to_list is only used by PDF? Then after removing PDF it's dead code. But grep didn't show this function's fate. Let me leave it — dead code is harmless.

Also, check imports. After removing PDF render, we might have unused imports (Paragraph, SimpleDocTemplate, getSampleStyleSheet, Table, TableStyle, StreamingResponse). Some of these might be used by XLSX/CSV too. Let me not touch imports beyond reportlab.

Actually StreamingResponse is likely used by CSV/XLSX too. Keep it.

OK writing final answer.

I'll give:

Brief confirmation

The patcher script (as a Python file to save)

Run commands

Expected output

What to send back

What's next (KB updates)

Let me write it.

Понял. Убираем веб-pivot (PivotTable.js) и PDF-экспорт из проекта. Оставляем CSV/XLSX и печать браузером (Ctrl+P → Сохранить как PDF). Это чистое упрощение, ничего не ломает.

Поиск показал: 43 файла с упоминаниями, но реально править код нужно в 6 файлах:

server/web_admin.py — роут pivot, эндпоинт pivot-data, функция _build_pivot_data, PDF-ветка, PDF-рендер.

server/templates/reports.html — опция PDF в выпадашке.

server/templates/report_result.html — кнопка «Скачать PDF».

server/i18n.py — ключи btn.download_pdf / btn.download_pdf_full.

server/templates/reports_pivot.html — сама страница.

docs\_sidebar.md — ссылка «Pivot-таблица».

Файлы docs\..., Ерохин\..., PROJECT_SNAPSHOT_*.txt — это KB и снапшоты, их тронем отдельно (обновим HANDOFF и пару KB-файлов после кода).

Шаг 1. Python-патчер удаления
Создай файл D:\tracker\tools\remove_pivot_pdf.py и вставь в него:

python
# D:\tracker\tools\remove_pivot_pdf.py
# Удаляет веб-pivot и PDF-экспорт из проекта «Трекер».
