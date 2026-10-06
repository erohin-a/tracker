<!-- Часть 860 из 1409 -->
# Вставляем новую строку с правильным отступом после target
*Хлебные крошки:* Вставляем новую строку с правильным отступом после target

[◀ Ищем строку language = ... внутри класса](859_Ischem_stroku_language_vnutri_klassa.md) | [Оглавление](00_BCE_INDEX.md) | [Показываем результат — что теперь в AdminUser ▶](861_Pokazyvaem_rezultat_chto_teper_v_AdminUser.md)

---

# Вставляем новую строку с правильным отступом после target
lines = class_body.split("\n")
out_lines = []
inserted = False
for line in lines:
    out_lines.append(line)
    if not inserted and target in line:
        # определяем отступ из текущей строки
        indent = line[:len(line) - len(line.lstrip())]
        out_lines.append(f"{indent}# Для роли manager — привязка к отделу (видит только свой отдел).")
        out_lines.append(f'{indent}department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)')
        inserted = True

new_class_body = "\n".join(out_lines)
new_content = content.replace(class_body, new_class_body, 1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("OK: department_id добавлен в AdminUser")
try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

