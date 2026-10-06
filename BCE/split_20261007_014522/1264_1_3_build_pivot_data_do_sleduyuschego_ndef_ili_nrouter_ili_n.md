<!-- Часть 1264 из 1409 -->
# 1.3 _build_pivot_data ... до следующего \ndef или \n@router или \n# ===
*Хлебные крошки:* 1.3 _build_pivot_data ... до следующего \ndef или \n@router или \n# ===

[◀ 1.2 pivot-data: @router.post("/api/pivot-data") ... до следующего @router.](1263_1_2_pivot_data_router_post_api_pivot_data_do_sleduyuschego_router.md) | [Оглавление](00_BCE_INDEX.md) | [1.4 PDF-ветка: 'if fmt == "pdf":' или 'elif fmt == "pdf":' ▶](1265_1_4_PDF_vetka_if_fmt_pdf_ili_elif_fmt_pdf.md)

---

# 1.3 _build_pivot_data ... до следующего \ndef или \n@router или \n# ===
c = remove_block(
    c,
    r'\ndef _build_pivot_data\(.*?(?=\n(?:def |@router\.|# =))',
    "функция _build_pivot_data",
)

