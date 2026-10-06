<!-- Часть 1344 из 1409 -->
# Восстанавливает файлы из последнего бэкапа remove_pivot_pdf.
*Хлебные крошки:* Восстанавливает файлы из последнего бэкапа remove_pivot_pdf.

[◀ D:\tracker\tools\restore_pivot_pdf.py](1343_D_tracker_tools_restore_pivot_pdf_py.md) | [Оглавление](00_BCE_INDEX.md) | [Находим последний бэкап ▶](1345_Nahodim_posledniy_bekap.md)

---

# Восстанавливает файлы из последнего бэкапа remove_pivot_pdf.
import shutil
from pathlib import Path

ROOT = Path(r"D:\tracker")
BACKUP_ROOT = ROOT / "_backup_remove_pivot_pdf"

