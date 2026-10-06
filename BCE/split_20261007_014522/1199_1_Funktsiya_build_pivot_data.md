<!-- Часть 1199 из 1409 -->
# === 1. Функция _build_pivot_data ===
*Хлебные крошки:* === 1. Функция _build_pivot_data ===

[◀ ============================================================](1198_part.md) | [Оглавление](00_BCE_INDEX.md) | [=== 2. Endpoint /admin/api/pivot-data === ▶](1200_2_Endpoint_admin_api_pivot_data.md)

---

# === 1. Функция _build_pivot_data ===
new_func = '''
def _build_pivot_data(db, employee_ids, department_ids, computer_ids,
                       date_from, date_to, tz, workday_start_hour):
    """
    Строит "плоские" строки для pivot-таблицы.
    Одна строка = один сотрудник за один рабочий день.
    """
    flat = _build_flat_records(db, employee_ids, department_ids, computer_ids,
                                date_from, date_to, tz, workday_start_hour)
    if not flat:
        return []

    WEEKDAY_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    WEEKDAY_FULL = ["Понедельник", "Вторник", "Среда", "Четверг",
                    "Пятница", "Суббота", "Воскресенье"]

    groups = {}
    for r in flat:
        key = (r.get("employee_id"), r["workday_date"])
        groups.setdefault(key, []).append(r)

    rows = []
    for (emp_id, day), sessions in groups.items():
        first = sessions[0]
        d_start = min(s["start_local"] for s in sessions)
        d_end = max(s["end_local"] for s in sessions)
        span = max(0, int((d_end - d_start).total_seconds()))

        intervals = [(s["activity_start_local"], s["activity_end_local"])
                     for s in sessions]
        union = _union_duration(intervals)

        effective = sum(s.get("effective_duration", 0) for s in sessions)
        intensive = sum(s.get("intensive_seconds", 0) for s in sessions)
        pause_btn = sum(s.get("pause_seconds", 0) for s in sessions)
        break_dur = pause_btn + max(0, span - union)

        computers = sorted({s.get("computer_name") or "—" for s in sessions})

        rows.append({
            "date_iso": day.isoformat(),
            "date": day.strftime("%d.%m.%Y"),
            "year": day.year,
            "month_num": day.month,
            "month_name": RU_MONTHS[day.month],
            "day": day.day,
            "weekday": WEEKDAY_SHORT[day.weekday()],
            "weekday_full": WEEKDAY_FULL[day.weekday()],
            "is_weekend": day.weekday() >= 5,
            "employee_id": emp_id or 0,
            "employee": first.get("employee_name") or "— не привязан —",
            "external_id": first.get("external_id") or "",
            "department": first.get("department_name") or "—",
            "computers": ", ".join(computers),
            "computer_count": len(computers),
            "sessions_count": len(sessions),
            "worked_span": span,
            "worked_union": union,
            "intensive": intensive,
            "effective": effective,
            "break_dur": break_dur,
            "pause_button": pause_btn,
        })

    rows.sort(key=lambda x: (x["date_iso"], x["employee"]), reverse=True)
    return rows


'''

anchor = "def _build_report("
if anchor not in content:
    print("ERROR: не найден _build_report")
    raise SystemExit(1)
content = content.replace(anchor, new_func + anchor, 1)

