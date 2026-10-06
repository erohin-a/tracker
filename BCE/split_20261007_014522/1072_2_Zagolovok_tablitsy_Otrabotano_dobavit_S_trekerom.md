<!-- Часть 1072 из 1409 -->
# 2. Заголовок таблицы "Отработано" ? добавить "С трекером"
*Хлебные крошки:* 2. Заголовок таблицы "Отработано" ? добавить "С трекером"

[◀ Заменяем "Отработано" на "С трекером" (то что было), а сверху добавим новую строку через замену заголовка](1071_Zamenyaem_Otrabotano_na_S_trekerom_to_chto_bylo_a_sverhu_dobavim_novuyu_stroku_c.md) | [Оглавление](00_BCE_INDEX.md) | [3. В строках таблицы (employees/months/computers) — заменяем первую колонку на span + добавляем worked_duration ▶](1073_3_V_strokah_tablitsy_employees_months_computers_zamenyaem_pervuyu_kolonku_na_spa.md)

---

# 2. Заголовок таблицы "Отработано" ? добавить "С трекером"
old2 = '<th style="width:110px">Отработано</th>'
if old2 in content:
    content = content.replace(old2, '<th style="width:100px">Отработано</th>\n <th style="width:100px">С трекером</th>', 1)
    changed += 1
    print("OK: заголовок Отработано расширен")

