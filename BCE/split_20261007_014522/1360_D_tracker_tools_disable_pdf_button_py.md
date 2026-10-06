<!-- Часть 1360 из 1409 -->
# D:\tracker\tools\disable_pdf_button.py
*Хлебные крошки:* D:\tracker\tools\disable_pdf_button.py

[◀ ============================================================](1359_part.md) | [Оглавление](00_BCE_INDEX.md) | [report_result.html: убрать форму PDF целиком ▶](1361_report_result_html_ubrat_formu_PDF_tselikom.md)

---

# D:\tracker\tools\disable_pdf_button.py
import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP = ROOT / "_backup_disable_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path):
    rel = path.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)

