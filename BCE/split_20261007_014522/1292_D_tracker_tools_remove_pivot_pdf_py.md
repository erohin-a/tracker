<!-- Часть 1292 из 1409 -->
# D:\tracker\tools\remove_pivot_pdf.py
*Хлебные крошки:* D:\tracker\tools\remove_pivot_pdf.py

[◀ ============================================================](1291_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1293_part.md)

---

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

