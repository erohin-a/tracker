<!-- Часть 662 из 1409 -->
# Проверим, не пропатчен ли уже
*Хлебные крошки:* Проверим, не пропатчен ли уже

[◀ ============================================================](661_part.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](663_part.md)

---

# Проверим, не пропатчен ли уже
if ($content -match "from \.web_i18n import") {
    Write-Host "web_admin.py уже пропатчен" -ForegroundColor Yellow
} else {
    # 2.1. Добавляем импорт i18n
    $oldImport = "from .config import settings"
    $newImport = @'
from .config import settings
from .i18n import SUPPORTED_LANGS, DEFAULT_LANG
from .web_i18n import _, set_current_lang, get_current_lang
'@
    if ($content.Contains($oldImport)) {
        $content = $content.Replace($oldImport, $newImport)
        Write-Host "OK: добавлены импорты i18n" -ForegroundColor Green
    } else {
        Write-Host "Не найден импорт config — правьте вручную" -ForegroundColor Red
        exit 1
    }

    # 2.2. Регистрируем _() в Jinja и context processor
    # Находим строку templates.env.filters["dur"] = _fmt_dur
    $oldFilters = @'
templates.env.filters["dur"] = _fmt_dur
templates.env.filters["dt"] = _fmt_dt_global
'@
    $newFilters = @'
templates.env.filters["dur"] = _fmt_dur
templates.env.filters["dt"] = _fmt_dt_global

