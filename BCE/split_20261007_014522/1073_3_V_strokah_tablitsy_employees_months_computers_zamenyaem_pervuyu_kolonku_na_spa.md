<!-- Часть 1073 из 1409 -->
# 3. В строках таблицы (employees/months/computers) — заменяем первую колонку на span + добавляем worked_duration
*Хлебные крошки:* 3. В строках таблицы (employees/months/computers) — заменяем первую колонку на span + добавляем worked_duration

[◀ 2. Заголовок таблицы "Отработано" ? добавить "С трекером"](1072_2_Zagolovok_tablitsy_Otrabotano_dobavit_S_trekerom.md) | [Оглавление](00_BCE_INDEX.md) | [4. Итого внизу ▶](1074_4_Itogo_vnizu.md)

---

# 3. В строках таблицы (employees/months/computers) — заменяем первую колонку на span + добавляем worked_duration
old3 = '<td><strong>{{ r.worked_duration | dur }}</strong></td>\n <td class="text-success">{{ r.effective_duration | dur }}</td>'
new3 = '<td><strong>{{ r.worked_span_duration | dur }}</strong></td>\n <td>{{ r.worked_duration | dur }}</td>\n <td class="text-success">{{ r.effective_duration | dur }}</td>'
count = content.count(old3)
if count > 0:
    content = content.replace(old3, new3)
    changed += 1
    print(f"OK: строки таблицы обновлены ({count} мест)")

