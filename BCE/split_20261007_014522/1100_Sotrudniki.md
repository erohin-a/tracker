<!-- Часть 1100 из 1409 -->
# ---------- Сотрудники ----------
*Хлебные крошки:* ---------- Сотрудники ----------

[◀ ---------- Отделы ----------](1099_Otdely.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Компьютеры ---------- ▶](1101_Kompyutery.md)

---

# ---------- Сотрудники ----------
print("Создаю сотрудников...")
emp_ids = {}  # (ext_id) -> employee_id
for last, first, middle, dept_idx, ext_id in EMPLOYEES:
    full_name = f"{last} {first} {middle}"
    dept_name = DEPARTMENTS[dept_idx]
    row = db.execute(text(
        "INSERT INTO employees (full_name, last_name, first_name, middle_name, "
        "external_id, department_id, is_active) "
        "VALUES (:fn, :ln, :fi, :mn, :ext, :dept, true) RETURNING id"
    ), {
        "fn": full_name, "ln": last, "fi": first, "mn": middle,
        "ext": f"1C-{ext_id}", "dept": dept_ids[dept_name],
    }).first()
    emp_ids[ext_id] = row[0]
db.commit()
print(f"  Создано сотрудников: {len(emp_ids)}")

