<!-- Часть 1071 из 1409 -->
# Заменяем "Отработано" на "С трекером" (то что было), а сверху добавим новую строку через замену заголовка
*Хлебные крошки:* Заменяем "Отработано" на "С трекером" (то что было), а сверху добавим новую строку через замену заголовка

[◀ 1. В сводке меняем метрики в существующих карточках](1070_1_V_svodke_menyaem_metriki_v_suschestvuyuschih_kartochkah.md) | [Оглавление](00_BCE_INDEX.md) | [2. Заголовок таблицы "Отработано" ? добавить "С трекером" ▶](1072_2_Zagolovok_tablitsy_Otrabotano_dobavit_S_trekerom.md)

---

# Заменяем "Отработано" на "С трекером" (то что было), а сверху добавим новую строку через замену заголовка
old1 = '<div class="text-muted small">Отработано</div>'
new1 = '<div class="text-muted small">Отработано <span class="hint" data-bs-toggle="tooltip" title="От старта первой до конца последней сессии за день (включает перерывы).">?</span></div>\n <div class="fs-4 text-primary">{{ report.totals.worked_span_duration | dur }}</div>\n <div class="text-muted small mt-2">С трекером <span class="hint" data-bs-toggle="tooltip" title="Суммарное время сессий без пересечений.">?</span></div>'
if old1 in content:
    content = content.replace(old1, new1, 1)
    # Удаляем дублирующий fs-4 с worked_duration, который был сразу после
    content = content.replace(
        '<div class="fs-4 text-primary">{{ report.totals.worked_span_duration | dur }}</div>\n'
        ' <div class="text-muted small mt-2">С трекером <span class="hint" data-bs-toggle="tooltip" title="Суммарное время сессий без пересечений.">?</span></div>\n'
        ' <div class="fs-4">{{ report.totals.worked_duration | dur }}</div>',
        '<div class="fs-4 text-primary">{{ report.totals.worked_span_duration | dur }}</div>\n'
        ' <div class="text-muted small mt-2">С трекером</div>\n'
        ' <div class="fs-4">{{ report.totals.worked_duration | dur }}</div>',
        1,
    )
    changed += 1
    print("OK: карточка Отработано расширена")

