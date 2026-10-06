<!-- Часть 732 из 1409 -->
# i18n: регистрируем функцию перевода _() в Jinja2.
*Хлебные крошки:* i18n: регистрируем функцию перевода _() в Jinja2.

[◀ ------------------------------------------------------------](731_part.md) | [Оглавление](00_BCE_INDEX.md) | [Middleware ▶](733_Middleware.md)

---

# i18n: регистрируем функцию перевода _() в Jinja2.
...
Good.
But wait — the _addition contains this line:
python
templates.env.globals["_"] = _
The _ on the right side — in Python this refers to the module-level name _, which we imported from .web_i18n. Good.
BUT — what if _ collides with something else in web_admin.py? Like a local variable _? Hmm, in some code we have _=Depends(current_admin) pattern in FastAPI route signatures! Look:
python
def dashboard(request: Request, db: Session = Depends(get_db), 
              _=Depends(current_admin)):
THE PARAMETER NAME _ SHADOWS THE GLOBAL! This is a problem because inside the function, _ refers to the return of current_admin (which is a string like "admin"), not our translation function.
But that's local to the function scope, so it shouldn't affect the module-level templates.env.globals["_"] = _. Actually, no — that line runs at MODULE level, so _ at that point refers to the module-level global. Then inside functions where _ is a parameter, it's shadowed.
So this shouldn't cause our issue... unless some function that renders templates uses _ for something.
But the actual issue — template rendering uses templates.env.globals["_"] which is our function. The route handler's local _ doesn't matter.
OK. I really need logs. Let me ask.
Actually, wait. Let me check something else. What if E2b Patch 3 (the /set-lang endpoint) went in BEFORE the "Логин / логаут" section, but the FastAPI app didn't reload because it's in Docker? Actually the user did docker compose down && docker compose up -d --build — so it rebuilt.
Hmm, actually — could there be a circular import? web_admin.py imports from .web_i18n, which imports from .i18n. .i18n imports only stdlib. So no cycle.
But wait — web_admin.py might be imported by main.py which imports... no, that shouldn't matter.
OK. Let me just ask for logs and be done.
Actually, you know what — I bet I know. Let me look at the set-lang endpoint more carefully:
python
@router.get("/set-lang/{code}")
def set_lang(code: str, request: Request):
FastAPI sees code: str — path param. request: Request — special type. That's fine.
But — is Request correctly imported in web_admin.py? Let me check the top:
python
from fastapi import APIRouter, Depends, Request, Form, HTTPException
Yes, it's there.
Hmm.
You know what, one more thing. When user clicks EN, our endpoint /admin/set-lang/en?next=/admin. But what if the browser or nginx does something weird? No.
Alright, let me stop guessing and just ask for logs.
Actually — I want to give the user a good experience. Let me:
Ask them to try switching in a way that gets logs.
Provide the exact commands.
Give 2-3 most likely fixes based on common patterns.
Let me write the response.
The most likely issues in my opinion:
set_current_lang raises because... some reason. Or contextvars doesn't work in the async context.
supported_langs is not passed to template ? some templates might break if they try to iterate it strictly.
templates.context_processors doesn't exist in this Starlette version ? but then it would break on RU too.
Hmm actually — #3. If templates.context_processors.append(...) raises AttributeError, then this line would fail at import time. But E2b said SYNTAX OK, which is just syntax check. If the runtime failed at import, the API container would fail to start ? user couldn't even access RU. But user says RU works.
So the context processor registration worked. So RU works. And when EN is set... hmm.
WAIT. Oh! I think I see it.
set_current_lang uses contextvars.ContextVar.set(). Context variables are COPIED when tasks are created. If the request handler runs in a task, and the context processor runs inside a nested function... the set might not propagate.
Actually no. In FastAPI sync route handlers run in a threadpool via run_in_threadpool. The context is copied for that thread. Setting a ContextVar in that thread's context doesn't propagate back to the caller.
BUT — the template rendering happens INSIDE the same sync route handler. So within dashboard(), we call templates.TemplateResponse(...) which internally calls the context processor and renders. All in the same sync thread, same context. So contextvars should work.
Hmm actually — is the context processor called inside TemplateResponse, which is inside dashboard()? Or is it called later by Starlette when sending the response?
Let me think about Starlette's Jinja2Templates.TemplateResponse:
python
def TemplateResponse(self, name, context=None, status_code=200, ...):
    ...
    return _TemplateResponse(self, name, context, ...)

class _TemplateResponse(HTMLResponse):
    def __init__(self, template, context, ...):
        self.template = template
        self.context = context
        content = template.render(context)  # RENDERED IMMEDIATELY
        ...
So rendering happens at construction time — inside dashboard(). Good. So contextvars should work.
Hmm, wait — actually newer Starlette may defer rendering. Let me check.
Actually in Starlette >= 0.35 or so, they made it ASYNC. _TemplateResponse is rendered lazily when .body is accessed. So by then, we're back in the async task, but in a DIFFERENT context — the contextvars set inside the sync thread are lost!
THAT'S THE BUG.
Let me verify. In recent Starlette, TemplateResponse supports async rendering. The template is rendered when the response body is accessed, which happens in the async event loop, not in the sync route handler's context.
Wait, but then context processor runs at render time — in the async context. And set_current_lang sets the ContextVar in the async context. And then _() is called in the template — also in the async context. So it should still work!
Unless — the context processor runs and sets it, but each _() call... no, _() doesn't set, it reads. Same context.
Hmm. OK let me just check whether context_processors in Starlette's Jinja2Templates actually works as I expect.
Looking at Starlette source (roughly):
python
class Jinja2Templates:
    def __init__(self, directory, *, context_processors=None, **env_options):
        ...
        self.context_processors = context_processors or []
    
    def TemplateResponse(self, request, name, context=None, ...):
        if context is None:
            context = {}
        
        context.setdefault("request", request)
        
        for context_processor in self.context_processors:
            context.update(context_processor(request))
        
        ...
        
        return _TemplateResponse(self.get_template(name), context, ...)
Yes — context processor is called at TemplateResponse() call time — inside the sync route handler. And context is expanded. Then rendering happens later when the body is accessed.
OK so the context processor runs inside dashboard(). Sets ContextVar. Then... does the template render AFTER this point, in the same context?
If Starlette's _TemplateResponse defers rendering, then yes, it happens after context processor returns, still inside dashboard(), so in the same thread/context. ContextVar should be readable.
Ugh, I keep going back and forth. Let me just get the logs.
OK, writing response now. Will:
Explain that I need actual error text.
Give 2 commands to get it.
Present a likely fix ready to apply if it turns out to be the contextvars issue.
Actually, the SAFEST fix regardless of the actual root cause: don't use contextvars at all. Instead, pass lang explicitly through the context processor into template context, and make _ a closure or use request.state.lang.
Alternative approach: register _ in Jinja as a function that reads from a thread-local variable or from request (via context). But template globals don't have access to request.
Better approach: pass a bound _ function into template context in the context processor.
python
def _i18n_context_processor(request):
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
        "t": lambda key: t(key, lang),
    }
And in templates use {{ t("menu.employees") }} instead of {{ _("...") }}.
Hmm — but this requires changing templates. Ugh.
Alternative: keep _ global but have it read from... somewhere. Contextvars set inside context_processor should be readable in template because they're in the same context.
Let me just go with a simpler approach that's guaranteed to work: use a module-level global that's reset per-request. This is thread-unsafe but works if requests don't interleave.
Actually — contextvars is the RIGHT tool. Let me stick with it. But maybe something else is wrong.
OK — let me stop and just ask for logs. Simple.
Actually I'll do both: ask for logs AND provide a fix that removes contextvars-based approach and uses context-processor-injected function.
Let me be decisive. Actually the SIMPLEST fix that's guaranteed to work is:
Store the language in request.state.lang (setting is async-safe within same request), and register _ in Jinja globals as a function that takes context and reads context.get('request').state.lang.
Hmm, Jinja globals receive the current context as first arg if they have pass_context decorator. Too complex.
OK, alternative: register _ as a global that reads from a variable that's set per-request via a middleware.
python
