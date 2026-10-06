<!-- Часть 1353 из 1409 -->
# Удаляем только те <button>, внутри которых есть "PDF"
*Хлебные крошки:* Удаляем только те <button>, внутри которых есть "PDF"

[◀ Удаляем строку с hidden input fmt=pdf](1352_Udalyaem_stroku_s_hidden_input_fmt_pdf.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1354_part.md)

---

# Удаляем только те <button>, внутри которых есть "PDF"
lines = c.splitlines(keepends=True)
new_lines = []
removed = 0
for ln in lines:
    if "<button" in ln and "PDF" in ln:
        removed += 1
        continue
    new_lines.append(ln)
c = "".join(new_lines)

p.write_text(c, encoding="utf-8")
print(f"  [OK] hidden fmt=pdf: {n1}, <button> с PDF: {removed}")

