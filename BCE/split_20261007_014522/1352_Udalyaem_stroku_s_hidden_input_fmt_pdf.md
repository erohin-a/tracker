<!-- Часть 1352 из 1409 -->
# Удаляем строку с hidden input fmt=pdf
*Хлебные крошки:* Удаляем строку с hidden input fmt=pdf

[◀ ============================================================](1351_part.md) | [Оглавление](00_BCE_INDEX.md) | [Удаляем только те <button>, внутри которых есть "PDF" ▶](1353_Udalyaem_tolko_te_button_vnutri_kotoryh_est_PDF.md)

---

# Удаляем строку с hidden input fmt=pdf
c, n1 = re.subn(r'[ \t]*<input[^>]*name="fmt"[^>]*value="pdf"[^>]*>\s*\n?', '', c)

