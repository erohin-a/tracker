<!-- Часть 672 из 1409 -->
# ------------------------------------------------------------
*Хлебные крошки:* ------------------------------------------------------------

[◀ current_lang и supported_langs (для переключателя).](671_current_lang_i_supported_langs_dlya_pereklyuchatelya.md) | [Оглавление](00_BCE_INDEX.md) | [Логин / логаут" ▶](673_Login_logaut.md)

---

# ------------------------------------------------------------
def _i18n_context_processor(request):
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    lang = set_current_lang(lang)
    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
    }

templates.context_processors.append(_i18n_context_processor)
'@
    if ($content.Contains($oldFilters)) {
        $content = $content.Replace($oldFilters, $newFilters)
        Write-Host "OK: _() и context processor зарегистрированы" -ForegroundColor Green
    } else {
        Write-Host "Не найден блок с фильтрами — правьте вручную" -ForegroundColor Red
        exit 1
    }

    # 2.3. Добавляем endpoint /admin/set-lang/{code}
    # Ищем блок "Логин / логаут" и вставляем перед ним
    $anchor = "# ============================================================
