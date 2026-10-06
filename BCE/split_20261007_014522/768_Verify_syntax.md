<!-- Часть 768 из 1409 -->
# Verify syntax
*Хлебные крошки:* Verify syntax

[◀ Collapse triple+ newlines to double](767_Collapse_triple_newlines_to_double.md) | [Оглавление](00_BCE_INDEX.md) | [Verify remaining operations ▶](769_Verify_remaining_operations.md)

---

# Verify syntax
try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    exit(1)

