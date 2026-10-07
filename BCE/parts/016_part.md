# ============================================================

*Часть 16 из 100. Источник: `BCE.md`.*

[◀ ============================================================](015_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](017_part.md)

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
        Отработано (эффективно)
        <span class="hint" data-bs-toggle="tooltip" title="Суммарное время от первой до последней активности в сессии. Большие паузы (простой) не учитываются.">?</span>
      </div>
      <div class="fs-4">{{ report.totals.duration | dur }}</div>
    </div></div>
  </div>
  <div class="col-md-3">
    <div class="card"><div class="card-body">
      <div class="text-muted small">
        Полное время сессий
        <span class="hint" data-bs-toggle="tooltip" title="От «Начать работу» до «Конец работы». Включает простои (обед, отход).">?</span>
      </div>
      <div class="fs-4 text-muted">{{ report.totals.full_duration | dur }}</div>
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
    <span class="hint" data-bs-toggle="tooltip" title="Время, клавиатура и мышь, разбитые по активным программам. Показывает, в какой программе сотрудник реально работал.">?</span>
  </div>
  <div class="card-body">
    {% set max_app_seconds = report.totals.top_apps[0].seconds %}
    <table class="table table-sm mb-0">
      <thead><tr>
        <th style="width:40%">Программа</th>
        <th>Время</th>
        <th>
          Клавиатура
          <span class="hint" data-bs-toggle="tooltip" title="Сколько секунд в этой программе была активность клавиатуры (по 5 сек за событие).">?</span>
        </th>
        <th>
          Мышь
          <span class="hint" data-bs-toggle="tooltip" title="Сколько секунд в этой программе была активность мыши (клики/скролл).">?</span>
        </th>
        <th style="width:25%"></th>
      </tr></thead>
      <tbody>
      {% for a in report.totals.top_apps %}
        <tr>
          <td>{{ a.app }}</td>
          <td style="white-space:nowrap">{{ a.seconds | dur }}</td>
          <td>{{ a.keyboard | dur }}</td>
          <td>{{ a.mouse | dur }}</td>
          <td>
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
              Рабочий день
              <span class="hint" data-bs-toggle="tooltip" title="Рабочий день с учётом настройки «Начало рабочего дня». Сессии, начавшиеся до этого часа, относятся к предыдущему дню.">?</span>
            </th>
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">
              Отработано
              <span class="hint" data-bs-toggle="tooltip" title="Эффективное время — от первой до последней активности в сессиях за день.">?</span>
            </th>
            <th style="width:110px">
              Полное
              <span class="hint" data-bs-toggle="tooltip" title="Суммарная длительность всех сессий за день, включая простои.">?</span>
            </th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% elif report.group_by == 'employees' %}
            <th>Сотрудник</th>
            <th style="width:100px">1C ID</th>
            <th style="width:80px">Дней</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Полное</th>
            {% if show_abnormal %}<th style="width:90px">Аварийное</th>{% endif %}
            {% if expand_details %}<th style="width:60px"></th>{% endif %}
          {% elif report.group_by == 'computers' %}
            <th>Компьютер</th>
            <th style="width:70px">Сессий</th>
            <th style="width:110px">Отработано</th>
            <th style="width:110px">Полное</th>
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
            <th style="width:100px">Полное</th>
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
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td class="text-muted">{{ (r.sessions | sum(attribute='full_duration')) | dur }}</td>
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
                      <thead><tr><th>Начало</th><th>Конец</th><th>Отработано</th><th>Полное</th><th>Авар.</th></tr></thead>
                      <tbody>
                      {% for s in r.sessions %}
                        <tr>
                          <td>{{ s.start_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.end_local.strftime('%H:%M:%S') }}</td>
                          <td>{{ s.effective_duration | dur }}</td>
                          <td class="text-muted">{{ s.full_duration | dur }}</td>
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
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td class="text-muted">{{ (r.sessions | sum(attribute='full_duration')) | dur }}</td>
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
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td class="text-muted">{{ (r.sessions | sum(attribute='full_duration')) | dur }}</td>
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
            <td><strong>{{ r.duration | dur }}</strong></td>
            <td class="text-muted">{{ r.full_duration | dur }}</td>
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
      отработано {{ report.totals.duration | dur }},
      полное {{ report.totals.full_duration | dur }}
    </div>
  </div>
</div>

<a class="btn btn-outline-secondary mt-3" href="/admin/reports">? Новый отчёт</a>

{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\report_result.html", $report_result_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  report_result.html" -ForegroundColor Green

Write-Host "`n--- Проверка файлов ---" -ForegroundColor Cyan
foreach ($f in @("reports.html", "report_result.html")) {
    $p = Join-Path $templatesDir $f
    if (Test-Path $p) {
        Write-Host ("  OK  {0}" -f $f) -ForegroundColor Green
    } else {
        Write-Host ("  MISSING  {0}" -f $f) -ForegroundColor Red
    }
}
________________________________________
Скрипт 3 — клиент: авто-закрытие «висящих» сессий
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

# ============================================================
# Патч db.py — добавляем auto_close_idle_session
# ============================================================
Write-Host "--- Патч db.py ---" -ForegroundColor Cyan

$dbPath = "$clientDir\db.py"
$dbContent = [System.IO.File]::ReadAllText($dbPath, [System.Text.UTF8Encoding]::new($false))

# Проверяем, есть ли уже функция
if ($dbContent.Contains("def auto_close_idle_session")) {
    Write-Host "  Уже пропатчен — пропускаем" -ForegroundColor Yellow
} else {
    $addition = @'

# --- Авто-закрытие «висящих» сессий ---

def auto_close_idle_session(idle_minutes: int = 30) -> str | None:
    """
    Если активная сессия не имела активности дольше idle_minutes,
    закрывает её временем последней активности и помечает abnormal=1.
    Возвращает UID закрытой сессии, либо None.
    """
    active = get_meta("active_session")
    if not active:
        return None

    last = get_meta("last_activity")
    if not last:
        return None

    try:
        last_dt = datetime.fromisoformat(last)
    except ValueError:
        return None
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if (now - last_dt).total_seconds() < idle_minutes * 60:
        return None

    # Закрываем сессию временем последней активности, а не «сейчас»
    end_iso = last_dt.isoformat()
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=1, synced=0 "
        "WHERE session_uid=? AND session_end IS NULL",
        (end_iso, active),
    )
    set_meta("active_session", "")
    log.warning("Auto-closed idle session %s (last activity %s)",
                active, end_iso)
    return active
'@

    # Добавляем в конец файла
    $newContent = $dbContent + $addition
    [System.IO.File]::WriteAllText($dbPath, $newContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  auto_close_idle_session добавлена в db.py" -ForegroundColor Green
}

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'$dbPath', encoding='utf-8').read()); print('  db.py SYNTAX OK')"

# ============================================================
# Патч main.py — таймер авто-закрытия + периодическая отправка
# ============================================================
Write-Host "`n--- Патч main.py ---" -ForegroundColor Cyan

$mainPath = "$clientDir\main.py"
$mainContent = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($mainContent.Contains("_idle_timer")) {
    Write-Host "  Уже пропатчен — пропускаем" -ForegroundColor Yellow
} else {
    # 1) Импорт QTimer
    $mainContent = $mainContent.Replace(
        "from PyQt6.QtCore import QSocketNotifier, QThread",
        "from PyQt6.QtCore import QSocketNotifier, QThread, QTimer"
    )

    # 2) Импорт IDLE_CLOSE_MINUTES из config
    $mainContent = $mainContent.Replace(
        "from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH",
        "from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH`nfrom .config import IDLE_CLOSE_MINUTES"
    )

    # 3) Запускаем таймер в _start после запуска sync-воркера
    $oldBlock = @'
        # Sync-воркер работает всегда — чтобы отправлять старые сессии и записи
        self._start_sync_worker()

        # Проверка обновлений
        self._check_updates()
'@

    $newBlock = @'
        # Sync-воркер работает всегда — чтобы отправлять старые сессии и записи
        self._start_sync_worker()

        # Таймер авто-закрытия «висящих» сессий (раз в минуту)
        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(60 * 1000)  # 1 минута
        self._idle_timer.timeout.connect(self._check_idle_session)
        self._idle_timer.start()

        # Проверка обновлений
        self._check_updates()
'@

    $mainContent = $mainContent.Replace($oldBlock, $newBlock)

    # 4) Добавляем метод _check_idle_session в класс MainWindow
    $methodToInsert = @'
    def _check_idle_session(self):
        """
        Раз в минуту проверяем: если активная сессия давно без активности,
        закрываем её автоматически временем последней активности.
        """
        try:
            closed_uid = db.auto_close_idle_session(IDLE_CLOSE_MINUTES)
            if closed_uid:
                log.info("Auto-closed idle session %s", closed_uid)
                self.session_uid = None
                self.session_label.setText("Сессия: авто-закрыта по бездействию")
                self.btn_start.setEnabled(True)
                self.btn_stop.setEnabled(False)
                self.status.setText("Сессия закрыта автоматически, отправляем на сервер…")
                if self.sync:
                    self.sync.trigger()
                # Останавливаем сборщик, если ещё работает
                self._stop_collector()
        except Exception:
            log.exception("_check_idle_session failed")

    # --- autostart ---
'@

    # Вставляем метод перед комментарием "# --- autostart ---"
    $mainContent = $mainContent.Replace("    # --- autostart ---", $methodToInsert)

    [System.IO.File]::WriteAllText($mainPath, $mainContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  main.py пропатчен" -ForegroundColor Green
}

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"

# ============================================================
# Добавляем IDLE_CLOSE_MINUTES в config.py клиента
