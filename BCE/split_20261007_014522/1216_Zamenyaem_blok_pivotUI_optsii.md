<!-- Часть 1216 из 1409 -->
# Заменяем блок pivotUI + опции
*Хлебные крошки:* Заменяем блок pivotUI + опции

[◀ Заменяем функцию _build_pivot_data целиком](1215_Zamenyaem_funktsiyu_build_pivot_data_tselikom.md) | [Оглавление](00_BCE_INDEX.md) | [Также убираем attributeLabels и locale, если остались ▶](1217_Takzhe_ubiraem_attributeLabels_i_locale_esli_ostalis.md)

---

# Заменяем блок pivotUI + опции
old_block = re.compile(
    r"\$\('#pivot_output'\)\.pivotUI\(data\.rows, \{.*?\n    \}\);",
    re.DOTALL,
)
m = old_block.search(content)
if not m:
    print("ERROR: не найден вызов pivotUI")
    raise SystemExit(1)

new_block = '''$('#pivot_output').pivotUI(data.rows, {
      rows: ['Отдел', 'Сотрудник'],
      cols: ['Месяц'],
      aggregatorName: 'Сумма (время)',
      vals: ['Отработано (сек)', 'Эффективно (сек)', 'Интенсивная (сек)', 'Пауза (сек)'],
      rendererName: 'Table',
      unusedAttrsVertical: false,
      autoSortUnusedAttrs: true,
      showUI: true,
      aggregators: {
        "Сумма (время)": makeDurationAggregator("Сумма (время)"),
        "Среднее (время)": $.pivotUtilities.aggregators["Среднее (время)"] || null,
        "Count": $.pivotUtilities.aggregators["Count"],
        "Count Unique Values": $.pivotUtilities.aggregators["Count Unique Values"],
        "List Unique Values": $.pivotUtilities.aggregators["List Unique Values"],
        "Sum": $.pivotUtilities.aggregators["Sum"],
        "Average": $.pivotUtilities.aggregators["Average"]
      }
    });'''

content = content[:m.start()] + new_block + content[m.end():]

