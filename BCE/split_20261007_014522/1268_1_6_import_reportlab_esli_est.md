<!-- Часть 1268 из 1409 -->
# 1.6 импорт reportlab, если есть
*Хлебные крошки:* 1.6 импорт reportlab, если есть

[◀ 1.5 PDF-рендер: секция '# PDF-рендер отчёта' до следующего '# ===' блока](1267_1_5_PDF_render_sektsiya_PDF_render_otcheta_do_sleduyuschego_bloka.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1269_part.md)

---

# 1.6 импорт reportlab, если есть
c, n = re.subn(r'\n(?:from reportlab[^\n]*\n|import reportlab[^\n]*\n)', '\n', c)
print(f"  [i] удалено импортов reportlab: {n}")

p.write_text(c, encoding="utf-8")
print(f"OK web_admin.py: {orig} -> {len(c)}")

