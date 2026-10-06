# Шаблоны
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 01_PRODUCT\03_ADMIN_UI.md, 03_SERVER\08_I18N.md

## Назначение
Описать HTML-шаблоны веб-админки: где лежат, как устроены, какие блоки и переменные используют, как связаны с роутами. Это карта для разработчика, который дорабатывает интерфейс.

## Содержание

### Общие принципы
- Шаблонизатор: **Jinja2**.
- Расположение: `server/templates/`.
- Все шаблоны наследуют `base.html` через `{% extends "base.html" %}`.
- Все UI-строки — через `_("key")` (i18n).
- Все защищённые страницы требуют `current_admin`.
- Bootstrap 5.3 через CDN.
- Тултипы через `data-bs-toggle="tooltip"` + `bootstrap.Tooltip`.
- Формат длительностей — фильтр `| dur`.
- Формат дат — фильтр `| dt`.

### Context processor
В каждый шаблон автоматически подмешиваются (см. `03_SERVER\08_I18N.md`):
- `current_lang` — текущий язык (ru/en).
- `supported_langs` — список языков.
- `_` — bound-функция перевода.
- `admin` — отображаемое имя админа.
- `admin_role`, `current_role` — код роли.
- `admin_username`, `admin_id`, `admin_department_id`.
- `roles_info` — словарь ролей.
- `request` — объект запроса.

### Список шаблонов (~22 штуки)

| Шаблон | Роут GET | Назначение |
|---|---|---|
| `base.html` | — | Общий каркас, navbar, sidebar, переключатель языка |
| `login.html` | `/admin/login` | Форма входа |
| `setup.html` | `/admin/setup` | Первичная настройка |
| `dashboard.html` | `/admin` | Дашборд: статистика, онлайн-ПК |
| `employees.html` | `/admin/employees` | Сотрудники: вкладки, inline-редактирование |
| `departments.html` | `/admin/departments` | Отделы: CRUD |
| `computers.html` | `/admin/computers` | ПК: привязка, массовая привязка CSV |
| `tokens.html` | `/admin/tokens` | Bootstrap-токены: выпуск, список |
| `reports.html` | `/admin/reports` | Форма отчёта + localStorage |
| `reports_pivot.html` | `/admin/reports/pivot` | PivotTable.js |
| `report_result.html` | (POST generate) | Результат отчёта |
| `settings.html` | `/admin/settings` | Настройки приложения |
| `calendar.html` | `/admin/calendar` | Календарь рабочих дней |
| `audit.html` | `/admin/audit` | Журнал аудита |
| `users.html` | `/admin/users` | Пользователи админки |
| `user_form.html` | `/admin/users/new`, `/admin/users/{id}/edit` | Форма пользователя |
| `user_reset_password.html` | `/admin/users/{id}/reset-password` | Сброс пароля |
| `logins.html` | `/admin/logins` | История входов |
| `scheduler.html` | `/admin/scheduler` | Планировщик задач |
| `schedules.html` | `/admin/schedules` | Список графиков |
| `schedule_form.html` | `/admin/schedules/new`, `/admin/schedules/{id}/edit` | Форма графика |
| `sessions.html` | `/admin/sessions` | Список сессий |
| `trash.html` | `/admin/trash` | Корзина (3 вкладки) |
| `profile.html` | `/admin/profile` | Мой профиль |
| `employee_settings.html` | `/admin/employees/{id}/settings` | Персональные настройки |

### Детали по ключевым шаблонам

#### `base.html`
**Блоки:**
```jinja
{% block title %}Tracker Admin{% endblock %}
{% block content %}{% endblock %}
Меню (sidebar) сгруппировано:

Main: Дашборд

Справочники: Сотрудники, Отделы, Графики, Компьютеры

Данные: Отчёты, Pivot, Сессии, Календарь, Аудит

Администрирование: Токены, Планировщик, Пользователи, Входы, Корзина, Настройки

Видимость пунктов — через {% if admin_role in (...) %}.

Topbar:

Ссылка на /admin/profile — имя + роль.

Кнопка «Мой профиль».

Кнопка «Выход».

Переключатель языка (RU/EN) — цикл по supported_langs, ссылка /admin/set-lang/{code}?next=....

login.html
Поля: username (по умолчанию admin), password.

method="post", action="/admin/login".

Плашка setup_done — если админ только что создан через /admin/setup.

Ошибка error — если неверный логин/пароль.

dashboard.html
Переменные:

stats.employees, stats.departments, stats.computers, stats.computers_online

stats.sessions_today, stats.sessions_week, stats.records, stats.tokens_active

recent_computers — последние 15 ПК

recent_audit — последние 10 действий

cutoff_online — порог онлайна

employees — словарь для ФИО

Блоки:

4 карточки: Сотрудники, Отделы, Компьютеры, Компьютеры онлайн.

3 карточки: Сессии сегодня, Сессии 7 дней, Всего записей.

Таблица «Компьютеры»: hostname, UID, ФИО, last_seen, статус.

Таблица «Последние действия».

Важно: поле employees обязательно в контексте, иначе c.employee → 500 (был баг).

employees.html
Вкладки: Активные / Уволенные / Все (query tab).

Форма добавления (только при tab == 'active'):

last_name, first_name, middle_name, external_id, department_id.

Таблица — inline-форма редактирования для каждой строки:

POST /admin/employees/{id}/edit.

Выпадающий список отделов + выпадающий список графиков (опция «как в отделе»).

Кнопки:

Уволить / Восстановить / Удалить навсегда.

computers.html
Форма массовой привязки:

POST /admin/computers/bulk-assign, enctype="multipart/form-data".

CSV: hostname; 1C_ID (разделитель ; или ,).

Таблица:

Hostname, UID, select сотрудника + OK, last_seen, статус (badge), кнопки Отключить / Включить / Перерегистрация / Удалить.

reports.html
Форма id="reportForm", POST /admin/reports/generate:

Период: date_from, date_to.

Отделы: department_ids (multiple select).

Сотрудники: employee_ids.

Компьютеры: computer_ids.

Группировка: group_by (days/months/employees/departments/computers/sessions).

Формат: fmt (html/xlsx/csv/pdf).

Чекбоксы: show_apps, show_abnormal, expand_details.

JS:

setRange(from, to), periodToday(), periodLastNDays(n), periodThisMonth(), periodLastMonth(), periodThisYear().

saveFilters() / loadFilters() — localStorage["tracker_report_filters_v1"].

resetFilters() — очистка.

onDepartmentsChanged() — зависимая фильтрация через emp_dept_map.

Плашка — текущие TZ, начало дня, порог паузы, ссылка на /admin/settings.

report_result.html
Верхняя строка контекста:

Период, TZ, начало рабочего дня, группировка, сессии, сотрудники, отделы, аварийные.

Плашка ИТОГО:

5 метрик: Отработано, С трекером, Интенсивная, Эффективно, Пауза.

Топ программ (если show_apps):

Таблица: Программа | Время | Клавиатура | Мышь.

Раскрытие details → a.by_employee.

Основная таблица:

Колонки зависят от группировки.

Подсветка table-warning (weekend) / table-danger (holiday).

Раскрытие строки details → сессии + программы.

Блок «Без привязки»:

report.unattached — список ПК с непривязанными сессиями.

Формы привязки / удаления.

Фильтры Jinja:

| dur — формат HH:MM:SS.

| dt — формат DD.MM.YYYY HH:MM.

settings.html
Поля cfg:

idle_close_minutes, workday_start_hour, activity_gap_minutes, report_timezone, sync_interval, batch_size, active_window_interval, idle_threshold, count_weekends, stale_session_hours, reminder_*, end_of_day_*.

Форма: POST /admin/settings/save.

Плашка «saved» — если ?saved=1.

calendar.html
Структура months:

python
{
  "num": 1..12,
  "name": "Январь",
  "weeks": [[None | {"date": date, "iso": str, "is_working": bool, "weekday": 0..6}]]
}
Форма сохранения: POST /admin/calendar/save, чекбоксы day_YYYY-MM-DD.
Кнопки: «Сгенерировать», «Сбросить».

users.html
Таблица: ID, Логин, ФИО, Email, Роль, Язык, Активен, Последний вход, Действия.
Кнопки: Изменить, Пароль, Отключить/Включить, Удалить.

user_form.html
Поля:

username (только при создании, pattern [a-zA-Z0-9._\-]+, min 3).

full_name, email, role (select из roles_info), department_id (только для manager), language, password + password_confirm (при создании).

JS: toggleDepartment() — показать/скрыть поле отдела.

scheduler.html
Колонки: Имя, Описание, Включена, Cron, Последний запуск, Статус, Действия.
Кнопки: Вкл/выкл, Изменить cron, Запустить сейчас.

sessions.html
Фильтры: date_from, date_to, employee_id, computer_id, show_deleted.
Действия: Удалить выбранные, Удалить по фильтру, Удалить одну.
Колонки: Начало, Конец, Сотрудник, Компьютер, Длительность, Статус.

trash.html
Вкладки: Сессии / Сотрудники / Компьютеры.
Действия: Восстановить, Удалить навсегда, Очистить всё.

profile.html
Форма 1: ФИО, Email, Язык.
Форма 2: Текущий пароль, новый пароль + подтверждение.

schedules.html / schedule_form.html
Список: Название, Рабочие часы, Рабочие дни, Используется (сотрудники / отделы).
Форма: Название, описание, рабочие дни недели, начало/конец дня, обед, пороги опоздания/переработки, гибкий график.

Фильтры Jinja2
Регистрируются в web_admin.py:

python
templates.env.filters["dur"] = _fmt_dur          # секунды → HH:MM:SS
templates.env.filters["dt"] = _fmt_dt_global     # datetime → DD.MM.YYYY HH:MM
templates.env.globals["_"] убран — _ приходит из context processor (bound на язык).

Известные баги и решения
Баг	Причина	Решение
500 на дашборде	Не передан cutoff_online в контекст	Добавить в TemplateResponse
500 на /admin/reports	Убран фильтр dt, но используется в шаблоне	Вернуть глобальный dt
500 при переключении на EN	contextvars в sync-обработчиках	Заменить на bound-функцию _
«Крокозябры» в logins.html, users.html	Неверная кодировка эмодзи	Переписать шаблоны в UTF-8
Мусор в PDF от вложенных <details>	reportlab не умеет парсить HTML	Строить PDF по плоскому списку
Pivot пустой	Кастомный агрегатор суммировал rowKey вместо vals	Зарегистрировать durationSum через aggregatorTemplates
Правила при правке шаблонов
Всегда {% extends "base.html" %}.

Все UI-строки через _("key").

Не использовать inline-стили для элементов, которые должны менять тему (только QSS через setObjectName — это для клиента; в вебе — Bootstrap-классы).

Формат длительностей — | dur, дат — | dt.

Тултипы — data-bs-toggle="tooltip" + bootstrap.Tooltip.

Иконка ⓘ — только если есть перевод (*.hint).

После правки HTML — docker compose restart api (без rebuild).

Ключевые решения
Единый base.html. Общий каркас, навигация, переключатель языка.

Sidebar с группировкой. Main / Справочники / Данные / Администрирование.

Видимость по ролям. admin_role в шаблоне.

Inline-редактирование в таблицах (сотрудники, отделы, ПК) — быстрее, чем отдельные формы.

localStorage для фильтров отчёта. Не теряются при перезагрузке.

PivotTable.js на отдельной странице. Не часть формы отчёта.

{% extends %} везде. Никаких копий каркаса.

Bound-функция _. Не теряет язык.

PRG-паттерн. После POST — редирект.

Ссылки на код
запросить: server/templates/ — все шаблоны

запросить: server/web_admin.py — templates, _i18n_context_processor, _fmt_dur, _fmt_dt_global

запросить: server/templates/base.html — каркас, sidebar, topbar

запросить: server/templates/reports.html, reports_pivot.html, report_result.html — отчёты

запросить: server/templates/scheduler.html — планировщик

запросить: server/templates/schedule_form.html — форма графика

Открытые вопросы / чего не хватает
нет данных: полный текст некоторых шаблонов (tokens.html, users.html, scheduler.html, trash.html, schedules.html, logins.html, audit.html) — показывались частично.

нет данных: точные ключи i18n во всех шаблонах — только в i18n.py.

нет данных: есть ли хардкод по-русски в части шаблонов — нужно проверить.

не решено: добавлять ли хлебные крошки — сейчас нет.

не решено: нужна ли тёмная тема админки — обсуждалось, но не реализовано.

не решено: как быть с очень широкими таблицами на мобильных — адаптивность не проверялась.

не решено: удалять ли web_i18n.py (legacy).

не решено: писать ли автотест на «все ключи из шаблонов есть в TRANSLATIONS».

не решено: нужна ли отдельная страница /admin/api (в планах).

не решено: нужна ли страница /admin/help (в планах).

Готово. Один файл выше. Следующий по индексу — 03_SERVER\10_SETTINGS.md.