<!-- Часть 1180 из 1409 -->
# 1. Две вспомогательные функции для строк отчёта
*Хлебные крошки:* 1. Две вспомогательные функции для строк отчёта

[◀ Найдём все функции экспорта отчёта](1179_Naydem_vse_funktsii_eksporta_otcheta.md) | [Оглавление](00_BCE_INDEX.md) | [2. _render_pdf — только строки ПОСЛЕ 60-й (то, что не видели) ▶](1181_2_render_pdf_tolko_stroki_POSLE_60_y_to_chto_ne_videli.md)

---

# 1. Две вспомогательные функции для строк отчёта
for name in ["_report_row_to_list", "_report_row_to_xlsx"]:
    m = re.search(rf"def {re.escape(name)}\(.*?(?=\ndef |\n# ============|\Z)",
                  content, re.DOTALL)
    print("=" * 70)
    print(f"=== {name} ===")
    print("=" * 70)
    if m:
        print(m.group(0))
    else:
        print("НЕ НАЙДЕНА")
    print()

