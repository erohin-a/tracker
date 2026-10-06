<!-- Часть 1348 из 1409 -->
# Мягко отключает pivot и PDF в UI. Бэкенд не трогает.
*Хлебные крошки:* Мягко отключает pivot и PDF в UI. Бэкенд не трогает.

[◀ D:\tracker\tools\disable_pivot_pdf_ui.py](1347_D_tracker_tools_disable_pivot_pdf_ui_py.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1349_part.md)

---

# Мягко отключает pivot и PDF в UI. Бэкенд не трогает.
import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP = ROOT / "_backup_disable_pivot_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    rel = path.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)
    print(f"  [bkp] {rel}")

