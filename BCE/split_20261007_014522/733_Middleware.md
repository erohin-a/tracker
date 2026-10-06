<!-- Часть 733 из 1409 -->
# Middleware
*Хлебные крошки:* Middleware

[◀ i18n: регистрируем функцию перевода _() в Jinja2.](732_i18n_registriruem_funktsiyu_perevoda_v_Jinja2.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Патч A: убираем старую регистрацию _() как глобала ---------- ▶](734_Patch_A_ubiraem_staruyu_registratsiyu_kak_globala.md)

---

# Middleware
@app.middleware("http")
async def i18n_middleware(request, call_next):
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    set_current_lang(lang)  # contextvars
    response = await call_next(request)
    return response
Middleware runs in async context, sets contextvar. Then route handler runs — inherited context. Then template render — same context. This should work reliably.
Hmm but with sync route handlers running in threadpool, the context is copied. When we set a ContextVar in the middleware (async context), and the sync route handler runs in a thread pool... the thread inherits a COPY of the context. So get_current_lang() would return the value set in middleware. And when the sync handler calls set_current_lang again, it modifies the COPY, which is discarded. But get still works.
Actually — this is getting complicated. Let me just tell the user: "send me the logs, I'll fix it based on the actual error."
Let me write that response.
Actually wait — let me reconsider. There's a super simple fix: pass lang directly to the context processor's output, and change the template to use a filter-like function that reads the current lang from the template context.
python
def _i18n_context_processor(request):
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
    }
And then in Jinja:
html
{{ _t("menu.employees", current_lang) }}
Where _t is a global:
python
templates.env.globals["_t"] = lambda key, lang: t(key, lang)
Hmm, ugly. Or better:
Pass a bound function:
python
def _i18n_context_processor(request):
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    def _(key):
        return t(key, lang)
    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
        "_": _,
    }
And in templates, keep using {{ _("menu.employees") }}. In templates, _ will be looked up first in the local context (from context processor), then in globals. So the context processor's _ takes precedence!
This is CLEAN. Each request gets its own bound _ function. No contextvars needed.
This is the fix. Let me apply it.
But wait — I need to know WHY current version fails first. Maybe it's not contextvars at all. Let me ask for logs but ALSO provide this fix.
Hmm, actually let me just go with: ask for logs + explain that I have a fix ready + ask for confirmation.
Or better: give the fix right away. If it works, great. If not, we still have logs.
Decision: give fix. Explain that contextvars approach might have issues with sync route handlers, replaced with per-request bound function. Ask for logs if it still fails.
Let me write it.
Actually — I realized I should ALSO check: what's the actual 500? Maybe the 500 is on the /admin/set-lang/en route, not on rendering. If cookie value has issues, or response construction fails.
But no — the user says "при переключении на английский" — so it happens when switching, meaning after the redirect when trying to render the page in EN.
OK, let me write the fix.
One more thought — the log file _e2b.log should show whether Patch 2 applied. Let me ask for that too.
Response structure:
Быстрая диагностика (2 команды)
Фикс (замена contextvars на bound function)
Если не помогло — логи
Actually — thinking more — let me just go with the fix. It's very likely the issue. And it's a good architectural change anyway.
Final answer structure:
Причина (гипотеза): contextvars с sync route handlers в threadpool могут терять значение между вызовами. Или что-то связанное с этим.
Что делаем: заменяем _ — вместо глобальной функции, читающей contextvars, будем возвращать bound _ из context processor. Это гарантированно работает: каждый запрос получает свою функцию _, замыкание на конкретный язык.
Скрипты:
Изменить web_admin.py: обновить context processor, добавить _ в возвращаемый dict.
Не трогать web_i18n.py — оставим set/get на всякий случай.
Пересобрать.
Let me write it now.
Диагностика: 500 при переключении на EN
Причина (гипотеза)
Вероятнее всего — проблема с contextvars в sync-обработчиках FastAPI.
Что происходит:
dashboard() — sync-функция. FastAPI выполняет её в threadpool (отдельный поток, не event loop).
Contextvars, установленные в одном потоке, могут не читаться в другом.
Когда мы в context processor вызываем set_current_lang("en"), значение пишется в contextvars текущего потока. Читаем — тоже в текущем потоке. На первый взгляд должно работать.
Но в момент рендера шаблона Starlette может отрендерить его позже — в другом контексте (зависит от версии Starlette).
Гарантированное решение
Отказываемся от contextvars в пользу bound-функции: каждый запрос получает свою _, замкнутую на конкретный язык. Это работает без всяких нюансов.
Также — попрошу логи, чтобы убедиться в правильности гипотезы. Но фикс даю сразу, он в любом случае правильный.
________________________________________
Скрипт E2b-fix — патчим web_admin.py
Убираем _ из глобалов и возвращаем её из context processor.
powershell
$ErrorActionPreference = "Continue"
$log = "D:\tracker\_e2fix.log"
"=== E2-fix started $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8 -Force

$path = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
$changed = $false

