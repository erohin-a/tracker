<!-- Часть 1103 из 1409 -->
# (для проверки блока "не привязан")
*Хлебные крошки:* (для проверки блока "не привязан")

[◀ Раздадим по одному ПК на сотрудника + несколько лишних БЕЗ привязки](1102_Razdadim_po_odnomu_PK_na_sotrudnika_neskolko_lishnih_BEZ_privyazki.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Сессии + Records ---------- ▶](1104_Sessii_Records.md)

---

# (для проверки блока "не привязан")
comp_info = []  # (comp_id, emp_id_or_None, hostname)
ws_counter = 100
for last, first, middle, dept_idx, ext_id in EMPLOYEES:
    ws_counter += 1
    hostname = f"ws-gen-{ws_counter:03d}"
    # 85% ПК привязаны к сотруднику, 15% — без привязки
    emp_id = emp_ids[ext_id] if random.random() < 0.85 else None
    row = db.execute(text(
        "INSERT INTO computers (computer_uid, hostname, os_info, client_version, "
        "client_secret_enc, secret_version, is_active, employee_id, assigned_at, "
        "registered_at, last_seen_at) "
        "VALUES (:uid, :h, 'Windows 10', '1.2.0', 'fake_encrypted', 1, true, "
        ":emp, :now, :now, :now) RETURNING id"
    ), {
        "uid": str(uuid.uuid4()),
        "h": hostname,
        "emp": emp_id,
        "now": datetime(2026, 8, 1, tzinfo=timezone.utc),
    }).first()
    comp_info.append((row[0], emp_id, hostname))
db.commit()
print(f"  Создано ПК: {len(comp_info)} (из них без привязки: {sum(1 for c in comp_info if c[1] is None)})")

