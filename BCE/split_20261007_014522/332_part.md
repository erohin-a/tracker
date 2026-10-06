<!-- Часть 332 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ reports.html — обновляем справку по колонкам](331_reports_html_obnovlyaem_spravku_po_kolonkam.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](333_part.md)

---

# ============================================================
$reports_html = @'
{% extends "base.html" %}
{% block title %}Отчёты{% endblock %}
{% block content %}
<h3 class="mb-4">Отчёты</h3>

<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/reports/generate" class="row g-3" id="reportForm">

      <div class="col-12">
        <label class="form-label fw-bold">Период</label>
        <div class="d-flex flex-wrap gap-2 mb-2">
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(0)">Сегодня</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(1)">Вчера</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(7)">7 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(30)">30 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setThisMonth()">Этот месяц</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setLastMonth()">Прошлый месяц</button>
        </div>
      </div>

      <div class="col-md-3">
        <label class="form-label">С даты</label>
        <input class="form-control" type="date" name="date_from" id="date_from" required value="{{ today }}">
      </div>
      <div class="col-md-3">
        <label class="form-label">По дату</label>
        <input class="form-control" type="date" name="date_to" id="date_to" required value="{{ today }}">
      </div>

      <div class="col-md-3">
        <label class="form-label">Сотрудник</label>
        <select name="employee_id" class="form-select">
          <option value="">Все сотрудники</option>
          {% for e in employees %}
            <option value="{{ e.id }}">{{ e.full_name }}{% if e.external_id %} ({{ e.external_id }}){% endif %}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Компьютер</label>
        <select name="computer_id" class="form-select">
          <option value="">Все компьютеры</option>
          {% for c in computers %}
            <option value="{{ c.id }}">{{ c.hostname or c.computer_uid[:14] }}</option>
          {% endfor %}
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">
          Группировка
          <span class="hint" data-bs-toggle="tooltip" title="Как сгруппировать строки в отчёте.">?</span>
        </label>
        <select name="group_by" class="form-select">
          <option value="days" selected>Рабочие дни ? Сотрудник (табель)</option>
          <option value="employees">По сотрудникам (итог за период)</option>
          <option value="computers">По компьютерам</option>
          <option value="sessions">Детально — каждая сессия</option>
        </select>
      </div>

      <div class="col-md-4">
        <label class="form-label">
          Часовой пояс
          <span class="hint" data-bs-toggle="tooltip" title="В каком часовом поясе отображать время. В БД время хранится в UTC.">?</span>
        </label>
        <select name="tz_name" class="form-select">
          {% for tz_id, tz_label in timezones %}
            <option value="{{ tz_id }}" {% if tz_id == default_tz %}selected{% endif %}>{{ tz_label }}</option>
          {% endfor %}
        </select>
      </div>

      <div class="col-md-2">
        <label class="form-label">
          Начало рабочего дня
          <span class="hint" data-bs-toggle="tooltip" title="Сессии, начавшиеся раньше этого часа, относятся к предыдущему рабочему дню. Для ночных смен.">?</span>
        </label>
        <select name="workday_start_hour" class="form-select">
          {% for h in range(0, 24) %}
            <option value="{{ h }}" {% if h == default_workday_start %}selected{% endif %}>{{ '%02d' % h }}:00</option>
          {% endfor %}
        </select>
      </div>

      <div class="col-md-2">
        <label class="form-label">Формат</label>
        <select name="fmt" class="form-select">
          <option value="html">Просмотр</option>
          <option value="xlsx">Excel (XLSX)</option>
          <option value="csv">CSV</option>
        </select>
      </div>

      <div class="col-12">
        <label class="form-label fw-bold">Что показывать</label>
        <div class="d-flex flex-wrap gap-4">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_apps" id="show_apps" checked>
            <label class="form-check-label" for="show_apps">Топ-программы (с разбивкой по сотрудникам)</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_abnormal" id="show_abnormal" checked>
            <label class="form-check-label" for="show_abnormal">Пометки аварийных завершений</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="expand_details" id="expand_details">
            <label class="form-check-label" for="expand_details">Разворачивать детали (сессии и программы)</label>
          </div>
        </div>
      </div>

      <div class="col-12">
        <div class="alert alert-secondary py-2 small mb-0">
          <strong>Что означают колонки:</strong>
          <ul class="mb-0 mt-1">
            <li><strong>Отработано</strong> — от старта первой сессии до конца последней сессии за день (включает перерывы между сессиями).</li>
            <li><strong>Эффективно</strong> — сумма активного времени во всех сессиях (без больших пауз &gt; 5 минут).</li>
          </ul>
        </div>
      </div>

      <div class="col-12">
        <button class="btn btn-primary">Сформировать отчёт</button>
      </div>
    </form>
  </div>
</div>

<script>
function fmt(d) {
  var y = d.getFullYear();
  var m = String(d.getMonth()+1).padStart(2,'0');
  var dd = String(d.getDate()).padStart(2,'0');
  return y + '-' + m + '-' + dd;
}
function setPeriod(daysAgo) {
  var to = new Date();
  var from = new Date();
  from.setDate(from.getDate() - daysAgo);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
function setThisMonth() {
  var now = new Date();
  var from = new Date(now.getFullYear(), now.getMonth(), 1);
  var to = new Date(now.getFullYear(), now.getMonth()+1, 0);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
function setLastMonth() {
  var now = new Date();
  var from = new Date(now.getFullYear(), now.getMonth()-1, 1);
  var to = new Date(now.getFullYear(), now.getMonth(), 0);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
</script>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\reports.html", $reports_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  reports.html" -ForegroundColor Green

