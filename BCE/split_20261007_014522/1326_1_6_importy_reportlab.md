<!-- Часть 1326 из 1409 -->
# 1.6 импорты reportlab
*Хлебные крошки:* 1.6 импорты reportlab

[◀ 1.5 большая секция PDF-рендер (заголовок в рамке ===)](1325_1_5_bolshaya_sektsiya_PDF_render_zagolovok_v_ramke.md) | [Оглавление](00_BCE_INDEX.md) | [1.7 убрать лишние пустые строки ▶](1327_1_7_ubrat_lishnie_pustye_stroki.md)

---

# 1.6 импорты reportlab
c, n = re.subn(r'\n(?:from reportlab[^\n]*|import reportlab[^\n]*)\n', '\n', c)
print(f"  [i]    импортов reportlab удалено: {n}")

