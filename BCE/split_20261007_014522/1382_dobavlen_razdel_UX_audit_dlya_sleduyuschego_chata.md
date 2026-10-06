<!-- Часть 1382 из 1409 -->
# - добавлен раздел "UX-аудит" для следующего чата
*Хлебные крошки:* - добавлен раздел "UX-аудит" для следующего чата

[◀ - AdminTab (гибрид) расписан](1381_AdminTab_gibrid_raspisan.md) | [Оглавление](00_BCE_INDEX.md) | [--- 1. Паспорт: готовность + список остатков --- ▶](1383_1_Pasport_gotovnost_spisok_ostatkov.md)

---

#   - добавлен раздел "UX-аудит" для следующего чата
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

def rp(path: Path, old: str, new: str, label: str):
    c = path.read_text(encoding="utf-8")
    if old not in c:
        print(f"  [skip] {label}")
        return
    path.write_text(c.replace(old, new, 1), encoding="utf-8")
    print(f"  [OK]   {label}")

p = KB / "HANDOFF.md"
bak(p)
print(f"=== {p.relative_to(ROOT)} ===")

