<!-- Часть 1099 из 1409 -->
# ---------- Отделы ----------
*Хлебные крошки:* ---------- Отделы ----------

[◀ ---------- Очистка (только наши тестовые данные) ----------](1098_Ochistka_tolko_nashi_testovye_dannye.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Сотрудники ---------- ▶](1100_Sotrudniki.md)

---

# ---------- Отделы ----------
print("Создаю отделы...")
dept_ids = {}
for name in DEPARTMENTS:
    row = db.execute(text(
        "INSERT INTO departments (name, is_active, created_at) "
        "VALUES (:n, true, NOW()) RETURNING id"
    ), {"n": name}).first()
    dept_ids[name] = row[0]
db.commit()
print(f"  Создано отделов: {len(dept_ids)}")

