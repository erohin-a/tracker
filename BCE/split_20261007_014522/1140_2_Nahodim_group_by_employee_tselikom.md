<!-- Часть 1140 из 1409 -->
# 2. Находим _group_by_employee целиком
*Хлебные крошки:* 2. Находим _group_by_employee целиком

[◀ 1. Находим _build_report целиком](1139_1_Nahodim_build_report_tselikom.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1141_part.md)

---

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

