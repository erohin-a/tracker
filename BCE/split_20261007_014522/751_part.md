<!-- Часть 751 из 1409 -->
# ------------------------------------------------------------
*Хлебные крошки:* ------------------------------------------------------------

[◀ (не из глобалов — глобал не нужен).](750_ne_iz_globalov_global_ne_nuzhen.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Патч B: импорт функции t() для использования в замыкании ---------- ▶](752_Patch_B_import_funktsii_t_dlya_ispolzovaniya_v_zamykanii.md)

---

# ------------------------------------------------------------
def _i18n_context_processor(request):
    """Читает cookie tracker_lang, возвращает текущий язык и bound _()."""
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG

    # Замыкание на конкретный язык этого запроса
    def _(key):
        return t(key, lang)

    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
        "_": _,
    }

templates.context_processors.append(_i18n_context_processor)
'@

if ($content.Contains($newGlobal)) {
    Write-Host "Патч A: уже применён" -ForegroundColor Yellow
    "stepA: already applied" | Out-File $log -Append -Encoding utf8
} elseif ($content.Contains($oldGlobal)) {
    $content = $content.Replace($oldGlobal, $newGlobal)
    Write-Host "Патч A: OK — context processor заменён" -ForegroundColor Green
    "stepA: context processor replaced" | Out-File $log -Append -Encoding utf8
    $changed = $true
} else {
    Write-Host "Патч A: НЕ НАЙДЕН старый блок context processor" -ForegroundColor Red
    "stepA: FAILED - no old block" | Out-File $log -Append -Encoding utf8
    Write-Host "Выполните: docker compose exec api grep -n '_i18n_context_processor' /app/server/web_admin.py" -ForegroundColor Yellow
}

