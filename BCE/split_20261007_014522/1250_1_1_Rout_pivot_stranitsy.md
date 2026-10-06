<!-- Часть 1250 из 1409 -->
# 1.1 Роут pivot-страницы
*Хлебные крошки:* 1.1 Роут pivot-страницы

[◀ ============================================================](1249_part.md) | [Оглавление](00_BCE_INDEX.md) | [1.2 Эндпоинт pivot-data ▶](1251_1_2_Endpoint_pivot_data.md)

---

# 1.1 Роут pivot-страницы
c, n = re.subn(
    r'\n@router\.get\("/reports/pivot"[^\n]*\n(?:[^\n]*\n)*?(?=@router\.|\Z)',
    '\n',
    c, count=1
)
print(f"  reports/pivot route removed: {n}")

