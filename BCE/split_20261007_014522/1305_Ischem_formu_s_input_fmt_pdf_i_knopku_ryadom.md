<!-- Часть 1305 из 1409 -->
# Ищем форму с input fmt=pdf и кнопку рядом
*Хлебные крошки:* Ищем форму с input fmt=pdf и кнопку рядом

[◀ ============================================================](1304_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1306_part.md)

---

# Ищем форму с input fmt=pdf и кнопку рядом
c2, n1 = re.subn(
    r'\s*<form[^>]*>\s*<input type="hidden" name="fmt" value="pdf"\s*/?>\s*<button[^>]*>[^<]*PDF[^<]*</button>\s*</form>',
    '', c, flags=re.DOTALL,
)
if n1:
    c = c2
    print(f"  [OK] форма PDF удалена: {n1}")
else:
    c, n2 = re.subn(r'\s*<input type="hidden" name="fmt" value="pdf"\s*/?>', '', c)
    c, n3 = re.subn(r'\s*<button[^>]*>[^<]*PDF[^<]*</button>', '', c)
    print(f"  [i] fallback: hidden={n2}, button={n3}")
p.write_text(c, encoding="utf-8")

