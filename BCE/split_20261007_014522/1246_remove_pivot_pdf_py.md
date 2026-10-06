<!-- Часть 1246 из 1409 -->
# remove_pivot_pdf.py
*Хлебные крошки:* remove_pivot_pdf.py

[◀ ...](1245_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1247_part.md)

---

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

