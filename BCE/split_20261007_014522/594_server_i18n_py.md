<!-- Часть 594 из 1409 -->
# server/i18n.py
*Хлебные крошки:* server/i18n.py

[◀ Генерируем автогенерацию — Alembic не запустит апгрейд, а только создаст файл миграции](593_Generiruem_avtogeneratsiyu_Alembic_ne_zapustit_apgreyd_a_tolko_sozdast_fayl_migr.md) | [Оглавление](00_BCE_INDEX.md) | [client/i18n.py — тот же подход ▶](595_client_i18n_py_tot_zhe_podhod.md)

---

# server/i18n.py
TRANSLATIONS = {
    "menu.employees": {"ru": "Сотрудники", "en": "Employees"},
    "menu.departments": {"ru": "Отделы", "en": "Departments"},
    "btn.save": {"ru": "Сохранить", "en": "Save"},
    # ...
}

def t(key: str, lang: str = "ru") -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("ru") or key
В Jinja2 подключаем через глобальную функцию:
python
templates.env.globals["_"] = lambda key: t(key, current_lang)
В шаблоне:
html
<a class="nav-link" href="/admin/employees">{{ _("menu.employees") }}</a>
Клиент:
python
