<!-- Часть 633 из 1409 -->
# Небольшой smoke-тест: проверим, что t() работает
*Хлебные крошки:* Небольшой smoke-тест: проверим, что t() работает

[◀ Проверка синтаксиса](632_Proverka_sintaksisa.md) | [Оглавление](00_BCE_INDEX.md) | [middleware или dependency: ▶](634_middleware_ili_dependency.md)

---

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

