<!-- Часть 1263 из 1409 -->
# 1.2 pivot-data: @router.post("/api/pivot-data") ... до следующего @router.
*Хлебные крошки:* 1.2 pivot-data: @router.post("/api/pivot-data") ... до следующего @router.

[◀ 1.1 pivot-страница: @router.get("/reports/pivot" ... до следующего @router.](1262_1_1_pivot_stranitsa_router_get_reports_pivot_do_sleduyuschego_router.md) | [Оглавление](00_BCE_INDEX.md) | [1.3 _build_pivot_data ... до следующего \ndef или \n@router или \n# === ▶](1264_1_3_build_pivot_data_do_sleduyuschego_ndef_ili_nrouter_ili_n.md)

---

# 1.2 pivot-data: @router.post("/api/pivot-data") ... до следующего @router.
c = remove_block(
    c,
    r'@router\.post\("/api/pivot-data"\).*?(?=\n@router\.)',
    "эндпоинт /api/pivot-data",
)

