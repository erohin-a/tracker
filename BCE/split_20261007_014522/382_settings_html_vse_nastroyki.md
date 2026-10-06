<!-- Часть 382 из 1409 -->
# settings.html — все настройки
*Хлебные крошки:* settings.html — все настройки

[◀ base.html — ссылка на Отделы](381_base_html_ssylka_na_Otdely.md) | [Оглавление](00_BCE_INDEX.md) | [departments.html ▶](383_departments_html.md)

---

# settings.html — все настройки
$settings_html = @'
{% extends "base.html" %}
{% block title %}Настройки{% endblock %}
{% block content %}
<h3 class="mb-4">Настройки системы</h3>

{% if saved %}
<div class="alert alert-success py-2">? Сохранено. Клиенты подхватят изменения в течение 5 минут.</div>
{% endif %}

<div class="card" style="max-width:900px">
  <div class="card-body">
    <form method="post" action="/admin/settings/save">

      <h5 class="mb-3">Отчёты</h5>

      <div class="row g-3 mb-3">
        <div class="col-md-6">
          <label class="form-label">
            Часовой пояс
            <span class="hint" data-bs-toggle="tooltip" title="В каком часовом поясе отображать время в отчётах. В БД хранится UTC.">?</span>
          </label>
          <select name="report_timezone" class="form-select">
            {% for tz_id, tz_label in timezones %}
              <option value="{{ tz_id }}" {% if tz_id == cfg.report_timezone %}selected{% endif %}>{{ tz_label }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Начало рабочего дня
            <span class="hint" data-bs-toggle="tooltip" title="Сессии, начавшиеся раньше этого часа, относятся к предыдущему рабочему дню. Для ночных смен.">?</span>
          </label>
          <select name="workday_start_hour" class="form-select">
            {% for h in range(0, 24) %}
              <option value="{{ h }}" {% if h == cfg.workday_start_hour %}selected{% endif %}>{{ '%02d' % h }}:00</option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Порог паузы для «Эффективно»
            <span class="hint" data-bs-toggle="tooltip" title="Если разрыв между событиями активности больше этого времени — интервал не считается «работой».">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="activity_gap_minutes" class="form-control"
                   value="{{ cfg.activity_gap_minutes }}" min="1" max="120">
            <span class="input-group-text">минут</span>
          </div>
        </div>
      </div>

      <h5 class="mb-3 mt-4">Клиенты</h5>

      <div class="row g-3 mb-3">
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
            Интервал синхронизации
            <span class="hint" data-bs-toggle="tooltip" title="Как часто клиент отправляет данные на сервер.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="sync_interval" class="form-control"
                   value="{{ cfg.sync_interval }}" min="5" max="3600">
            <span class="input-group-text">секунд</span>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Размер батча
            <span class="hint" data-bs-toggle="tooltip" title="Сколько записей клиент отправляет за один запрос.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="batch_size" class="form-control"
                   value="{{ cfg.batch_size }}" min="10" max="1000">
            <span class="input-group-text">записей</span>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Период опроса активного окна
            <span class="hint" data-bs-toggle="tooltip" title="Как часто клиент проверяет активное окно.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="active_window_interval" class="form-control"
                   value="{{ cfg.active_window_interval }}" min="1" max="60">
            <span class="input-group-text">секунд</span>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">
            Порог бездействия (idle)
            <span class="hint" data-bs-toggle="tooltip" title="Если нет активности дольше этого времени, клиент считает пользователя неактивным и записывает idle.">?</span>
          </label>
          <div class="input-group">
            <input type="number" name="idle_threshold" class="form-control"
                   value="{{ cfg.idle_threshold }}" min="10" max="3600">
            <span class="input-group-text">секунд</span>
          </div>
        </div>
      </div>

      <div class="alert alert-info py-2 small mb-3">
        Изменения доезжают до клиентов при следующем цикле синхронизации (максимум 5 минут).
      </div>

      <button class="btn btn-primary">Сохранить все настройки</button>
    </form>
  </div>
</div>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\settings.html", $settings_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  settings.html" -ForegroundColor Green

