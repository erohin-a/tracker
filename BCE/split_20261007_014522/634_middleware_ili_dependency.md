<!-- Часть 634 из 1409 -->
# middleware или dependency:
*Хлебные крошки:* middleware или dependency:

[◀ Небольшой smoke-тест: проверим, что t() работает](633_Nebolshoy_smoke_test_proverim_chto_t_rabotaet.md) | [Оглавление](00_BCE_INDEX.md) | [server/web_i18n.py ▶](635_server_web_i18n_py.md)

---

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
