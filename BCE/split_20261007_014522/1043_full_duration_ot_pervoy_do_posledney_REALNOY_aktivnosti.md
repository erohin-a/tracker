<!-- Часть 1043 из 1409 -->
# full_duration = от первой до последней РЕАЛЬНОЙ активности
*Хлебные крошки:* full_duration = от первой до последней РЕАЛЬНОЙ активности

[◀ Вычитаем время паузы (если есть)](1042_Vychitaem_vremya_pauzy_esli_est.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1044_part.md)

---

# full_duration = от первой до последней РЕАЛЬНОЙ активности
full_duration = max(0, int((activity_end_local - activity_start_local).total_seconds()))

return {
    ...
    "full_duration": full_duration,
    "effective_duration": effective_duration,
    "activity_start_local": activity_start_local,
    "activity_end_local": activity_end_local,
    ...
}
And in _span_of_sessions:
python
def _span_of_sessions(sessions: list) -> int:
    if not sessions:
        return 0
    first = min(s["activity_start_local"] for s in sessions)
    last = max(s["activity_end_local"] for s in sessions)
    return max(0, int((last - first).total_seconds()))
But wait — _span_of_sessions is also called from _group_by_employee and _group_by_department and _group_by_computer. So all of them get the new behavior. Good.
Also for _group_by_session, we use r["full_duration"] — which is already computed from activity. Good.
Let me check: does _analyze_session return dict get used anywhere expecting end_local specifically? Let's see — _group_by_session uses r["end_local"] for display "Конец". Hmm, so we should keep end_local for display, but add activity_end_local for calculations.
Let me keep both.
OK let me write the patch as a Python script.
Let me also plan step 4 (server cap) since it goes together:
In upsert_session in main.py, if end - start > 24h, set end = start + 24h, log to audit.
And step 5 (stale session task):
New task close_stale_sessions in tasks.py.
Register in TASKS_REGISTRY with default_cron = "*/30 * * * *" (every 30 min) and default_enabled = False (user enables).
New setting stale_session_hours in AppSetting (default 2, range 1-24).
Add to settings page and settings_dict.
Migration not needed (AppSetting is generic).
And step 6 (union intervals):
New function _union_duration(sessions) — takes list of session dicts, computes union of [activity_start_local, activity_end_local] intervals.
In _split_by_day — replace _span_of_sessions with _union_duration.
In _group_by_employee — sum days with union per day. Actually — wait, if we group by employee, we want to union across days? No, sum per day.
Actually _group_by_employee sums d["span"] for each day. So span = _span_of_sessions(sessions_of_day). If we make _span_of_sessions use union internally... hmm no. Let me keep it simple:
_span_of_sessions uses union of intervals (min_start to max_end is wrong for multiple sessions with gaps — actually min_start to max_end IS the outer span, not union).
Wait, I need to think. Union of intervals [a-b] [c-d] where b < c: union = [a-b] + [c-d] = (b-a)+(d-c). Sum = same. But min_start to max_end = (d-a). Different!
Example: sessions [09:00-12:00] [14:00-18:00].
_span_of_sessions (min_max) = 18:00 - 09:00 = 9 hours.
_union_duration = 3h + 4h = 7 hours.
sum of full_durations = 3h + 4h = 7 hours.
So union = sum of full_durations when sessions don't overlap. Union < sum when sessions overlap.
For our purpose (два ПК у одного сотрудника), union is what we want.
So _span_of_sessions should actually be replaced by union. Then for the group-by-day case, union of all sessions of that day for that employee. And _group_by_employee sums union-per-day, which is correct.
Hmm but the row-per-day when there's one employee one PC — [09:00-18:00] — min_max = union = 9h. Same. Only matters with overlaps.
OK, so we can just replace _span_of_sessions implementation with _union_duration and everything works.
Let me combine steps 3, 5 (task+setting) and 6 in one big patch of web_admin.py. Plus step 4 in main.py.
Actually let me split:
Скрипт 1: main.py — server cap (step 4)
Скрипт 2: web_admin.py — report fix + union (steps 3 + 6)
Скрипт 3: tasks.py — new task + registry (step 5)
Скрипт 4: web_admin.py — settings page: add stale_session_hours field (step 5)
Скрипт 5: settings.html template — add field (step 5)
Скрипт 6: пересборка
Hmm, but that's a lot. Let me combine where possible.
Let me structure the response:
Шаг 3 + 6 — патч web_admin.py (отчёты: full_duration + union)
Шаг 4 — патч main.py (сервер: cap на 24h)
Шаг 5a — патч tasks.py (новая задача close_stale_sessions)
Шаг 5b — патч web_admin.py (settings_dict + settings_save + settings_page)
Шаг 5c — патч шаблона settings.html
Шаг 6 — пересборка и тест
Let me write it compactly but completely. Start with шаг 3+6 (report fix), since that's the main one and it's what the user sees.
Actually — since web_admin.py will be patched twice (steps 3+6 and 5b), I could do them together. But it's easier to keep separate.
Let me split into two big Python patchers for web_admin.py: one for step 3+6 (reports), one for step 5b (settings). And separate for main.py and tasks.py.
OK, let me write the response now.
Actually, let me reconsider the order:
Шаг 3 (report full_duration) — critical, fixes the actual bug the user sees
Шаг 4 (server cap) — needed to prevent future bad data
Шаг 5 (stale task) — needed to close sessions that client never closes
Шаг 6 (union) — needed for two-PC case
All of them are needed. Let me just do them in order.
Response structure:
Подтверждение шагов 1-2
Скрипт для шага 3 (web_admin.py — full_duration + union)
Скрипт для шага 4 (main.py — cap 24h)
Скрипт для шага 5a (tasks.py — new task)
Скрипт для шага 5b (web_admin.py — settings)
Скрипт для шага 5c (settings.html)
Пересборка
Тест
Let me write it now.
Wait — one issue with union and day grouping. In _split_by_day, sessions are grouped by (workday_date, employee_id). Then _span_of_sessions(sessions) is called. If we make _span_of_sessions use union, that handles intra-day overlaps.
But _group_by_employee calls _span_of_sessions per day and then sums spans. Different days don't overlap (they're different days). So sum is correct.
_group_by_department, _group_by_computer — aggregate across all days for that department/computer. Union of intervals from different days wouldn't be well-defined (they're different calendar days). We should sum per-day unions. Hmm.
Let me look at _group_by_department:
python
def _group_by_department(flat: list) -> list:
    groups = defaultdict(list)
    for r in flat:
        groups[r["department_name"]].append(r)
    result = []
    for dept, sessions in groups.items():
        agg = _aggregate_group(sessions, {"department_name": dept})
        ...
_aggregate_group calls _span_of_sessions(sessions) where sessions = all flat records for that dept across all days. If we use union here, we'd get min(start) to max(end) if they all overlap, but they don't — they're different days. So union of [09:00 23.09, 18:00 23.09] and [09:00 24.09, 18:00 24.09] gives 9h + 9h = 18h. Sum of spans = 18h. Same. OK.
But _group_by_employee doesn't call _aggregate_group for the total — it calls _aggregate_group(all_sessions, ...) then overrides worked_duration by summing daily spans:
python
agg["worked_duration"] = sum(d["span"] for d in days)
Hmm wait, so _aggregate_group is called for all_sessions, but then worked_duration is overwritten. But _aggregate_group also computes effective_duration as sum. OK.
Actually looking closer at _group_by_department:
python
def _group_by_department(flat: list) -> list:
    groups = defaultdict(list)
    for r in flat:
        groups[r["department_name"]].append(r)
    result = []
    for dept, sessions in groups.items():
        agg = _aggregate_group(sessions, {"department_name": dept})
        agg["days_count"] = len({s["workday_date"] for s in sessions})
        agg["employees_count"] = len({s["employee_id"] for s in sessions})
        result.append(agg)
Yes, _aggregate_group calls _span_of_sessions(sessions) where sessions is ALL sessions for the department across the whole period.
If we use union, and there are multiple days, then intervals from day 1 and day 2 are non-overlapping. Union returns sum of daily spans.
Example: 3 days, 8h each: union = 24h. Sum of spans = 24h. Same. Good.
But — if we later add grouping where we want "average per day" — we'd need different logic. Not now.
OK, _span_of_sessions ? union works fine everywhere.
Wait actually — hold on. _span_of_sessions currently uses min_start to max_end, which for multi-day could be 30 days! Let me re-read...
Yes: first = min(s["start_local"] for s in sessions); last = max(s["end_local"] for s in sessions); return (last - first). So for a department over a month, worked_duration would be ~30 days. That's a bug too!
Actually looking at the report the user sent: _split_by_day groups by day first, so _span_of_sessions gets only one day's sessions. But _group_by_department gives a month's worth of sessions ? span = month-length. Hmm, and the report shows "Отработано" for "по отделам" grouping...
Anyway — using union is MORE correct than span. So let's do it.
For the multi-day scenario, union = sum of daily unions (since days are disjoint intervals).
OK let me write the patch for _span_of_sessions:
python
def _span_of_sessions(sessions: list) -> int:
    """
    Возвращает СУММАРНОЕ рабочее время за период, исключая пересечения.

    Раньше: last_end - first_start. Это давало огромные значения, если
    период длинный (например, месяц = 30 дней "работы").
    Плюс это давало «двойной счёт» при параллельной работе на двух ПК.

    Теперь: union интервалов [activity_start, activity_end]. Пересечения
    схлопываются, разрывы исключаются.
    """
    if not sessions:
        return 0
    intervals = [(s["activity_start_local"], s["activity_end_local"]) for s in sessions]
    return _union_duration(intervals)


def _union_duration(intervals: list) -> int:
    """
    Возвращает суммарную длительность объединения интервалов.
    intervals: список кортежей (datetime, datetime).
    Если интервалы пересекаются — пересечение считается один раз.
    """
    if not intervals:
        return 0
    # Сортируем по началу
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    merged = [list(sorted_iv[0])]
    for start, end in sorted_iv[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            # Пересекаются или касаются — расширяем
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    total = 0
    for s, e in merged:
        total += max(0, int((e - s).total_seconds()))
    return total
Now I need to add activity_start_local and activity_end_local to the _analyze_session return dict.
Let me write the full patch.
Also need to update _group_by_session — it uses r["full_duration"] for worked_duration, which is already what we want.
Let me write the response.
Отлично, шаги 1–2 работают. Все маркеры на месте, импорт проходит.
Дальше — шаги 3, 4, 5, 6 одной пачкой. Все четыре изменения независимы, но проверять их удобно вместе.
Что делаем:
Шаг 3 — в отчётах full_duration = от первой до последней реальной активности внутри сессии, а не session_end - session_start.
Шаг 6 — _span_of_sessions заменяем на union интервалов (пересечения схлопываются). Это заодно чинит баг «30 дней работы по отделу за месяц».
Шаг 4 — на сервере защита: сессии длиннее 24 часов обрезаются.
Шаг 5 — новая задача close_stale_sessions + настройка «Порог автозакрытия зависших сессий» в админке.
Начинаем с главного — шаг 3 + 6 (патч web_admin.py).
________________________________________
Шаг 3 + 6 — Патч server/web_admin.py (отчёты)
Два изменения в _analyze_session + переписываем _span_of_sessions + добавляем хелпер _union_duration.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

