<!-- Часть 1395 из 1409 -->
# Обновляет документацию SCP: 05_SCP\01_OVERVIEW.md и 05_SCP\04_ADMIN.md.
*Хлебные крошки:* Обновляет документацию SCP: 05_SCP\01_OVERVIEW.md и 05_SCP\04_ADMIN.md.

[◀ D:\tracker\tools\kb_patch_5_scp_admin.py](1394_D_tracker_tools_kb_patch_5_scp_admin_py.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1396_part.md)

---

# Обновляет документацию SCP: 05_SCP\01_OVERVIEW.md и 05_SCP\04_ADMIN.md.
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"D:\tracker")
KB = ROOT / "docs"
BACKUP = ROOT / "_backup_kb_patch" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def bak(p: Path):
    rel = p.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)

