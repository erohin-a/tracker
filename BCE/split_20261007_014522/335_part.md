<!-- Часть 335 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ report_result.html — новая логика колонок + топ программ с разбивкой](334_report_result_html_novaya_logika_kolonok_top_programm_s_razbivkoy.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Client config ---------- ▶](336_Client_config.md)

---

# ============================================================
$report_result_html = @'
{% extends "base.html" %}
{% block title %}Отчёт{% endblock %}
{% block content %}

<div class="d-flex justify-content-between align-items-start mb-3">
  <div>
    <h3 class="mb-1">Отчёт</h3>
    <div class="text-muted">
      {{ report.date_from.strftime('%d.%m.%Y') }} — {{ report.date_to.strftime('%d.%m.%Y') }}
      &nbsp;·&nbsp;
      TZ: <code>{{ report.tz_name }}</code>
      &nbsp;·&nbsp;
      Рабочий день начинается в <strong>{{ '%02d' % report.workday_start_hour }}:00</strong>
      &nbsp;·&nbsp;
      Группировка:
      <strong>
      {% if report.group_by == 'days' %}Рабочие дни ? Сотрудник
      {% elif report.group_by == 'employees' %}По сотрудникам
      {% elif report.group_by == 'computers' %}По компьютерам
      {% else %}Детально (сессии){% endif %}
      </strong>
    </div>
  </div>
  <a class="btn btn-outline-secondary" href="/admin/reports">? Назад</a>
</div>

<div class="row g-3 mb-4">
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">Сессий</div>
      <div class="fs-4">{{ report.totals.sessions }}</div>
    </div></div>
  </div>
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">
        Отработано
        <span class="hint" data-bs-toggle="tooltip" title="От старта первой сессии до конца последней сессии за день. Включает перерывы между сессиями.">?</span>
      </div>
      <div class="fs-4">{{ report.totals.worked_duration | dur }}</div>
    </div></div>
  </div>
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">
        Эффективно
        <span class="hint" data-bs-toggle="tooltip" title="Сумма активного времени во всех сессиях. Большие паузы (> 5 минут) не учитываются.">?</span>
      </div>
      <div class="fs-4 text-success">{{ report.totals.effective_duration | dur }}</div>
    </div></div>
  </div>
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">Аварийных закрытий</div>
      <div class="fs-4">{{ report.totals.abnormal }}</div>
    </div></div>
  </div>
</div>

{% if show_abnormal and report.totals.abnormal %}
<div class="alert alert-warning py-2">
  ? В выборке {{ report.totals.abnormal }} сессий с аварийным завершением —
  клиент был выключен без нажатия «Конец работы», либо закрыт автоматически по бездействию.
</div>
{% endif %}

{% if show_apps and report.totals.top_apps %}
<div class="card mb-4">
  <div class="card-header">
    Топ программ за период
    <span class="hint" data-bs-toggle="tooltip" title="Нажмите на треугольник под программой — увидите разбивку по сотрудникам: кто и сколько в ней работал.">?</span>
  </div>
  <div class="card-body p-0">
    {% set max_app_seconds = report.totals.top_apps[0].seconds %}
    <table class="table table-sm mb-0">
      <thead class="table-light">
        <tr>
          <th style="width:35%">Программа</th>
          <th>Время</th>
          <th>
            Клавиатура
            <span class="hint" data-bs-toggle="tooltip" title="Секунды с активностью клавиатуры в этой программе.">?</span>
          </th>
          <th>
            Мышь
            <span class="hint" data-bs-toggle="tooltip" title="Секунды с активностью мыши в этой программе.">?</span>
          </th>
          <th style="width:25%"></th>
        </tr>
      </thead>
      <tbody>
      {% for a in report.totals.top_apps %}
        <tr>
          <td>{{ a.app }}</td>
          <td style="white-space:nowrap"><strong>{{ a.seconds | dur }}</strong></td>
          <td>{{ a.keyboard | dur }}</td>
          <td>{{ a.mouse | dur }}</td>
          <td>
            <span class="app-bar" style="width: {{ (a.seconds / max_app_seconds * 100) if max_app_seconds else 0 }}%"></span>
          </td>
        </tr>
        {% if a.by_employee and a.by_employee|length > 0 %}
        <tr>
          <td colspan="5" class="p-0">
            <details>
              <summary style="padding:6px 12px;cursor:pointer;color:#555;font-size:0.9em;background:#f8f9fa">
                ? Кто работал в «{{ a.app }}» — {{ a.by_employee|length }} сотр.
              </summary>
              <div style="padding:8px 12px">
                <table class="table table-sm mb-0">
                  <thead><tr>
                    <th>Сотрудник</th>
                    <th>1C ID</th>
                    <th>Время</th>
                    <th>Клавиатура</th>
                    <th>Мышь</th>
                  </tr></thead>
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
          </td>
        </tr>
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
            <th style="width:120px">
              Рабочий день
              <span class="hint" data-bs-toggle="tooltip" title="С учётом настройки «Начало рабочего дня». Сессии, начавшиеся до этого часа, относятся к предыдущему дню.">?</span>
            </th>
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">
              Отработано
              <span class="hint" data-bs-toggle="tooltip" title="От старта первой сессии до конца последней сессии за этот рабочий день.">?</span>
            </th>
            <th style="width:110px">
              Эффективно
              <span class="hint" data-bs-toggle="tooltip" title="Сумма активного времени без пауз > 5 минут.">?</span>
            </th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% elif report.group_by == 'employees' %}
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th style="width:80px">Дней</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Эффективно</th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% elif report.group_by == 'computers' %}
            <th>Компьютер</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Эффективно</th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% else %}
            <th style="width:120px">Рабочий день</th>
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th>Компьютер</th>
            <th style="width:110px">Начало</th>
            <th style="width:110px">Конец</th>
            <th style="width:100px">Отработано</th>
            <th style="width:100px">Эффективно</th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
          {% endif %}
        </tr>
      </thead>
      <tbody>
      {% for r in report.rows %}
        {% if report.group_by == 'days' %}
          <tr>
            <td>{{ r.date.strftime('%d.%m.%Y') }}</td>
            <td>{{ r.employee_name }}</td>
            <td><code>{{ r.external_id or '—' }}</code></td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
            {% if show_abnormal %}
              <td>
                {% set abn = r.sessions | selectattr('abnormal') | list | length %}
                {% if abn %}<span class="badge bg-warning text-dark">{{ abn }}</span>{% endif %}
              </td>
            {% endif %}
            {% if expand_details %}
              <td>
                <details>
                  <summary class="btn btn-sm btn-outline-secondary py-0">?</summary>
                  <div class="mt-2" style="min-width:600px">
                    <strong>Сессии:</strong>
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
                          <tr>
                            <td>{{ a.app }}</td>
                            <td>{{ a.seconds | dur }}</td>
                            <td>{{ a.keyboard | dur }}</td>
                            <td>{{ a.mouse | dur }}</td>
                          </tr>
                        {% endfor %}
                        </tbody>
                      </table>
                    {% endif %}
                  </div>
                </details>
              </td>
            {% endif %}
          </tr>
        {% elif report.group_by == 'employees' %}
          <tr>
            <td>{{ r.employee_name }}</td>
            <td><code>{{ r.external_id or '—' }}</code></td>
            <td class="text-center">{{ r.days_count }}</td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
            {% if show_abnormal %}
              <td>
                {% set abn = r.sessions | selectattr('abnormal') | list | length %}
                {% if abn %}<span class="badge bg-warning text-dark">{{ abn }}</span>{% endif %}
              </td>
            {% endif %}
            {% if expand_details %}
              <td>
                <details>
                  <summary class="btn btn-sm btn-outline-secondary py-0">?</summary>
                  <div class="mt-2" style="min-width:600px">
                    {% if r.top_apps %}
                      <strong>Программы:</strong>
                      <table class="table table-sm mb-0">
                        <thead><tr><th>Программа</th><th>Время</th><th>Клавиатура</th><th>Мышь</th></tr></thead>
                        <tbody>
                        {% for a in r.top_apps %}
                          <tr>
                            <td>{{ a.app }}</td>
                            <td>{{ a.seconds | dur }}</td>
                            <td>{{ a.keyboard | dur }}</td>
                            <td>{{ a.mouse | dur }}</td>
                          </tr>
                        {% endfor %}
                        </tbody>
                      </table>
                    {% endif %}
                  </div>
                </details>
              </td>
            {% endif %}
          </tr>
        {% elif report.group_by == 'computers' %}
          <tr>
            <td>{{ r.computer_name }}</td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.worked_duration | dur }}</strong></td>
            <td class="text-success">{{ r.effective_duration | dur }}</td>
            {% if show_abnormal %}
              <td>
                {% set abn = r.sessions | selectattr('abnormal') | list | length %}
                {% if abn %}<span class="badge bg-warning text-dark">{{ abn }}</span>{% endif %}
              </td>
            {% endif %}
            {% if expand_details %}
              <td>
                <details>
                  <summary class="btn btn-sm btn-outline-secondary py-0">?</summary>
                  <div class="mt-2" style="min-width:600px">
                    {% if r.top_apps %}
                      <strong>Программы:</strong>
                      <table class="table table-sm mb-0">
                        <thead><tr><th>Программа</th><th>Время</th><th>Клавиатура</th><th>Мышь</th></tr></thead>
                        <tbody>
                        {% for a in r.top_apps %}
                          <tr>
                            <td>{{ a.app }}</td>
                            <td>{{ a.seconds | dur }}</td>
                            <td>{{ a.keyboard | dur }}</td>
                            <td>{{ a.mouse | dur }}</td>
                          </tr>
                        {% endfor %}
                        </tbody>
                      </table>
                    {% endif %}
                  </div>
                </details>
              </td>
            {% endif %}
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
            {% if show_abnormal %}
              <td>{% if r.abnormal %}<span class="badge bg-warning text-dark">да</span>{% endif %}</td>
            {% endif %}
          </tr>
        {% endif %}
      {% else %}
        <tr><td colspan="12" class="text-center text-muted py-4">
          Нет данных за выбранный период
        </td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>

<div class="d-flex justify-content-end mt-3">
  <div class="card">
    <div class="card-body py-2">
      <strong>ИТОГО:</strong>
      сессий {{ report.totals.sessions }},
      отработано {{ report.totals.worked_duration | dur }},
      эффективно {{ report.totals.effective_duration | dur }}
    </div>
  </div>
</div>

<a class="btn btn-outline-secondary mt-3" href="/admin/reports">? Новый отчёт</a>

{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\report_result.html", $report_result_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  report_result.html" -ForegroundColor Green

Write-Host "`n=== Скрипт 2 завершён ===" -ForegroundColor Cyan
________________________________________
Скрипт 3 — server/main.py: добавляем /api/v1/client-config
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("/api/v1/client-config")) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} else {
    $endpoint = @'

