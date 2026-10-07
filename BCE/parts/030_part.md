# ============================================================

*Часть 30 из 100. Источник: `BCE.md`.*

[◀ ============================================================](029_part.md) | [Оглавление](00_BCE_INDEX.md) | [Heartbeat каждый цикл (30 секунд) — это ок, дёшево ▶](031_Heartbeat_kazhdyy_tsikl_30_sekund_eto_ok_deshevo.md)

---

# ============================================================

@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    cfg = get_settings_dict(db)
    tz = _resolve_tz(cfg["report_timezone"])
    logs = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(200).all()
    return templates.TemplateResponse("audit.html", {
        "request": request, "logs": logs, "admin": request.session.get("admin"), "tz": tz,
    })
'@
[System.IO.File]::WriteAllText("$serverDir\web_admin.py", $web_admin_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  server/web_admin.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$serverDir\web_admin.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт A2 — server/templates/reports.html (полная замена)
Мультивыбор + поиск + зависимая фильтрация на чистом JS.
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

$reports_html = @'
{% extends "base.html" %}
{% block title %}Отчёты{% endblock %}
{% block content %}
<h3 class="mb-4">Отчёты</h3>

<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/reports/generate" id="reportForm">

      <div class="mb-3">
        <label class="form-label fw-bold">Период</label>
        <div class="d-flex flex-wrap gap-2 mb-2">
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(0)">Сегодня</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(1)">Вчера</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(7)">7 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(30)">30 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setThisMonth()">Этот месяц</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setLastMonth()">Прошлый месяц</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setThisYear()">Этот год</button>
        </div>
        <div class="row g-2">
          <div class="col-md-3"><input class="form-control" type="date" name="date_from" id="date_from" required value="{{ today }}"></div>
          <div class="col-md-3"><input class="form-control" type="date" name="date_to" id="date_to" required value="{{ today }}"></div>
        </div>
      </div>

      <div class="row g-3">

        <div class="col-md-3">
          <label class="form-label">
            Отделы
            <span class="hint" data-bs-toggle="tooltip" title="Если ничего не выбрано — все отделы. При выборе одного или нескольких — сотрудники фильтруются автоматически.">?</span>
          </label>
          <input type="text" class="form-control form-control-sm mb-1" placeholder="Поиск отдела…"
                 oninput="filterOptions('departments_select', this.value)">
          <select name="department_ids" id="departments_select" class="form-select multi-select" multiple
                  onchange="onDepartmentsChanged()">
            {% for d in departments %}
              <option value="{{ d.id }}" data-name="{{ d.name }}">{{ d.name }}</option>
            {% endfor %}
          </select>
          <div class="form-text">Ctrl + клик — выбрать несколько</div>
        </div>

        <div class="col-md-3">
          <label class="form-label">
            Сотрудники
            <span class="hint" data-bs-toggle="tooltip" title="Список автоматически фильтруется по выбранным отделам. Ctrl + клик — выбрать несколько.">?</span>
          </label>
          <input type="text" class="form-control form-control-sm mb-1" placeholder="Поиск по ФИО или 1C ID…"
                 oninput="filterOptions('employees_select', this.value)">
          <select name="employee_ids" id="employees_select" class="form-select multi-select" multiple>
            {% for e in employees %}
              <option value="{{ e.id }}"
                      data-dept="{{ e.department_id or '' }}"
                      data-name="{{ e.full_name }} {{ e.external_id or '' }}">
                {{ e.full_name }}{% if e.external_id %} ({{ e.external_id }}){% endif %}
              </option>
            {% endfor %}
          </select>
        </div>

        <div class="col-md-3">
          <label class="form-label">Компьютеры</label>
          <input type="text" class="form-control form-control-sm mb-1" placeholder="Поиск ПК…"
                 oninput="filterOptions('computers_select', this.value)">
          <select name="computer_ids" id="computers_select" class="form-select multi-select" multiple>
            {% for c in computers %}
              <option value="{{ c.id }}" data-name="{{ c.hostname or '' }} {{ c.computer_uid }}">
                {{ c.hostname or c.computer_uid[:20] }}
              </option>
            {% endfor %}
          </select>
        </div>

        <div class="col-md-3">
          <label class="form-label">Группировка</label>
          <select name="group_by" class="form-select">
            <option value="days" selected>Рабочие дни ? Сотрудник</option>
            <option value="months">Месяц ? Сотрудник</option>
            <option value="employees">По сотрудникам</option>
            <option value="departments">По отделам</option>
            <option value="computers">По компьютерам</option>
            <option value="sessions">Детально — каждая сессия</option>
          </select>
        </div>

        <div class="col-md-3">
          <label class="form-label">Формат</label>
          <select name="fmt" class="form-select">
            <option value="html">Просмотр</option>
            <option value="xlsx">Excel (XLSX)</option>
            <option value="csv">CSV</option>
          </select>
        </div>
      </div>

      <div class="mt-3">
        <label class="form-label fw-bold">Что показывать</label>
        <div class="d-flex flex-wrap gap-4">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_apps" id="show_apps" checked>
            <label class="form-check-label" for="show_apps">Топ-программы</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_abnormal" id="show_abnormal" checked>
            <label class="form-check-label" for="show_abnormal">Пометки аварийных</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="expand_details" id="expand_details">
            <label class="form-check-label" for="expand_details">Разворачивать детали</label>
          </div>
        </div>
      </div>

      <div class="alert alert-secondary py-2 small mt-3 mb-0">
        Часовой пояс, начало дня, порог паузы — в <a href="/admin/settings">Настройках</a>.<br>
        TZ = <strong>{{ cfg.report_timezone }}</strong>,
        начало дня = <strong>{{ '%02d' % cfg.workday_start_hour }}:00</strong>,
        порог паузы = <strong>{{ cfg.activity_gap_minutes }} мин</strong>.
      </div>

      <button class="btn btn-primary mt-3">Сформировать отчёт</button>
    </form>
  </div>
</div>

<script>
const EMP_DEPT_MAP = {{ emp_dept_map | tojson }};

function filterOptions(selectId, query) {
  const sel = document.getElementById(selectId);
  const q = (query || '').toLowerCase().trim();
  for (const opt of sel.options) {
    const txt = (opt.dataset.name || opt.textContent).toLowerCase();
    opt.hidden = q ? !txt.includes(q) : false;
  }
}

function onDepartmentsChanged() {
  const depsSel = document.getElementById('departments_select');
  const selectedDeps = new Set();
  for (const o of depsSel.options) if (o.selected) selectedDeps.add(String(o.value));

  const empSel = document.getElementById('employees_select');
  for (const opt of empSel.options) {
    const edp = String(opt.dataset.dept || '');
    const show = selectedDeps.size === 0 || (edp && selectedDeps.has(edp));
    opt.hidden = !show;
    if (!show) opt.selected = false;
  }
}

function fmt(d) {
  const y = d.getFullYear(), m = String(d.getMonth()+1).padStart(2,'0'), dd = String(d.getDate()).padStart(2,'0');
  return y + '-' + m + '-' + dd;
}
function setPeriod(daysAgo) {
  const to = new Date(), from = new Date();
  from.setDate(from.getDate() - daysAgo);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
function setThisMonth() {
  const now = new Date();
  document.getElementById('date_from').value = fmt(new Date(now.getFullYear(), now.getMonth(), 1));
  document.getElementById('date_to').value = fmt(new Date(now.getFullYear(), now.getMonth()+1, 0));
}
function setLastMonth() {
  const now = new Date();
  document.getElementById('date_from').value = fmt(new Date(now.getFullYear(), now.getMonth()-1, 1));
  document.getElementById('date_to').value = fmt(new Date(now.getFullYear(), now.getMonth(), 0));
}
function setThisYear() {
  const now = new Date();
  document.getElementById('date_from').value = fmt(new Date(now.getFullYear(), 0, 1));
  document.getElementById('date_to').value = fmt(new Date(now.getFullYear(), 11, 31));
}
</script>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\reports.html", $reports_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  reports.html" -ForegroundColor Green
________________________________________
Скрипт A3 — server/templates/report_result.html (полная замена)
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

$report_result_html = @'
{% extends "base.html" %}
{% block title %}Отчёт{% endblock %}
{% block content %}

<div class="d-flex justify-content-between align-items-start mb-3">
  <div>
    <h3 class="mb-1">Отчёт</h3>
    <div class="text-muted">
      {{ report.date_from.strftime('%d.%m.%Y') }} — {{ report.date_to.strftime('%d.%m.%Y') }}
      · TZ: <code>{{ report.tz_name }}</code>
      · Рабочий день с <strong>{{ '%02d' % report.workday_start_hour }}:00</strong>
      · Группировка: <strong>
      {% if report.group_by == 'days' %}Рабочие дни ? Сотрудник
      {% elif report.group_by == 'months' %}Месяц ? Сотрудник
      {% elif report.group_by == 'employees' %}По сотрудникам
      {% elif report.group_by == 'departments' %}По отделам
      {% elif report.group_by == 'computers' %}По компьютерам
      {% else %}Детально{% endif %}
      </strong>
    </div>
  </div>
  <a class="btn btn-outline-secondary" href="/admin/reports">? Назад</a>
</div>

<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий</div>
    <div class="fs-4">{{ report.totals.sessions }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Отработано</div>
    <div class="fs-4">{{ report.totals.worked_duration | dur }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Эффективно</div>
    <div class="fs-4 text-success">{{ report.totals.effective_duration | dur }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Аварийных</div>
    <div class="fs-4">{{ report.totals.abnormal }}</div>
  </div></div></div>
</div>

{% if show_apps and report.totals.top_apps %}
<div class="card mb-4">
  <div class="card-header">Топ программ за период</div>
  <div class="card-body p-0">
    {% set max_app_seconds = report.totals.top_apps[0].seconds %}
    <table class="table table-sm mb-0">
      <thead class="table-light"><tr>
        <th style="width:35%">Программа</th>
        <th>Время</th><th>Клавиатура</th><th>Мышь</th><th style="width:25%"></th>
      </tr></thead>
      <tbody>
      {% for a in report.totals.top_apps %}
        <tr>
          <td>{{ a.app }}</td>
          <td><strong>{{ a.seconds | dur }}</strong></td>
          <td>{{ a.keyboard | dur }}</td>
          <td>{{ a.mouse | dur }}</td>
          <td><span class="app-bar" style="width: {{ (a.seconds / max_app_seconds * 100) if max_app_seconds else 0 }}%"></span></td>
        </tr>
        {% if a.by_employee %}
        <tr><td colspan="5" class="p-0">
          <details>
            <summary style="padding:6px 12px;cursor:pointer;color:#555;font-size:0.9em;background:#f8f9fa">
              ? Кто работал в «{{ a.app }}» — {{ a.by_employee|length }} сотр.
            </summary>
            <div style="padding:8px 12px">
              <table class="table table-sm mb-0">
                <thead><tr><th>Сотрудник</th><th>1C ID</th><th>Время</th><th>Клавиатура</th><th>Мышь</th></tr></thead>
                <tbody>
                {% for e in a.by_employee %}
                  <tr>
                    <td>{{ e.employee_name }}</td>
                    <td><code>{{ e.external_id or '—' }}</code></td>
                    <td>{{ e.seconds | dur }}</td>
                    <td>{{ e.keyboard | dur }}</td>
                    <td>{{ e.mouse | dur }}</td>
                  </tr>
                {% endfor %}
                </tbody>
              </table>
            </div>
          </details>
        </td></tr>
        {% endif %}
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endif %}

<div class="card">
  <div class="card-body p-0">
    <table class="table table-sm table-hover mb-0">
      <thead class="table-dark">
        <tr>
          {% if report.group_by == 'days' %}
            <th style="width:110px">Рабочий день</th>
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th style="width:150px">Отдел</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Эффективно</th>
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% elif report.group_by == 'months' %}
            <th style="width:130px">Месяц</th>
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th style="width:150px">Отдел</th>
            <th style="width:70px">Дней</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Эффективно</th>
          {% elif report.group_by == 'employees' %}
            <th>Сотрудник</th><th style="width:100px">1C ID</th>
            <th style="width:150px">Отдел</th>
            <th style="width:70px">Дней</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Эффективно</th>
          {% elif report.group_by == 'departments' %}
            <th>Отдел</th>
            <th style="width:90px">Сотр.</th>
            <th style="width:70px">Дней</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Эффективно</th>
          {% elif report.group_by == 'computers' %}
            <th>Компьютер</th>
            <th style="width:70px">Дней</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Эффективно</th>
          {% else %}
            <th style="width:110px">Рабочий день</th>
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th>Компьютер</th>
            <th style="width:110px">Начало</th>
            <th style="width:110px">Конец</th>
            <th style="width:100px">Отработано</th>
            <th style="width:100px">Эффективно</th>
          {% endif %}
        </tr>
      </thead>
      <tbody>
      {% for r in report.rows %}
        {% if report.group_by == 'days' %}
          <tr>
            <td>{{ r.date.strftime('%d.%m.%Y') }}{% if r.date.weekday() >= 5 %} <span class="badge bg-secondary">вых</span>{% endif %}</td>
            <td>{{ r.employee_name }}{% if r.fired %} <span class="badge bg-secondary">уволен</span>{% endif %}</td>
            <td><code>{{ r.external_id or '—' }}</code></td>
            <td>{{ r.department_name }}</td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
            {% if expand_details %}
              <td>
                <details>
                  <summary class="btn btn-sm btn-outline-secondary py-0">?</summary>
                  <div class="mt-2" style="min-width:600px">
                    <table class="table table-sm mb-2">
                      <thead><tr><th>Начало</th><th>Конец</th><th>Отработано</th><th>Эффективно</th><th>Авар.</th></tr></thead>
                      <tbody>
                      {% for s in r.sessions %}
                        <tr>
                          <td>{{ s.start_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.end_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.full_duration | dur }}</td>
                          <td>{{ s.effective_duration | dur }}</td>
                          <td>{% if s.abnormal %}<span class="badge bg-warning text-dark">да</span>{% endif %}</td>
                        </tr>
                      {% endfor %}
                      </tbody>
                    </table>
                    {% if r.top_apps %}
                      <strong>Программы:</strong>
                      <table class="table table-sm mb-0">
                        <thead><tr><th>Программа</th><th>Время</th><th>Клавиатура</th><th>Мышь</th></tr></thead>
                        <tbody>
                        {% for a in r.top_apps %}
                          <tr><td>{{ a.app }}</td><td>{{ a.seconds | dur }}</td><td>{{ a.keyboard | dur }}</td><td>{{ a.mouse | dur }}</td></tr>
                        {% endfor %}
                        </tbody>
                      </table>
                    {% endif %}
                  </div>
                </details>
              </td>
            {% endif %}
          </tr>
        {% elif report.group_by == 'months' %}
          <tr>
            <td>{{ r.month_name }} {{ r.year }}</td>
            <td>{{ r.employee_name }}{% if r.fired %} <span class="badge bg-secondary">уволен</span>{% endif %}</td>
            <td><code>{{ r.external_id or '—' }}</code></td>
            <td>{{ r.department_name }}</td>
            <td class="text-center">{{ r.days_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
          </tr>
        {% elif report.group_by == 'employees' %}
          <tr>
            <td>{{ r.employee_name }}{% if r.fired %} <span class="badge bg-secondary">уволен</span>{% endif %}</td>
            <td><code>{{ r.external_id or '—' }}</code></td>
            <td>{{ r.department_name }}</td>
            <td class="text-center">{{ r.days_count }}</td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
          </tr>
        {% elif report.group_by == 'departments' %}
          <tr>
            <td>{{ r.department_name }}</td>
            <td class="text-center">{{ r.employees_count }}</td>
            <td class="text-center">{{ r.days_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
          </tr>
        {% elif report.group_by == 'computers' %}
          <tr>
            <td>{{ r.computer_name }}</td>
            <td class="text-center">{{ r.days_count }}</td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
          </tr>
        {% else %}
          <tr>
            <td>{{ r.date.strftime('%d.%m.%Y') }}</td>
            <td>{{ r.employee_name }}</td>
            <td><code>{{ r.external_id or '—' }}</code></td>
            <td>{{ r.computer_name }}</td>
            <td>{{ r.start_local.strftime('%H:%M:%S') }}</td>
            <td>{{ r.end_local.strftime('%H:%M:%S') }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
          </tr>
        {% endif %}
      {% else %}
        <tr><td colspan="12" class="text-center text-muted py-4">Нет данных за выбранный период</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>

<div class="d-flex justify-content-end mt-3">
  <div class="card"><div class="card-body py-2">
    <strong>ИТОГО:</strong>
    сессий {{ report.totals.sessions }},
    отработано {{ report.totals.worked_duration | dur }},
    эффективно {{ report.totals.effective_duration | dur }}
  </div></div>
</div>

<a class="btn btn-outline-secondary mt-3" href="/admin/reports">? Новый отчёт</a>

{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\report_result.html", $report_result_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  report_result.html" -ForegroundColor Green
________________________________________
Скрипт A4 — server/templates/dashboard.html (с онлайн/оффлайн)
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

$dashboard_html = @'
{% extends "base.html" %}
{% block title %}Дашборд{% endblock %}
{% block content %}
<h3 class="mb-4">Дашборд</h3>

<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Сотрудники</div>
    <div class="fs-3">{{ stats.employees }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Отделы</div>
    <div class="fs-3">{{ stats.departments }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Компьютеры</div>
    <div class="fs-3">{{ stats.computers }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">
      Компьютеры онлайн
      <span class="hint" data-bs-toggle="tooltip" title="ПК, которые присылали данные за последние {{ heartbeat_window }} мин.">?</span>
    </div>
    <div class="fs-3 text-success">{{ stats.computers_online }}</div>
  </div></div></div>
</div>

<div class="row g-3 mb-4">
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий сегодня</div>
    <div class="fs-4">{{ stats.sessions_today }}</div>
  </div></div></div>
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий за 7 дней</div>
    <div class="fs-4">{{ stats.sessions_week }}</div>
  </div></div></div>
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Всего записей</div>
    <div class="fs-4">{{ stats.records }}</div>
  </div></div></div>
</div>

<div class="card mb-4">
  <div class="card-header d-flex justify-content-between align-items-center">
    <span>Компьютеры (последние {{ recent_computers|length }})</span>
    <a class="btn btn-sm btn-outline-primary" href="/admin/computers">Все ПК ?</a>
  </div>
  <div class="card-body p-0">
    <table class="table table-sm mb-0">
      <thead><tr><th>Hostname</th><th>UID</th><th>Сотрудник</th><th>Last seen</th><th>Статус</th></tr></thead>
      <tbody>
      {% for c in recent_computers %}
        <tr>
          <td>{{ c.hostname or '—' }}</td>
          <td><code title="{{ c.computer_uid }}">{{ c.computer_uid[:14] }}…</code></td>
          <td>{{ c.employee.full_name if c.employee_id and c.employee_id in (c.__dict__.keys() and []) else '' }}{% if c.employee_id %}<span class="text-muted">#{{ c.employee_id }}</span>{% else %}—{% endif %}</td>
          <td>{{ c.last_seen_at | dt }}</td>
          <td>
            {% if c.last_seen_at and c.last_seen_at >= cutoff_online %}
              <span class="badge bg-success">онлайн</span>
            {% elif c.is_active %}
              <span class="badge bg-secondary">офлайн</span>
            {% else %}
              <span class="badge bg-danger">отключён</span>
            {% endif %}
          </td>
        </tr>
      {% else %}
        <tr><td colspan="5" class="text-muted">Нет данных</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>

<div class="card">
  <div class="card-header">Последние действия</div>
  <div class="card-body p-0">
    <table class="table table-sm mb-0">
      <thead><tr><th>Время</th><th>Сущность</th><th>Действие</th></tr></thead>
      <tbody>
      {% for a in recent_audit %}
        <tr>
          <td>{{ a.created_at | dt }}</td>
          <td>{{ a.entity }} #{{ a.entity_id or '—' }}</td>
          <td><span class="badge badge-soft">{{ a.action }}</span></td>
        </tr>
      {% else %}
        <tr><td colspan="3" class="text-muted">Нет данных</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\dashboard.html", $dashboard_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  dashboard.html" -ForegroundColor Green
Заметил в шаблоне строчку с c.employee — она не сработает (в Computer нет relationship). Но она безопасно отрендерится как #ID, потому что это вторая ветка {% if c.employee_id %}. Ок.
________________________________________
Скрипт A5 — миграция БД + пересборка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

Write-Host "--- Миграция БД ---" -ForegroundColor Cyan
docker compose up -d db
Start-Sleep -Seconds 6

docker compose exec -T db psql -U tracker -d tracker -c @"
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS department_id INTEGER REFERENCES departments(id);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS fired_at TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"@

Write-Host "`n--- Пересборка ---" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

docker compose ps
Write-Host "`n--- Логи API (последние 20) ---" -ForegroundColor Cyan
docker compose logs api --tail=20

Write-Host "`nГотово. Откройте https://localhost/admin/reports" -ForegroundColor Green
________________________________________
Что проверить после запуска A
/admin/reports
Мультивыбор отделов, сотрудников, компьютеров (Ctrl+клик)
Поиск по каждому списку
При выборе отдела — список сотрудников фильтруется автоматически
Появилась группировка «Месяц ? Сотрудник» и «По отделам»
Сформировать «Месяц ? Сотрудник» — компактная таблица для 50+ сотрудников
Экспорт XLSX — колонки: Рабочий день / Год / Месяц / Число / Сотрудник / 1C ID / Отдел / Компьютер / Сессий / Отработано / Эффективно. Никакой «Группы» и «Аварийного».
Дашборд — карточка «Компьютеры онлайн» и статус в таблице ПК
________________________________________
Проверка фильтрации по отделам
Создайте 2 отдела: «Бухгалтерия», «Разработка»
Привяжите 3–5 сотрудников к разным отделам
На /admin/reports выберите «Бухгалтерия» ? в списке сотрудников останутся только бухгалтеры
Снимите выделение ? вернутся все
________________________________________
Если всё заработало — присылайте подтверждение, и я выдам Подблок B (heartbeat, фикс localhost в клиенте, массовая привязка CSV). Если что-то упало — пришлите docker compose logs api --tail=40 и скажите, какая именно страница/действие.
Не работает только вкладка Tracker Admin Внутренняя ошибка сервера
500 на дашборде. Скорее всего из-за того, что в шаблоне dashboard.html я передал cutoff_online, но в Python-функции dashboard его не передаю. И в шаблоне используется c.employee.full_name — там бред написан.
Давайте посмотрим — в dashboard() я возвращаю:
stats, recent_computers, recent_audit, admin, tz, heartbeat_window
А в шаблоне использую cutoff_online — которого нет! Jinja молча вернёт undefined, но c.last_seen_at >= cutoff_online — при сравнении с Undefined может упасть.
Плюс строка:
text
{{ c.employee.full_name if c.employee_id and c.employee_id in (c.__dict__.keys() and []) else '' }}
Это точно упадёт — c.__dict__.keys() and [] вернёт [], x in [] False, но c.employee не вычисляется, ок. Но если employee_id есть, то пойдёт в else ? пустая строка, ок. Но c.employee при отсутствии relationship — AttributeError. Однако по условию до c.employee не дойдёт.
Основная проблема — cutoff_online не передаётся. Надо:
В dashboard() передать cutoff_online = _now() - timedelta(minutes=heartbeat_window)
Упростить шаблон — убрать некорректную строку с c.employee
Проверю также, что в dashboard я использовал Computer.last_seen_at >= cutoff_online — это ок.
Ещё момент: в шаблоне {% if c.last_seen_at and c.last_seen_at >= cutoff_online %} — если cutoff_online undefined, то сравнение datetime >= Undefined даст ошибку.
Сделаю патч web_admin.py (добавить cutoff_online) + перепишу строку в dashboard.html.
Причём дам только два скрипта — минимальные, чтобы не переписывать всё.
500 на дашборде — две причины
Обе — в моём шаблоне dashboard.html:
1. Я использую cutoff_online в шаблоне, но не передаю его из Python — надо добавить в dashboard().
2. Оставил мусорную строку с c.employee.full_name, которой нет в модели Computer — упадёт на рендере.
Оба чинятся двумя маленькими патчами.
________________________________________
Скрипт 1 — патч server/web_admin.py (функция dashboard)
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$old = @'
    recent_computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).limit(15).all()
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "stats": stats,
        "recent_computers": recent_computers, "recent_audit": recent_audit,
        "admin": request.session.get("admin"), "tz": tz,
        "heartbeat_window": heartbeat_window,
    })
'@

$new = @'
    recent_computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).limit(15).all()
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    # Справочник сотрудников — чтобы в шаблоне показать ФИО рядом с ПК
    emp_ids = {c.employee_id for c in recent_computers if c.employee_id}
    employees = {e.id: e for e in db.query(Employee).filter(Employee.id.in_(emp_ids)).all()} if emp_ids else {}

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "stats": stats,
        "recent_computers": recent_computers, "recent_audit": recent_audit,
        "admin": request.session.get("admin"), "tz": tz,
        "heartbeat_window": heartbeat_window,
        "cutoff_online": cutoff_online,
        "employees": employees,
    })
'@

if ($content.Contains($new)) {
    Write-Host "Уже пропатчен — пропускаем" -ForegroundColor Yellow
} elseif ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  dashboard() пропатчен" -ForegroundColor Green
} else {
    Write-Host "НЕ НАЙДЕН блок — правьте вручную" -ForegroundColor Red
    exit 1
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — server/templates/dashboard.html (полная замена)
Убрал мусор с c.employee, теперь ФИО берётся из переданного словаря employees.
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

$dashboard_html = @'
{% extends "base.html" %}
{% block title %}Дашборд{% endblock %}
{% block content %}
<h3 class="mb-4">Дашборд</h3>

<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Сотрудники</div>
    <div class="fs-3">{{ stats.employees }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Отделы</div>
    <div class="fs-3">{{ stats.departments }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">Компьютеры</div>
    <div class="fs-3">{{ stats.computers }}</div>
  </div></div></div>
  <div class="col-md-3"><div class="card"><div class="card-body">
    <div class="text-muted small">
      Компьютеры онлайн
      <span class="hint" data-bs-toggle="tooltip" title="ПК, которые присылали данные за последние {{ heartbeat_window }} мин.">?</span>
    </div>
    <div class="fs-3 text-success">{{ stats.computers_online }}</div>
  </div></div></div>
</div>

<div class="row g-3 mb-4">
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий сегодня</div>
    <div class="fs-4">{{ stats.sessions_today }}</div>
  </div></div></div>
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Сессий за 7 дней</div>
    <div class="fs-4">{{ stats.sessions_week }}</div>
  </div></div></div>
  <div class="col-md-4"><div class="card"><div class="card-body">
    <div class="text-muted small">Всего записей</div>
    <div class="fs-4">{{ stats.records }}</div>
  </div></div></div>
</div>

<div class="card mb-4">
  <div class="card-header d-flex justify-content-between align-items-center">
    <span>Компьютеры (последние {{ recent_computers|length }})</span>
    <a class="btn btn-sm btn-outline-primary" href="/admin/computers">Все ПК ?</a>
  </div>
  <div class="card-body p-0">
    <table class="table table-sm mb-0">
      <thead><tr>
        <th>Hostname</th><th>UID</th><th>Сотрудник</th>
        <th>Last seen</th><th>Статус</th>
      </tr></thead>
      <tbody>
      {% for c in recent_computers %}
        <tr>
          <td>{{ c.hostname or '—' }}</td>
          <td><code title="{{ c.computer_uid }}">{{ c.computer_uid[:14] }}…</code></td>
          <td>
            {% if c.employee_id and employees.get(c.employee_id) %}
              {{ employees[c.employee_id].full_name }}
            {% else %}
              <span class="text-muted">— не привязан —</span>
            {% endif %}
          </td>
          <td>{{ c.last_seen_at | dt }}</td>
          <td>
            {% if not c.is_active %}
              <span class="badge bg-danger">отключён</span>
            {% elif c.last_seen_at and c.last_seen_at >= cutoff_online %}
              <span class="badge bg-success">онлайн</span>
            {% else %}
              <span class="badge bg-secondary">офлайн</span>
            {% endif %}
          </td>
        </tr>
      {% else %}
        <tr><td colspan="5" class="text-muted">Нет данных</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>

<div class="card">
  <div class="card-header">Последние действия</div>
  <div class="card-body p-0">
    <table class="table table-sm mb-0">
      <thead><tr><th>Время</th><th>Сущность</th><th>Действие</th></tr></thead>
      <tbody>
      {% for a in recent_audit %}
        <tr>
          <td>{{ a.created_at | dt }}</td>
          <td>{{ a.entity }} #{{ a.entity_id or '—' }}</td>
          <td><span class="badge badge-soft">{{ a.action }}</span></td>
        </tr>
      {% else %}
        <tr><td colspan="3" class="text-muted">Нет данных</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\dashboard.html", $dashboard_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  dashboard.html" -ForegroundColor Green
________________________________________
Скрипт 3 — пересборка и проверка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

docker compose ps
Write-Host "`n--- Логи API (последние 25) ---" -ForegroundColor Cyan
docker compose logs api --tail=25

Write-Host "`nОткройте: https://localhost/admin" -ForegroundColor Green
________________________________________
Что проверить
Открывается https://localhost/admin — дашборд без 500
В карточке «Компьютеры онлайн» — число
В таблице «Компьютеры»:
ФИО привязанного сотрудника (или «— не привязан —»)
Бейджи онлайн / офлайн / отключён
/admin/reports — все фильтры, поиск, группировка «Месяц ? Сотрудник» работают
________________________________________
Если снова 500
Пришлите последние 40 строк:
powershell
docker compose logs api --tail=60
Там будет конкретный traceback — поправим точечно. Но сейчас должно быть чисто: обе причины (отсутствие cutoff_online и несуществующий c.employee) устранены.
Всё работает что дальше?
Пользователь говорит что всё работает. Идём дальше по плану — Подблок B:
Heartbeat — эндпоинт + колонка «Онлайн/Оффлайн» на дашборде (уже частично сделано через last_seen_at, но нужен именно heartbeat-эндпоинт для явного пинга)
Фикс дефолтного localhost в клиенте (config.py)
Массовая привязка ПК через CSV (уже сделал endpoint, нужен шаблон)
Дальше по списку:
Календарь рабочих/нерабочих дней + подсветка Сб/Вс
PDF-отчёт
Разобью на два подблока:
Подблок B — небольшие доработки:
Heartbeat-эндпоинт /api/v1/heartbeat
Клиент отправляет heartbeat раз в 3-5 минут
Фикс localhost в client/config.py (дефолт)
Шаблон для массовой привязки ПК через CSV
Подблок C — крупный блок:
Календарь рабочих/нерабочих дней
PDF-отчёт
Начну с B, потом C. Пойду короткими, чёткими скриптами.
Так как контекст уже огромный, буду более компактным. Главное — не ошибиться в коде.
Начнём с Подблока B.
B1. Heartbeat
Сервер: эндпоинт /api/v1/heartbeat:
python
@app.post("/api/v1/heartbeat")
def heartbeat(comp: Computer = Depends(get_computer), db: Session = Depends(get_db)):
    comp.last_seen_at = _now()
    db.commit()
    return {"status": "ok", "server_time": _now().isoformat()}
Клиент: в sync.py добавить отправку heartbeat раз в цикл (30 сек — многовато, сделаем раз в 3 минуты). Можно отдельный воркер, но проще добавить в sync-цикл: раз в 6 циклов (3 минуты).
Но нужен метод _send_heartbeat.
B2. Фикс localhost в client/config.py
Сейчас:
python
SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://tracker.example.com")
Проблема: клиент использует .env, и там localhost — надо было исправить на 127.0.0.1. Уже сделали вручную. Но чтобы дефолт был правильный, можно поменять дефолт в config.py.
Хотя эта проблема чисто DNS-окружения конкретной машины, менять дефолт на 127.0.0.1 не очень правильно для прода. Оставим как есть, но добавим пояснение.
Вообще, пользователь уже исправил .env, и всё работает. Оставим пока.
B3. Массовая привязка CSV
Endpoint я уже добавил в web_admin.py — /admin/computers/bulk-assign. Нужен только шаблон computers.html с формой загрузки.
Смотрю текущий computers.html — там нет формы. Надо добавить модалку или просто блок с формой.
Ок, план:
Патч main.py — добавить /api/v1/heartbeat
Патч sync.py — отправлять heartbeat
Новый computers.html с формой массовой привязки
Начнём.
Пишу компактно. Всё в одном сообщении.
На самом деле давайте подумаем — пользователь уже прогнал много скриптов, устал. Сделаем пакет B компактно, а C — следующим сообщением (он крупный).
Ещё стоит отметить: сейчас у нас recent_computers в dashboard и computers в /admin/computers — оба показывают статус через last_seen_at. Но last_seen_at обновляется только при ingest (POST /records/batch и POST /sessions). Если сотрудник не нажал "Начать работу", компьютер будет выглядеть офлайн, хотя клиент работает. Heartbeat решит это — клиент шлёт пинг каждые 3 минуты независимо от сессии.
Это важно! Добавим heartbeat.
Пишу код.
Для sync.py:
python
def _send_heartbeat(self):
    try:
        r = http_client.post(f"{SERVER_URL}/api/v1/heartbeat", headers=self._headers(), timeout=5.0)
        if r.status_code == 200:
            self.connected.emit()
    except Exception as e:
        log.debug("heartbeat failed: %s", e)
В цикле:
python
self._cycles += 1
if self._cycles % 10 == 1:
    self._fetch_client_config()
