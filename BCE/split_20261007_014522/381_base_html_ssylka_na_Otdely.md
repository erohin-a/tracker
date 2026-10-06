<!-- Часть 381 из 1409 -->
# base.html — ссылка на Отделы
*Хлебные крошки:* base.html — ссылка на Отделы

[◀ ============================================================](380_part.md) | [Оглавление](00_BCE_INDEX.md) | [settings.html — все настройки ▶](382_settings_html_vse_nastroyki.md)

---

# base.html — ссылка на Отделы
$base_html = @'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Tracker Admin{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { padding-bottom: 40px; }
    .table-sm td, .table-sm th { vertical-align: middle; }
    .badge-soft { background: #eef2f7; color: #334; }
    code { background: #f4f6f8; padding: 2px 6px; border-radius: 4px; }
    .hint { color: #8a94a6; cursor: help; font-size: 0.85em; margin-left: 3px; }
    .app-bar { display:inline-block; height: 10px; background:#4a90e2; border-radius:2px; vertical-align:middle; }
    details > summary { list-style: none; }
    details > summary::-webkit-details-marker { display: none; }
    .multi-select { height: 220px; }
    .fired-row { opacity: 0.65; }
  </style>
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container-fluid px-4">
    <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
    <div class="navbar-nav ms-auto">
      {% if admin %}
        <a class="nav-link {% if request.url.path == '/admin/employees' %}active{% endif %}" href="/admin/employees">Сотрудники</a>
        <a class="nav-link {% if '/departments' in request.url.path %}active{% endif %}" href="/admin/departments">Отделы</a>
        <a class="nav-link {% if '/computers' in request.url.path %}active{% endif %}" href="/admin/computers">Компьютеры</a>
        <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}" href="/admin/tokens">Токены</a>
        <a class="nav-link {% if '/reports' in request.url.path %}active{% endif %}" href="/admin/reports">Отчёты</a>
        <a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>
        <a class="nav-link {% if '/audit' in request.url.path %}active{% endif %}" href="/admin/audit">Аудит</a>
        <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
        <a class="nav-link" href="/admin/logout">Выход</a>
      {% endif %}
    </div>
  </div>
</nav>
<div class="container-fluid px-4">
  {% block content %}{% endblock %}
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {
    var tip = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tip.forEach(function (el) { new bootstrap.Tooltip(el, { html: false, placement: 'top' }); });
  });
</script>
</body>
</html>
'@
[System.IO.File]::WriteAllText("$templatesDir\base.html", $base_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  base.html" -ForegroundColor Green

