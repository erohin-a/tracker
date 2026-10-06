<!-- Часть 716 из 1409 -->
# --- Патч 1: импорты ---
*Хлебные крошки:* --- Патч 1: импорты ---

[◀ Проверка синтаксиса](715_Proverka_sintaksisa.md) | [Оглавление](00_BCE_INDEX.md) | [--- Патч 2: регистрация _() и context processor --- ▶](717_Patch_2_registratsiya_i_context_processor.md)

---

# --- Патч 1: импорты ---
if ($content -match "from \.web_i18n import") {
    Write-Host "Патч 1: импорты i18n уже есть" -ForegroundColor Yellow
    "step1: already patched" | Out-File $log -Append -Encoding utf8
} else {
    $old = "from .config import settings"
    $new = @'
from .config import settings
from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang
from .web_i18n import _, set_current_lang, get_current_lang
'@
    if ($content.Contains($old)) {
        $content = $content.Replace($old, $new)
        Write-Host "Патч 1: OK — импорты добавлены" -ForegroundColor Green
        "step1: imports added" | Out-File $log -Append -Encoding utf8
        $changed = $true
    } else {
        Write-Host "Патч 1: НЕ НАЙДЕН 'from .config import settings'" -ForegroundColor Red
        "step1: FAILED" | Out-File $log -Append -Encoding utf8
    }
}

