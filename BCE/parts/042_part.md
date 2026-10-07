# ============================================================

*Часть 42 из 100. Источник: `BCE.md`.*

[◀ чтобы не ломать ничего.](041_chtoby_ne_lomat_nichego.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](043_part.md)

---

# ============================================================
def t(key: str, lang: Optional[str] = None) -> str:
    """
    Возвращает перевод по ключу.

    Аргументы:
      key  — ключ вида "menu.employees" (см. TRANSLATIONS выше).
      lang — код языка ("ru" или "en"). Если None или неизвестный —
             используется DEFAULT_LANG.

    Логика fallback (если перевод отсутствует):
      1. Пробуем взять перевод на нужном языке.
      2. Если нет — на DEFAULT_LANG.
      3. Если нет — возвращаем сам ключ (чтобы было видно, где дырка).
    """
    lang = lang or DEFAULT_LANG
    entry = TRANSLATIONS.get(key)
    if entry is None:
        # Такого ключа нет — возвращаем сам ключ, чтобы ошибка была видна
        return key
    if lang in entry:
        return entry[lang]
    return entry.get(DEFAULT_LANG) or key


def is_valid_lang(code: str) -> bool:
    """Проверяет, поддерживается ли такой код языка."""
    return code in {l["code"] for l in SUPPORTED_LANGS}
'@

[System.IO.File]::WriteAllText($i18nPath, $i18nPy, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $i18nPath" -ForegroundColor Green

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'$i18nPath', encoding='utf-8').read()); print('SYNTAX OK')"

# Небольшой smoke-тест: проверим, что t() работает
Write-Host "`n=== Проверка функции t() ===" -ForegroundColor Cyan
Set-Location D:\tracker
python -c @"
import sys
sys.path.insert(0, r'D:\tracker')
from server.i18n import t, SUPPORTED_LANGS
print('RU:', t('menu.employees', 'ru'))
print('EN:', t('menu.employees', 'en'))
print('Fallback (несущ. ключ):', t('no.such.key', 'en'))
print('Default (без lang):', t('btn.save'))
print('Поддерживаемые языки:', [l['code'] for l in SUPPORTED_LANGS])
"@
Ожидаемый вывод:
text
OK: создан D:\tracker\server\i18n.py
SYNTAX OK

=== Проверка функции t() ===
RU: Сотрудники
EN: Employees
Fallback (несущ. ключ): no.such.key
Default (без lang): Сохранить
Поддерживаемые языки: ['ru', 'en']
________________________________________
Что мы сделали в E1:
Создали server/i18n.py — центральный словарь переводов.
Функция t(key, lang) — с fallback на русский, потом на сам ключ.
60+ базовых строк на две языка (меню, кнопки, статусы, метрики).
Строки, которые не переводим, оговорены в комментарии в начале файла.
Что это даёт:
Дальше в любом месте сервера можно писать t("menu.employees") вместо хардкода.
В шаблонах — после E2 — будет {{ _("menu.employees") }}.
Когда добавляем новую строку — просто добавляем в TRANSLATIONS.
Запускай E1, проверь вывод, потом переходим к E2 — хук в Jinja2.
OK: создан D:\tracker\server\i18n.py SYNTAX OK === Проверка функции t() === RU: Сотрудники EN: Employees Fallback (несущ. ключ): no.such.key Default (без lang): Сохранить Поддерживаемые языки: ['ru', 'en']
Отлично, E1 работает. Переходим к E2 — хук в Jinja2 и определение текущего языка.
E2 должен:
Добавить в web_admin.py функцию определения текущего языка (из cookie или из admin_users.language в будущем).
Зарегистрировать глобальную функцию _ в Jinja2, которая использует текущий язык.
Добавить в шаблоны context переменную current_lang и langs для переключателя.
Добавить middleware для чтения cookie с языком.
Но проблема — глобальная функция _ в Jinja2 статична, она не знает про request. Решение — использовать contextvars или передавать язык через request.session / request.cookies.
Правильный подход:
В FastAPI есть Request, у которого есть request.state. Можно записать в request.state.lang в middleware.
Jinja2 templates вызывают _("key"), а сама функция _ должна как-то узнать язык.
Лучшее решение — использовать contextvars:
python
import contextvars
_current_lang = contextvars.ContextVar("current_lang", default="ru")

def _(key):
    return t(key, _current_lang.get())

# middleware или dependency:
def set_lang_from_request(request):
    lang = request.cookies.get("tracker_lang", "ru")
    if not is_valid_lang(lang):
        lang = "ru"
    _current_lang.set(lang)
Но contextvars работают в рамках async-задач. FastAPI обрабатывает каждый запрос в отдельной задаче, так что contextvars.set() в депенденси будет работать в рамках этого запроса.
Альтернатива — использовать request.state.lang и передавать язык в контекст шаблона явно. Но тогда в каждом шаблоне нужно писать {{ t("key", lang) }} или вызывать _(key) — а _ не знает язык.
Проще всего — contextvars. Реализуем.
Также надо:
Переключатель языка в шапке (base.html) — маленькие кнопки RU/EN.
Endpoint /admin/set-lang/{code} — ставит cookie.
В шаблонах доступна переменная current_lang и supported_langs.
Давай напишу E2. Это будет:
Модуль server/web_i18n.py — с contextvars, хуком.
Патч web_admin.py — регистрация хука + endpoint.
Патч base.html — переключатель + использование _().
Хотя пользователь сказал "начнём с Скрипт D1" — но у нас уже E1 сделано. Продолжаем E-серию, потом вернёмся к Alembic.
Давай сделаю E2 аккуратно. Один скрипт, который делает всё нужное.
Мне нужно:
Создать server/web_i18n.py — с contextvars и функцией _, подключённой к t().
В web_admin.py:
Добавить import
Зарегистрировать _ в Jinja2 globals
Добавить dependency get_lang для чтения из cookie
Endpoint POST /admin/set-lang
В base.html:
Добавить переключатель RU/EN в navbar
Использовать _() для пунктов меню
Давай напишу одним скриптом.
Осторожно с PowerShell-кавычками. Использую here-strings с одинарными кавычками (литеральные).
Для изменений в base.html — там сложно. Давай сначала только инфраструктуру сделаем (server/web_i18n.py + патчи web_admin.py), а базовый шаблон переделаем в E3.
Хотя проще сразу — подключим и проверим, что работает переключение. Пусть E2 = инфраструктура + минимальный переключатель в base.html (только navbar и меню). Остальные строки в шаблонах переведём потом.
Пишу.
Структура скрипта E2:
Часть 1: создать server/web_i18n.py
Часть 2: патч web_admin.py
Часть 3: патч base.html (переключатель + меню через _())
Часть 4: пересборка + проверка
Let me write it out carefully.
Для base.html мне нужно заменить navbar. Текущий navbar:
html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid px-4">
        <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
        <div class="navbar-nav ms-auto">
            {% if admin %}
            <a class="nav-link ..." href="/admin/employees">Сотрудники</a>
            ...
            <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
            <a class="nav-link" href="/admin/logout">Выход</a>
            {% endif %}
        </div>
    </div>
</nav>
Заменяем на:
html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid px-4">
        <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
        <div class="navbar-nav ms-auto">
            {% if admin %}
            <a class="nav-link ..." href="/admin/employees">{{ _("menu.employees") }}</a>
            ...
            {# Переключатель языка #}
            <div class="d-flex align-items-center ms-3">
                {% for l in supported_langs %}
                <a class="btn btn-sm {% if l.code == current_lang %}btn-warning{% else %}btn-outline-light{% endif %} me-1"
                   href="/admin/set-lang/{{ l.code }}?next={{ request.url.path }}">{{ l.short }}</a>
                {% endfor %}
            </div>
            <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
            <a class="nav-link" href="/admin/logout">{{ _("menu.logout") }}</a>
            {% endif %}
        </div>
    </div>
</nav>
Endpoint /admin/set-lang/{code} — GET (чтобы работало через ссылку), ставит cookie и редиректит.
Напишу код.
Для contextvars в async FastAPI:
python
# server/web_i18n.py
import contextvars
from typing import Optional
from .i18n import t, DEFAULT_LANG, is_valid_lang

_current_lang: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_lang", default=DEFAULT_LANG
)

def set_current_lang(lang: str) -> None:
    """Устанавливает язык для текущего запроса."""
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    _current_lang.set(lang)

def get_current_lang() -> str:
    """Возвращает язык текущего запроса."""
    return _current_lang.get()

def _(key: str) -> str:
    """Короткая обёртка для шаблонов и кода."""
    return t(key, _current_lang.get())
В web_admin.py:
python
from .web_i18n import _, set_current_lang, get_current_lang
from .i18n import SUPPORTED_LANGS

# Регистрируем `_` в Jinja
templates.env.globals["_"] = _

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

# ============================================================
# 1. Создаём server/web_i18n.py
# ============================================================
$webI18n = @'
# ============================================================
# Хук i18n для веб-интерфейса (связка i18n.py и Jinja2)
# ============================================================
# Зачем этот файл отдельно от i18n.py:
#   В i18n.py лежат переводы и функция t(key, lang). Она требует
#   явно указать язык.
#   В веб-интерфейсе язык берётся из cookie текущего запроса.
#   Чтобы не таскать язык явно в каждый вызов, используем
#   contextvars — это переменная, привязанная к текущему потоку/задаче.
#   Каждый HTTP-запрос обрабатывается в отдельной задаче, поэтому
#   язык, установленный для одного запроса, не влияет на другие.
#
# Как это работает:
#   1. При рендере шаблона context processor в web_admin.py читает
#      cookie "tracker_lang" и вызывает set_current_lang(lang).
#   2. В шаблоне работает функция `_("ключ")` — она берёт язык из
#      contextvars и передаёт в t().
# ============================================================

import contextvars
from typing import Optional

from .i18n import t, DEFAULT_LANG, is_valid_lang


# Текущий язык запроса. По умолчанию — русский.
_current_lang: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_lang", default=DEFAULT_LANG
)


def set_current_lang(lang: Optional[str]) -> str:
    """
    Устанавливает язык для текущего запроса.
    Если язык не поддерживается — ставит DEFAULT_LANG.
    Возвращает фактически установленный код.
    """
    if not lang or not is_valid_lang(lang):
        lang = DEFAULT_LANG
    _current_lang.set(lang)
    return lang


def get_current_lang() -> str:
    """Возвращает язык текущего запроса."""
    return _current_lang.get()


def _(key: str) -> str:
    """
    Короткая обёртка для использования в шаблонах и коде.
    Пример: _("menu.employees") -> "Сотрудники" или "Employees".
    """
    return t(key, _current_lang.get())
'@

[System.IO.File]::WriteAllText("$serverDir\web_i18n.py", $webI18n, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $serverDir\web_i18n.py" -ForegroundColor Green


# ============================================================
# 2. Патчим web_admin.py — регистрируем _() и context processor
# ============================================================
$webAdminPath = "$serverDir\web_admin.py"
$content = [System.IO.File]::ReadAllText($webAdminPath, [System.Text.UTF8Encoding]::new($false))

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

# ------------------------------------------------------------
# i18n: регистрируем функцию перевода _() в Jinja2.
# Теперь в любом шаблоне работает {{ _("ключ") }}.
# ------------------------------------------------------------
templates.env.globals["_"] = _


# ------------------------------------------------------------
# Context processor: перед рендером каждого шаблона
# читает cookie "tracker_lang", устанавливает язык
# в contextvars и добавляет в контекст шаблона переменные
# current_lang и supported_langs (для переключателя).
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
# Логин / логаут"
    $setLangBlock = @'
# ============================================================
# Переключение языка интерфейса
# ============================================================
@router.get("/set-lang/{code}")
def set_lang(code: str, request: Request):
    """
    Устанавливает язык админки через cookie.
    После переключения возвращает пользователя на ту же страницу,
    с которой пришёл (параметр next в query string).
    """
    from fastapi.responses import RedirectResponse as _RR
    if not is_valid_lang(code):
        code = DEFAULT_LANG
    next_url = request.query_params.get("next") or "/admin"
    # Не разрешаем редирект на внешние URL — только на наши
    if not next_url.startswith("/"):
        next_url = "/admin"
    resp = _RR(next_url, status_code=303)
    # Cookie на 1 год, доступна для всех страниц админки
    resp.set_cookie(
        "tracker_lang", code,
        max_age=365 * 24 * 3600,
        path="/",
        samesite="lax",
    )
    return resp


# ============================================================
# Логин / логаут
# ============================================================
'@
    if ($content.Contains($anchor)) {
        $content = $content.Replace($anchor, $setLangBlock.TrimEnd())
        Write-Host "OK: endpoint /admin/set-lang/{code} добавлен" -ForegroundColor Green
    } else {
        Write-Host "Не найден маркер 'Логин / логаут' — правьте вручную" -ForegroundColor Red
        exit 1
    }
}

[System.IO.File]::WriteAllText($webAdminPath, $content, [System.Text.UTF8Encoding]::new($false))
python -c "import ast; ast.parse(open(r'$webAdminPath', encoding='utf-8').read()); print('SYNTAX OK')"


# ============================================================
# 3. Патчим base.html — переключатель + меню через _()
# ============================================================
$basePath = "$serverDir\templates\base.html"
$baseContent = [System.IO.File]::ReadAllText($basePath, [System.Text.UTF8Encoding]::new($false))

if ($baseContent.Contains('set-lang')) {
    Write-Host "base.html уже содержит переключатель языка" -ForegroundColor Yellow
} else {
    # 3.1. Меняем navbar: меню через _() + переключатель RU/EN
    $oldNav = @'
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid px-4">
        <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
        <div class="navbar-nav ms-auto">
            {% if admin %}
            <a class="nav-link {% if request.url.path == '/admin/employees' %}active{% endif %}" href="/admin/employees">Сотрудники</a>
            <a class="nav-link {% if '/departments' in request.url.path %}active{% endif %}" href="/admin/departments">Отделы</a>
            <a class="nav-link {% if '/computers' in request.url.path %}active{% endif %}" href="/admin/computers">Компьютеры</a>
            <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}" href="/admin/tokens">Токены</a>
            <a class="nav-link {% if '/reports' in request.url.path %}active{% endif %}" href="/admin/reports">Отчёты</a>
            <a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>
            <a class="nav-link {% if '/calendar' in request.url.path %}active{% endif %}" href="/admin/calendar">Календарь</a>
            <a class="nav-link {% if '/audit' in request.url.path %}active{% endif %}" href="/admin/audit">Аудит</a>
            <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
            <a class="nav-link" href="/admin/logout">Выход</a>
            {% endif %}
        </div>
    </div>
</nav>
'@

    $newNav = @'
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid px-4">
        <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
        <div class="navbar-nav ms-auto align-items-center">
            {% if admin %}
            <a class="nav-link {% if request.url.path == '/admin/employees' %}active{% endif %}" href="/admin/employees">{{ _("menu.employees") }}</a>
            <a class="nav-link {% if '/departments' in request.url.path %}active{% endif %}" href="/admin/departments">{{ _("menu.departments") }}</a>
            <a class="nav-link {% if '/computers' in request.url.path %}active{% endif %}" href="/admin/computers">{{ _("menu.computers") }}</a>
            <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}" href="/admin/tokens">{{ _("menu.tokens") }}</a>
            <a class="nav-link {% if '/reports' in request.url.path %}active{% endif %}" href="/admin/reports">{{ _("menu.reports") }}</a>
            <a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">{{ _("menu.settings") }}</a>
            <a class="nav-link {% if '/calendar' in request.url.path %}active{% endif %}" href="/admin/calendar">{{ _("menu.calendar") }}</a>
            <a class="nav-link {% if '/audit' in request.url.path %}active{% endif %}" href="/admin/audit">{{ _("menu.audit") }}</a>

            {# ---------- Переключатель языка ---------- #}
            <div class="d-flex align-items-center ms-3" role="group" aria-label="Language">
                {% for l in supported_langs %}
                <a class="btn btn-sm {% if l.code == current_lang %}btn-warning text-dark fw-bold{% else %}btn-outline-light{% endif %} me-1"
                   href="/admin/set-lang/{{ l.code }}?next={{ request.url.path }}"
                   title="{{ l.label }}">{{ l.short }}</a>
                {% endfor %}
            </div>

            <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
            <a class="nav-link" href="/admin/logout">{{ _("menu.logout") }}</a>
            {% endif %}
        </div>
    </div>
</nav>
'@

    if ($baseContent.Contains($oldNav)) {
        $baseContent = $baseContent.Replace($oldNav, $newNav)
        Write-Host "OK: navbar обновлён — меню через _(), добавлен переключатель" -ForegroundColor Green
    } else {
        Write-Host "Не найден блок navbar — правьте вручную" -ForegroundColor Yellow
        Write-Host "Откройте server/templates/base.html и найдите <nav ...>" -ForegroundColor Yellow
        exit 1
    }

    [System.IO.File]::WriteAllText($basePath, $baseContent, [System.Text.UTF8Encoding]::new($false))
}


# ============================================================
# 4. Пересборка
# ============================================================
Set-Location D:\tracker
Write-Host "`n=== Пересборка API ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose ps
Write-Host "`n=== Логи API ===" -ForegroundColor Cyan
docker compose logs api --tail=20

Write-Host "`n=== Проверка ===" -ForegroundColor Green
Write-Host "Откройте https://localhost/admin" -ForegroundColor Green
Write-Host "В шапке справа — кнопки RU / EN." -ForegroundColor Green
Write-Host "Нажмите EN — меню должно переключиться на английский." -ForegroundColor Green
Write-Host "Обновите страницу — язык должен сохраниться (cookie)." -ForegroundColor Green
________________________________________
Что проверять после E2
Открой https://localhost/admin — должен увидеть шапку с пунктами меню на русском и кнопками RU | EN справа.
Нажми EN — меню переключится: «Employees», «Departments», «Computers», «Tokens», «Reports», «Settings», «Calendar», «Audit», «Logout».
Обнови страницу — язык сохранился (cookie tracker_lang=en).
Нажми RU — вернулось на русский.
Что ещё НЕ переведено (постепенно переведём в следующих шагах):
Содержимое страниц — заголовки внутри (<h3>Дашборд</h3> и т.п.).
Кнопки внутри форм («Сохранить», «Удалить»).
Тултипы (title="").
Сообщения в JS.
Это нормально — переводим инкрементально. Сейчас главное, чтобы инфраструктура работала и переключалась.
________________________________________
Если что-то пошло не так
Симптом: 500 при открытии /admin.
Причина: скорее всего, context processor не отработал.
Действия: пришли docker compose logs api --tail=40.
Симптом: шаблон падает с UndefinedError: '_' is undefined.
Причина: templates.env.globals["_"] = _ не зарегистрировалось.
Проверка: docker compose exec api grep -n "templates.env.globals" /app/server/web_admin.py.
Симптом: при клике на RU/EN ничего не меняется.
Причина: cookie не сохраняется (может быть из-за того, что next_url неправильный).
Проверка: в браузере DevTools ? Application ? Cookies ? должна быть tracker_lang.
________________________________________
Запускай E2, пришли результат. Если меню переключается — идём дальше: E3 (перевод содержимого страниц, инкрементально), потом E4–E5 (клиент), и возвращаемся к Alembic D2–D9.
Windows PowerShell после Скрипт E2 выключается
The user says PowerShell closes after running Script E2. This is a common issue - probably the script crashed somewhere and the window closed, or there's a syntax error causing the shell to terminate. Let me think about what could cause this.
Most likely cause: $ErrorActionPreference = "Stop" combined with something that fails, but that would just show an error and stop the script, not close the window.
Actually, thinking about it more - the user is running the script by copy-pasting into PowerShell. If the script contains something that terminates the shell (like exit command in the middle), or if there's a syntax error that causes the here-string to never close properly, the shell might hang waiting for input... but user says it closes.
Possible causes:
Here-string delimiter collision - one of my @' or '@ sequences might be malformed
Inside the here-string content, there might be a line that starts with '@ (closing delimiter), which would prematurely end the string
An issue with special characters
Let me look at my E2 script carefully:
In the set_lang_block here-string, I have:
text
    from fastapi.responses import RedirectResponse as _RR
    if not is_valid_lang(code):
        code = DEFAULT_LANG
Nothing unusual there.
In the base.html patch, I have:
text
    $oldNav = @'
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
...
'@
Wait - inside the $newNav block, I have Jinja template syntax like {% if ... %} and {{ ... }} - those are fine in a single-quoted here-string. But I have {@ ... @}? No, I don't think so.
Hmm, one issue: the @' should be at the END of a line followed by newline. In my PowerShell scripts, when I paste them into the response, formatting should preserve this. But if the user's copy-paste loses the trailing newlines, or if there's a line-break issue...
Actually, the more likely cause: the user copied the ENTIRE script and pasted it. If the paste happened too fast, or if there was a very long paste, the terminal might have buffered it incorrectly.
But user says "Windows PowerShell после Скрипт E2 выключается" - PowerShell closes after E2.
Wait - another likely cause. The docker compose down and docker compose up -d --build at the end. If Docker Desktop isn't running... no, that wouldn't close PowerShell.
Actually - thinking again - what if the user is running PowerShell in a way that it exits on any terminating error? Like powershell -Command "..." mode? Probably not.
Or maybe when the script finishes, the window auto-closes because the user launched it via double-click on a .ps1 file. In that case, the shell closes after the script ends. But user says after E2 specifically.
Hmm, most likely cause: there's a syntax error somewhere in my script that causes PowerShell to enter a waiting state, and the user pressed Ctrl+C or closed the window. Then when they said "it closes" they mean the previous session ended.
Or: one of the here-strings contains a line that is exactly '@ which ends it early. Let me check...
Looking at my $newNav block - no line is exactly '@.
Actually, wait. There might be an issue. In my PowerShell script I have:
powershell
$anchor = "# ============================================================
# Логин / логаут"
This is a double-quoted string spanning multiple lines. In PowerShell, double-quoted strings can span lines, so that should be fine. But it could cause issues if the multi-line string isn't handled the way I expect.
Actually, let me look at the actual issue. The user just says "выключается" (turns off/closes). This is very vague. Let me:
First ask what exactly they see before it closes (any error message?)
Suggest they run it in a way that keeps the window open
Give a more robust approach - split into smaller scripts or write to file first
Actually, the simplest explanation: the user is running a .ps1 file with double-click, and the script completes normally (maybe with error) but the window closes immediately so they can't see anything.
Best approach: rewrite E2 as multiple smaller scripts, each with pause at the end. Or give instructions to capture output to a file.
Let me also reconsider - there may be a syntax problem. One issue I see:
powershell
$anchor = "# ============================================================
# Логин / логаут"
This should work but let me be safer and use here-string. Actually the issue is - inside that string I have # which is fine in a string, but the closing " needs to be at end of second line. Should work.
Another possibility: the $content.Contains($anchor) might not match because in the file the actual text is:
text
# ============================================================
# Логин / логаут
