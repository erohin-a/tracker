<!-- Часть 730 из 1409 -->
# --- Проверка синтаксиса ---
*Хлебные крошки:* --- Проверка синтаксиса ---

[◀ --- Сохраняем файл ---](729_Sohranyaem_fayl.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](731_part.md)

---

# --- Проверка синтаксиса ---
try {
    python -c "import ast; ast.parse(open(r'D:\tracker\server\web_admin.py', encoding='utf-8').read()); print('SYNTAX OK')"
} catch {
    Write-Host "Не удалось проверить синтаксис: $_" -ForegroundColor Yellow
}

"=== E2b DONE $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Host "`n=== E2b завершён. Лог: $log ===" -ForegroundColor Cyan
Что ожидать:
text
Патч 1: OK — импорты добавлены
Патч 2: OK — _() и context processor зарегистрированы
Патч 3: OK — endpoint /set-lang/ добавлен

OK: web_admin.py сохранён
SYNTAX OK

=== E2b завершён. Лог: D:\tracker\_e2b.log ===
________________________________________
Скрипт E2c — патчим base.html
Меняем navbar: меню через _(), добавляем переключатель RU/EN. Ищем две отдельные короткие строки (не многострочный блок), чтобы не споткнуться о переносы строк.
powershell
$ErrorActionPreference = "Continue"
$log = "D:\tracker\_e2c.log"
"=== E2c started $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8 -Force

$path = "D:\tracker\server\templates\base.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains('/set-lang/')) {
    Write-Host "base.html уже содержит переключатель языка" -ForegroundColor Yellow
    "already patched" | Out-File $log -Append -Encoding utf8
} else {
    # --- Меняем каждую ссылку меню по отдельности ---
    # Это надёжнее, чем менять весь блок navbar целиком.
    $replacements = @(
        @{ old = 'href="/admin/employees">Сотрудники</a>';           new = 'href="/admin/employees">{{ _("menu.employees") }}</a>' },
        @{ old = 'href="/admin/departments">Отделы</a>';             new = 'href="/admin/departments">{{ _("menu.departments") }}</a>' },
        @{ old = 'href="/admin/computers">Компьютеры</a>';           new = 'href="/admin/computers">{{ _("menu.computers") }}</a>' },
        @{ old = 'href="/admin/tokens">Токены</a>';                  new = 'href="/admin/tokens">{{ _("menu.tokens") }}</a>' },
        @{ old = 'href="/admin/reports">Отчёты</a>';                 new = 'href="/admin/reports">{{ _("menu.reports") }}</a>' },
        @{ old = 'href="/admin/settings">Настройки</a>';             new = 'href="/admin/settings">{{ _("menu.settings") }}</a>' },
        @{ old = 'href="/admin/calendar">Календарь</a>';             new = 'href="/admin/calendar">{{ _("menu.calendar") }}</a>' },
        @{ old = 'href="/admin/audit">Аудит</a>';                    new = 'href="/admin/audit">{{ _("menu.audit") }}</a>' },
        @{ old = 'href="/admin/logout">Выход</a>';                   new = 'href="/admin/logout">{{ _("menu.logout") }}</a>' }
    )

    $count = 0
    foreach ($r in $replacements) {
        if ($content.Contains($r.old)) {
            $content = $content.Replace($r.old, $r.new)
            $count++
        }
    }
    Write-Host "Заменено пунктов меню: $count из 9" -ForegroundColor Cyan
    "replaced menu items: $count/9" | Out-File $log -Append -Encoding utf8

    # --- Добавляем переключатель языка перед "</div>" закрывающим navbar-nav ---
    # Ищем строку с "Выход" и вставляем блок ДО неё
    $logoutMarker = 'href="/admin/logout">{{ _("menu.logout") }}</a>'
    if ($content.Contains($logoutMarker) -and -not $content.Contains('set-lang')) {
        $langSwitcher = @'
{# ---------- Переключатель языка ---------- #}
<div class="d-flex align-items-center ms-3 me-2" role="group">
    {% for l in supported_langs %}
    <a class="btn btn-sm {% if l.code == current_lang %}btn-warning text-dark fw-bold{% else %}btn-outline-light{% endif %} me-1"
       href="/admin/set-lang/{{ l.code }}?next={{ request.url.path }}"
       title="{{ l.label }}">{{ l.short }}</a>
    {% endfor %}
</div>
            <a class="nav-link" href="/admin/logout">{{ _("menu.logout") }}</a>
'@
        $content = $content.Replace($logoutMarker, $langSwitcher.TrimEnd())
        Write-Host "OK: переключатель языка добавлен" -ForegroundColor Green
        "lang switcher: added" | Out-File $log -Append -Encoding utf8
    } else {
        Write-Host "Переключатель языка добавить не удалось (маркер не найден или уже есть)" -ForegroundColor Yellow
    }

    # --- Сохраняем ---
    try {
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: base.html сохранён" -ForegroundColor Green
        "saved: base.html" | Out-File $log -Append -Encoding utf8
    } catch {
        Write-Host "ОШИБКА сохранения: $_" -ForegroundColor Red
        "ERROR: $_" | Out-File $log -Append -Encoding utf8
    }
}

"=== E2c DONE $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Host "`n=== E2c завершён. Лог: $log ===" -ForegroundColor Cyan
________________________________________
Скрипт E2d — пересборка и проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Пересборка API ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

Write-Host "`n=== Статус контейнеров ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи API (последние 25 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=25

Write-Host "`n=== Что проверить ===" -ForegroundColor Green
Write-Host "1. Откройте https://localhost/admin" -ForegroundColor Green
Write-Host "2. В шапке должны быть кнопки RU / EN справа" -ForegroundColor Green
Write-Host "3. Нажмите EN — меню переключится на английский" -ForegroundColor Green
Write-Host "4. Обновите страницу — язык сохранился" -ForegroundColor Green
________________________________________
Что делать сейчас
Открой PowerShell через терминал VS Code (или закрепи окно PowerShell — не давай ему закрыться).
Запусти E2a — пришли вывод.
Если OK — запусти E2b — пришли вывод (важно увидеть: какие из 3 патчей применились).
Если OK — E2c — пришли вывод.
Если OK — E2d — открывай https://localhost/admin и проверяй переключатель.
Если где-то будет НЕ НАЙДЕН маркер или ОШИБКА — пришли текст ошибки и содержимое лога (Get-Content D:\tracker\_e2b.log). Ничего не закрывается, можно спокойно разобраться.
при переключении на английский Внутренняя ошибка сервера
The user gets a 500 when switching to English. Need to see the error. Most likely cause: the context processor runs, but supported_langs isn't being passed to the template, or _ isn't registered, or something.
Actually — the most likely cause: templates.context_processors may not be the correct attribute in Starlette Jinja2Templates. Let me think.
In Starlette's Jinja2Templates (used by FastAPI), the way to add context processors is:
python
templates = Jinja2Templates(directory="templates")
templates.env.globals["my_global"] = my_function

def my_context_processor(request):
    return {"foo": "bar"}

templates.context_processors.append(my_context_processor)
Actually, I'm not 100% sure context_processors exists on Jinja2Templates. Let me check... In older versions of Starlette, there wasn't a context_processors attribute. In newer versions, there is templates.context_processors and it's a list of callables.
Wait — actually Jinja2Templates in Starlette uses _create_env and doesn't have context_processors by default. Hmm. Let me think again.
Actually yes, in Starlette's Jinja2Templates, there IS a context_processors attribute added in version 0.22+ or so. It's a list of functions that take a Request and return a dict of context to merge.
So the setup should work... but maybe the issue is different.
Possible issues:
templates.context_processors.append(...) — if context_processors doesn't exist, this raises AttributeError at import time ? 500 on every page. But user says pages work until they switch to EN.
Actually "при переключении на английский" — so RU works, EN breaks. That means the code runs, but something specific to lang=en fails.
Looking at my template:
jinja
{% for l in supported_langs %}
If supported_langs is undefined when rendering... Jinja2 in Starlette by default would raise UndefinedError if strict undefined. But by default Starlette uses Undefined which silently becomes empty. Hmm.
Wait — actually the issue might be next={{ request.url.path }}. If path contains something that's HTML — no, this is URL. Should be fine.
Or — the issue: when switching to EN, next parameter in URL gets set. Then request.url.path in EN is still /admin or wherever. So cookie is set, redirect goes back. Then context processor reads cookie ? en. Then tries to render ? something is undefined.
Actually, let me think about the actual bug. When lang=en, the template renders {{ _("menu.employees") }}. The _ function uses contextvars. If contextvars isn't set (because context processor didn't run or failed silently), it defaults to "ru", so no issue with rendering.
Hmm, so what changes between ru and en?
OH. I see it. is_valid_lang is imported in web_admin.py from .i18n, but I also added it to imports. Let me check... yes, I added from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang. So that's fine.
But wait — in E2b, when I added the endpoint, I used is_valid_lang(code). If the import failed... but SYNTAX OK was printed.
Hmm. Let me think differently. When user clicks EN, the browser sends GET /admin/set-lang/en?next=/admin. Then:
set_lang runs, sets cookie, redirects to /admin with 303.
Browser follows redirect, GET /admin, now with cookie tracker_lang=en.
Dashboard handler runs. It renders dashboard.html which extends base.html.
Context processor reads cookie ? "en" ? set_current_lang("en") ? returns {current_lang: "en", supported_langs: [...]}.
Template renders. {{ _("menu.employees") }} ? t("menu.employees", "en") ? "Employees". Should work.
Unless... set_current_lang raises an exception. Let's check — is_valid_lang("en") ? True. _current_lang.set("en") — should work in a contextvars context.
Wait — contextvars in async context. When FastAPI handles request, it runs in an async task. The contextvars.ContextVar.set() inside a sync function called from async context — is that safe? Yes, it's safe — it creates a new context variable binding for the current task.
But there might be a subtle issue: if the set is done inside a nested function that runs in a DIFFERENT task/thread, changes don't propagate back. But template rendering is synchronous within the same task, so it should be fine.
Hmm. Let me look again at base.html modifications. In E2c I did:
text
$logoutMarker = 'href="/admin/logout">{{ _("menu.logout") }}</a>'
But WAIT — this is INSIDE a PowerShell here-string '...'@. The {{ and }} are literal — good. But _("menu.logout") — the double quotes inside single-quoted here-string... hmm, in PowerShell single-quoted here-string @'...'@, everything is literal EXCEPT you can't have '@ on its own line. So _("menu.logout") should be preserved literally.
But then in .Replace($logoutMarker, $langSwitcher.TrimEnd()) — this replaces the logout link text with a block containing the language switcher AND the logout link. So it should work.
Hmm, but there's another issue. In base.html, after E2c, we have:
html
{# ---------- Переключатель языка ---------- #}
<div class="d-flex align-items-center ms-3 me-2" role="group">
    {% for l in supported_langs %}
    ...
    {% endfor %}
</div>
            <a class="nav-link" href="/admin/logout">{{ _("menu.logout") }}</a>
If supported_langs is None or undefined ? {% for l in supported_langs %} might raise. In Jinja2 with default settings, for x in undefined ? I think it just iterates zero times (since Undefined is iterable-empty in default config). Actually no — default Undefined raises on iteration unless it's ChainableUndefined. Let me check.
In Jinja2, the default Undefined class:
__iter__ raises UndefinedError? Actually no — Undefined.__iter__ returns empty iterator. Wait...
Let me recall: Jinja2's Undefined class:
__len__ ? 0
__iter__ ? yields nothing
__bool__ ? False
__str__ ? ""
but __getattr__ raises
So {% for l in supported_langs %} where supported_langs is Undefined ? 0 iterations. Fine.
Hmm so what's the 500?
Wait — could it be that the context processor didn't run at all, and _ is Undefined in template? Then {{ _("menu.employees") }} ? tries to call Undefined ? raises. But that would break RU too.
Unless... templates.env.globals["_"] = _ was set for RU but not for EN? No, globals are global.
OK let me think about the actual specific difference between RU and EN request:
Both go to /admin.
Both hit dashboard().
Both go through same context processor.
Difference: cookie tracker_lang=ru vs tracker_lang=en.
Context processor returns different current_lang.
Hmm...
WAIT. Maybe the issue is different — maybe the cookie is too large? No, tracker_lang=en is tiny.
Or maybe the redirect is going wrong. Let me trace:
Click EN ? GET /admin/set-lang/en?next=/admin
FastAPI matches /set-lang/{code} — code="en"
is_valid_lang("en") ? True
next_url = "/admin"
RedirectResponse("/admin", status_code=303)
resp.set_cookie("tracker_lang", "en", ...)
Should be fine.
Hmm, unless... set_cookie in Starlette requires certain parameters, or samesite value causes issue. "lax" is valid. Actually wait, in older Starlette samesite was case-sensitive? Let me not go down that path.
Actually — maybe the issue is that is_valid_lang is NOT imported properly, and the import failed silently. But then E2b's SYNTAX OK would still pass (syntax doesn't check imports).
Let me think... from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang — but I wrote from .i18n import ... is_valid_lang? Let me check. In E2b I wrote:
text
from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang
And in i18n.py I have:
python
def is_valid_lang(code: str) -> bool:
    return code in {l["code"] for l in SUPPORTED_LANGS}
Yes, exists. OK.
Hmm. Let me approach differently — ask user for logs. That's the reliable way.
Actually let me think one more time. Could templates.context_processors.append(...) fail on older Starlette? Yes! If Jinja2Templates doesn't have context_processors attribute, then templates.context_processors returns... actually it would raise AttributeError at import time.
In Starlette:
Before version 0.26: no context_processors
Since 0.26 or so: Jinja2Templates has context_processors list
FastAPI 0.111.0 ? uses Starlette 0.37.x ? has context_processors. So OK.
Hmm, let me look at the actual flow again.
OH WAIT. I think I see it. In base.html, we have:
html
<a class="nav-link {% if '/departments' in request.url.path %}active{% endif %}" href="/admin/departments">{{ _("menu.departments") }}</a>
{{ _("menu.departments") }} — the _ is a global. Good.
But {{ _("menu.employees") }} — what if in the Replace step, the quotes got mangled? Let me check E2c's replacement logic:
powershell
$replacements = @(
    @{ old = 'href="/admin/employees">Сотрудники</a>'; new = 'href="/admin/employees">{{ _("menu.employees") }}</a>' }
)
In PowerShell single-quoted strings, " is literal. So new string is literally href="/admin/employees">{{ _("menu.employees") }}</a>. Good.
BUT — $content.Replace($r.old, $r.new) — the .Replace() method... wait, we're calling .Replace() on a string. That's .NET String.Replace(), which is case-sensitive literal replace. Should work.
Then it's saved as UTF-8 without BOM.
Hmm. OK, one more theory — maybe when next parameter is present with /admin, and we set cookie... the cookie setting itself might fail if domain/path is wrong. Let me think... set_cookie in Starlette: path="/" is fine.
Actually — you know what, let me look at this differently. The user said "при переключении на английский Внутренняя ошибка сервера". Maybe the 500 is on the REDIRECT step — i.e., GET /admin/set-lang/en itself returns 500. Let me check that.
@router.get("/set-lang/{code}") — this is a FastAPI route. code is a path parameter. request: Request — FastAPI injects. Then is_valid_lang("en") — should work.
Wait — did I import Request? Let me check... In web_admin.py, at the top there's:
python
from fastapi import APIRouter, Depends, Request, Form, HTTPException
Yes, Request is imported.
from fastapi.responses import RedirectResponse as _RR — local import, fine.
Hmm, but wait — the original web_admin.py imports:
python
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
So RedirectResponse is already imported. My local import shadows it with _RR — fine.
Actually, hmm, one more thing. response.set_cookie signature in Starlette:
python
def set_cookie(
    self, key, value="", max_age=None, expires=None, path="/",
    domain=None, secure=False, httponly=False,
    samesite="lax",
)
OK, samesite="lax" is valid. Good.
Hmm, I'm stuck guessing. Need logs.
Actually, wait. Let me re-read the E2b script more carefully.
The context processor signature — I wrote:
python
def _i18n_context_processor(request):
But Starlette's context_processors — how does it call them? In Starlette's TemplateResponse:
python
for context_processor in self.context_processors:
    context.update(context_processor(request))
So it passes request. Good, matches my signature.
Hmm, but what if Starlette calls it with a different signature? Let me check the source... In Starlette 0.37:
python
async def __call__(self, request: Request) -> None:
    ...

@property
def _context_processors(self):
    ...
Actually let me just check — I recall that Starlette's Jinja2Templates has:
python
self.context_processors: list[Callable[[Request], dict]] = []
and in the Response:
python
if self.context_processors:
    for cp in self.context_processors:
        context.update(cp(request))
Hmm, I'm not 100% sure. Let me just get the logs and see the actual error.
Actually wait — I just realized. Maybe the issue is from .config import settings was the ORIGINAL import that got REPLACED with the multi-line version. Let me re-check what the original import line looked like.
In the original web_admin.py (from our earlier work), I think we had:
python
from .config import settings
from .database import SessionLocal
from .models import (...)
So replacing from .config import settings with:
python
from .config import settings
from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang
from .web_i18n import _, set_current_lang, get_current_lang
Should be fine.
BUT — one problem: .database imports. Does database.py import something from config? Yes it does:
python
from config import settings
Wait, that's an absolute import without the leading dot. In the original that would work because the working directory is /app and there's a config.py in /app... no, wait. The imports are relative to the package. In server/database.py, from config import settings would look for a top-level config module — which doesn't exist. Unless PYTHONPATH includes server/.
Hmm, this is the "original" issue but it apparently works in the current setup. Let me not touch that.
OK, at this point, the fastest path is to get the actual error from logs. Let me ask for that.
Let me structure my response:
Explain that I need to see the error
Give commands to get the error
Suggest a likely fix proactively
Actually, let me think one more time. What could cause a 500 ONLY when lang=en?
If the context processor sets set_current_lang("en"), then _(...) returns English. Where in the template could an English string break something?
Hmm... In base.html we have:
jinja
{% block title %}Tracker Admin{% endblock %}
No translation there. OK.
What about the current_lang comparison? {% if l.code == current_lang %} — if current_lang is undefined, comparison with "en"/"ru" fails silently. Fine.
Hmm what about SUPPORTED_LANGS structure? It's a list of dicts. In Jinja, l.code accesses dict key — works. l.label — works. l.short — works.
OK wait. Maybe the issue is completely different. Maybe E2b actually FAILED at Patch 2 (registering context_processor), and the E2d rebuild caused a crash. Let me think about what would happen if Patch 2 didn't apply:
_ not registered as global ? template raises UndefinedError: '_' is undefined on any page.
That would break RU too, not just EN.
Unless — the user's base.html wasn't patched (E2c failed silently) and they never clicked EN because the switcher isn't there... but they said they DID click EN and got 500. So base.html WAS patched (switcher visible).
Hmm.
OK — one more theory. In base.html, after patching, we have:
html
<div class="d-flex align-items-center ms-3 me-2" role="group">
    {% for l in supported_langs %}
    ...
    {% endfor %}
</div>
If supported_langs is NOT in context — with default Undefined, iteration yields 0 items ? block renders empty ? no error.
But wait — is it possible that Starlette's Jinja2Templates uses StrictUndefined? Let me check... No, it uses default Undefined.
Hmm but actually let me check — the user sees 500 when switching. What if the error is in set_lang handler itself? Let me trace through:
text
@router.get("/set-lang/{code}")
def set_lang(code: str, request: Request):
    from fastapi.responses import RedirectResponse as _RR
    if not is_valid_lang(code):
        code = DEFAULT_LANG
    next_url = request.query_params.get("next") or "/admin"
    if not next_url.startswith("/"):
        next_url = "/admin"
    resp = _RR(next_url, status_code=303)
    resp.set_cookie(
        "tracker_lang", code,
        max_age=365 * 24 * 3600,
        path="/",
        samesite="lax",
    )
    return resp
Everything looks fine. Hmm.
WAIT. I bet I know the issue. @router.get("/set-lang/{code}") — this is a route on admin_web_router, which has prefix="/admin". So the full URL is /admin/set-lang/{code}. That's what we wanted.
But — the ORDER of route registration matters in FastAPI. If some other route pattern matches first... unlikely.
Hmm let me think about /admin/set-lang/en?next=/admin. FastAPI parses path as /admin/set-lang/en, query is next=/admin. Should match.
OK I really need the logs.
Actually — one more idea. request.url.path when we render base.html — if we're at /admin/set-lang/en?next=/admin — but wait, we redirect before rendering. So the render happens at /admin or wherever.
Hmm.
Actually, one thing that MIGHT be happening: when we do resp.set_cookie with the value "en", and then the browser sends it back — no wait, cookie value is fine.
OK. Let me just ask for logs. But let me ALSO proactively check a likely issue:
The context processor returns supported_langs from SUPPORTED_LANGS. But wait — I'm importing SUPPORTED_LANGS from .i18n. Let me verify that exists in i18n.py... yes, it does.
Hmm. Let me just ask for logs and see.
Actually — hold on. I just realized something. Let me re-check the replacement in E2b Patch 2.
Original line I was looking for:
python
templates.env.filters["dt"] = _fmt_dt_global
My replacement ADDS content AFTER this line:
python
$content = $content.Replace($oldFilter, $oldFilter + $addition)
Where $addition starts with \n\n# ----.... So the result is:
python
templates.env.filters["dt"] = _fmt_dt_global

