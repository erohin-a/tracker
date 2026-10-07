# Находим функцию целиком

*Часть 84 из 100. Источник: `BCE.md`.*

[◀ Проверим, не пропатчен ли уже](083_Proverim_ne_propatchen_li_uzhe.md) | [Оглавление](00_BCE_INDEX.md) | [Вырезаем функцию и смотрим — не должно быть override ▶](085_Vyrezaem_funktsiyu_i_smotrim_ne_dolzhno_byt_override.md)

---

# Находим функцию целиком
m = re.search(
    r"def _aggregate_group\(sessions: list, extra_fields: dict\) -> dict:.*?(?=\ndef |\n# ============)",
    content, re.DOTALL)
if not m:
    print("ERROR: _aggregate_group не найдена")
    raise SystemExit(1)

new_aggregate = '''def _aggregate_group(sessions: list, extra_fields: dict) -> dict:
    """
    Универсальная агрегация сессий в группу (день, сотрудник, отдел и т.д.).

    Возвращает 6 ключевых метрик + производные:
      worked_span_duration — табель: сумма daily spans
      worked_duration      — union интервалов (без двойного счёта 2 ПК)
      effective_duration   — сумма времени работы активных программ
      intensive_seconds    — 5 сек ? активные activity-события
      pause_seconds_total  — сумма нажатий кнопки «Пауза»
      break_duration       — кнопка + перерывы между сессиями
                           = pause_seconds_total + (span ? union)
    """
    if not sessions:
        return {
            **extra_fields,
            "sessions_count": 0,
            "worked_span_duration": 0,
            "worked_duration": 0,
            "effective_duration": 0,
            "intensive_seconds": 0,
            "pause_seconds_total": 0,
            "break_duration": 0,
            "keyboard": 0,
            "mouse": 0,
            "abnormal": False,
            "top_apps": [],
            "sessions": [],
        }

    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    for s in sessions:
        _merge_apps(app_stats, s["top_apps"])

    span = _aggregate_spans(sessions)
    union = _aggregate_unions(sessions)
    effective = sum(s.get("effective_duration", 0) for s in sessions)
    intensive = sum(s.get("intensive_seconds", 0) for s in sessions)
    pause_btn = sum(s.get("pause_seconds", 0) for s in sessions)
    # Пауза = нажатие кнопки + перерывы между сессиями
    break_dur = pause_btn + max(0, span - union)

    return {
        **extra_fields,
        "sessions_count": len(sessions),
        "worked_span_duration": span,
        "worked_duration": union,
        "effective_duration": effective,
        "intensive_seconds": intensive,
        "pause_seconds_total": pause_btn,
        "break_duration": break_dur,
        "keyboard": sum(s.get("keyboard", 0) for s in sessions),
        "mouse": sum(s.get("mouse", 0) for s in sessions),
        "abnormal": any(s.get("abnormal") for s in sessions),
        "top_apps": _apps_to_list(app_stats),
        "sessions": sessions,
    }

'''
content = content[:m.start()] + new_aggregate + content[m.end():]
print("OK: _aggregate_group переписан")

# ============================================================
# 3. Убираем ручные override в _group_by_employee
# ============================================================
old_override_e = '        agg["worked_duration"] = sum(d["span"] for d in days)\n        result.append(agg)'
if old_override_e in content:
    content = content.replace(old_override_e, '        result.append(agg)', 1)
    print("OK: убран override в _group_by_employee")
else:
    print("SKIP: override _group_by_employee не найден")

# ============================================================
# 4. Убираем ручные override в _group_by_computer
# ============================================================
if old_override_e in content:
    content = content.replace(old_override_e, '        result.append(agg)', 1)
    print("OK: убран override в _group_by_computer")
else:
    print("SKIP: override _group_by_computer не найден")

# ============================================================
# 5. Обновляем _group_by_session — добавляем новые поля
# ============================================================
old_sess_fields = '''"worked_duration": r["full_duration"],
            "effective_duration": r["effective_duration"],'''
new_sess_fields = '''"worked_span_duration": r["full_duration"],
            "worked_duration": r["full_duration"],
            "effective_duration": r["effective_duration"],
            "intensive_seconds": r.get("intensive_seconds", 0),
            "pause_seconds_total": r.get("pause_seconds", 0),
            "break_duration": r.get("pause_seconds", 0),'''
if old_sess_fields in content:
    content = content.replace(old_sess_fields, new_sess_fields, 1)
    print("OK: _group_by_session дополнена полями")
else:
    print("SKIP: поля в _group_by_session уже новые или не найдены")

# ============================================================
# 6. Обновляем totals в _build_report
# ============================================================
old_totals = '''total_worked = sum(r.get("worked_duration", 0) for r in rows)
    total_effective = sum(r.get("effective_duration", 0) for r in rows)
    total_keyboard = sum(r.get("keyboard", 0) for r in rows)
    total_mouse = sum(r.get("mouse", 0) for r in rows)
    total_abnormal = sum(1 for r in rows if r.get("abnormal"))'''

new_totals = '''total_span = sum(r.get("worked_span_duration", 0) for r in rows)
    total_worked = sum(r.get("worked_duration", 0) for r in rows)
    total_effective = sum(r.get("effective_duration", 0) for r in rows)
    total_intensive = sum(r.get("intensive_seconds", 0) for r in rows)
    total_pause_btn = sum(r.get("pause_seconds_total", 0) for r in rows)
    total_break = sum(r.get("break_duration", 0) for r in rows)
    total_keyboard = sum(r.get("keyboard", 0) for r in rows)
    total_mouse = sum(r.get("mouse", 0) for r in rows)
    total_abnormal = sum(1 for r in rows if r.get("abnormal"))'''

if old_totals in content:
    content = content.replace(old_totals, new_totals, 1)
    print("OK: totals в _build_report обновлены")
else:
    print("SKIP: totals уже обновлены или не найдены")

# Ищем блок return с totals и дополняем
old_return = '''"totals": {
            "sessions": len(flat), "worked_duration": total_worked,
            "effective_duration": total_effective, "keyboard": total_keyboard,
            "mouse": total_mouse, "abnormal": total_abnormal, "top_apps": top_apps,
        },'''

new_return = '''"totals": {
            "sessions": len(flat),
            "worked_span_duration": total_span,
            "worked_duration": total_worked,
            "effective_duration": total_effective,
            "intensive_seconds": total_intensive,
            "pause_seconds_total": total_pause_btn,
            "break_duration": total_break,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "abnormal": total_abnormal,
            "top_apps": top_apps,
        },'''

if old_return in content:
    content = content.replace(old_return, new_return, 1)
    print("OK: totals в return обновлены")
else:
    # Возможно уже был другой формат после нашего патча — пробуем иначе
    if '"worked_span_duration": total_span' in content:
        print("SKIP: return уже обновлён")
    else:
        print("WARN: блок return с totals не найден — правьте вручную")

# ============================================================
# 7. Сохраняем
# ============================================================
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# ============================================================
# 8. Финальная проверка
# ============================================================
print()
print("Проверка маркеров:")
for m in [
    "def _aggregate_spans",
    "def _aggregate_unions",
    '"worked_span_duration": span',
    '"intensive_seconds": intensive',
    '"break_duration": break_dur',
    '"pause_seconds_total": pause_btn',
    '"worked_span_duration": total_span',
]:
    found = m in content
    print(f" {'OK' if found else 'MISS'}: {m}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_aggregates_v2.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч агрегатов (v2) ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_aggregates_v2.py
Что ожидаем
text
OK: добавлены _aggregate_spans и _aggregate_unions
OK: _aggregate_group переписан
OK: убран override в _group_by_employee
OK: убран override в _group_by_computer
OK: _group_by_session дополнена полями
OK: totals в _build_report обновлены
OK: totals в return обновлены
SYNTAX OK

Проверка маркеров:
 OK: def _aggregate_spans
 OK: def _aggregate_unions
 OK: "worked_span_duration": span
 OK: "intensive_seconds": intensive
 OK: break_duration": break_dur
 OK: "pause_seconds_total": pause_btn
 OK: "worked_span_duration": total_span
Если WARN: блок return с totals не найден — не страшно, потом посмотрим вручную.
Что после 1.B
Пересборка (docker compose down && up -d --build).
Открыть /admin/reports, сформировать отчёт за август — увидеть, что цифры не сломались (проверка что API не 500).
Только потом — 1.C (шаблон: убираем карточки, новые столбцы) и 1.D (блок «Без привязки»).
Запускай 1.B, пришли вывод (10–12 строк). Если всё OK — сразу дам 1.C + 1.D одной пачкой (там уже HTML, короче).
>> & client\.venv\Scripts\python.exe _patch_aggregates_v2.py === Патч агрегатов (v2) === OK: добавлены _aggregate_spans и _aggregate_unions OK: _aggregate_group переписан SKIP: override _group_by_employee не найден SKIP: override _group_by_computer не найден OK: _group_by_session дополнена полями OK: totals в _build_report обновлены WARN: блок return с totals не найден — правьте вручную SYNTAX OK Проверка маркеров: OK: def _aggregate_spans OK: def _aggregate_unions OK: "worked_span_duration": span OK: "intensive_seconds": intensive OK: "break_duration": break_dur OK: "pause_seconds_total": pause_btn MISS: "worked_span_duration": total_span
Пользователь запустил 1.B. Большая часть прошла, но две проблемы:
WARN: блок return с totals не найден — значит, формат return в _build_report отличается от того, что я ожидал.
MISS: "worked_span_duration": total_span — это следствие проблемы 1. Значит, _build_report возвращает старый totals без worked_span_duration.
Нужно:
Посмотреть реальный кусок _build_report, где собирается return {...}.
Пропатчить точечно.
Плюс интересно, что override в _group_by_employee не найден — возможно, _group_by_employee был переписан ранее и уже не содержит agg["worked_duration"] = sum(...). Это ок — можно оставить как есть, там уже должно быть правильно. Но нужно проверить, что _group_by_employee действительно возвращает span корректно.
Дам скрипт-диагностику: посмотреть _build_report целиком и _group_by_employee целиком. По ним пойму что там реально и сделаю точечный патч.
Диагностика: блок return в _build_report имеет другой формат. Плюс интересно, что override в _group_by_employee не нашелся — значит, там уже другая логика. Прежде чем патчить слепо — надо посмотреть реальное содержимое.
Скрипт диагностики
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$diag = @'
import re
PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

# 1. Находим _build_report целиком
m = re.search(r"def _build_report\(.*?(?=\ndef |\n# ============|\Z)",
              content, re.DOTALL)
if m:
    print("=" * 60)
    print("=== _build_report ЦЕЛИКОМ ===")
    print("=" * 60)
    print(m.group(0))
else:
    print("ERROR: _build_report не найдена")

# 2. Находим _group_by_employee целиком
m2 = re.search(r"def _group_by_employee\(.*?(?=\ndef |\n# ============|\Z)",
               content, re.DOTALL)
if m2:
    print()
    print("=" * 60)
    print("=== _group_by_employee ЦЕЛИКОМ ===")
    print("=" * 60)
    print(m2.group(0))
else:
    print("WARN: _group_by_employee не найдена")
'@

[System.IO.File]::WriteAllText("D:\tracker\_diag_build_report.py", $diag, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _diag_build_report.py
Пришли мне полный вывод. Дальше я:
Точечно поправлю return в _build_report — чтобы worked_span_duration, intensive_seconds, break_duration, pause_seconds_total попали в totals.
Проверю _group_by_employee — там уже должно быть корректно (раз нет старого override), но убедимся глазами.
Дам окончательный патч.
Скорее всего там просто старый формат с "key": value в одну строку, и мой паттерн не совпал из-за пробелов/переносов.
Разбираю вывод диагностики.
_build_report: totals частично обновлён — есть worked_span_duration (но total_worked_span дублируется с total_span), но НЕ хватает intensive_seconds, pause_seconds_total, break_duration.
Плюс есть дубль переменных: total_worked_span и total_span — обе суммы одинаковые. Убираем одну.
_group_by_employee: там уже есть ручной override:
python
agg["worked_duration"] = sum(d["span"] for d in days)
agg["worked_span_duration"] = total_span
Это НЕПРАВИЛЬНО! worked_duration тут = сумма спанов, а должен быть union. И worked_span_duration тоже считается как сумма daily spans — это как раз правильная логика для табеля. То есть _group_by_employee сейчас делает:
worked_span_duration = сумма daily spans ? (правильно для табеля)
worked_duration = сумма daily spans ? (должно быть union интервалов)
И _aggregate_group внутри себя уже возвращает правильные значения. Значит, override'ы — лишние и вредные.
План:
Убрать total_worked_span из _build_report (дубль total_span).
Добавить в totals: intensive_seconds, pause_seconds_total, break_duration.
Убрать override'ы в _group_by_employee — оставить только то, что даёт _aggregate_group. Но там ещё days_count — его надо сохранить.
Про _group_by_employee:
python
agg = _aggregate_group(all_sessions, {
    "employee_name": ..., "external_id": ..., "department_name": ...,
    "fired": ..., "days_count": len(days),
})
agg["worked_duration"] = sum(d["span"] for d in days)  # ? лишнее
total_span = 0
for d in days:  # ? лишнее (дублирует то, что уже считает _aggregate_group)
    ...
agg["worked_span_duration"] = total_span
_aggregate_group уже:
worked_span_duration = _aggregate_spans(sessions) — это для каждого (emp, day) считает span и суммирует. Для одного сотрудника это = sum(d["span"] for d in days). ?
worked_duration = _aggregate_unions(sessions) — union по дням. ?
Значит, override полностью лишние. Убираем.
То же самое проверим для _group_by_computer — там похожая логика, но её не видели. Просто уберём похожий код.
Пишу скрипт.
Также важно: надо чтобы новые поля точно попали в totals в шаблон. Проверю что имена правильные:
worked_span_duration — табель
worked_duration — union
effective_duration — эффективно
intensive_seconds — интенсивно
pause_seconds_total — пауза кнопкой
break_duration — общая пауза
Пишу патчер.
Один момент — дублирующаяся total_worked_span. Может там уже был мой старый патч. Оставляем total_span. Заменяем total_worked_span на total_span везде.
Пишу.
Отлично, картина ясная. Проблемы:
_build_report — частично пропатчен, но в totals не хватает intensive_seconds, pause_seconds_total, break_duration. Плюс есть дубль-переменная total_worked_span = total_span.
_group_by_employee — есть неправильный override: worked_duration = sum(d["span"]) — это сумма спанов, а должно быть union. И worked_span_duration считается через ручной цикл, хотя _aggregate_group это уже делает. Override'ы надо убрать.
Скрипт 1.B-fix
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

changes = []

# ============================================================
# 1. Убираем дубль total_worked_span в _build_report
# ============================================================
old_dup = '''    total_worked_span = sum(r.get("worked_span_duration", 0) for r in rows)
    total_span = sum(r.get("worked_span_duration", 0) for r in rows)'''
new_dup = '''    total_span = sum(r.get("worked_span_duration", 0) for r in rows)'''
if old_dup in content:
    content = content.replace(old_dup, new_dup, 1)
    changes.append("убран дубль total_worked_span")
else:
    changes.append("SKIP: дубль total_worked_span не найден")

# ============================================================
# 2. Расширяем totals в return
# ============================================================
old_totals = '''"totals": {
            "sessions": len(flat),
            "worked_span_duration": total_worked_span,
            "worked_duration": total_worked,
            "effective_duration": total_effective,
            "keyboard": total_keyboard,
            "mouse": total_mouse, "abnormal": total_abnormal, "top_apps": top_apps,
        },'''

new_totals = '''"totals": {
            "sessions": len(flat),
            "worked_span_duration": total_span,
            "worked_duration": total_worked,
            "effective_duration": total_effective,
            "intensive_seconds": total_intensive,
            "pause_seconds_total": total_pause_btn,
            "break_duration": total_break,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "abnormal": total_abnormal,
            "top_apps": top_apps,
        },'''

if old_totals in content:
    content = content.replace(old_totals, new_totals, 1)
    changes.append("totals расширены (intensive + break + pause)")
else:
    changes.append("ERROR: блок totals не найден")

# ============================================================
# 3. Убираем неправильный override в _group_by_employee
# ============================================================
# Ищем хвост функции после _aggregate_group(all_sessions, {...})
old_override_e = '''        })
        agg["worked_duration"] = sum(d["span"] for d in days)
        # span за период = сумма spans по дням (не один общий span).
        total_span = 0
        for d in days:
            day_sessions = d["sessions"]
            d_start = min(s["start_local"] for s in day_sessions)
            d_end = max(s["end_local"] for s in day_sessions)
            total_span += max(0, int((d_end - d_start).total_seconds()))
        agg["worked_span_duration"] = total_span
        result.append(agg)'''

new_override_e = '''        })
        result.append(agg)'''

if old_override_e in content:
    content = content.replace(old_override_e, new_override_e, 1)
    changes.append("убран override в _group_by_employee")
else:
    changes.append("SKIP: override в _group_by_employee не найден")

# ============================================================
# 4. Убираем похожий override в _group_by_computer (если есть)
# ============================================================
old_override_c = '''        })
        agg["worked_duration"] = sum(d["span"] for d in days)
        total_span = 0
        for d in days:
            day_sessions = d["sessions"]
            d_start = min(s["start_local"] for s in day_sessions)
            d_end = max(s["end_local"] for s in day_sessions)
            total_span += max(0, int((d_end - d_start).total_seconds()))
        agg["worked_span_duration"] = total_span
        result.append(agg)'''

if old_override_c in content:
    content = content.replace(old_override_c, new_override_e, 1)
    changes.append("убран override в _group_by_computer")
else:
    changes.append("SKIP: override в _group_by_computer не найден")

# ============================================================
# 5. Сохраняем
# ============================================================
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    changes.append("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

for c in changes:
    print(c)

print()
print("Проверка totals:")
for m in ['"intensive_seconds": total_intensive',
          '"pause_seconds_total": total_pause_btn',
          '"break_duration": total_break',
          '"worked_span_duration": total_span',
          '"worked_duration": total_worked']:
    found = m in content
    print(f" {'OK' if found else 'MISS'}: {m}")

print()
print("Проверка _group_by_employee (должно быть чисто):")
