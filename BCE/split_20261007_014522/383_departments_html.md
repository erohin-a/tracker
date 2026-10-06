<!-- Часть 383 из 1409 -->
# departments.html
*Хлебные крошки:* departments.html

[◀ settings.html — все настройки](382_settings_html_vse_nastroyki.md) | [Оглавление](00_BCE_INDEX.md) | [employees.html — с отделами и вкладками Активные/Уволенные ▶](384_employees_html_s_otdelami_i_vkladkami_Aktivnye_Uvolennye.md)

---

# departments.html
$departments_html = @'
{% extends "base.html" %}
{% block title %}Отделы{% endblock %}
{% block content %}
<h3 class="mb-4">Отделы</h3>

<div class="card mb-4" style="max-width:720px">
  <div class="card-header">Добавить отдел</div>
  <div class="card-body">
    <form method="post" action="/admin/departments/create" class="d-flex gap-2">
      <input class="form-control" name="name" placeholder="Название отдела" required>
      <button class="btn btn-success">+ Добавить</button>
    </form>
  </div>
</div>

<table class="table table-sm table-hover bg-white" style="max-width:900px">
  <thead><tr>
    <th>ID</th><th>Название</th><th>Сотрудников</th><th>Действия</th>
  </tr></thead>
  <tbody>
  {% for d in departments %}
    <tr>
      <td>{{ d.id }}</td>
      <td>
        <form method="post" action="/admin/departments/{{ d.id }}/rename" class="d-flex gap-1">
          <input class="form-control form-control-sm" name="name" value="{{ d.name }}" style="width:300px">
          <button class="btn btn-sm btn-outline-primary">??</button>
        </form>
      </td>
      <td>{{ counts.get(d.id, 0) }}</td>
      <td>
        <form method="post" action="/admin/departments/{{ d.id }}/delete" class="d-inline"
              onsubmit="return confirm('Удалить отдел «{{ d.name }}»? Сотрудники останутся без отдела.');">
          <button class="btn btn-sm btn-outline-danger">Удалить</button>
        </form>
      </td>
    </tr>
  {% else %}
    <tr><td colspan="4" class="text-muted">Отделов нет</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\departments.html", $departments_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  departments.html" -ForegroundColor Green

