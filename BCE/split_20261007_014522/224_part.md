<!-- Часть 224 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ report_result.html](223_report_result_html.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](225_part.md)

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
      Группировка:
      <strong>
      {% if report.group_by == 'days' %}Дни ? Сотрудник
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
      <div class="text-muted small">
        Сессий
        <span class="hint" data-bs-toggle="tooltip" title="Общее количество сессий в выборке.">?</span>
      </div>
      <div class="fs-4">{{ report.totals.sessions }}</div>
    </div></div>
  </div>
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">
        Всего времени
        <span class="hint" data-bs-toggle="tooltip" title="Суммарная длительность всех сессий: от «Начать работу» до «Конец работы».">?</span>
      </div>
      <div class="fs-4">{{ report.totals.duration | dur }}</div>
    </div></div>
  </div>
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">
        Клавиатура
        <span class="hint" data-bs-toggle="tooltip" title="Оценка активного времени с клавиатурой. Каждое событие = 5 секунд (интервал опроса).">?</span>
      </div>
      <div class="fs-4">{{ report.totals.keyboard | dur }}</div>
    </div></div>
  </div>
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">
        Мышь
        <span class="hint" data-bs-toggle="tooltip" title="Оценка активного времени с мышью. Каждое событие = 5 секунд.">?</span>
      </div>
      <div class="fs-4">{{ report.totals.mouse | dur }}</div>
    </div></div>
  </div>
</div>

{% if show_abnormal and report.totals.abnormal %}
<div class="alert alert-warning py-2">
  ? В выборке {{ report.totals.abnormal }} сессий с аварийным завершением —
  клиент был выключен без нажатия «Конец работы».
</div>
{% endif %}

{% if show_apps and report.totals.top_apps %}
<div class="card mb-4">
  <div class="card-header">
    Топ программ за период
    <span class="hint" data-bs-toggle="tooltip" title="Суммарное время активности в каждой программе. Рассчитывается по сменам активного окна.">?</span>
  </div>
  <div class="card-body">
    {% set max_app_seconds = report.totals.top_apps[0].seconds %}
    <table class="table table-sm mb-0">
      <thead><tr>
        <th style="width:50%">Программа</th>
        <th>Время</th>
        <th></th>
      </tr></thead>
      <tbody>
      {% for a in report.totals.top_apps %}
        <tr>
          <td>{{ a.app }}</td>
          <td style="white-space:nowrap">{{ a.seconds | dur }}</td>
          <td style="width:40%">
            <span class="app-bar" style="width: {{ (a.seconds / max_app_seconds * 100) if max_app_seconds else 0 }}%"></span>
          </td>
        </tr>
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
              День
              <span class="hint" data-bs-toggle="tooltip" title="Дата в выбранном часовом поясе. Если сессия пересекает полночь, она целиком относится к дню старта.">?</span>
            </th>
            <th>Сотрудник</th>
            <th style="width:80px">
              Сессий
              <span class="hint" data-bs-toggle="tooltip" title="Сколько раз сотрудник нажимал «Начать работу» в этот день.">?</span>
            </th>
            <th style="width:110px">
              Длительность
              <span class="hint" data-bs-toggle="tooltip" title="Суммарное время всех сессий за день.">?</span>
            </th>
            <th style="width:100px">
              Клавиатура
              <span class="hint" data-bs-toggle="tooltip" title="Оценка активной работы на клавиатуре.">?</span>
            </th>
            <th style="width:100px">
              Мышь
              <span class="hint" data-bs-toggle="tooltip" title="Оценка активной работы с мышью.">?</span>
            </th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% elif report.group_by == 'employees' %}
            <th>Сотрудник</th>
            <th style="width:90px">
              Дней
              <span class="hint" data-bs-toggle="tooltip" title="Сколько разных календарных дней сотрудник работал за период.">?</span>
            </th>
            <th style="width:80px">Сессий</th>
            <th style="width:110px">Длительность</th>
            <th style="width:100px">Клавиатура</th>
            <th style="width:100px">Мышь</th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% elif report.group_by == 'computers' %}
            <th>Компьютер</th>
            <th style="width:80px">Сессий</th>
            <th style="width:110px">Длительность</th>
            <th style="width:100px">Клавиатура</th>
            <th style="width:100px">Мышь</th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% else %}
            <th style="width:120px">День</th>
            <th>Сотрудник</th>
            <th>Компьютер</th>
            <th style="width:140px">
              Начало
              <span class="hint" data-bs-toggle="tooltip" title="Момент нажатия «Начать работу». Часовой пояс — выбранный в форме.">?</span>
            </th>
            <th style="width:140px">Конец</th>
            <th style="width:110px">Длительность</th>
            <th style="width:100px">Клавиатура</th>
            <th style="width:100px">Мышь</th>
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
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td>{{ r.keyboard | dur }}</td>
            <td>{{ r.mouse | dur }}</td>
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
                  <div class="mt-2" style="min-width:520px">
                    <table class="table table-sm mb-0">
                      <thead><tr><th>Начало</th><th>Конец</th><th>Длит.</th><th>Авар.</th></tr></thead>
                      <tbody>
                      {% for s in r.sessions %}
                        <tr>
                          <td>{{ s.start_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.end_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.duration | dur }}</td>
                          <td>{% if s.abnormal %}<span class="badge bg-warning text-dark">да</span>{% endif %}</td>
                        </tr>
                      {% endfor %}
                      </tbody>
                    </table>
                  </div>
                </details>
              </td>
            {% endif %}
          </tr>
        {% elif report.group_by == 'employees' %}
          <tr>
            <td>{{ r.employee_name }}</td>
            <td class="text-center">{{ r.days_count }}</td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td>{{ r.keyboard | dur }}</td>
            <td>{{ r.mouse | dur }}</td>
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
                  <div class="mt-2" style="min-width:520px">
                    <table class="table table-sm mb-0">
                      <thead><tr><th>День</th><th>Начало</th><th>Конец</th><th>Длит.</th></tr></thead>
                      <tbody>
                      {% for s in r.sessions %}
                        <tr>
                          <td>{{ s.date_local.strftime('%d.%m.%Y') }}</td>
                          <td>{{ s.start_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.end_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.duration | dur }}</td>
                        </tr>
                      {% endfor %}
                      </tbody>
                    </table>
                  </div>
                </details>
              </td>
            {% endif %}
          </tr>
        {% elif report.group_by == 'computers' %}
          <tr>
            <td>{{ r.computer_name }}</td>
            <td class="text-center">{{ r.sessions_count }}</td>
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td>{{ r.keyboard | dur }}</td>
            <td>{{ r.mouse | dur }}</td>
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
                  <div class="mt-2" style="min-width:520px">
                    <table class="table table-sm mb-0">
                      <thead><tr><th>День</th><th>Сотрудник</th><th>Начало</th><th>Длит.</th></tr></thead>
                      <tbody>
                      {% for s in r.sessions %}
                        <tr>
                          <td>{{ s.date_local.strftime('%d.%m.%Y') }}</td>
                          <td>{{ s.employee_name }}</td>
                          <td>{{ s.start_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.duration | dur }}</td>
                        </tr>
                      {% endfor %}
                      </tbody>
                    </table>
                  </div>
                </details>
              </td>
            {% endif %}
          </tr>
        {% else %}
          <tr>
            <td>{{ r.date.strftime('%d.%m.%Y') }}</td>
            <td>{{ r.employee_name }}</td>
            <td>{{ r.computer_name }}</td>
            <td>{{ r.start_local.strftime('%H:%M:%S') }}</td>
            <td>{{ r.end_local.strftime('%H:%M:%S') }}</td>
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td>{{ r.keyboard | dur }}</td>
            <td>{{ r.mouse | dur }}</td>
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
      длительность {{ report.totals.duration | dur }},
      клавиатура {{ report.totals.keyboard | dur }},
      мышь {{ report.totals.mouse | dur }}
    </div>
  </div>
</div>

<a class="btn btn-outline-secondary mt-3" href="/admin/reports">? Новый отчёт</a>

{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\report_result.html", $report_result_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  report_result.html" -ForegroundColor Green

Write-Host "`n=== Скрипт 2 завершён ===" -ForegroundColor Cyan
Ожидаемый вывод:
text
OK  base.html
OK  reports.html
OK  report_result.html

=== Скрипт 2 завершён ===
________________________________________
Скрипт 3 — проверка + пересборка Docker
powershell
$ErrorActionPreference = "Stop"

Write-Host "`n--- Проверка файлов ---" -ForegroundColor Cyan

$files = @(
    "D:\tracker\server\config.py",
    "D:\tracker\server\requirements.txt",
    "D:\tracker\server\web_admin.py",
    "D:\tracker\server\templates\base.html",
    "D:\tracker\server\templates\reports.html",
    "D:\tracker\server\templates\report_result.html"
)
foreach ($f in $files) {
    if (Test-Path $f) {
        $size = (Get-Item $f).Length
        Write-Host ("  OK  {0}  ({1} bytes)" -f $f, $size) -ForegroundColor Green
    } else {
        Write-Host ("  MISSING  {0}" -f $f) -ForegroundColor Red
    }
}

Write-Host "`n--- Проверка синтаксиса Python ---" -ForegroundColor Cyan

docker compose exec -T api python -c "import ast; ast.parse(open('/app/server/config.py').read()); ast.parse(open('/app/server/web_admin.py').read()); print('SYNTAX OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  (контейнер ещё не пересобран — пересоберём)" -ForegroundColor Yellow
}

Write-Host "`n--- Пересборка Docker ---" -ForegroundColor Cyan
Set-Location D:\tracker
docker compose down
docker compose up -d --build

Start-Sleep -Seconds 25

Write-Host "`n--- Статус контейнеров ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Логи API (последние 40 строк) ---" -ForegroundColor Cyan
docker compose logs api --tail=40

Write-Host "`nГотово. Откройте: https://localhost/admin/reports" -ForegroundColor Green
________________________________________
Что должно получиться
После скрипта 3:
Статус контейнеров — все Up.
Логи API — без Traceback.
Откройте https://localhost/admin/reports:
Кнопки быстрых периодов: Сегодня, Вчера, 7 дней, 30 дней, Этот месяц, Прошлый месяц.
Выпадающая группировка: Дни ? Сотрудник (по умолчанию).
Выбор часового пояса: Москва (UTC+3) по умолчанию.
Значки ? рядом с полями — наведите, появится подсказка.
Нажмите «Этот месяц» ? «Сформировать отчёт».
В отчёте:
Время в московском поясе, не UTC.
Строки — по дням и сотрудникам.
Топ программ сверху.
Чекбокс «Разворачивать детали» открывает подсказки в группах.
________________________________________
Если что-то не так
500 при открытии /admin/reports ? пришлите docker compose logs api --tail=60.
TemplateNotFound ? проверьте:
powershell
docker compose exec -T api ls /app/server/templates
Должно быть 9 файлов .html.
Ошибка tzdata или ZoneInfoNotFoundError ? пересоберите образ (--build), пакет tzdata из новых requirements.txt должен встать.
Синтаксическая ошибка в Python ? проверьте:
powershell
docker compose exec -T api python -c "import ast; ast.parse(open('/app/server/web_admin.py').read()); print('OK')"
Запускайте скрипты по очереди и присылайте результат — если что-то упадёт, сразу поправим.
Этот ответ сгенерирован AI, только для справки.
не все вкладки открываются например компьютеры, токены, вкладки пишет Внутренняя ошибка сервера
Проблема: страницы /admin/computers, /admin/tokens, /admin/audit падают с 500. Причина скорее всего в шаблонах: они используют фильтр dt (устаревший, я его убрал из web_admin.py), но шаблоны у них старые. Я заменил только base.html, reports.html и report_result.html. А остальные шаблоны (computers.html, tokens.html, audit.html) остались со старым фильтром | dt.
Также я в web_admin.py убрал фильтр dt, оставил только dur. А старые шаблоны используют {{ c.registered_at | dt }}, {{ t.expires_at | dt }}, {{ a.created_at | dt }} и т.д.
Нужно либо вернуть фильтр dt, либо обновить шаблоны. Проще — вернуть фильтр dt, но он должен использовать tz. Проблема в том, что фильтр не знает tz.
Можно сделать фильтр через глобальную переменную или передавать tz в контекст шаблона. Проще всего — добавить фильтр dt, который использует settings.report_timezone.
Давайте я добавлю в web_admin.py:
python
def _fmt_dt_global(dt):
    if dt is None:
        return "—"
    try:
        tz = ZoneInfo(settings.report_timezone)
    except Exception:
        tz = ZoneInfo("UTC")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")

templates.env.filters["dt"] = _fmt_dt_global
Это решит проблему с шаблонами computers.html, tokens.html, audit.html, dashboard.html.
Также нужно проверить dashboard.html — там тоже может быть | dt.
Давайте дам PowerShell-скрипт, который перезапишет web_admin.py с добавленным фильтром, а также проверим, что все шаблоны на месте.
Но проще — дать патч на web_admin.py. Проблема в том, что web_admin.py большой. Можно сделать маленький патч через PowerShell, который найдёт строку templates.env.filters["dur"] = _fmt_dur и добавит после неё фильтр dt.
Или дать полный скрипт перезаписи web_admin.py. Пусть будет патч — так короче.
Хотя, проще всего — сказать пользователю перезаписать web_admin.py целиком, но он длинный. Сделаю через поиск и вставку строки.
Решение:
Добавить в web_admin.py глобальный фильтр dt.
Проверить, что все шаблоны содержат только те переменные, которые им передаются.
Давайте через PowerShell сделаю добавление. Найдём строку templates.env.filters["dur"] = _fmt_dur и заменим на блок с двумя фильтрами.
Actually, лучше через скрипт: читаем файл, заменяем одну строку на блок из трёх строк.
powershell
$path = "D:\tracker\server\web_admin.py"
$content = Get-Content $path -Raw -Encoding UTF8
$old = 'templates.env.filters["dur"] = _fmt_dur'
$new = @'
def _fmt_dt_global(dt):
    if dt is None:
        return "—"
    try:
        tz = ZoneInfo(settings.report_timezone)
    except Exception:
        tz = ZoneInfo("UTC")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")


templates.env.filters["dur"] = _fmt_dur
templates.env.filters["dt"] = _fmt_dt_global
'@
$content = $content.Replace($old, $new)
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Это добавит функцию и регистрацию фильтра.
Также надо убедиться, что dashboard.html не сломан. И другие шаблоны.
Проверю: в dashboard.html я уже передаю tz в контекст, но использую {{ c.registered_at | dt }} — фильтр dt.
В компьютерах тоже {{ c.last_seen_at | dt }}.
В tokens {{ t.expires_at | dt }} и {{ t.used_at | dt }}.
В audit {{ l.created_at | dt }}.
Все они будут работать с новым глобальным фильтром dt.
Но лучше всё-таки убедиться, что все шаблоны на месте. Скрипт должен проверить.
Также нужно понять, не падают ли какие-то другие шаблоны. Логи покажут.
Мне нужно дать скрипт, который:
Патчит web_admin.py — добавляет фильтр dt.
Проверяет наличие всех 9 шаблонов.
Пересобирает docker.
Также важно: возможно, падают и другие страницы из-за отсутствующих шаблонов. Список шаблонов:
base.html ? (обновил)
login.html (не обновлял — старый, но не падает, т.к. логин работал)
dashboard.html (не обновлял — старый, но должен работать)
employees.html (не обновлял — старый, но, возможно, падает из-за фильтра или чего-то ещё)
computers.html (не обновлял — падает из-за | dt)
tokens.html (не обновлял — падает из-за | dt)
reports.html ?
report_result.html ?
audit.html (не обновлял — падает из-за | dt)
Значит, после патча фильтра dt должны заработать: computers, tokens, audit, dashboard, employees (если он не падает по другой причине).
Дам скрипт.
Причина: в шаблонах используется фильтр dt, который я удалил
Я убрал его из web_admin.py при переходе на локализованные _fmt_dt_local, но шаблоны dashboard.html, computers.html, tokens.html, audit.html продолжают вызывать {{ ... | dt }}. Jinja падает с TemplateAssertionError: No filter named 'dt' ? FastAPI отдаёт 500.
Правим это одним патчем — вернём фильтр dt обратно, но уже с автоматической конвертацией в Europe/Moscow.
________________________________________
Скрипт — патч web_admin.py + проверка шаблонов + пересборка
Скопируйте весь блок целиком в PowerShell и нажмите Enter:
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"
$templatesDir = "$serverDir\templates"

