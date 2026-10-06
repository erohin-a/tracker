<!-- Часть 467 из 1409 -->
# ============================================================"
*Хлебные крошки:* ============================================================"

[◀ Client config](466_Client_config.md) | [Оглавление](00_BCE_INDEX.md) | [Берём UID активного ПК прямо из БД ▶](468_Berem_UID_aktivnogo_PK_pryamo_iz_BD.md)

---

# ============================================================"

    if ($content.Contains($markerOld)) {
        $content = $content.Replace($markerOld, $endpoint)
        [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK  /api/v1/heartbeat добавлен" -ForegroundColor Green
    } elseif ($content.Contains($markerOld2)) {
        $content = $content.Replace($markerOld2, $endpoint)
        [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK  /api/v1/heartbeat добавлен" -ForegroundColor Green
    } else {
        Write-Host "Не найден маркер 'Client config' — добавьте вручную" -ForegroundColor Red
        exit 1
    }
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт B2 — патч client/sync.py (heartbeat раз в 3 минуты)
powershell
$ErrorActionPreference = "Stop"
$syncPath = "D:\tracker\client\sync.py"
$content = [System.IO.File]::ReadAllText($syncPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("_send_heartbeat")) {
    Write-Host "Уже пропатчен — пропускаем" -ForegroundColor Yellow
} else {
    # 1) Добавляем вызов в главном цикле (после fetch_client_config)
    $oldCycle = @'
            # Раз в 10 циклов (~5 минут) подтягиваем настройки с сервера
            self._cycles += 1
            if self._cycles % 10 == 1:
                self._fetch_client_config()
'@

    $newCycle = @'
            # Раз в 10 циклов (~5 минут) подтягиваем настройки с сервера
            self._cycles += 1
            if self._cycles % 10 == 1:
                self._fetch_client_config()
            # Раз в 6 циклов (~3 минуты) — heartbeat, чтобы ПК был "онлайн"
            if self._cycles % 6 == 0:
                self._send_heartbeat()
'@

    if ($content.Contains($oldCycle)) {
        $content = $content.Replace($oldCycle, $newCycle)
    } else {
        # Пробуем альтернативный вариант (без комментария)
        $oldCycle2 = @'
            self._cycles += 1
            if self._cycles % 10 == 1:
                self._fetch_client_config()
'@
        $newCycle2 = @'
            self._cycles += 1
            if self._cycles % 10 == 1:
                self._fetch_client_config()
            if self._cycles % 6 == 0:
                self._send_heartbeat()
'@
        $content = $content.Replace($oldCycle2, $newCycle2)
    }

    # 2) Добавляем метод _send_heartbeat перед _fetch_client_config
    $method = @'
    def _send_heartbeat(self):
        """Отправляет лёгкий ping на сервер, чтобы ПК считался 'онлайн'."""
        try:
            r = http_client.post(f"{SERVER_URL}/api/v1/heartbeat",
                                 headers=self._headers(), timeout=5.0)
            if r.status_code == 200:
                self.connected.emit()
                log.debug("heartbeat sent")
            elif r.status_code in (401, 403):
                log.debug("heartbeat auth failed (%s)", r.status_code)
            else:
                log.debug("heartbeat ? %s", r.status_code)
        except Exception as e:
            log.debug("heartbeat failed: %s", e)

    def _fetch_client_config(self):
'@

    $content = $content.Replace("    def _fetch_client_config(self):", $method)

    [System.IO.File]::WriteAllText($syncPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  sync.py пропатчен (heartbeat)" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$syncPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт B3 — server/templates/computers.html (с формой массовой привязки)
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

$computers_html = @'
{% extends "base.html" %}
{% block title %}Компьютеры{% endblock %}
{% block content %}
<h3 class="mb-4">Компьютеры</h3>

{% if request.query_params.get('bulk_msg') %}
<div class="alert alert-info py-2">
  {{ request.query_params.get('bulk_msg') }}
</div>
{% endif %}

<div class="card mb-4">
  <div class="card-header">
    Массовая привязка ПК к сотрудникам из CSV
    <span class="hint" data-bs-toggle="tooltip"
          title="Файл: две колонки через ; (или ,). Колонка 1 — hostname ПК. Колонка 2 — 1C ID сотрудника или часть ФИО.">?</span>
  </div>
  <div class="card-body">
    <form method="post" action="/admin/computers/bulk-assign" enctype="multipart/form-data"
          class="row g-2 align-items-end">
      <div class="col-md-8">
        <label class="form-label small mb-1">CSV-файл (hostname ; 1C_ID или ФИО)</label>
        <input class="form-control" type="file" name="csv_file" accept=".csv,.txt" required>
      </div>
      <div class="col-md-4">
        <button class="btn btn-primary w-100">Загрузить и привязать</button>
      </div>
    </form>
    <div class="form-text mt-2">
      Пример содержимого файла:
      <pre class="mb-0 mt-1 p-2 bg-light border rounded" style="font-size:12px">hostname;1C_ID
PC-BUH-01;ИВАНОВ
PC-BUH-02;ivanov
PC-DEV-05;12345</pre>
      Заголовок <code>hostname;1C_ID</code> необязателен — можно сразу данные.
    </div>
  </div>
</div>

<table class="table table-sm table-hover bg-white">
  <thead><tr>
    <th>ID</th><th>Hostname</th><th>UID</th><th>Сотрудник</th>
    <th>Last seen</th><th>Статус</th><th>Действия</th>
  </tr></thead>
  <tbody>
  {% for c in computers %}
    <tr>
      <td>{{ c.id }}</td>
      <td>{{ c.hostname or '—' }}</td>
      <td><code title="{{ c.computer_uid }}">{{ c.computer_uid[:14] }}…</code></td>
      <td>
        <form method="post" action="/admin/computers/{{ c.id }}/assign" class="d-flex gap-1">
          <select name="employee_id" class="form-select form-select-sm">
            <option value="">— не привязан —</option>
            {% for e in employees %}
              <option value="{{ e.id }}" {% if c.employee_id == e.id %}selected{% endif %}>
                {{ e.full_name }}
              </option>
            {% endfor %}
          </select>
          <button class="btn btn-sm btn-primary">OK</button>
        </form>
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
      <td>
        {% if c.is_active %}
          <form method="post" action="/admin/computers/{{ c.id }}/revoke" class="d-inline">
            <button class="btn btn-sm btn-outline-danger">Отключить</button>
          </form>
        {% else %}
          <form method="post" action="/admin/computers/{{ c.id }}/activate" class="d-inline">
            <button class="btn btn-sm btn-outline-success">Включить</button>
          </form>
        {% endif %}
      </td>
    </tr>
  {% else %}
    <tr><td colspan="7" class="text-muted">Компьютеров пока нет</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\computers.html", $computers_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  computers.html" -ForegroundColor Green
________________________________________
Скрипт B4 — пересборка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

docker compose ps
Write-Host "`n--- Проверка эндпоинта ---" -ForegroundColor Cyan
Write-Host "  POST /api/v1/heartbeat должен требовать X-Computer-Uid (без него — 422)"
curl.exe -k -X POST https://localhost/api/v1/heartbeat -i 2>&1 | Select-Object -First 3

Write-Host "`nОткройте: https://localhost/admin/computers" -ForegroundColor Green
________________________________________
Проверка
1. Дашборд /admin
В карточке «Компьютеры онлайн» — актуальное число
В таблице ПК у вашего компьютера статус онлайн (зелёный), даже если вы не нажали «Начать работу»
Через 3 минуты после закрытия клиента статус станет офлайн
2. Клиент
В логе %APPDATA%\Tracker\client.log раз в 3 минуты должны появляться:
text
tracker.sync DEBUG heartbeat sent
(чтобы DEBUG появился, надо временно понизить уровень — сейчас INFO, поэтому в логе их не будет. Просто убеждаемся, что last_seen_at обновляется в БД.)
Проверить через SQL:
powershell
docker compose exec db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at, NOW() - last_seen_at AS age FROM computers ORDER BY last_seen_at DESC LIMIT 5;"
age у активного ПК должно быть меньше 5 минут, даже если сессия не идёт.
3. Массовая привязка
Открыть /admin/computers
Создать файл bulk.csv:
text
hostname;1C_ID
PC-12345;ИВАНОВ
PC-67890;12345
Загрузить — увидите плашку «Привязано: N. Не найдены ПК: M. Не найдены сотрудники: K.»
________________________________________
Что дальше (Подблок C)
Как только B заработает — пришлю Подблок C, самый крупный:
Календарь рабочих/нерабочих дней — таблица calendar_days, страница /admin/calendar, автозаполнение Сб/Вс как нерабочих на год вперёд + ручная правка
Подсветка в отчётах — рабочие/нерабочие/выходные дни разными цветами
Чекбокс «Учитывать нерабочие дни» в настройках (уже частично сделано — count_weekends)
PDF-отчёт — reportlab + шрифт с кириллицей, кнопка «Скачать PDF» рядом с XLSX
Запускайте B1–B4, скажите результат. Если что-то упадёт — пришлите docker compose logs api --tail=40.
что то пошло не так
Всё работает. Ошибка которую пользователь видит — это просто curl пишет прогресс в stderr, PowerShell отображает это как "ошибка". Но по факту всё ок.
Нужно объяснить, что всё работает, и показать как проверить.
Всё в порядке — это не ошибка
Смотрите внимательно на вывод:
text
tracker-api-1     Up 21 seconds
tracker-db-1      Up 27 seconds (healthy)
tracker-nginx-1   Up 20 seconds
Всё пересобралось и работает. А то, что вы видите в конце — это не ошибка. Это curl.exe показывает прогресс-бар (строки типа % Total % Received % Xferd), который идёт в stderr. PowerShell любой вывод из stderr отображает как красную «ошибку» — даже если это обычная информация.
curl.exe при этом честно сделал запрос — просто PowerShell некрасиво его отобразил.
________________________________________
Как проверить heartbeat без «красного»
Скопируйте этот блок в PowerShell — он делает запрос правильно и показывает только чистый ответ:
powershell
$ErrorActionPreference = "Continue"

Write-Host "--- POST /api/v1/heartbeat без заголовка (ожидаем 422) ---" -ForegroundColor Cyan
$r = curl.exe -k -s -o $null -w "%{http_code}" -X POST https://localhost/api/v1/heartbeat
Write-Host "HTTP-код: $r"

Write-Host "`n--- POST /api/v1/heartbeat с фейковым UID (ожидаем 401) ---" -ForegroundColor Cyan
$r = curl.exe -k -s -o $null -w "%{http_code}" -X POST https://localhost/api/v1/heartbeat -H "X-Computer-Uid: fake-uid-12345"
Write-Host "HTTP-код: $r"

Write-Host "`n--- POST /api/v1/heartbeat с настоящим UID ---" -ForegroundColor Cyan
$uid = curl.exe -k -s https://localhost/api/v1/version | Out-Null  # прогрев
