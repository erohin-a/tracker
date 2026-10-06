<!-- Часть 1236 из 1409 -->
# D:\tracker\tools\find_pivot_pdf.py
*Хлебные крошки:* D:\tracker\tools\find_pivot_pdf.py

[◀ 14. Пароли и секреты](1235_14_Paroli_i_sekrety.md) | [Оглавление](00_BCE_INDEX.md) | [D:\tracker\tools\find_pivot_pdf.py ▶](1237_D_tracker_tools_find_pivot_pdf_py.md)

---

# D:\tracker\tools\find_pivot_pdf.py
import os, re

ROOT = r"D:\tracker"
SKIP_DIRS = {'.venv', 'venv', '__pycache__', '.git', 'node_modules', 'dist', 'build'}
PATTERNS = [re.compile(r'pivot', re.IGNORECASE), re.compile(r'\bpdf\b', re.IGNORECASE)]
EXTS = {'.py', '.html', '.js', '.md', '.txt', '.json', '.ini', '.bat', '.ps1', '.css'}

hits = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in EXTS:
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            continue
        for i, line in enumerate(lines, 1):
            for p in PATTERNS:
                if p.search(line):
                    hits.setdefault(path, []).append((i, line.rstrip()))
                    break

for path, items in sorted(hits.items()):
    rel = os.path.relpath(path, ROOT)
    print(f"\n=== {rel} ({len(items)} hits) ===")
    for i, line in items[:20]:
        print(f"  {i}: {line[:200]}")
    if len(items) > 20:
        print(f"  ... и ещё {len(items) - 20}")
print(f"\nВсего файлов: {len(hits)}")
Then we patch. Let me deliver this first, ask user to run it and paste output.

Actually to save turns, I could also prepare the patch assuming common layouts. But safer to discover first.

Let me keep it short. Give discovery script, wait for output.

But user also wants the KB updated. I'll do that after patch.

Let me respond in Russian, "ты" style, concise.

Понял. Pivot и PDF убираем, оставляем CSV/XLSX + печать из браузера (там «Сохранить как PDF» есть в системном диалоге). Это упростит проект и уберёт два пункта из P0.

Чтобы удалить аккуратно, мне нужно сначала найти все места, где упоминается pivot и pdf. Сделаю это скриптом-искателем, чтобы ничего не забыть (роуты, шаблоны, меню, экспорт, KB).

Шаг 1. Скрипт поиска
Создай файл D:\tracker\tools\find_pivot_pdf.py (папку tools создай, если её нет) и вставь:

python
