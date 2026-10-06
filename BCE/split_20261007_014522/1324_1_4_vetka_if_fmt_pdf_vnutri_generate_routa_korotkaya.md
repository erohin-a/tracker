<!-- Часть 1324 из 1409 -->
# 1.4 ветка 'if fmt == "pdf"' внутри generate-роута (короткая)
*Хлебные крошки:* 1.4 ветка 'if fmt == "pdf"' внутри generate-роута (короткая)

[◀ 1.3 функция _build_pivot_data (до следующего def/@router/# ===)](1323_1_3_funktsiya_build_pivot_data_do_sleduyuschego_def_router.md) | [Оглавление](00_BCE_INDEX.md) | [1.5 большая секция PDF-рендер (заголовок в рамке ===) ▶](1325_1_5_bolshaya_sektsiya_PDF_render_zagolovok_v_ramke.md)

---

# 1.4 ветка 'if fmt == "pdf"' внутри generate-роута (короткая)
c = rm_block(
    c,
    r'\n    (?:el)?if fmt == "pdf":\n(?:        .*\n|\n)+?(?=\n    (?:el)?if fmt|\n\n# |\n@router\.)',
    'ветка if fmt == "pdf"',
)

