<!-- Часть 1266 из 1409 -->
# Убираем от строки с проверкой до следующего if/elif fmt или return/конца
*Хлебные крошки:* Убираем от строки с проверкой до следующего if/elif fmt или return/конца

[◀ 1.4 PDF-ветка: 'if fmt == "pdf":' или 'elif fmt == "pdf":'](1265_1_4_PDF_vetka_if_fmt_pdf_ili_elif_fmt_pdf.md) | [Оглавление](00_BCE_INDEX.md) | [1.5 PDF-рендер: секция '# PDF-рендер отчёта' до следующего '# ===' блока ▶](1267_1_5_PDF_render_sektsiya_PDF_render_otcheta_do_sleduyuschego_bloka.md)

---

# Убираем от строки с проверкой до следующего if/elif fmt или return/конца
c = remove_block(
    c,
    r'\n    (?:el)?if fmt == "pdf":\n(?:        .*\n|\n)*?(?=\n    (?:el)?if fmt|\n    return|\n\n@router|\n\n# =)',
    "ветка if fmt == \"pdf\"",
)

