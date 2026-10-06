<!-- Часть 1297 из 1409 -->
# Большая секция PDF-рендер
*Хлебные крошки:* Большая секция PDF-рендер

[◀ PDF-ветка (короткая, если fmt == "pdf")](1296_PDF_vetka_korotkaya_esli_fmt_pdf.md) | [Оглавление](00_BCE_INDEX.md) | [Импорты reportlab ▶](1298_Importy_reportlab.md)

---

# Большая секция PDF-рендер
c = rm_block(
    c,
    r'\n# =+\n# PDF-рендер отчёта\n# =+\n.*?(?=\n# =+\n# |\Z)',
    "секция PDF-рендер",
)

