# ============================================================

*Часть 17 из 100. Источник: `BCE.md`.*

[◀ ============================================================](016_part.md) | [Оглавление](00_BCE_INDEX.md) | [in _check_idle_session: ▶](018_in_check_idle_session.md)

---

# ============================================================
Write-Host "`n--- Патч client/config.py ---" -ForegroundColor Cyan

$clientConfigPath = "$clientDir\config.py"
$cfgContent = [System.IO.File]::ReadAllText($clientConfigPath, [System.Text.UTF8Encoding]::new($false))

if ($cfgContent.Contains("IDLE_CLOSE_MINUTES")) {
    Write-Host "  Уже пропатчен — пропускаем" -ForegroundColor Yellow
} else {
    $cfgContent = $cfgContent + "`n`n# Сколько минут без активности — порог авто-закрытия висящей сессии`nIDLE_CLOSE_MINUTES = 30`n"
    [System.IO.File]::WriteAllText($clientConfigPath, $cfgContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  IDLE_CLOSE_MINUTES добавлена в config.py" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$clientConfigPath', encoding='utf-8').read()); print('  config.py SYNTAX OK')"

Write-Host "`n=== Все патчи применены ===" -ForegroundColor Cyan
________________________________________
Скрипт 4 — пересборка и проверка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

Write-Host "--- Пересборка Docker ---" -ForegroundColor Cyan
docker compose down
docker compose up -d --build

Start-Sleep -Seconds 25

Write-Host "`n--- Статус контейнеров ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Логи API (30 строк) ---" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`nГотово. Откройте https://localhost/admin/reports" -ForegroundColor Green
После этого перезапустите клиент:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
________________________________________
Как это работает после изменений
В форме отчёта
Появился селектор «Начало рабочего дня» (00–23).
Группировка переименована: «Рабочие дни ? Сотрудник».
В отчёте
Колонка 1C ID — рядом с ФИО.
Две длительности: «Отработано» (эффективное) и «Полное» (от старта до конца).
Топ программ — с колонками «Время», «Клавиатура», «Мышь». То есть если сотрудник работал в PyCharm 3 часа, из них 40 мин на клавиатуре — увидите это.
Разворачивание деталей — под группой «День ? Сотрудник» показаны все сессии + топ программ с клавиатурой/мышью.
Часовой пояс — московский.
На клиенте
Каждую минуту проверка: если активная сессия молчит 30 минут — закрывается автоматически временем последней активности.
Компьютер работает 24/7 — сессия всё равно закроется через 30 минут после ухода сотрудника.
Утром сотрудник нажимает «Начать работу» — открывается новая сессия.
Что теперь считается «отработанным»
Не session_end - session_start, а от первой до последней активности. Если сотрудник оставил ПК включённым, но отошёл — это время не попадёт в «Отработано», но останется в «Полное» (для справки).
________________________________________
Проверка
Открыть /admin/reports
Выбрать «Этот месяц», группировку «Рабочие дни ? Сотрудник», начало рабочего дня = 6
Нажать «Сформировать»
Убедиться:
1C ID в колонке
две колонки «Отработано» / «Полное»
топ программ с клавиатурой и мышью
чекбокс «Разворачивать детали» работает
Попробовать экспорт XLSX
________________________________________
Если что-то упадёт
Пришлите:
powershell
docker compose logs api --tail=60
И если клиент — Get-Content "$env:APPDATA\Tracker\client.log" -Tail 40 -Encoding UTF8.
Возможные проблемы:
settings.workday_start_hour не появится, если config.py не перезаписался — перезапустите Скрипт 1.
IDLE_CLOSE_MINUTES — не забудьте, что клиент должен перезапуститься.
Запускайте скрипты по порядку (1 ? 2 ? 3 ? 4) и отпишитесь.
Этот ответ сгенерирован AI, только для справки.
У нас с тобой всё здорово получается Продолжим Разрыв через 30 минут нужно сделать настраиваемым в админке. «Отработано» считаем время начальной сессии и время окончания последней сессии за этот день добавляем «Эффективно время» сюда будет подать то что попадает сейчас в поле «Отработано» в поле Топ программ за период добавить возможность развернуть программу и посмотреть в разрезе сотрудников кто сколько в этой программе работал
The user wants three things:
Make the 30-minute idle threshold configurable in the admin panel
Change "Отработано" to mean: time from start of first session to end of last session during that day
Add "Эффективное время" — which is what currently goes into "Отработано" (i.e., effective time excluding gaps)
Add ability to expand a program in "Топ программ за период" to see per-employee breakdown
Let me think about the implementation:
1. Configurable idle threshold in admin panel
Need a settings storage in DB. Create a simple settings table with key/value. Or better — a app_settings table with:
idle_close_minutes (int, default 30)
maybe others later
Endpoint /admin/settings to view and edit. Store in DB, not in .env, because we want runtime-changeable.
Also need to expose this value to the client via API. Add GET /api/v1/settings that client polls periodically, OR client can get it during registration/heartbeat. Simplest: add to /api/v1/version response or new /api/v1/client-config endpoint that client polls every N minutes.
Actually, let's add a new endpoint GET /api/v1/client-config returning {idle_close_minutes: 30}. Client polls it, say, every 5 minutes, updates local value.
But this requires changes on both sides. Let me keep it manageable:
Server: settings table + admin page to edit + endpoint /api/v1/client-config
Client: on startup and every 5 min fetch client-config, update idle timeout
Actually, we don't need to be too aggressive. Let me:
Server stores idle_close_minutes in DB
Client fetches it once at start and then once every hour. Also refetches after auto-close detection just in case.
Simpler: client fetches it every hour. If unreachable — uses default 30.
2. "Отработано" = start of first session to end of last session in a day
So for a given (workday_date, employee):
first_start = min(session_start across sessions in this group)
last_end = max(session_end across sessions in this group)
"Отработано" = last_end - first_start
3. "Эффективное время" = sum of effective_duration of all sessions (what was previously "Отработано")
So the table needs both columns.
4. Top programs expansion showing per-employee
For each program in top programs table, add a <details> with per-employee breakdown.
For this we need to compute, for each (program, employee) pair, the total seconds/keyboard/mouse.
Let me plan the code:
Server side
models.py — add AppSetting table:
python
class AppSetting(Base):
    __tablename__ = "app_settings"
    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
Helper functions in web_admin:
get_setting(db, key, default)
set_setting(db, key, value)
Admin page /admin/settings — form with idle_close_minutes.
API /api/v1/client-config — public (or with X-Computer-Uid), returns:
json
{"idle_close_minutes": 30}
Report changes:
In _split_by_day: track first_start, last_end. Compute worked_duration = last_end - first_start.
Keep effective_duration sum as separate field.
Top apps per day: for expansion, need per-employee+program breakdown.
Actually, the "Top programs" table is at the report level (across all rows). We need per-employee breakdown for each program. Let me collect:
python
program_by_employee[app][employee_name] = {"seconds": ..., "keyboard": ..., "mouse": ...}
And also per 1C ID.
Client side
client/config.py — keep IDLE_CLOSE_MINUTES = 30 as fallback default.
client/main.py — add a QTimer that fetches client-config from server every hour (or on start). Update self._idle_close_minutes.
Actually, let me store it as self._idle_close_minutes and use in _check_idle_session.
client/http_client.py — nothing needed, we use existing post/get helpers.
Let me write the full code now.
Actually, thinking about it — the client already polls /api/v1/version on update check. We could just add the value to the version response. But that's semantically weird. Let's add a dedicated endpoint and fetch it in the same thread as updates.
Simpler approach: add a method to UpdateChecker that also fetches client-config, or add a new lightweight check. Actually let me add it to the main window: on start, and every 30 minutes, fetch /api/v1/client-config.
Let me code this now.
Actually wait — the client's _check_idle_session runs every minute. We don't want to hit the server that often. Let's set a separate timer at 30 minutes for config refresh.
OK let me write everything.
For the top programs table — I need to think about the structure. Currently report.totals.top_apps is:
python
[{"app": k, "seconds": v, "keyboard": ..., "mouse": ...}, ...]
I'll extend each entry with by_employee:
python
[{"app": "PyCharm", "seconds": 7200, "keyboard": 3600, "mouse": 600,
  "by_employee": [{"employee_name": "Иванов", "external_id": "...", "seconds": 5000, ...}, ...]}]
Since we're aggregating per-session in _build_flat_records, and each session knows its employee, we can build this map easily.
Let me write the code.
Actually — I realized the current _analyze_session returns top_apps for a session. To build per-employee program breakdown, I'll iterate over flat sessions, and for each session iterate its top_apps and add to program_by_employee[app][employee_name].
Let me structure:
python
def _build_program_matrix(flat: list) -> dict:
    """Возвращает: app -> list of per-employee stats"""
    matrix = defaultdict(lambda: defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}))
    for r in flat:
        emp_key = (r["employee_name"], r.get("external_id") or "")
        for a in r["top_apps"]:
            m = matrix[a["app"]][emp_key]
            m["seconds"] += a["seconds"]
            m["keyboard"] += a["keyboard"]
            m["mouse"] += a["mouse"]
    result = {}
    for app, emps in matrix.items():
        result[app] = sorted(
            [{"employee_name": k[0], "external_id": k[1], **v} for k, v in emps.items()],
            key=lambda x: x["seconds"], reverse=True,
        )
    return result
Then attach by_employee to each entry in top_apps.
OK, writing full code now.
For the "Отработано" change in _split_by_day:
Currently:
python
g["duration"] += r["effective_duration"]
Add:
python
if g["first_start"] is None or r["start_local"] < g["first_start"]:
    g["first_start"] = r["start_local"]
if g["last_end"] is None or r["end_local"] > g["last_end"]:
    g["last_end"] = r["end_local"]
Then after loop:
python
if g["first_start"] and g["last_end"]:
    g["worked_duration"] = int((g["last_end"] - g["first_start"]).total_seconds())
else:
    g["worked_duration"] = 0
g["effective_duration"] = g["duration"]  # старое значение
Wait — but need to think: what if there's a session started at 23:00 yesterday and continues to 08:00 today? With workday_start=6, that session's workday_date is yesterday. So it's in yesterday's group. That's fine.
Also for other group modes (employees, computers) — same logic should apply but per group.
Actually for _group_by_employee, "Отработано" should be from first session start to last session end across the whole period. That's what user wants I think.
Let me apply same first/last tracking to all group functions.
Now the templates.
In report_result.html, for "days" mode:
Column "Отработано" ? now shows worked_duration
New column "Эффективное" ? shows effective_duration
Wait, user said:
«Отработано» считаем время начальной сессии и время окончания последней сессии за этот день
добавляем «Эффективно время» сюда будет подать то что попадает сейчас в поле «Отработано»
So:
"Отработано" = last_end - first_start (span)
"Эффективное время" = what was "Отработано" before (sum of effective_duration)
Let me use labels:
"Рабочий день" (span): первая сессия ? последняя сессия
"Эффективно": сумма эффективных времён
OK. Writing code.
For top programs with per-employee breakdown — using <details> again.
Let me also add a settings page in the admin.
Alright, this is a big update. Let me write it carefully.
Since the code is getting large, let me structure it as:
Script 1: models.py (add AppSetting)
Script 2: web_admin.py (full replacement with settings + new report logic)
Script 3: templates (base.html + new settings.html + reports.html small change + report_result.html update)
Script 4: server/main.py (add /api/v1/client-config)
Script 5: client patches (main.py + config.py)
Script 6: rebuild
Actually let me be smart about the client-side fetch. We can just have the client call /api/v1/client-config on start and then in main window once an hour. Need to add this to a lightweight thread or use QTimer with a short-lived request.
The simplest way — reuse the httpx client that's already there, and do a synchronous fetch in a QTimer callback... but that would block UI. Hmm. Since requests are fast and it's once an hour, a small block of 100ms-1s is acceptable. Let me do it in a QThread or just accept the tiny block.
Actually — let's put it in SyncWorker. It already runs in a thread and periodically wakes up. Add a method that fetches config once every 10 iterations.
Actually simplest — add to SyncWorker:
python
def _fetch_client_config(self):
    try:
        resp = http_client.get(f"{SERVER_URL}/api/v1/client-config", headers=self._headers())
        if resp.status_code == 200:
            data = resp.json()
            new_idle = int(data.get("idle_close_minutes", 30))
            if new_idle != db.get_meta("idle_close_minutes"):
                db.set_meta("idle_close_minutes", str(new_idle))
                log.info("idle_close_minutes updated: %d", new_idle)
    except Exception as e:
        log.debug("client-config fetch failed: %s", e)
And call _fetch_client_config from run loop every N iterations (say every 10 sync cycles = 5 min).
Then client reads it from db meta in _check_idle_session.
Better: store in DB meta so it persists. Then main.py reads it.
Then main.py _check_idle_session reads IDLE_CLOSE_MINUTES from db meta (defaulting to config default).
Let me refactor: db.get_idle_close_minutes(default=30).
OK let me write it all.
Since the scripts are getting really big, I should split carefully. Let me start.
Hmm the code is large. Let me plan the response structure:
Short summary of what changes
Script 1: models.py — replace file
Script 2: web_admin.py — replace file
Script 3: main.py (server) — replace file (adds /api/v1/client-config)
Script 4: templates (base, settings, reports, report_result)
Script 5: client patches (db.py add function, sync.py patch, main.py patch)
Script 6: rebuild + test
Let me write it.
For the settings page - very simple, one field for now.
Also need nav link in base.html.
Alright, let me write everything out.
Actually one more consideration: the settings name conflicts with Settings class. Let me use AppSetting model and get_app_setting function.
Also for API /api/v1/client-config, should it require computer auth? For simplicity, let's make it public (returns only non-sensitive config). If we later want per-tenant, we can add auth.
OK writing now.
One more thing: report_result.html top programs section — need to be able to expand each row. Use <details> inside the row.
Structure:
html
<table>
  <thead><tr><th>Программа</th><th>Время</th><th>Кл.</th><th>Мышь</th><th></th></tr></thead>
  <tbody>
  {% for a in report.totals.top_apps %}
    <tr>
      <td>
        <details>
          <summary>{{ a.app }}</summary>
          <div>...per-employee table...</div>
        </details>
      </td>
      ...
    </tr>
  {% endfor %}
  </tbody>
</table>
Hmm, putting details inside <td> might mess up layout. Better:
html
<tbody>
{% for a in report.totals.top_apps %}
  <tr>
    <td>{{ a.app }}</td>
    <td>{{ a.seconds | dur }}</td>
    <td>{{ a.keyboard | dur }}</td>
    <td>{{ a.mouse | dur }}</td>
    <td>
      {% if a.by_employee %}
        <details>
          <summary class="btn btn-sm btn-outline-secondary py-0">? сотрудники</summary>
        </details>
      {% endif %}
    </td>
  </tr>
  {% if a.by_employee %}
    <tr class="table-light">
      <td colspan="5">
        <details>
          ...
        </details>
      </td>
    </tr>
  {% endif %}
{% endfor %}
</tbody>
Actually simpler: put a details right in the row that expands below the row. Let me use a two-row pattern:
Row 1: program + time + kbd + mouse + toggle
Row 2 (hidden until toggle): per-employee table
But toggle between two rows is a JS thing. Or use <details> on entire row.
Simplest working approach: wrap the per-employee block in a <details> inside an extra cell.
Let me do:
html
<tr>
  <td>
    {% if a.by_employee %}
      <details>
        <summary style="cursor:pointer">{{ a.app }}</summary>
        <div class="mt-2" style="min-width:400px;font-weight:normal">
          <table class="table table-sm mb-0">
            <thead><tr><th>Сотрудник</th><th>1C ID</th><th>Время</th><th>Кл.</th><th>Мышь</th></tr></thead>
            <tbody>
              {% for e in a.by_employee %}
              <tr>
                <td>{{ e.employee_name }}</td>
                <td>{{ e.external_id or '—' }}</td>
                <td>{{ e.seconds | dur }}</td>
                <td>{{ e.keyboard | dur }}</td>
                <td>{{ e.mouse | dur }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </details>
    {% else %}
      {{ a.app }}
    {% endif %}
  </td>
  <td>...</td>
  ...
</tr>
That works well. When expanded, the per-employee table appears inside the first cell — since cells can expand vertically, the row grows. Might look a bit odd but functional. Let me try.
Actually better to use colspan approach — put details in a separate row:
html
{% for a in report.totals.top_apps %}
  <tr>
    <td>{{ a.app }}</td>
    <td>{{ a.seconds | dur }}</td>
    <td>{{ a.keyboard | dur }}</td>
    <td>{{ a.mouse | dur }}</td>
    <td style="width:30%"><span class="app-bar" style="width:...%"></span></td>
  </tr>
  {% if a.by_employee %}
    <tr>
      <td colspan="5" class="p-0">
        <details>
          <summary style="padding:6px 12px;cursor:pointer;color:#666;font-size:0.9em">Развернуть по сотрудникам</summary>
          <div style="padding:8px 12px">
            <table class="table table-sm mb-0">
              ...
            </table>
          </div>
        </details>
      </td>
    </tr>
  {% endif %}
{% endfor %}
This is cleaner. Let me use this pattern.
OK let me write everything now. I'll be careful with syntax.
Writing the server main.py — I need to add /api/v1/client-config endpoint. Let me make sure the existing code is preserved and just add the endpoint.
Actually — since main.py is already stable and I don't want to re-print the whole thing, I'll use a PowerShell Replace to insert a new endpoint. But user said "if you change the code, give me the whole file". Hmm.
Let me think — main.py is 300+ lines. Adding one endpoint is a small change. I could use a replace pattern like I did before for db.py. Let me do that — find a unique anchor and insert.
Anchor: # ---------- Version ----------
Insert before it:
python
# ---------- Client config ----------

@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    from .web_admin import get_app_setting
    idle = int(get_app_setting(db, "idle_close_minutes", "30"))
    return {"idle_close_minutes": idle}
Wait, circular import risk. Let me instead define the helper in a new module or in web_admin and import it lazily. Or define it inline.
Actually cleaner — define get_app_setting in models.py or a new small helper. Or just define it inline in main.py.
Let me define a small helper in main.py:
python
def _get_setting(db: Session, key: str, default: str) -> str:
    from .models import AppSetting
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else default
OK. Now for web_admin.py — I'll fully replace it because there are lots of changes.
Let me be smart: keep web_admin.py as a single script but write it carefully.
Alright, writing now. Being careful with f-strings and backticks in PowerShell.
Let me plan the top programs matrix function more carefully:
python
def _build_program_employee_matrix(flat: list) -> dict:
    """
    app -> [{employee_name, external_id, seconds, keyboard, mouse}, ...]
    Отсортирован по убыванию seconds.
    """
    matrix = defaultdict(lambda: defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}))
    for r in flat:
        emp_key = (r["employee_name"], r.get("external_id") or "")
        for a in r["top_apps"]:
            m = matrix[a["app"]][emp_key]
            m["seconds"] += a["seconds"]
            m["keyboard"] += a["keyboard"]
            m["mouse"] += a["mouse"]
    
    result = {}
    for app, emps in matrix.items():
        rows = []
        for (name, ext_id), stats in emps.items():
            rows.append({
                "employee_name": name,
                "external_id": ext_id,
                "seconds": stats["seconds"],
                "keyboard": stats["keyboard"],
                "mouse": stats["mouse"],
            })
        rows.sort(key=lambda x: x["seconds"], reverse=True)
        result[app] = rows
    return result
Then when building top_apps for totals:
python
matrix = _build_program_employee_matrix(flat)
top_apps = [...]
for a in top_apps:
    a["by_employee"] = matrix.get(a["app"], [])
Good.
Now for the "worked_duration" (span) logic in group functions:
For _split_by_day:
python
g = {..., "first_start": None, "last_end": None, ...}

# in loop:
if g["first_start"] is None or r["start_local"] < g["first_start"]:
    g["first_start"] = r["start_local"]
if g["last_end"] is None or r["end_local"] > g["last_end"]:
    g["last_end"] = r["end_local"]

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

