<!-- Часть 1368 из 1409 -->
# Плюс пробует убрать ссылку на pivot из шаблонов, если найдёт.
*Хлебные крошки:* Плюс пробует убрать ссылку на pivot из шаблонов, если найдёт.

[◀ Удаляет форму PDF из report_result.html (целиком, вместе с hidden-полями).](1367_Udalyaet_formu_PDF_iz_report_result_html_tselikom_vmeste_s_hidden_polyami.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1369_part.md)

---

# Плюс пробует убрать ссылку на pivot из шаблонов, если найдёт.
import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP = ROOT / "_backup_disable_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    rel = path.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)
    print(f"  [bkp] {rel}")

