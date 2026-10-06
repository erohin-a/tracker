<!-- Часть 637 из 1409 -->
# Dependency для чтения языка
*Хлебные крошки:* Dependency для чтения языка

[◀ Регистрируем `_` в Jinja](636_Registriruem_v_Jinja.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](638_part.md)

---

# Dependency для чтения языка
def current_lang_dep(request: Request) -> str:
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    set_current_lang(lang)
    return lang
Но проблема: templates.TemplateResponse не проходит через dependency автоматически. Нужно в каждом роуте добавить lang: str = Depends(current_lang_dep). Или использовать middleware.
Middleware — чище:
python
@app.middleware("http")
async def i18n_middleware(request: Request, call_next):
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    set_current_lang(lang)
    response = await call_next(request)
    return response
Middleware устанавливает язык ДО обработки роута, поэтому _() внутри шаблона уже работает.
Хорошо, пойдём через middleware. Но middleware вешается на app (FastAPI), а не на router. Значит, в main.py или в web_admin.py через app — но web_admin.py возвращает router, не app.
Решение: добавить middleware в main.py. Или использовать templates.context_processors — тогда контекст шаблона получит current_lang и supported_langs автоматически.
Jinja2Templates в Starlette поддерживает context_processors:
python
def i18n_context(request: Request):
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    set_current_lang(lang)
    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
    }
templates.context_processors.append(i18n_context)
Это чище. Context processor вызывается перед рендером шаблона, получает request, может установить язык через contextvars, и вернуть доп. переменные.
Хорошо, идём так. Плюс — не нужен middleware в main.py, всё локально в web_admin.py.
Пишу E2.
Скрипт E2 — хук i18n в Jinja2
Что делаем:
Создаём server/web_i18n.py — обёртка вокруг i18n.py с contextvars (чтобы _() знал, какой сейчас язык).
Патчим web_admin.py — регистрируем _() в Jinja2 + context processor, который читает язык из cookie.
Добавляем endpoint /admin/set-lang/{code} — переключает cookie и возвращает на страницу.
Патчим base.html — переключатель RU/EN в шапке + меню через _().
________________________________________
Скрипт E2
powershell
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

