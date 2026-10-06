<!-- Часть 582 из 1409 -->
# Идентификаторы ревизии (используются Alembic для отслеживания)
*Хлебные крошки:* Идентификаторы ревизии (используются Alembic для отслеживания)

[◀ ------------------------------------------------------------](581_part.md) | [Оглавление](00_BCE_INDEX.md) | [1) Добавляем импорты Alembic после существующих импортов ▶](583_1_Dobavlyaem_importy_Alembic_posle_suschestvuyuschih_importov.md)

---

# Идентификаторы ревизии (используются Alembic для отслеживания)
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Применение миграции — что делаем при обновлении схемы."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Откат миграции — что делаем при возврате к предыдущей версии."""
    ${downgrades if downgrades else "pass"}
'@

[System.IO.File]::WriteAllText($mako, $makoContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $mako" -ForegroundColor Green
________________________________________
Скрипт D5 — патчим server/main.py
Заменяем init_db() на запуск Alembic.
powershell
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

