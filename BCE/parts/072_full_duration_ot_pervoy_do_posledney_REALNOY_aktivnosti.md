# full_duration = от первой до последней РЕАЛЬНОЙ активности

*Часть 72 из 100. Источник: `BCE.md`.*

[◀ close_session не меняем, оставляем для ручного закрытия](071_close_session_ne_menyaem_ostavlyaem_dlya_ruchnogo_zakrytiya.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ▶](073_Proverka.md)

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

# ============================================================
# ПАТЧ 1: _analyze_session — использует last_event_local для full_duration
# ============================================================
if "activity_start_local" in content:
    print("SKIP: _analyze_session уже пропатчен")
else:
    old_block = '''    if first_event_local and last_event_local:
        effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
    else:
        effective_duration = 0

    # Вычитаем время паузы (если есть)
    pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)
    if pause_sec > 0:
        effective_duration = max(0, effective_duration - pause_sec)

    full_duration = max(0, int((end_local - start_local).total_seconds()))

    top_apps = sorted('''

    new_block = '''    if first_event_local and last_event_local:
        effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
        activity_start_local = first_event_local
        activity_end_local = last_event_local
    else:
        effective_duration = 0
        # Fallback: если в сессии нет ни одной записи
        # (бывает при аварийном закрытии) — используем сами границы.
        activity_start_local = start_local
        activity_end_local = end_local

    # Вычитаем время паузы (если есть)
    pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)
    if pause_sec > 0:
        effective_duration = max(0, effective_duration - pause_sec)

    # full_duration — «Отработано» в отчёте.
    # Считаем от первой до последней РЕАЛЬНОЙ активности, а не
    # от session_start до session_end. Это исключает «мусорные» часы,
    # когда сессия висела незакрытой (клиент упал, ПК выключили).
    full_duration = max(0, int((activity_end_local - activity_start_local).total_seconds()))

    top_apps = sorted('''

    if old_block in content:
        content = content.replace(old_block, new_block, 1)
        print("OK: _analyze_session — full_duration от активности")
    else:
        print("ERROR: не найден блок full_duration в _analyze_session")
        raise SystemExit(1)

    # Добавляем activity_start_local/activity_end_local в return-словарь
    old_ret = '''        "full_duration": full_duration,
        "effective_duration": effective_duration,
        "pause_seconds": pause_sec,'''

    new_ret = '''        "full_duration": full_duration,
        "effective_duration": effective_duration,
        "activity_start_local": activity_start_local,
        "activity_end_local": activity_end_local,
        "pause_seconds": pause_sec,'''

    if old_ret in content:
        content = content.replace(old_ret, new_ret, 1)
        print("OK: return-словарь дополнен activity_*_local")
    else:
        print("ERROR: не найден return в _analyze_session")
        raise SystemExit(1)

# ============================================================
# ПАТЧ 2: _span_of_sessions ? union интервалов
# ============================================================
if "_union_duration" in content:
    print("SKIP: _union_duration уже есть")
else:
    old_span = '''def _span_of_sessions(sessions: list) -> int:
    if not sessions:
        return 0
    first = min(s["start_local"] for s in sessions)
    last = max(s["end_local"] for s in sessions)
    return max(0, int((last - first).total_seconds()))'''

    new_span = '''def _union_duration(intervals: list) -> int:
    """
    Возвращает суммарную длительность ОБЪЕДИНЕНИЯ интервалов.

    intervals: список кортежей (start_datetime, end_datetime).
    Если два интервала пересекаются — пересечение считается один раз.

    Пример:
        [09:00 - 12:00] + [11:00 - 14:00]  ?  5 часов (не 6)
        [09:00 - 12:00] + [14:00 - 18:00]  ?  7 часов (не пересекаются)
    """
    if not intervals:
        return 0
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    merged = [list(sorted_iv[0])]
    for start, end in sorted_iv[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            # Пересекаются или касаются — расширяем последний интервал
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    total = 0
    for s, e in merged:
        total += max(0, int((e - s).total_seconds()))
    return total


def _span_of_sessions(sessions: list) -> int:
    """
    Суммарное рабочее время за период, БЕЗ пересечений.

    Раньше: last_end - first_start. Давало огромные значения, если
    период длинный (месяц = «30 дней работы»). Плюс давало двойной
    счёт при параллельной работе на двух ПК.
    Теперь: union интервалов [activity_start, activity_end].
    """
    if not sessions:
        return 0
    intervals = [(s["activity_start_local"], s["activity_end_local"])
                 for s in sessions]
    return _union_duration(intervals)'''

    if old_span in content:
        content = content.replace(old_span, new_span, 1)
        print("OK: _span_of_sessions ? _union_duration")
    else:
        print("ERROR: старая _span_of_sessions не найдена")
        raise SystemExit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_reports_full.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч отчётов ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_reports_full.py
Что ожидаем:
text
OK: _analyze_session — full_duration от активности
OK: return-словарь дополнен activity_*_local
OK: _span_of_sessions ? _union_duration
SYNTAX OK
________________________________________
Шаг 4 — Патч server/main.py (предохранитель 24 часа)
Если прилетает сессия длиннее 24 часов — обрезаем на стороне сервера и пишем в аудит. Это защита от багов в клиенте.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\server\main.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "MAX_SESSION_HOURS" in content:
    print("SKIP: cap уже есть")
else:
    old = '''    start = datetime.fromisoformat(payload.session_start.replace("Z", "+00:00"))
    end = (datetime.fromisoformat(payload.session_end.replace("Z", "+00:00"))
           if payload.session_end else None)

    if end is not None and end < start:
        raise HTTPException(422, "session_end < session_start")

    ws = (db.query(WorkSession)
          .filter(WorkSession.session_uid == payload.session_uid).first())'''

    new = '''    start = datetime.fromisoformat(payload.session_start.replace("Z", "+00:00"))
    end = (datetime.fromisoformat(payload.session_end.replace("Z", "+00:00"))
           if payload.session_end else None)

    if end is not None and end < start:
        raise HTTPException(422, "session_end < session_start")

    # ------------------------------------------------------------
    # ПРЕДОХРАНИТЕЛЬ: сессия не может быть длиннее 24 часов.
    # Защита от бага в клиенте («сессия висела незакрытой ночью»).
    # Если прилетело — обрезаем и пишем в аудит.
    # ------------------------------------------------------------
    MAX_SESSION_HOURS = 24
    if end is not None:
        duration_hours = (end - start).total_seconds() / 3600.0
        if duration_hours > MAX_SESSION_HOURS:
            original_end = end
            end = start + timedelta(hours=MAX_SESSION_HOURS)
            log.warning(
                "Session %s too long (%.2fh) — capped to 24h "
                "(session_uid=%s, comp=%s)",
                payload.session_uid, duration_hours,
                payload.session_uid, comp.computer_uid,
            )
            db.add(AuditLog(
                actor=f"server:cap",
                entity="work_session",
                entity_id=payload.session_uid,
                action="capped_24h",
                new_value=json.dumps({
                    "original_end": original_end.isoformat(),
                    "capped_end": end.isoformat(),
                    "duration_hours": round(duration_hours, 2),
                }, ensure_ascii=False),
            ))

    ws = (db.query(WorkSession)
          .filter(WorkSession.session_uid == payload.session_uid).first())'''

    if old in content:
        content = content.replace(old, new, 1)
        print("OK: добавлен предохранитель 24 часа")
    else:
        print("ERROR: не найден блок в upsert_session")
        raise SystemExit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_server_cap.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч server/main.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_server_cap.py
Что ожидаем:
text
OK: добавлен предохранитель 24 часа
SYNTAX OK
________________________________________
Шаг 5a — Патч server/tasks.py (новая задача)
Добавляем задачу close_stale_sessions — раз в 30 минут закрывает сессии, у которых нет session_end и прошло больше N часов (настройка stale_session_hours, default 2).
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\server\tasks.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "def close_stale_sessions" in content:
    print("SKIP: close_stale_sessions уже есть")
    raise SystemExit(0)

# Вставляем функцию перед TASKS_REGISTRY
marker = "# ============================================================\n# Карта задач: имя в scheduler"

new_func = '''# ============================================================
# 7. Автозакрытие зависших сессий
# ============================================================
def close_stale_sessions(db: Session) -> str:
    """
    Закрывает сессии, которые клиент так и не закрыл.

    Сценарий: сотрудник ушёл домой, забыл нажать «Конец работы»,
    ПК выключили или клиент упал. Сессия висит в БД с session_end = NULL.
    Такая сессия портит отчёты (у нас был случай: 17 часов за один день).

    Логика:
      1. Читаем настройку stale_session_hours (по умолчанию 2 часа).
      2. Ищем сессии, где session_end IS NULL
         и session_start < NOW() - stale_session_hours.
      3. Закрываем каждую:
         - session_end = MAX(client_ts) из records (последняя активность)
         - если записей нет — session_end = session_start
         - abnormal_termination = True
      4. Пишем в audit_log.

    Запускается каждые 30 минут (cron */30 * * * *).
    """
    from .models import AppSetting as _AppSetting, Record as _Record

    # Читаем настройку
    row = db.query(_AppSetting).filter(
        _AppSetting.key == "stale_session_hours"
    ).first()
    try:
        stale_hours = max(1, min(24, int(row.value))) if row else 2
    except (ValueError, TypeError):
        stale_hours = 2

    cutoff = _now() - timedelta(hours=stale_hours)

    stale = (
        db.query(WorkSession)
        .filter(
            WorkSession.session_end.is_(None),
            WorkSession.session_start < cutoff,
        )
        .all()
    )

    if not stale:
        return f"Зависших сессий нет (порог {stale_hours}ч)"

    closed = 0
    for ws in stale:
        # Ищем последнюю запись в этой сессии
        last_record_ts = (
            db.query(_Record.client_ts)
            .filter(_Record.session_uid == ws.session_uid)
            .order_by(_Record.client_ts.desc())
            .limit(1)
            .scalar()
        )

        if last_record_ts is not None:
            end_ts = last_record_ts
        else:
            # Записей нет вообще — закрываем нулевой длительностью
            end_ts = ws.session_start

        ws.session_end = end_ts
        ws.abnormal_termination = True
        closed += 1

        db.add(AuditLog(
            actor="scheduler:close_stale_sessions",
            entity="work_session",
            entity_id=ws.session_uid,
            action="auto_close_stale",
            new_value=(
                f"start={ws.session_start.isoformat()}, "
                f"end={end_ts.isoformat() if end_ts else 'None'}, "
                f"threshold={stale_hours}h"
            ),
        ))

    db.commit()
    log.warning(
        "close_stale_sessions: закрыто %d сессий (порог %dч)",
        closed, stale_hours,
    )
    return f"Закрыто зависших сессий: {closed} (порог {stale_hours}ч)"


'''

if marker not in content:
    print("ERROR: маркер TASKS_REGISTRY не найден")
    raise SystemExit(1)

content = content.replace(marker, new_func + marker, 1)

# Регистрируем в TASKS_REGISTRY — вставляем новый элемент
old_reg = '''    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

new_reg = '''    "close_stale_sessions": {
        "func": close_stale_sessions,
        "label_ru": "Автозакрытие зависших сессий",
        "label_en": "Auto-close stale sessions",
        "desc_ru": "Закрывает сессии без активности дольше N часов (N настраивается в /admin/settings).",
        "desc_en": "Closes sessions without activity for N hours (configured in /admin/settings).",
        "default_cron": "*/30 * * * *",   # каждые 30 минут
        "default_enabled": True,
    },
    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

if old_reg in content:
    content = content.replace(old_reg, new_reg, 1)
    print("OK: задача зарегистрирована в TASKS_REGISTRY")
else:
    print("WARN: не найден блок aggregate_daily_stats в реестре")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_tasks_stale.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч tasks.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_tasks_stale.py
Что ожидаем:
text
OK: задача зарегистрирована в TASKS_REGISTRY
SYNTAX OK
________________________________________
Шаг 5b — Патч server/web_admin.py (настройка stale_session_hours)
Добавляем новую настройку в get_settings_dict, settings_save и settings_page.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "stale_session_hours" in content:
    print("SKIP: stale_session_hours уже есть")
    raise SystemExit(0)

# 1. В get_settings_dict добавляем поле
old_dict = '''        "end_of_day_hour": get_app_setting_int(db, "end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": get_app_setting_int(db, "end_of_day_minute", 0, 0, 59),
}'''

new_dict = '''        "end_of_day_hour": get_app_setting_int(db, "end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": get_app_setting_int(db, "end_of_day_minute", 0, 0, 59),
        # --- Автозакрытие зависших сессий ---
        "stale_session_hours": get_app_setting_int(db, "stale_session_hours", 2, 1, 24),
}'''

if old_dict in content:
    content = content.replace(old_dict, new_dict, 1)
    print("OK: stale_session_hours в settings_dict")
else:
    print("ERROR: не найден конец settings_dict")
    raise SystemExit(1)

# 2. В settings_save добавляем параметр
old_save_sig = '''    end_of_day_hour: int = Form(19),
    end_of_day_minute: int = Form(0),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):'''

new_save_sig = '''    end_of_day_hour: int = Form(19),
    end_of_day_minute: int = Form(0),
    stale_session_hours: int = Form(2),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):'''

if old_save_sig in content:
    content = content.replace(old_save_sig, new_save_sig, 1)
    print("OK: параметр stale_session_hours в settings_save")
else:
    print("ERROR: не найдена сигнатура settings_save")
    raise SystemExit(1)

# 3. В new_vals добавляем обработку
old_vals = '''        "end_of_day_hour": max(0, min(23, int(end_of_day_hour))),
        "end_of_day_minute": max(0, min(59, int(end_of_day_minute))),
    }'''

new_vals = '''        "end_of_day_hour": max(0, min(23, int(end_of_day_hour))),
        "end_of_day_minute": max(0, min(59, int(end_of_day_minute))),
        "stale_session_hours": max(1, min(24, int(stale_session_hours))),
    }'''

if old_vals in content:
    content = content.replace(old_vals, new_vals, 1)
    print("OK: обработка stale_session_hours в new_vals")
else:
    print("ERROR: не найден блок new_vals")
    raise SystemExit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_settings_stale.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч настроек ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_settings_stale.py
Что ожидаем:
text
OK: stale_session_hours в settings_dict
OK: параметр stale_session_hours в settings_save
OK: обработка stale_session_hours в new_vals
SYNTAX OK
________________________________________
Шаг 5c — Патч шаблона settings.html
Добавляем поле на страницу /admin/settings. Найдём блок «Idle-порог» и вставим рядом.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\settings.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("stale_session_hours")) {
    Write-Host "SKIP: поле уже есть" -ForegroundColor Yellow
} else {
    # Ищем блок Idle-порог и вставляем новую строку после него
    $oldBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
'@

    $newBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">
                        Автозакрытие зависших сессий
                        <span class="hint" data-bs-toggle="tooltip" title="Если сессия висит без session_end дольше указанного времени — сервер закроет её временем последней активности. Защита от ситуации «сотрудник забыл нажать Конец работы, ПК выключили».">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="stale_session_hours" class="form-control"
                               value="{{ cfg.stale_session_hours }}" min="1" max="24">
                        <span class="input-group-text">часов</span>
                    </div>
                    <div class="form-text">По умолчанию 2 часа. Рекомендуется 1–3.</div>
                </div>
'@

    if ($content.Contains($oldBlock)) {
        $content = $content.Replace($oldBlock, $newBlock)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: поле stale_session_hours добавлено" -ForegroundColor Green
    } else {
        Write-Host "ERROR: не найден блок Idle-порог в settings.html" -ForegroundColor Red
        Write-Host "Откройте вручную и вставьте блок рядом с idle_close_minutes" -ForegroundColor Yellow
    }
}

