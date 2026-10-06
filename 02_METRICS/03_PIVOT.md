# 03_PIVOT.md — Pivot-таблица (УДАЛЕНО)

**Статус:** функционал удалён 2026-10-06.
**Решение:** веб-pivot на PivotTable.js убран. Причина — сложно настраивать, нельзя нормально сортировать и менять. Сводные таблицы строятся пользователем в **Excel** из нашего XLSX-экспорта (лист «Данные» + лист «ИТОГО»).

## Что было

- Страница `/admin/reports/pivot` — интерактивная сводная на PivotTable.js.
- API `POST /admin/api/pivot-data` — плоские строки для pivot.
- Кастомные агрегаторы `durationSum` / `durationAvg`.

## Что стало

- Роут `/admin/reports/pivot` больше не открывается (шаблон `reports_pivot.html.disabled`).
- Ссылок на pivot в меню нет.
- Бэкенд-код не удалён (безвреден), но UI-доступа нет.

## Замена

- Экспорт в **XLSX**: `/admin/reports` → «Скачать XLSX». Лист «Данные» — pivot-friendly (заголовки без точек и `[]`), лист «ИТОГО» — сводка.
- Пользователь открывает XLSX в Excel и делает **Вставка → Сводная таблица**.

## Связанные файлы

- `02_METRICS\04_EXPORTS.md` — форматы CSV/XLSX.
- `server/templates/reports.html` — экспорт из UI.
- `server/templates/reports_pivot.html.disabled` — старый шаблон (на всякий случай).
