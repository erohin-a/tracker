<!-- Часть 289 из 1409 -->
# after loop:
*Хлебные крошки:* after loop:

[◀ in loop:](288_in_loop.md) | [Оглавление](00_BCE_INDEX.md) | [in _check_idle_session: ▶](290_in_check_idle_session.md)

---

# after loop:
if g["first_start"] and g["last_end"]:
    g["worked_duration"] = int((g["last_end"] - g["first_start"]).total_seconds())
else:
    g["worked_duration"] = 0
g["effective_duration"] = g["duration"]  # сохраняем старое значение
Wait but the duration field is already used elsewhere. Let me use clear naming:
g["effective_duration"] = sum of session effective_durations
g["worked_duration"] = last_end - first_start (span)
Rename existing g["duration"] to g["effective_duration"].
But then in template I need to update. And other group functions too.
Let me be consistent: change all group functions to set both:
worked_duration (span, first_start to last_end)
effective_duration (sum of effective)
full_duration (sum of full_duration of sessions, for info)
For _group_by_session — individual sessions have both full_duration and effective_duration (duration). And "worked" span = same as effective per session? No. For a single session: worked span = full_duration, effective = duration. So keep as is.
Hmm actually now I need to be careful — for the "days" and "employees" grouping, we add worked_duration. For sessions, it doesn't make sense (each session is what it is).
OK let me also think about how to handle column headers in template:
"Рабочий день" — date
"Сессий" — count
"Работал (span)" — worked_duration
"Эффективно" — effective_duration
...
Hmm. Wait, user said:
«Отработано» считаем время начальной сессии и время окончания последней сессии за этот день
добавляем «Эффективно время» сюда будет подать то что попадает сейчас в поле «Отработано»
So they want:
Column "Отработано" ? span (first_start to last_end)
Column "Эффективное время" ? effective sum
I'll use:
"Отработано" = worked_duration (span)
"Эффективно" = effective_duration
But then what about the old "Полное" column? It was "full_duration = end - start for each session, summed". That doesn't quite match either.
Let me simplify:
"Отработано" = last_end - first_start (user's new definition)
"Эффективно" = sum of session effective_durations
(Убрать "Полное" колонку чтобы не путать? Или оставить как подробность)
Actually the "Полное" was showing sum of session full_durations (which includes gaps within a single session). It's a bit redundant with the new "Отработано".
Let me think again:
Session: start at 09:00, end at 18:00 (с обедом в 13:00-14:00)
full_duration = 9h (09:00-18:00)
effective_duration = maybe 6h (учитывая разрывы > 5 min)
If two sessions in a day:
session1 = 09:00-13:00
session2 = 14:00-18:00
worked_duration (span) = 09:00 to 18:00 = 9h
effective_duration = sum = maybe 6h (out of 4h each, учитывая gaps within)
full_duration sum = 8h
So three different numbers. Let me show:
"Работал" (span): 09:00 ? 18:00 = 9:00:00
"Эффективно": 6:00:00
"Полное": 8:00:00 (info, менее приоритетно)
Hmm, but user explicitly said:
«Отработано» считаем время начальной сессии и время окончания последней сессии за этот день
добавляем «Эффективно время» сюда будет подать то что попадает сейчас в поле «Отработано»
So:
"Отработано" = span (первое начало ? последний конец)
"Эффективно" = то что было в "Отработано" до этого (effective sum)
Only two columns needed for these. The "Полное" (full_duration) can be dropped or kept small. Let me keep it small/informational.
Actually — user said только два. Let me:
"Отработано" = span
"Эффективное время" = effective
And remove "Полное" column, or keep it under expansion details. I'll remove it from main view to not overload.
Hmm, but user might want both. Actually they said:
"«Отработано» считаем время начальной сессии и время окончания последней сессии за этот день"
"добавляем «Эффективно время» сюда будет подать то что попадает сейчас в поле «Отработано»"
They only mention 2 columns. Let me do:
"Отработано" (span) — новая логика
"Эффективное время" — то что было
And remove "Полное" column. Or hide it in expanded view.
Let me keep it simpler: only 2 columns.
But wait — I need to preserve backward compat. Let me do:
"Отработано" (was "Отработано") ? now becomes span
"Эффективное" ? new column, has old value
"Полное" ? removed from main table (or kept in expansion)
OK. Let me decide:
"Отработано" = worked_duration (span)
"Эффективно" = effective_duration
Remove "Полное" from main columns
Wait — thinking again, in each group we sum full_duration of all sessions. Let me call that summed_full and drop from main view.
Alright, let me finalize the column structure for days mode:
| Рабочий день | Сотрудник | 1C ID | Сессий | Отработано | Эффективно | Аварийных | ? |
For employees mode:
| Сотрудник | 1C ID | Дней | Сессий | Отработано | Эффективно | Аварийных | ? |
Hmm for employees mode: "Отработано" = from first session of period to last session of period. That's a big span. Maybe not useful. But user asked so let's do it consistently.
Actually — for "по сотрудникам" over a month, "Отработано" span would be from 1st to 30th = ~30 days. Not meaningful.
Hmm. For employees mode, maybe we should sum worked_duration per day? That is, for each day, span; then sum spans.
Actually that's what user wants probably: sum across days of daily spans.
Let me do it properly:
For employees mode: group by employee, but within employee group, group by day, and sum daily spans.
So worked_duration = sum over days of (last_end - first_start for that day)
That's the "табель" approach.
Actually let me keep it simpler and just sum across all sessions' effective_durations and use first/last as "span" — but rename to something honest.
Hmm. OK. I'll do the "correct" thing: for employee group, do the days-group first, then sum.
Let me restructure: build by_day first (list of day-groups), then group by employees/computers.
Wait but that changes structure. Let me instead compute per employee per day, then aggregate.
Actually simpler: modify the grouping functions:
python
def _group_by_employee(flat):
    # 1. group by (employee_id, workday_date) — intermediate
    by_day = defaultdict(list)
    for r in flat:
        by_day[(r["employee_id"], r["workday_date"])].append(r)
    
    # 2. for each employee, compute daily spans and effective sums
    emp_days = defaultdict(list)  # emp_id -> list of (day, span, eff_sum)
    for (emp_id, day), sessions in by_day.items():
        first_start = min(s["start_local"] for s in sessions)
        last_end = max(s["end_local"] for s in sessions)
        span = int((last_end - first_start).total_seconds())
        eff = sum(s["effective_duration"] for s in sessions)
        emp_days[emp_id].append({"day": day, "span": span, "effective": eff, "sessions": sessions})
    
    # 3. build employee groups
    for emp_id, days in emp_days.items():
        worked_duration = sum(d["span"] for d in days)
        effective_duration = sum(d["effective"] for d in days)
        ...
OK this is more involved. Let me do this in code.
Alright — enough analysis. Time to write.
Actually, given the size, let me be pragmatic: I'll implement:
For days: worked = span within day; effective = sum
For employees: worked = sum of daily spans; effective = sum of all effective
For computers: same as employees
For sessions: worked = full_duration, effective = effective_duration
For employees/computers I'll do the intermediate grouping.
Alright, let me write everything.
Actually let me just write. Doing this now.
For PowerShell scripts, I need to be careful with backticks and signs.Letmeuse‘?@...?@‘formulti?linestrings.Inside,‘signs.Letmeuse‘?@...?@‘formulti?linestrings.Inside,‘in template strings will be preserved (single-quote here-strings are literal). But‘inPowerShellisvariableexpansion?insidesingle?quotedhere?string,‘‘inPowerShellisvariableexpansion?insidesingle?quotedhere?string,‘var` is NOT expanded. Good.
For f-strings in Python code, {var} is inside Python, not PowerShell. Good.
Watch out for backtick: PowerShell uses backtick as escape. In single-quoted here-string, backticks are literal. Good.
OK writing now.
Let me limit the size by combining sensibly. I'll have:
Script 1: models.py + web_admin.py (server Python)
Script 2: templates (base, settings, reports, report_result)
Script 3: main.py server patch (insert client-config endpoint)
Script 4: client patches
Script 5: rebuild
Let me write.
For models.py, I'll add AppSetting class. Otherwise unchanged.
For web_admin.py, big changes.
For templates, new settings.html, changes to base.html, report_result.html, small change to reports.html.
For main.py (server), insert endpoint.
For client:
db.py: add get_idle_close_minutes helper
sync.py: fetch client-config periodically
main.py: use db meta value for idle close
Actually simpler for client: since we're storing value in server DB, and client needs it — sync worker fetches it and stores locally in db meta. Then main window reads db meta for idle close.
Let me finalize. Writing now.
Wait, I realized — main.py client currently imports IDLE_CLOSE_MINUTES from config. I need to change that to read from db. Let me patch accordingly.
Also — client fetches config from server: needs SERVER_URL. That's already imported in sync.py.
Let me code the sync fetch:
python
def _fetch_client_config(self):
    try:
        r = http_client.get(f"{SERVER_URL}/api/v1/client-config",
                            headers=self._headers(), timeout=5.0)
        if r.status_code == 200:
            data = r.json()
            idle = int(data.get("idle_close_minutes", 30))
            current = db.get_meta("idle_close_minutes")
            if str(idle) != current:
                db.set_meta("idle_close_minutes", str(idle))
                log.info("idle_close_minutes updated: %d", idle)
    except Exception as e:
        log.debug("client-config fetch failed: %s", e)
Call once every 10 sync cycles (5 min if SYNC_INTERVAL=30).
Now let me also add db.get_idle_close_minutes(default):
python
def get_idle_close_minutes(default: int = 30) -> int:
    val = get_meta("idle_close_minutes")
    if val:
        try:
            return int(val)
        except ValueError:
            pass
    return default
And in client/main.py:
python
from .config import IDLE_CLOSE_MINUTES as IDLE_DEFAULT

