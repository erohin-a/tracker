<!-- Часть 583 из 1409 -->
# 1) Добавляем импорты Alembic после существующих импортов
*Хлебные крошки:* 1) Добавляем импорты Alembic после существующих импортов

[◀ Идентификаторы ревизии (используются Alembic для отслеживания)](582_Identifikatory_revizii_ispolzuyutsya_Alembic_dlya_otslezhivaniya.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](584_part.md)

---

# 1) Добавляем импорты Alembic после существующих импортов
if ($content -notmatch "alembic.config") {
    # Находим строку с "from .web_admin import router"
    $anchor = "from .web_admin import router as admin_web_router"
    $imports = @'
from .web_admin import router as admin_web_router

