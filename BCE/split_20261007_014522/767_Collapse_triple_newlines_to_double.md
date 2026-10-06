<!-- Часть 767 из 1409 -->
# Collapse triple+ newlines to double
*Хлебные крошки:* Collapse triple+ newlines to double

[◀ Collapse multiple blank lines](766_Collapse_multiple_blank_lines.md) | [Оглавление](00_BCE_INDEX.md) | [Verify syntax ▶](768_Verify_syntax.md)

---

# Collapse triple+ newlines to double
new_content = re.sub(r"\n\n\n+", "\n\n", new_content)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Удалено операций:")
for k, v in skipped_counts.items():
    print(f"  {k}: {v}")

