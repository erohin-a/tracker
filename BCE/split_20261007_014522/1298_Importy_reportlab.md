<!-- Часть 1298 из 1409 -->
# Импорты reportlab
*Хлебные крошки:* Импорты reportlab

[◀ Большая секция PDF-рендер](1297_Bolshaya_sektsiya_PDF_render.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1299_part.md)

---

# Импорты reportlab
c, n = re.subn(r'\n(?:from reportlab[^\n]*|import reportlab[^\n]*)\n', '\n', c)
print(f"  [i]    импортов reportlab: {n}")

c = re.sub(r'\n{4,}', '\n\n\n', c)  # убрать лишние пустые строки
p.write_text(c, encoding="utf-8")
print(f"OK web_admin.py: {orig} -> {len(c)}")

