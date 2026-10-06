<!-- Часть 581 из 1409 -->
# ------------------------------------------------------------
*Хлебные крошки:* ------------------------------------------------------------

[◀ Точка входа: Alembic сам решает, какой режим использовать](580_Tochka_vhoda_Alembic_sam_reshaet_kakoy_rezhim_ispolzovat.md) | [Оглавление](00_BCE_INDEX.md) | [Идентификаторы ревизии (используются Alembic для отслеживания) ▶](582_Identifikatory_revizii_ispolzuyutsya_Alembic_dlya_otslezhivaniya.md)

---

# ------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'@

[System.IO.File]::WriteAllText("$alembicDir\env.py", $envPy, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $alembicDir\env.py" -ForegroundColor Green
________________________________________
Скрипт D4 — создаём server/alembic/script.py.mako
Это шаблон, по которому Alembic создаёт новые файлы миграций.
powershell
powershell
$ErrorActionPreference = "Stop"
$mako = "D:\tracker\server\alembic\script.py.mako"

$makoContent = @'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Описание миграции — что меняется и зачем.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

