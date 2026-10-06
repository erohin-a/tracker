# Pivot-таблица
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 02_METRICS\01_METRICS.md, 02_METRICS\02_REPORTS.md, 03_SERVER\02_API.md

## Назначение
Описать интерактивную сводную таблицу (pivot) в веб-админке: зачем она нужна, как устроена, какие данные получает, как рендерится и какие имеет ограничения. Это карта для администратора, который строит сводную, и для разработчика, который её дорабатывает.

## Содержание

### Что такое pivot в «Трекере»
- Страница `/admin/reports/pivot` — интерактивная сводная таблица, аналог сводной в Excel.
- Реализована на **PivotTable.js** — open-source JavaScript-библиотеке с drag-and-drop интерфейсом[reference:0].
- Отличается от обычного отчёта: пользователь сам перетаскивает поля между зонами «Строки», «Колонки», «Значения» и мгновенно видит результат.
- Данные загружаются один раз по кнопке «Загрузить данные», дальше все перестроения происходят на клиенте, без запросов к серверу.

### Зачем нужен pivot
- Быстрый анализ без выгрузки в Excel: за 10 секунд можно увидеть, кто в каком отделе сколько работает в каких программах.
- Гибкая смена группировки: отдел → сотрудник → месяц → программа.
- Несколько метрик одновременно: Отработано, Эффективно, Интенсивная, Пауза.
- Уникальная фишка: среди конкурентов (Hubstaff, Toggl, Clockify) pivot-таблиц нет.

### Структура страницы (`/admin/reports/pivot`)
**Форма фильтров** (не отправляется, используется через JS `fetch`):
| Поле | id | Тип |
|---|---|---|
| С даты | `pivot_date_from` | date |
| По дату | `pivot_date_to` | date |
| Отделы | `pivot_depts` | multiple select |
| Сотрудники | `pivot_employees` | multiple select |
| Компьютеры | `pivot_computers` | multiple select |

**Кнопки быстрых периодов:** «0» (сегодня), «1» (вчера), «7», «30», «Этот месяц», «Прошлый месяц».

**Кнопка загрузки:** «🔄 Загрузить данные» → `loadPivotData()`.

**Статус:** `<div id="pivot_status">` — показывает «Загрузка...», «Загружено строк: N», «Ошибка».

**Контейнер сводной:** `<div id="pivot_output">` — сюда рендерится pivotUI.

### CDN-зависимости
PivotTable.js требует jQuery, jQuery UI и сам PivotTable:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/themes/base/jquery-ui.min.css">
<script src="https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/dist/jquery-ui.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.js"></script>