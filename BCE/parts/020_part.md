# ============================================================

*Часть 20 из 100. Источник: `BCE.md`.*

[◀ ============================================================](019_part.md) | [Оглавление](00_BCE_INDEX.md) | [date ▶](021_date.md)

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

# ---------- Client config ----------

@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    """Клиент подтягивает эту конфигурацию раз в 5 минут."""
    from .models import AppSetting as _AppSetting
    row = db.query(_AppSetting).filter(_AppSetting.key == "idle_close_minutes").first()
    try:
        idle = max(5, min(480, int(row.value))) if row else 30
    except (ValueError, TypeError):
        idle = 30
    return {"idle_close_minutes": idle}


# ---------- Version ----------
'@

    if ($content.Contains("# ---------- Version ----------")) {
        $content = $content.Replace("# ---------- Version ----------", $endpoint)
        [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "  OK  /api/v1/client-config добавлен" -ForegroundColor Green
    } else {
        Write-Host "  ОШИБКА: не найден маркер '# ---------- Version ----------'" -ForegroundColor Red
    }
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"
________________________________________
Скрипт 4 — клиент: db.py + sync.py + main.py
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

# ============================================================
# 1. db.py — добавляем get_idle_close_minutes
# ============================================================
Write-Host "--- db.py ---" -ForegroundColor Cyan
$dbPath = "$clientDir\db.py"
$dbContent = [System.IO.File]::ReadAllText($dbPath, [System.Text.UTF8Encoding]::new($false))

if ($dbContent.Contains("def get_idle_close_minutes")) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} else {
    $addition = @'

# --- Настройка idle-порога (получается с сервера) ---

def get_idle_close_minutes(default: int = 30) -> int:
    val = get_meta("idle_close_minutes")
    if val:
        try:
            return max(5, min(480, int(val)))
        except (ValueError, TypeError):
            pass
    return default
'@
    $dbContent = $dbContent + $addition
    [System.IO.File]::WriteAllText($dbPath, $dbContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  get_idle_close_minutes добавлена" -ForegroundColor Green
}
python -c "import ast; ast.parse(open(r'$dbPath', encoding='utf-8').read()); print('  db.py SYNTAX OK')"

# ============================================================
# 2. sync.py — подтягиваем client-config раз в 10 циклов
# ============================================================
Write-Host "`n--- sync.py ---" -ForegroundColor Cyan
$syncPath = "$clientDir\sync.py"
$syncContent = [System.IO.File]::ReadAllText($syncPath, [System.Text.UTF8Encoding]::new($false))

if ($syncContent.Contains("_fetch_client_config")) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} else {
    # 1) добавляем счётчик циклов в __init__
    $syncContent = $syncContent.Replace(
        "        self._running = False`n        self._wake = threading.Event()",
        "        self._running = False`n        self._wake = threading.Event()`n        self._cycles = 0"
    )

    # 2) добавляем вызов в run() перед wait
    $syncContent = $syncContent.Replace(
        "            # Спим SYNC_INTERVAL секунд, но можно разбудить через trigger()`n            self._wake.wait(timeout=SYNC_INTERVAL)",
        "            # Подтягиваем client-config раз в 10 циклов (примерно раз в 5 минут)`n            self._cycles += 1`n            if self._cycles % 10 == 1:`n                self._fetch_client_config()`n`n            # Спим SYNC_INTERVAL секунд, но можно разбудить через trigger()`n            self._wake.wait(timeout=SYNC_INTERVAL)"
    )

    # 3) добавляем метод _fetch_client_config перед _headers
    $method = @'
    def _fetch_client_config(self):
        """Забирает настройки с сервера (idle_close_minutes) и сохраняет в локальную БД."""
        try:
            r = http_client.get(f"{SERVER_URL}/api/v1/client-config",
                                headers=self._headers(), timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                idle = int(data.get("idle_close_minutes", 30))
                current = db.get_meta("idle_close_minutes")
                if str(idle) != current:
                    db.set_meta("idle_close_minutes", str(idle))
                    log.info("idle_close_minutes updated: %d", idle)
        except Exception as e:
            log.debug("client-config fetch failed: %s", e)

    def _headers(self):
'@
    $syncContent = $syncContent.Replace("    def _headers(self):", $method)

    [System.IO.File]::WriteAllText($syncPath, $syncContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  _fetch_client_config добавлена" -ForegroundColor Green
}
python -c "import ast; ast.parse(open(r'$syncPath', encoding='utf-8').read()); print('  sync.py SYNTAX OK')"

# ============================================================
# 3. main.py (клиент) — используем значение из БД
# ============================================================
Write-Host "`n--- client/main.py ---" -ForegroundColor Cyan
$mainPath = "$clientDir\main.py"
$mainContent = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$oldCall = "            closed_uid = db.auto_close_idle_session(IDLE_CLOSE_MINUTES)"
$newCall = "            idle = db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)`n            closed_uid = db.auto_close_idle_session(idle)"

if ($mainContent.Contains($newCall)) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} elseif ($mainContent.Contains($oldCall)) {
    $mainContent = $mainContent.Replace($oldCall, $newCall)
    [System.IO.File]::WriteAllText($mainPath, $mainContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  main.py использует значение из БД" -ForegroundColor Green
} else {
    Write-Host "  ВНИМАНИЕ: не найден вызов auto_close_idle_session(IDLE_CLOSE_MINUTES)" -ForegroundColor Yellow
    Write-Host "  Откройте client/main.py и найдите вручную строку с auto_close_idle_session" -ForegroundColor Yellow
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"

Write-Host "`n=== Все патчи клиента применены ===" -ForegroundColor Cyan
________________________________________
Скрипт 5 — пересборка и проверка
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

Write-Host "`n--- Проверка endpoint ---" -ForegroundColor Cyan
curl.exe -k https://localhost/api/v1/client-config

Write-Host "`n`nГотово." -ForegroundColor Green
Write-Host "Откройте:" -ForegroundColor Green
Write-Host "  https://localhost/admin/settings       — настройка idle-порога" -ForegroundColor Green
Write-Host "  https://localhost/admin/reports        — новая форма отчёта" -ForegroundColor Green
Write-Host "`nПерезапустите клиент:" -ForegroundColor Green
Write-Host "  cd D:\tracker" -ForegroundColor Green
Write-Host "  client\.venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "  python -m client.main" -ForegroundColor Green
________________________________________
Как это работает
Настройка idle-порога
Открыть /admin/settings
Изменить число (например, на 60)
Сохранить
Клиенты подхватят значение максимум через 5 минут (после следующего цикла sync)
Если клиент офлайн — подхватит при следующем выходе на связь
«Отработано» vs «Эффективно»
Пример для одного дня:
Сессия	Старт	Конец	Эффективно
1	09:00	13:00	3:30 (обед, паузы)
2	14:00	18:00	3:30
Отработано = 18:00 ? 09:00 = 9:00:00 (от старта первой до конца последней)
Эффективно = 3:30 + 3:30 = 7:00:00 (сумма без пауз)
Топ программ с разбивкой
В таблице «Топ программ за период» под каждой программой есть треугольник ? Кто работал в «PyCharm» — N сотр. Кликните — раскроется таблица с ФИО, 1C ID, временем, клавиатурой и мышью по каждому сотруднику.
Экспорт CSV/XLSX
9 колонок: группа, день, сотрудник, 1C ID, компьютер, сессий, отработано, эффективно, аварийных.
Итоговая строка внизу.
________________________________________
Проверка
/admin/settings — открывается, поле заполнено 30, при сохранении всплывает зелёная плашка.
/admin/reports — новая форма с подсказкой про колонки.
Сформировать отчёт «Этот месяц», группировка «Рабочие дни ? Сотрудник».
В таблице: 1C ID, Отработано (span), Эффективно (зелёное).
В топе программ: развернуть любую ? разбивка по сотрудникам.
Экспорт XLSX — колонок 9.
Если что-то падает — пришлите:
powershell
docker compose logs api --tail=60
и Get-Content "$env:APPDATA\Tracker\client.log" -Tail 40 -Encoding UTF8.
отлично всё работает. В клиентской программе когда начинается работа отображается сессия с такого времени. Вот это время не соответствует текущему пускай отображается реальное. Что можно, нужно вынести на панель клиентскую? если что то стоящие давай добавим. В связи с появлением в админской части вкладки настройка давай туда уберем Часовой пояс Начало рабочего дня. Какие еще есть переменные в нашей программе которые мы можем вынести в настройку? давай выведем. В отчётах в .xlsx выводятся столбцы Отработано (сек) Эффективно (сек) Пускай выводятся сразу в формате время часы минуты секунды что бы программа сразу понимала Рабочий день Пускай выводятся сразу в формате дата день месяц год что бы программа сразу понимала В отчётах должна быть возможность выбрать нескольких сотрудников двух, трёх, десяти. А что делать с уволенными сотрудниками? Наверное их нужно убрать в отдельный список или как правильно по ним может понадобится информация? А если будет 100 сотрудников наверное стоит добавить отделы и также добавить для фильтра в отчёты. Давай попробуем реализовать всё это. А какие у тебя есть еще предложения?
The user wants a lot of changes. Let me break this down carefully:
Client time display fix - session start time shows wrong time (probably UTC instead of local). Need to display real local time.
Client panel improvements - what to display on client panel.
Move Timezone and Workday start to admin settings - so they're not per-report but global settings.
Other settings to move - identify all configurable variables.
Excel export:
"Отработано (сек)" and "Эффективно (сек)" ? format as HH:MM:SS time
"Рабочий день" ? format as DD.MM.YYYY
Multi-select employees - allow choosing multiple employees in reports.
Fired employees - separate list, soft delete, keep history.
Departments - add departments for 100+ employees, filter by department in reports.
Plus my own suggestions.
This is a huge chunk of work. Let me organize it as:
Part 1: Client time display fix
In client/main.py, the _short_dt function uses UTC time from DB. Need to convert to local time.
Part 2: Client panel
Add to client panel:
Current server status
Last sync time
Records pending
Current session duration (live)
Idle status indicator
Menu buttons
Part 3: Admin settings page
Add to AppSetting-based settings:
report_timezone
workday_start_hour
activity_gap_minutes
idle_close_minutes (already there)
Part 4: Excel export formats
In _report_to_table, convert:
Durations to HH:MM:SS strings (openpyxl can also format as time)
Dates to DD.MM.YYYY
Actually for openpyxl, we can set the cell format via number_format, but easier to just write strings.
Part 5: Multi-select employees
Change employee_id from single select to multi-select (checkbox list or <select multiple>). Parse as list.
Part 6: Fired employees
Add filter tabs: Active / Fired / All. Employee page shows only active by default.
Part 7: Departments
New model Department, Employee.department_id, filter in reports, page to manage departments.
This is going to be LONG. Let me structure this as a multi-part response. I should probably focus on giving complete PowerShell scripts as before.
Let me think about what order to do this:
Actually, given the scope, I think I should:
Acknowledge everything
Ask if user wants to proceed step by step OR all at once
Give suggestions
Start with the most critical/simplest first
Actually no, the user asked to do it all. Let me just do it, but split into clear scripts and give explanations.
Let me organize:
Server changes:
models.py: add Department, Employee.department_id, Employee.fired_at
web_admin.py: settings page gets new fields, reports multi-select, department filter, filters for fired employees, Excel formatting
Templates: settings, employees (with departments and fired tab), reports (multi-select), report_result
New page: /admin/departments
Client changes:
main.py: fix time display, add panel widgets
Let me be strategic. This is huge. I'll produce:
Script 1: Server models + new admin pages for departments & settings
Script 2: Server web_admin.py (reports with multi-select, departments, fired employees, Excel formatting)
Script 3: Templates (base, settings, employees, departments, reports, report_result)
Script 4: Client main.py (time fix + panel)
Let me plan carefully.
________________________________________
Server models.py
Add:
python
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

# Employee:
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fired_at = Column(DateTime(timezone=True), nullable=True)
AppSetting keys:
idle_close_minutes (exists)
report_timezone (new)
workday_start_hour (new)
activity_gap_minutes (new)
Web_admin changes:
get_app_setting_int(db, key, default, min, max) helper.
Settings page: form with all 4 settings.
Employees page:
tabs: "Активные" (fired_at IS NULL), "Уволенные" (fired_at IS NOT NULL), "Все"
each row: ФИО, отдел, 1C ID
action: edit, fire/restore, deactivate
Departments page:
CRUD
Reports page:
employees: multi-select (use <select multiple> or checkbox list)
department filter
timezone comes from settings (global), workday_start comes from settings (global)
remove these from form (they're in settings now)
Excel formatting:
Format durations as HH:MM:SS
Format date as DD.MM.YYYY
Actually with openpyxl we can write the actual datetime.time or datetime.timedelta objects and set number format. But safest to write strings.
Actually, for Excel to "understand", better to write:
datetime.timedelta(seconds=X) with number_format [HH]:MM:SS
datetime.date with number_format DD.MM.YYYY
But that's more complex. Let me write strings that Excel understands as time — hmm, strings won't be treated as time. Better to write actual values with formats.
Let me do:
python
from datetime import timedelta, date
from openpyxl.styles import numbers
# ...
cell = ws.cell(row=r, column=c, value=timedelta(seconds=dur))
cell.number_format = '[HH]:MM:SS'
