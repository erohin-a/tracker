<!-- Часть 1139 из 1409 -->
# 1. Находим _build_report целиком
*Хлебные крошки:* 1. Находим _build_report целиком

[◀ ============================================================](1138_part.md) | [Оглавление](00_BCE_INDEX.md) | [2. Находим _group_by_employee целиком ▶](1140_2_Nahodim_group_by_employee_tselikom.md)

---

# 1. Находим _build_report целиком
m = re.search(r"def _build_report\(.*?(?=\ndef |\n# ============|\Z)",
              content, re.DOTALL)
if m:
    print("=" * 60)
    print("=== _build_report ЦЕЛИКОМ ===")
    print("=" * 60)
    print(m.group(0))
else:
    print("ERROR: _build_report не найдена")

