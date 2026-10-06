<!-- Часть 1317 из 1409 -->
# Делает бэкапы всех правленых файлов в D:\tracker\_backup_remove_pivot_pdf\<дата_время>\
*Хлебные крошки:* Делает бэкапы всех правленых файлов в D:\tracker\_backup_remove_pivot_pdf\<дата_время>\

[◀ Удаляет веб-pivot и PDF-экспорт из проекта «Трекер».](1316_Udalyaet_veb_pivot_i_PDF_eksport_iz_proekta_Treker.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1318_part.md)

---

# Делает бэкапы всех правленых файлов в D:\tracker\_backup_remove_pivot_pdf\<дата_время>\
import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP = ROOT / "_backup_remove_pivot_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
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

