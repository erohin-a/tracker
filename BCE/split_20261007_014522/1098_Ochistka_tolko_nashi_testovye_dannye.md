<!-- Часть 1098 из 1409 -->
# ---------- Очистка (только наши тестовые данные) ----------
*Хлебные крошки:* ---------- Очистка (только наши тестовые данные) ----------

[◀ Приложения для records (вес = вероятность)](1097_Prilozheniya_dlya_records_ves_veroyatnost.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Отделы ---------- ▶](1099_Otdely.md)

---

# ---------- Очистка (только наши тестовые данные) ----------
print("Очистка прошлых тестовых данных...")
db.execute(text("DELETE FROM records WHERE client_ts >= '2026-08-01' AND client_ts < '2026-09-01'"))
db.execute(text("DELETE FROM work_sessions WHERE session_start >= '2026-08-01' AND session_start < '2026-09-01'"))
db.execute(text("DELETE FROM computers WHERE hostname LIKE 'ws-gen-%'"))
db.execute(text("DELETE FROM employees WHERE external_id LIKE '1C-%'"))
db.execute(text("DELETE FROM departments WHERE name IN :names").bindparams(
    names=tuple(DEPARTMENTS)
))
db.commit()

