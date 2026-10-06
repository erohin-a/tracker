<!-- Часть 738 из 1409 -->
# ------------------------------------------------------------
*Хлебные крошки:* ------------------------------------------------------------

[◀ Теперь в любом шаблоне работает {{ _("ключ") }}.](737_Teper_v_lyubom_shablone_rabotaet_klyuch.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](739_part.md)

---

# ------------------------------------------------------------
templates.env.globals["_"] = _


def _i18n_context_processor(request):
    """
    Context processor: перед рендером каждого шаблона
    читает cookie "tracker_lang", устанавливает язык
    в contextvars и добавляет в шаблон переменные
    current_lang и supported_langs (для переключателя).
    """
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    lang = set_current_lang(lang)
    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
    }

templates.context_processors.append(_i18n_context_processor)
'@

$newGlobal = @'
