<!-- Часть 816 из 1409 -->
# Используем regex, который найдёт строку "compare_type=True," и добавит после неё
*Хлебные крошки:* Используем regex, который найдёт строку "compare_type=True," и добавит после неё

[◀ 2. Добавляем include_object=include_object в оба context.configure()](815_2_Dobavlyaem_include_object_include_object_v_oba_context_configure.md) | [Оглавление](00_BCE_INDEX.md) | [Проверяем, что include_object применён в обоих configure() ▶](817_Proveryaem_chto_include_object_primenen_v_oboih_configure.md)

---

# Используем regex, который найдёт строку "compare_type=True," и добавит после неё
content = re.sub(
    r"^(\s*)compare_type=True,$",
    r"\1compare_type=True,\n\1include_object=include_object,",
    content,
    flags=re.MULTILINE,
)

with open(ENV, "w", encoding="utf-8") as f:
    f.write(content)

print("OK: env.py пропатчен")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

