<!-- Часть 721 из 1409 -->
# ------------------------------------------------------------
*Хлебные крошки:* ------------------------------------------------------------

[◀ Теперь в любом шаблоне работает {{ _("ключ") }}.](720_Teper_v_lyubom_shablone_rabotaet_klyuch.md) | [Оглавление](00_BCE_INDEX.md) | [--- Патч 3: endpoint /admin/set-lang/{code} --- ▶](722_Patch_3_endpoint_admin_set_lang_code.md)

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
        $content = $content.Replace($oldFilter, $oldFilter + $addition)
        Write-Host "Патч 2: OK — _() и context processor зарегистрированы" -ForegroundColor Green
        "step2: filters+context_processor added" | Out-File $log -Append -Encoding utf8
        $changed = $true
    } else {
        Write-Host "Патч 2: НЕ НАЙДЕН маркер '_fmt_dt_global'" -ForegroundColor Red
        Write-Host "   Проверьте: docker compose exec api grep -n 'templates.env.filters' /app/server/web_admin.py" -ForegroundColor Yellow
        "step2: FAILED - no marker" | Out-File $log -Append -Encoding utf8
    }
}

