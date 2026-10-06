<!-- Часть 1364 из 1409 -->
# Очистим лишние пустые строки
*Хлебные крошки:* Очистим лишние пустые строки

[◀ точнее: применяем и считаем удаления](1363_tochnee_primenyaem_i_schitaem_udaleniya.md) | [Оглавление](00_BCE_INDEX.md) | [base.html: удалить ссылку на /reports/pivot ▶](1365_base_html_udalit_ssylku_na_reports_pivot.md)

---

# Очистим лишние пустые строки
c = re.sub(r'\n{3,}', '\n\n', c)
p.write_text(c, encoding="utf-8")
print(f"report_result.html: PDF-форм удалено: {removed}")

