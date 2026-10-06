<!-- Часть 1217 из 1409 -->
# Также убираем attributeLabels и locale, если остались
*Хлебные крошки:* Также убираем attributeLabels и locale, если остались

[◀ Заменяем блок pivotUI + опции](1216_Zamenyaem_blok_pivotUI_optsii.md) | [Оглавление](00_BCE_INDEX.md) | [Удаляем ненужный теперь fieldLabels (или оставим, не мешает) ▶](1218_Udalyaem_nenuzhnyy_teper_fieldLabels_ili_ostavim_ne_meshaet.md)

---

# Также убираем attributeLabels и locale, если остались
content = re.sub(r"\s*locale:\s*'ru',", "", content)
content = re.sub(
    r"\s*attributeLabels:\s*fieldLabels,",
    "",
    content,
)

