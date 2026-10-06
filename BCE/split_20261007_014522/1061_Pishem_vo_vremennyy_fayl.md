<!-- Часть 1061 из 1409 -->
# Пишем во временный файл
*Хлебные крошки:* Пишем во временный файл

[◀ ============================================================](1060_part.md) | [Оглавление](00_BCE_INDEX.md) | [Заменяем оригинал ▶](1062_Zamenyaem_original.md)

---

# Пишем во временный файл
with open(TMP, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    os.remove(TMP)
    raise SystemExit(1)

