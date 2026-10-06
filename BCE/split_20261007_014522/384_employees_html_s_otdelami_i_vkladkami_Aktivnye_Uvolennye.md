<!-- Часть 384 из 1409 -->
# employees.html — с отделами и вкладками Активные/Уволенные
*Хлебные крошки:* employees.html — с отделами и вкладками Активные/Уволенные

[◀ departments.html](383_departments_html.md) | [Оглавление](00_BCE_INDEX.md) | [reports.html — мультивыбор сотрудников + отдел, без tz/workday (они в настройках) ▶](385_reports_html_multivybor_sotrudnikov_otdel_bez_tz_workday_oni_v_nastroykah.md)

---

# employees.html — с отделами и вкладками Активные/Уволенные
$employees_html = @'
{% extends "base.html" %}
{% block content %}
<h3 class="mb-4">Сотрудники</h3>

<ul class="nav nav-tabs mb-3">
  <li class="nav-item"><a class="nav-link {% if tab == 'active' %}active{% endif %}" href="/admin/employees?tab=active">Активные</a></li>
  <li class="nav-item"><a class="nav-link {% if tab == 'fired' %}active{% endif %}" href="/admin/employees?tab=fired">Уволенные</a></li>
  <li class="nav-item"><a class="nav-link {% if tab == 'all' %}active{% endif %}" href="/admin/employees?tab=all">Все</a></li>
</ul>

{% if tab == 'active' %}
<div class="card mb-4">
  <div class="card-header">Добавить сотрудника</div>
  <div class="card-body">
    <form method="post" action="/admin/employees/create" class="row g-2">
      <div class="col-md-2"><input class="form-control" name="last_name" placeholder="Фамилия *" required></div>
      <div class="col-md-2"><input class="form-control" name="first_name" placeholder="Имя *" required></div>
      <div class="col-md-2"><input class="form-control" name="middle_name" placeholder="Отчество"></div>
      <div class="col-md-2"><input class="form-control" name="external_id" placeholder="1C ID"></div>
      <div class="col-md-3">
        <select name="department_id" class="form-select">
          <option value="">— без отдела —</option>
          {% for d in departments %}<option value="{{ d.id }}">{{ d.name }}</option>{% endfor %}
        </select>
      </div>
      <div class="col-md-1"><button class="btn btn-success w-100">+</button></div>
    </form>
  </div>
</div>
{% endif %}

<table class="table table-sm table-hover bg-white">
  <thead><tr>
    <th>ID</th><th>ФИО</th><th>1C ID</th><th>Отдел</th><th>Статус</th><th>Действия</th>
  </tr></thead>
  <tbody>
  {% for e in employees %}
    <tr class="{% if e.fired_at %}fired-row{% endif %}">
      <td>{{ e.id }}</td>
      <td>
        <form method="post" action="/admin/employees/{{ e.id }}/edit" class="d-flex gap-1">
          <input class="form-control form-control-sm" name="last_name" value="{{ e.last_name or '' }}" style="width:130px">
          <input class="form-control form-control-sm" name="first_name" value="{{ e.first_name or '' }}" style="width:110px">
          <input class="form-control form-control-sm" name="middle_name" value="{{ e.middle_name or '' }}" style="width:130px">
          <input class="form-control form-control-sm" name="external_id" value="{{ e.external_id or '' }}" placeholder="1C" style="width:90px">
          <select name="department_id" class="form-select form-select-sm" style="width:160px">
            <option value="">— без отдела —</option>
            {% for d in departments %}
              <option value="{{ d.id }}" {% if e.department_id == d.id %}selected{% endif %}>{{ d.name }}</option>
            {% endfor %}
          </select>
          <button class="btn btn-sm btn-outline-primary">??</button>
        </form>
      </td>
      <td><code>{{ e.external_id or '—' }}</code></td>
      <td>{% for d in departments %}{% if d.id == e.department_id %}{{ d.name }}{% endif %}{% endfor %}</td>
      <td>
        {% if e.fired_at %}
          <span class="badge bg-secondary">Уволен {{ e.fired_at | dt }}</span>
        {% else %}
          <span class="badge bg-success">Работает</span>
        {% endif %}
      </td>
      <td>
        {% if e.fired_at %}
          <form method="post" action="/admin/employees/{{ e.id }}/restore" class="d-inline">
            <button class="btn btn-sm btn-outline-success">Восстановить</button>
          </form>
        {% else %}
          <form method="post" action="/admin/employees/{{ e.id }}/fire" class="d-inline"
                onsubmit="return confirm('Уволить {{ e.full_name }}? Данные сохранятся, сотрудник переместится во вкладку «Уволенные».');">
            <button class="btn btn-sm btn-outline-danger">Уволить</button>
          </form>
        {% endif %}
      </td>
    </tr>
  {% else %}
    <tr><td colspan="6" class="text-muted">Нет сотрудников</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\employees.html", $employees_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  employees.html" -ForegroundColor Green

