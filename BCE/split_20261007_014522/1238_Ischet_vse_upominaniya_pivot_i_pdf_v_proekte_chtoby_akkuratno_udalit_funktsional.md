<!-- Часть 1238 из 1409 -->
# Ищет все упоминания "pivot" и "pdf" в проекте, чтобы аккуратно удалить функционал.
*Хлебные крошки:* Ищет все упоминания "pivot" и "pdf" в проекте, чтобы аккуратно удалить функционал.

[◀ D:\tracker\tools\find_pivot_pdf.py](1237_D_tracker_tools_find_pivot_pdf_py.md) | [Оглавление](00_BCE_INDEX.md) | [1. Удаляем роут pivot-страницы ▶](1239_1_Udalyaem_rout_pivot_stranitsy.md)

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

