# === 1. Функция _build_pivot_data ===

*Часть 92 из 100. Источник: `BCE.md`.*

[◀ ============================================================](091_part.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](093_Proverka_sintaksisa.md)

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

# === 2. Endpoint /admin/api/pivot-data ===
new_endpoint = '''@router.post("/api/pivot-data")
def pivot_data(
    request: Request,
    employee_ids: List[str] = Form(default=[]),
    department_ids: List[str] = Form(default=[]),
    computer_ids: List[str] = Form(default=[]),
    date_from: str = Form(...),
    date_to: str = Form(...),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    """Возвращает плоские строки для pivot-таблицы (JSON)."""
    try:
        d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(400, f"Неверный формат даты: {e}")
    if d_to < d_from:
        raise HTTPException(400, "date_to < date_from")
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    emp_ids = [int(x) for x in employee_ids if x and x.isdigit()] or None
    dep_ids = [int(x) for x in department_ids if x and x.isdigit()] or None
    comp_ids = [int(x) for x in computer_ids if x and x.isdigit()] or None
    rows = _build_pivot_data(db, emp_ids, dep_ids, comp_ids, d_from, d_to,
                              tz, cfg["workday_start_hour"])
    return {
        "rows": rows,
        "total": len(rows),
        "date_from": date_from,
        "date_to": date_to,
    }


'''

anchor2 = '@router.post("/reports/generate")'
if anchor2 not in content:
    print("ERROR: не найден /reports/generate")
    raise SystemExit(1)
content = content.replace(anchor2, new_endpoint + anchor2, 1)

# === 3. Route /admin/reports/pivot ===
new_route = '''@router.get("/reports/pivot", response_class=HTMLResponse)
def reports_pivot_page(request: Request, db: Session = Depends(get_db),
                        _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    employees = (db.query(Employee)
                 .filter(Employee.fired_at.is_(None))
                 .order_by(Employee.last_name, Employee.first_name)
                 .all())
    departments = (db.query(Department)
                   .filter(Department.is_active == True)
                   .order_by(Department.name)
                   .all())
    computers = (db.query(Computer)
                 .filter(Computer.is_active == True)
                 .order_by(Computer.hostname)
                 .all())
    emp_dept_map = {e.id: e.department_id for e in employees}
    return templates.TemplateResponse("reports_pivot.html", {
        "request": request,
        "employees": employees,
        "departments": departments,
        "computers": computers,
        "emp_dept_map": emp_dept_map,
        "admin": request.session.get("admin"),
        "cfg": cfg,
        "today": date.today().isoformat(),
    })


'''

anchor3 = '@router.get("/reports", response_class=HTMLResponse)'
if anchor3 not in content:
    print("ERROR: не найден /reports")
    raise SystemExit(1)
content = content.replace(anchor3, new_route + anchor3, 1)

PATH.write_text(content, encoding="utf-8")

# Проверка синтаксиса
try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# Проверки
for m in ["def _build_pivot_data", '"/api/pivot-data"', '"/reports/pivot"']:
    print(f" {'OK' if m in content else 'MISS'}: {m}")
Now the template. Let me design it:
html
{% extends "base.html" %}
{% block title %}Сводная таблица{% endblock %}
{% block content %}
<h3 class="mb-3">Сводная таблица (Pivot)</h3>

<div class="card mb-3">
  <div class="card-body">
    <div class="row g-2 align-items-end">
      <div class="col-md-3">
        <label class="form-label small mb-1">Период: с</label>
        <input type="date" class="form-control form-control-sm" id="pivot_date_from" value="{{ today }}">
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">по</label>
        <input type="date" class="form-control form-control-sm" id="pivot_date_to" value="{{ today }}">
      </div>
      <div class="col-md-2">
        <button class="btn btn-sm btn-outline-secondary w-100" onclick="setPivotPeriod(0)">Сегодня</button>
      </div>
      <div class="col-md-2">
        <button class="btn btn-sm btn-outline-secondary w-100" onclick="setPivotPeriod(1)">Вчера</button>
      </div>
      <div class="col-md-2">
        <button class="btn btn-sm btn-outline-secondary w-100" onclick="setPivotPeriod(30)">30 дней</button>
      </div>
    </div>
    
    <div class="row g-2 mt-2">
      <div class="col-md-3">
        <label class="form-label small mb-1">Отделы (Ctrl+клик)</label>
        <select id="pivot_depts" class="form-select form-select-sm" multiple size="4">
          {% for d in departments %}
          <option value="{{ d.id }}">{{ d.name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">Сотрудники</label>
        <select id="pivot_employees" class="form-select form-select-sm" multiple size="4">
          {% for e in employees %}
          <option value="{{ e.id }}" data-dept="{{ e.department_id or '' }}">{{ e.full_name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">Компьютеры</label>
        <select id="pivot_computers" class="form-select form-select-sm" multiple size="4">
          {% for c in computers %}
          <option value="{{ c.id }}">{{ c.hostname or c.computer_uid[:14] }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3 d-flex align-items-end">
        <button class="btn btn-primary w-100" onclick="loadPivotData()">Загрузить данные</button>
      </div>
    </div>
    
    <div id="pivot_status" class="small text-muted mt-2"></div>
  </div>
</div>

<div class="card">
  <div class="card-body">
    <div id="pivot_output"></div>
  </div>
</div>

{# ---- PivotTable.js via CDN ---- #}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/themes/base/jquery-ui.min.css">
<script src="https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/dist/jquery-ui.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.ru.min.js"></script>

<script>
// Форматирование секунд в HH:MM:SS
function fmtDuration(seconds) {
  seconds = Math.round(seconds || 0);
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}

// Регистрируем кастомный агрегатор "Сумма (HH:MM:SS)"
if (window.$.pivotUtilities && $.pivotUtilities.aggregators) {
  // Кастомный агрегатор, который возвращает объект {seconds, formatted}
  $.pivotUtilities.aggregators["Сумма (время)"] = function(data, rowKey, colKey) {
    return {
      sum: 0,
      push: function(record) {
        for (var i = 0; i < rowKey.length; i++) {
          var v = record[rowKey[i]];
          if (typeof v === 'number') this.sum += v;
        }
      },
      value: function() { return this.sum; },
      format: function(x) { return fmtDuration(x); }
    };
  };
}

function getSelectedValues(id) {
  const sel = document.getElementById(id);
  return Array.from(sel.options).filter(o => o.selected).map(o => o.value);
}

function setPivotPeriod(daysAgo) {
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - daysAgo);
  const fmt = d => d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
  document.getElementById('pivot_date_from').value = fmt(from);
  document.getElementById('pivot_date_to').value = fmt(to);
}

async function loadPivotData() {
  const status = document.getElementById('pivot_status');
  status.textContent = 'Загрузка…';
  
  const formData = new FormData();
  formData.append('date_from', document.getElementById('pivot_date_from').value);
  formData.append('date_to', document.getElementById('pivot_date_to').value);
  getSelectedValues('pivot_depts').forEach(v => formData.append('department_ids', v));
  getSelectedValues('pivot_employees').forEach(v => formData.append('employee_ids', v));
  getSelectedValues('pivot_computers').forEach(v => formData.append('computer_ids', v));
  
  try {
    const resp = await fetch('/admin/api/pivot-data', { method: 'POST', body: formData });
    if (!resp.ok) {
      status.textContent = 'Ошибка: ' + resp.status;
      return;
    }
    const data = await resp.json();
    status.textContent = 'Загружено строк: ' + data.total;
    
    if (data.rows.length === 0) {
      document.getElementById('pivot_output').innerHTML = '<div class="text-muted p-3">Нет данных за выбранный период</div>';
      return;
    }
    
    $('#pivot_output').pivotUI(data.rows, {
      rows: ['department', 'employee'],
      cols: ['month_name'],
      aggregatorName: 'Sum',
      vals: ['worked_span', 'worked_union', 'effective', 'intensive', 'break_dur'],
      rendererName: 'Table',
      locale: 'ru',
      unusedAttrsVertical: false,
      renderers: $.extend(
        $.pivotUtilities.renderers,
        $.pivotUtilities.export_renderers || {}
      )
    });
  } catch (e) {
    status.textContent = 'Ошибка: ' + e.message;
  }
}

// Автозагрузка при открытии
document.addEventListener('DOMContentLoaded', () => {
  setPivotPeriod(30);
  loadPivotData();
});

// Синхронизация отделов ? сотрудники
document.getElementById('pivot_depts').addEventListener('change', function() {
  const deps = new Set(Array.from(this.selectedOptions).map(o => o.value));
  const empSel = document.getElementById('pivot_employees');
  Array.from(empSel.options).forEach(o => {
    const d = String(o.dataset.dept || '');
    const show = deps.size === 0 || (d && deps.has(d));
    o.hidden = !show;
    if (!show) o.selected = false;
  });
});
</script>

<style>
.pvtUi { font-size: 13px; }
.pvtAxisContainer, .pvtVals { background: #f8f9fa; border-radius: 4px; }
table.pvtTable { font-size: 12px; }
table.pvtTable tbody tr th, table.pvtTable thead tr th { padding: 4px 6px; }
</style>
{% endblock %}
Hmm — the pivottable.ru.min.js — let me check if that exists. Actually I think locales are separate files. Let me check... pivot.ru.js might not exist. Let me remove locale: 'ru' for now.
Actually pivottable has i18n. Let me check — from memory, they have separate files for locales in dist/. Let me just skip locale.
OK let me finalize.
Actually, a concern: pivottable 2.23.0 min is quite big. And jQuery UI. Total maybe 500KB. Loading via CDN is fine for now.
But wait — the CDN URL might not work. Let me use a more reliable one or use unpkg:
https://unpkg.com/jquery@3.7.1/dist/jquery.min.js
https://unpkg.com/jquery-ui@1.13.2/dist/jquery-ui.min.js
https://unpkg.com/pivottable@2.23.0/dist/pivot.min.js
Both jsdelivr and unpkg should work. Let me use jsdelivr.
OK let me write the response.
Structure:
План веб-pivot (короткий)
Скрипт 1 — backend patcher (function + endpoint + route)
Скрипт 2 — template reports_pivot.html
Скрипт 3 — nav link in base.html
Rebuild + test
Let me write.
Actually — I need to double-check that List is imported in web_admin.py. Let me check... From earlier context: from typing import Optional, List — yes it's there.
And date is imported from datetime — yes.
And RU_MONTHS is defined — yes.
OK writing.
One more thing: the pivottable min.css needs to be included. Yes.
Alright, let me write the response. Given the length, I'll split into this message being the plan + backend, and next message the template.
Actually — let me just do everything in one message. If it's too long, so be it.
No wait — the response could be 800+ lines with all scripts. Let me split:
Message 1 (this): Plan + backend patcher + instructions to test endpoint
Message 2 (next): Template + nav + rebuild
OK, first message.
Hmm, but user might be impatient. Let me do both in one message but be compact.
Let me write the backend first (most important), then template.
Final decision: give both in one message. Long but complete.
Let me write.
For chat length warning: I'll add a short note at top.
Let me go.
Отлично, делаем веб-pivot. По объёму — это 2–3 итерации: сначала бэкенд + API + страница, потом шаблон с PivotTable.js, потом пресеты и полировка. Начинаем с бэкенда, чтобы убедиться, что API отдаёт правильные данные, а потом уже рисовать UI.
Про длину чата: сейчас около 70%. Хватит на 1–2 крупные итерации. Если почувствую, что близко к лимиту — сразу предупрежу и сделаю handoff. Ты тоже, если увидишь, что чат тормозит, скажи.
________________________________________
План веб-pivot
Идея: страница /admin/reports/pivot — с фильтрами (период, отделы, сотрудники, компьютеры) и интерактивной сводной таблицей на PivotTable.js. Тянешь поля «Сотрудник», «Отдел», «Месяц», «День недели» — получаешь ту же логику, что в Excel-сводной.
Что нужно:
Backend — функция _build_pivot_data, которая выдаёт плоские строки (одна строка = один сотрудник за день) в JSON.
API-эндпоинт /admin/api/pivot-data — принимает фильтры, возвращает JSON.
Роут /admin/reports/pivot — отдаёт страницу с фильтрами.
Шаблон reports_pivot.html — с PivotTable.js.
Ссылка в меню.
________________________________________
Скрипт 1 — Backend: функция, API, роут
Что делает:
Добавляет _build_pivot_data(db, filters) — возвращает плоский список: одна строка = (сотрудник, рабочий день), с полями date, year, month_num, month_name, day, weekday, employee, external_id, department, computers, sessions_count, worked_span, worked_union, intensive, effective, break_dur, pause_button.
Добавляет POST /admin/api/pivot-data — принимает те же фильтры, что и отчёты, возвращает {rows, total, date_from, date_to}.
Добавляет GET /admin/reports/pivot — отдаёт страницу (пока пустую, шаблон сделаем следующим шагом).
Запускай:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$patcher = @'
import ast
from pathlib import Path

PATH = Path(r"D:\tracker\server\web_admin.py")
content = PATH.read_text(encoding="utf-8")

if "def _build_pivot_data" in content:
    print("SKIP: pivot уже есть")
    raise SystemExit(0)

# ============================================================
# 1. Функция _build_pivot_data
# ============================================================
new_func = """def _build_pivot_data(db, employee_ids, department_ids, computer_ids,
                       date_from, date_to, tz, workday_start_hour):
    \"\"\"
    Строит \"плоские\" строки для pivot-таблицы.
    Одна строка = один сотрудник за один рабочий день.
    Поля:
      date_iso, date, year, month_num, month_name, day, weekday,
      weekday_full, is_weekend,
      employee_id, employee, external_id, department,
      computers, computer_count, sessions_count,
      worked_span, worked_union, intensive, effective,
      break_dur, pause_button
    Метрики в секундах — Excel/PivotTable сами отформатируют.
    \"\"\"
    flat = _build_flat_records(db, employee_ids, department_ids, computer_ids,
                                date_from, date_to, tz, workday_start_hour)
    if not flat:
        return []

    WEEKDAY_SHORT = [\"Пн\", \"Вт\", \"Ср\", \"Чт\", \"Пт\", \"Сб\", \"Вс\"]
    WEEKDAY_FULL = [\"Понедельник\", \"Вторник\", \"Среда\", \"Четверг\",
                    \"Пятница\", \"Суббота\", \"Воскресенье\"]

    groups = {}
    for r in flat:
        key = (r.get(\"employee_id\"), r[\"workday_date\"])
        groups.setdefault(key, []).append(r)

    rows = []
    for (emp_id, day), sessions in groups.items():
        first = sessions[0]
        d_start = min(s[\"start_local\"] for s in sessions)
        d_end = max(s[\"end_local\"] for s in sessions)
        span = max(0, int((d_end - d_start).total_seconds()))

        intervals = [(s[\"activity_start_local\"], s[\"activity_end_local\"])
                     for s in sessions]
        union = _union_duration(intervals)

        effective = sum(s.get(\"effective_duration\", 0) for s in sessions)
        intensive = sum(s.get(\"intensive_seconds\", 0) for s in sessions)
        pause_btn = sum(s.get(\"pause_seconds\", 0) for s in sessions)
        break_dur = pause_btn + max(0, span - union)

        computers = sorted({s.get(\"computer_name\") or \"—\" for s in sessions})

        rows.append({
            \"date_iso\": day.isoformat(),
            \"date\": day.strftime(\"%d.%m.%Y\"),
            \"year\": day.year,
            \"month_num\": day.month,
            \"month_name\": RU_MONTHS[day.month],
            \"day\": day.day,
            \"weekday\": WEEKDAY_SHORT[day.weekday()],
            \"weekday_full\": WEEKDAY_FULL[day.weekday()],
            \"is_weekend\": day.weekday() >= 5,
            \"employee_id\": emp_id or 0,
            \"employee\": first.get(\"employee_name\") or \"— не привязан —\",
            \"external_id\": first.get(\"external_id\") or \"\",
            \"department\": first.get(\"department_name\") or \"—\",
            \"computers\": \", \".join(computers),
            \"computer_count\": len(computers),
            \"sessions_count\": len(sessions),
            \"worked_span\": span,
            \"worked_union\": union,
            \"intensive\": intensive,
            \"effective\": effective,
            \"break_dur\": break_dur,
            \"pause_button\": pause_btn,
        })

    rows.sort(key=lambda x: (x[\"date_iso\"], x[\"employee\"]), reverse=True)
    return rows


"""

anchor = "def _build_report("
if anchor not in content:
    print("ERROR: не найден _build_report")
    raise SystemExit(1)
content = content.replace(anchor, new_func + anchor, 1)
print("OK: _build_pivot_data добавлена")

# ============================================================
# 2. Endpoint /admin/api/pivot-data
# ============================================================
new_endpoint = """@router.post(\"/api/pivot-data\")
def pivot_data(
    request: Request,
    employee_ids: List[str] = Form(default=[]),
    department_ids: List[str] = Form(default=[]),
    computer_ids: List[str] = Form(default=[]),
    date_from: str = Form(...),
    date_to: str = Form(...),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    \"\"\"Плоские строки для pivot-таблицы (JSON).\"\"\"
    try:
        d_from = datetime.strptime(date_from, \"%Y-%m-%d\").date()
        d_to = datetime.strptime(date_to, \"%Y-%m-%d\").date()
    except ValueError as e:
        raise HTTPException(400, f\"Неверный формат даты: {e}\")
    if d_to < d_from:
        raise HTTPException(400, \"date_to < date_from\")
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg[\"report_timezone\"])
    emp_ids = [int(x) for x in employee_ids if x and x.isdigit()] or None
    dep_ids = [int(x) for x in department_ids if x and x.isdigit()] or None
    comp_ids = [int(x) for x in computer_ids if x and x.isdigit()] or None
    rows = _build_pivot_data(db, emp_ids, dep_ids, comp_ids, d_from, d_to,
                              tz, cfg[\"workday_start_hour\"])
    return {
        \"rows\": rows,
        \"total\": len(rows),
        \"date_from\": date_from,
        \"date_to\": date_to,
    }


"""

anchor2 = "@router.post(\"/reports/generate\")"
if anchor2 not in content:
    print("ERROR: не найден /reports/generate")
    raise SystemExit(1)
content = content.replace(anchor2, new_endpoint + anchor2, 1)
print("OK: endpoint /api/pivot-data добавлен")

# ============================================================
# 3. Роут /admin/reports/pivot
# ============================================================
new_route = """@router.get(\"/reports/pivot\", response_class=HTMLResponse)
def reports_pivot_page(request: Request, db: Session = Depends(get_db),
                        _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    employees = (db.query(Employee)
                 .filter(Employee.fired_at.is_(None))
                 .order_by(Employee.last_name, Employee.first_name)
                 .all())
    departments = (db.query(Department)
                   .filter(Department.is_active == True)
                   .order_by(Department.name)
                   .all())
    computers = (db.query(Computer)
                 .filter(Computer.is_active == True)
                 .order_by(Computer.hostname)
                 .all())
    emp_dept_map = {e.id: e.department_id for e in employees}
    return templates.TemplateResponse(\"reports_pivot.html\", {
        \"request\": request,
        \"employees\": employees,
        \"departments\": departments,
        \"computers\": computers,
        \"emp_dept_map\": emp_dept_map,
        \"admin\": request.session.get(\"admin\"),
        \"cfg\": cfg,
        \"today\": date.today().isoformat(),
    })


"""

anchor3 = "@router.get(\"/reports\", response_class=HTMLResponse)"
if anchor3 not in content:
    print("ERROR: не найден /reports")
    raise SystemExit(1)
content = content.replace(anchor3, new_route + anchor3, 1)
print("OK: роут /reports/pivot добавлен")

PATH.write_text(content, encoding="utf-8")

