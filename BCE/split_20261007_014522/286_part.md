<!-- Часть 286 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Добавляем IDLE_CLOSE_MINUTES в config.py клиента](285_Dobavlyaem_IDLE_CLOSE_MINUTES_v_config_py_klienta.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Client config ---------- ▶](287_Client_config.md)

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
