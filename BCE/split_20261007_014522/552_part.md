<!-- Часть 552 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 3. Как подключаться к БД (online или offline режим)](551_3_Kak_podklyuchatsya_k_BD_online_ili_offline_rezhim.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](553_part.md)

---

# ============================================================

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

