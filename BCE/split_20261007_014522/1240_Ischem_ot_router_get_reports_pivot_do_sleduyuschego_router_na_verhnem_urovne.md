<!-- Часть 1240 из 1409 -->
# Ищем от `@router.get("/reports/pivot"` до следующего @router. на верхнем уровне
*Хлебные крошки:* Ищем от `@router.get("/reports/pivot"` до следующего @router. на верхнем уровне

[◀ 1. Удаляем роут pivot-страницы](1239_1_Udalyaem_rout_pivot_stranitsy.md) | [Оглавление](00_BCE_INDEX.md) | [2. Удаляем эндпоинт pivot-data ▶](1241_2_Udalyaem_endpoint_pivot_data.md)

---

# Ищем от `@router.get("/reports/pivot"` до следующего @router. на верхнем уровне
content, n1 = re.subn(
    r'\n@router\.get\("/reports/pivot"[^\n]*\n(?:.*?\n)*?(?=@router\.)',
    '\n',
    content,
    count=1,
)

