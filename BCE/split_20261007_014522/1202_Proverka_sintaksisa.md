<!-- Часть 1202 из 1409 -->
# Проверка синтаксиса
*Хлебные крошки:* Проверка синтаксиса

[◀ === 3. Route /admin/reports/pivot ===](1201_3_Route_admin_reports_pivot.md) | [Оглавление](00_BCE_INDEX.md) | [Проверки ▶](1203_Proverki.md)

---

# Проверка синтаксиса
try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

