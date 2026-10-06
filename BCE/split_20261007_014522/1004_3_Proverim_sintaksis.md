<!-- Часть 1004 из 1409 -->
# ---------- 3. Проверим синтаксис ----------
*Хлебные крошки:* ---------- 3. Проверим синтаксис ----------

[◀ Ищем проблемный comment и заменяем](1003_Ischem_problemnyy_comment_i_zamenyaem.md) | [Оглавление](00_BCE_INDEX.md) | [Диагностика: сколько раз datetime используется ▶](1005_Diagnostika_skolko_raz_datetime_ispolzuetsya.md)

---

# ---------- 3. Проверим синтаксис ----------
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

