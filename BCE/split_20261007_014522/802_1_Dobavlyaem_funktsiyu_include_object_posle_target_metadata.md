<!-- Часть 802 из 1409 -->
# 1. Добавляем функцию include_object после target_metadata
*Хлебные крошки:* 1. Добавляем функцию include_object после target_metadata

[◀ 2. Содержимое baseline](801_2_Soderzhimoe_baseline.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](803_part.md)

---

# 1. Добавляем функцию include_object после target_metadata
old_marker = "target_metadata = Base.metadata"
if old_marker not in content:
    print("ERROR: 'target_metadata = Base.metadata' не найден в env.py")
    raise SystemExit(1)

new_block = '''target_metadata = Base.metadata


