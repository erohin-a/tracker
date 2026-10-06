<!-- Часть 1215 из 1409 -->
# Заменяем функцию _build_pivot_data целиком
*Хлебные крошки:* Заменяем функцию _build_pivot_data целиком

[◀ Проверка маркеров](1214_Proverka_markerov.md) | [Оглавление](00_BCE_INDEX.md) | [Заменяем блок pivotUI + опции ▶](1216_Zamenyaem_blok_pivotUI_optsii.md)

---

# Заменяем функцию _build_pivot_data целиком
pattern = re.compile(
    r"def _build_pivot_data\(.*?(?=\ndef |\n# ============|\Z)",
    re.DOTALL,
)
m = pattern.search(content)
if not m:
    print("ERROR: _build_pivot_data не найдена")
    raise SystemExit(1)

new_func = '''def _build_pivot_data(db, employee_ids, department_ids, computer_ids,
                       date_from, date_to, tz, workday_start_hour):
    """
    Строит "плоские" строки для pivot-таблицы.
    Ключи сразу на русском — PivotTable.js показывает их как есть.
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
            "Дата": day.strftime("%d.%m.%Y"),
            "Год": day.year,
            "Месяц №": day.month,
            "Месяц": RU_MONTHS[day.month],
            "Число": day.day,
            "День недели": WEEKDAY_SHORT[day.weekday()],
            "День недели (полный)": WEEKDAY_FULL[day.weekday()],
            "Выходной": "Да" if day.weekday() >= 5 else "Нет",
            "Сотрудник": first.get("employee_name") or "— не привязан —",
            "1C ID": first.get("external_id") or "",
            "Отдел": first.get("department_name") or "—",
            "Компьютеры": ", ".join(computers),
            "ПК (кол-во)": len(computers),
            "Сессий": len(sessions),
            "Отработано (сек)": span,
            "С трекером (сек)": union,
            "Интенсивная (сек)": intensive,
            "Эффективно (сек)": effective,
            "Пауза (сек)": break_dur,
            "Пауза кнопкой (сек)": pause_btn,
        })

    rows.sort(key=lambda x: (x["Дата"], x["Сотрудник"]), reverse=True)
    return rows


'''

content = content[:m.start()] + new_func + content[m.end():]
PATH.write_text(content, encoding="utf-8")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: line={e.lineno}, msg={e.msg}")
    raise SystemExit(1)

for key in ["Отработано (сек)", "С трекером (сек)", "Интенсивная (сек)",
            "Эффективно (сек)", "Пауза (сек)", "Сотрудник", "Отдел"]:
    print(f" {'OK' if key in content else 'MISS'}: {key}")
'@
[System.IO.File]::WriteAllText("D:\tracker\_patch_pivot_ru.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч pivot — русские ключи ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_pivot_ru.py
Что ожидаем:
text
SYNTAX OK
 OK: Отработано (сек)
 OK: С трекером (сек)
 OK: Интенсивная (сек)
 OK: Эффективно (сек)
 OK: Пауза (сек)
 OK: Сотрудник
 OK: Отдел
________________________________________
Скрипт 2 — Патч шаблона: русские ключи в pivotUI
Меняем дефолтные rows, cols, vals и убираем locale: 'ru' (без загруженной локали он всё равно откатывается на английский).
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$patcher = @'
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\templates\reports_pivot.html")
content = PATH.read_text(encoding="utf-8")

