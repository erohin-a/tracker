<!-- Часть 1241 из 1409 -->
# 2. Удаляем эндпоинт pivot-data
*Хлебные крошки:* 2. Удаляем эндпоинт pivot-data

[◀ Ищем от `@router.get("/reports/pivot"` до следующего @router. на верхнем уровне](1240_Ischem_ot_router_get_reports_pivot_do_sleduyuschego_router_na_verhnem_urovne.md) | [Оглавление](00_BCE_INDEX.md) | [3. Удаляем функцию _build_pivot_data ▶](1242_3_Udalyaem_funktsiyu_build_pivot_data.md)

---

# 2. Удаляем эндпоинт pivot-data
content, n2 = re.subn(
    r'\n@router\.post\("/api/pivot-data"\)\n(?:.*?\n)*?(?=@router\.)',
    '\n',
    content,
    count=1,
)

