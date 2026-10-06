<!-- Часть 1251 из 1409 -->
# 1.2 Эндпоинт pivot-data
*Хлебные крошки:* 1.2 Эндпоинт pivot-data

[◀ 1.1 Роут pivot-страницы](1250_1_1_Rout_pivot_stranitsy.md) | [Оглавление](00_BCE_INDEX.md) | [1.3 Функция _build_pivot_data ▶](1252_1_3_Funktsiya_build_pivot_data.md)

---

# 1.2 Эндпоинт pivot-data
c, n = re.subn(
    r'\n@router\.post\("/api/pivot-data"\)\n(?:[^\n]*\n)*?(?=@router\.|\Z)',
    '\n',
    c, count=1
)
print(f"  api/pivot-data endpoint removed: {n}")

