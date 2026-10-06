<!-- Часть 769 из 1409 -->
# Verify remaining operations
*Хлебные крошки:* Verify remaining operations

[◀ Verify syntax](768_Verify_syntax.md) | [Оглавление](00_BCE_INDEX.md) | [Add include_object after target_metadata ▶](770_Add_include_object_after_target_metadata.md)

---

# Verify remaining operations
remaining = []
for m in re.finditer(r"op\.(create_table|drop_table|create_index|drop_index)\(([^,)]+)", new_content):
    remaining.append(m.group(0)[:80])

print(f"\nОсталось операций: {len(remaining)}")
for r in remaining:
    print(f"  {r}")
Wait, the regex for remaining might not work well with nested parens. Let me simplify — just check specific strings:
python
print("\nПроверка содержимого:")
for pattern in [
    "'employee_settings'",
    "'records_2025_01'",
    "'records_2026_09'",
    "'records_default'",
]:
    count = new_content.count(pattern)
    print(f"  {pattern}: {count} раз")
Expected: employee_settings — appears 4 times (create_table + create_index + drop_index + drop_table), records_* — 0.
OK, let me finalize the response.
Actually one more thing — I should tell them that after this fix, when they apply the migration, only employee_settings will be created. That's the goal.
And for env.py fix, I'll give a Python patcher too.
Let me write it all now.
For env.py, the target function is run_migrations_online(). Inside, there's context.configure(...). I need to add include_object=include_object there, and define include_object above.
Actually, better: define it at module level near target_metadata = Base.metadata, and pass in both offline and online modes.
Let me write:
python
def include_object(object, name, type_, reflected, compare_to):
    """
    Фильтр для autogenerate.
    Исключаем партиционированные таблицы records_YYYY_MM и records_default —
    они не в metadata (это партиции PostgreSQL), и Alembic не должен
    пытаться их удалять или создавать.
    """
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True
Then in run_migrations_offline and run_migrations_online, add include_object=include_object to the context.configure(...) call.
The patcher:
python
ENV = r"D:\tracker\server\alembic\env.py"
with open(ENV, "r", encoding="utf-8") as f:
    content = f.read()

if "def include_object" in content:
    print("SKIP: already patched")
    exit(0)

