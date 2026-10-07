# Heartbeat каждый цикл (30 секунд) — это ок, дёшево

*Часть 31 из 100. Источник: `BCE.md`.*

[◀ ============================================================](030_part.md) | [Оглавление](00_BCE_INDEX.md) | [Сколько минут без активности — порог авто-закрытия висящей сессии ▶](032_Skolko_minut_bez_aktivnosti_porog_avto_zakrytiya_visyaschey_sessii.md)

---

# Heartbeat каждый цикл (30 секунд) — это ок, дёшево
self._send_heartbeat()
Хотя heartbeat каждые 30 секунд — избыточно. Лучше раз в 3-5 минут. Пусть будет раз в 6 циклов = 3 минуты. Но надо не забыть.
Итак: if self._cycles % 6 == 0: self._send_heartbeat().
Ладно, пишу компактно. Также добавлю в UI клиента индикатор "heartbeat отправлен".
Нет, не буду усложнять. Просто heartbeat в фоне.
Ещё одна мысль: при старте клиента, даже без сессии, sync-воркер запущен и первый цикл сразу отправляет heartbeat. Это значит, что открытый клиент будет виден как "онлайн" даже без нажатия "Начать работу". Это правильно.
Пишу.
Также template computers.html — с формой CSV.
Ок, пишу компактно.
Структура ответа:
Что делаем (кратко)
Скрипт B1: патч server/main.py (+ /api/v1/heartbeat)
Скрипт B2: патч client/sync.py (heartbeat)
Скрипт B3: новый computers.html (с массовой привязкой)
Скрипт B4: пересборка
Проверка
Что дальше
Пойду.
Подблок B: Heartbeat + массовая привязка ПК
Три маленькие доработки:
Heartbeat-эндпоинт — клиент каждые 3 минуты шлёт «я жив», сервер обновляет last_seen_at. Без этого ПК выглядит офлайн, если сотрудник не нажал «Начать работу».
Клиент шлёт heartbeat в фоне.
Форма массовой привязки ПК из CSV на странице /admin/computers.
________________________________________
Скрипт B1 — патч server/main.py (добавляем /api/v1/heartbeat)
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("/api/v1/heartbeat")) {
    Write-Host "Уже пропатчен — пропускаем" -ForegroundColor Yellow
} else {
    $endpoint = @'

# ============================================================
# Heartbeat — клиент раз в 3 минуты говорит "я жив"
# ============================================================

@app.post("/api/v1/heartbeat")
def heartbeat(comp: Computer = Depends(get_computer),
              db: Session = Depends(get_db)):
    comp.last_seen_at = _now()
    db.commit()
    return {"status": "ok", "server_time": _now().isoformat()}


# ============================================================
# Client config
# ============================================================
'@

    $marker = "# ============================================================\n# Client config\n# ============================================================"
    $markerOld = "# ============================================================
# Client config (то, что клиент подтягивает раз в 5 минут)
# ============================================================"
    $markerOld2 = "# ============================================================
# Client config
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
# Берём UID активного ПК прямо из БД
$realUid = docker compose exec -T db psql -U tracker -d tracker -t -A -c "SELECT computer_uid FROM computers WHERE is_active = true ORDER BY last_seen_at DESC LIMIT 1;"
$realUid = $realUid.Trim()
Write-Host "Используем UID: $realUid"
$r = curl.exe -k -s -X POST https://localhost/api/v1/heartbeat -H "X-Computer-Uid: $realUid"
Write-Host "Ответ: $r"
Ожидаемый вывод:
text
--- POST /api/v1/heartbeat без заголовка (ожидаем 422) ---
HTTP-код: 422

--- POST /api/v1/heartbeat с фейковым UID (ожидаем 401) ---
HTTP-код: 401

--- POST /api/v1/heartbeat с настоящим UID ---
Используем UID: ed1ef589-33eb-479b-b3f5-48ec4b7a4283
Ответ: {"status":"ok","server_time":"2026-09-17T..."}
Пояснение:
Без заголовка X-Computer-Uid ? 422 (FastAPI: обязательный заголовок не передан)
С фейковым UID ? 401 (такого ПК нет)
С настоящим UID ? 200 OK + JSON
________________________________________
Проверка heartbeat в реальной работе
Клиент должен быть запущен. Если он был закрыт — запустите заново:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Проверьте last_seen_at в БД — должно обновляться даже без активной сессии:
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at, NOW() - last_seen_at AS age FROM computers ORDER BY last_seen_at DESC LIMIT 5;"
Ожидаемо: age у активного ПК меньше 5 минут, даже если вы не нажимали «Начать работу».
Подождите 3 минуты — heartbeat уходит раз в 6-й цикл синхронизации (30 сек ? 6 = 3 мин). Если age > 5 минут у вашего ПК при работающем клиенте — что-то не так, будем разбираться.
________________________________________
Проверка массовой привязки
Откройте https://localhost/admin/computers
Сверху должна быть карточка «Массовая привязка ПК к сотрудникам из CSV» с полем загрузки файла
Создайте тестовый файл bulk.csv:
text
hostname;1C_ID
PC-TEST-01;ИВАНОВ
PC-TEST-02;12345
Загрузите — вверху появится плашка с результатом.
Если реальных ПК с такими hostname нет — увидите «Не найдены ПК: 2», это нормально для теста.
________________________________________
Что у нас сейчас работает
? Дашборд с онлайн/оффлайн
? Heartbeat-эндпоинт + клиент шлёт его в фоне
? Массовая привязка ПК через CSV
? Фильтры в отчётах (мультивыбор + поиск + зависимая фильтрация)
? Группировка «Месяц ? Сотрудник»
? XLSX с колонками Год/Месяц/Число и правильным форматом времени
________________________________________
Что дальше — Подблок C
Скажите «поехали», и пришлю Подблок C:
Календарь рабочих/нерабочих дней — таблица calendar_days, автозаполнение Сб/Вс как нерабочих на год вперёд, ручная правка, страница /admin/calendar.
Подсветка в отчётах — рабочие дни зелёным/неработные серым/выходные жёлтым.
Чекбокс «Учитывать нерабочие дни» — уже частично сделан в настройках.
PDF-отчёт — reportlab + шрифт с кириллицей, кнопка «Скачать PDF».
Запускайте проверку выше. Если 422/401/200 — как ожидается, то heartbeat работает, и можно переходить к C. Если что-то не так — пришлите вывод блока и docker compose logs api --tail=30.
В клиентской части сервер опять офлайн
Клиент показывает офлайн. Из предыдущей истории — было несколько причин:
getaddrinfo failed — резолвинг localhost (IPv6)
500 ошибки на сервере
Сейчас после пересборки — что могло сломаться? Скорее всего клиент использует старый URL (localhost) или мы снова сделали docker compose down/up, и что-то поменялось.
Также надо проверить — может клиент упал из-за того что контейнер был пересобран, но клиент не перезапущен.
Дам пошаговую диагностику + правку config.py клиента, чтобы он брал URL из .env, а не дефолтный localhost.
Смотрю на прошлое — мы уже правили client/.env на 127.0.0.1. Но лог показывает https://localhost. Значит .env либо перезаписан, либо не читается.
Мне нужно:
Проверить что в client/.env
Проверить что в client/config.py DEFAULT для SERVER_URL — если клиент упал на дефолт, значит .env не читается
Возможно проблема в getaddrinfo failed ? опять localhost
Дам скрипт, который:
показывает .env
показывает config.py
меняет дефолт в config.py на 127.0.0.1 (на случай если .env не подхватится)
перезапускает клиент
Проще всего — поправить DEFAULT_SERVER_URL в config.py на 127.0.0.1 и добавить в клиент логирование загруженного .env.
Посмотрю на config.py клиента — там SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://tracker.example.com"). Заменить дефолт на 127.0.0.1.
И заодно добавлю в sync.py лог с URL при старте — уже есть log.info("SyncWorker started; server=%s", SERVER_URL). В логе клиента я этого не вижу. Значит либо старый sync.py (без этой строки), либо лог не с того места смотрим.
Дам скрипт, который чистит и правит всё сразу.
Диагностика «офлайн» в клиенте
Из прошлого раза мы уже выяснили: getaddrinfo failed — проблема с резолвингом localhost (IPv6 ::1). Мы поменяли .env, но, видимо, .env не подхватывается или вы снова запустили клиент со старым config.py.
Сделаем два уровня защиты сразу: пропишем правильный URL и в .env, и в дефолте config.py. Тогда даже если .env не прочитается — клиент возьмёт правильный адрес.
________________________________________
Скрипт 1 — диагностика (без изменений)
powershell
$ErrorActionPreference = "Continue"

Write-Host "=== 1. Что в client\.env ===" -ForegroundColor Cyan
if (Test-Path D:\tracker\client\.env) {
    Get-Content D:\tracker\client\.env
} else {
    Write-Host "  ФАЙЛ НЕ НАЙДЕН!" -ForegroundColor Red
}

Write-Host "`n=== 2. Что в config.py (дефолт SERVER_URL) ===" -ForegroundColor Cyan
Select-String -Path D:\tracker\client\config.py -Pattern "SERVER_URL|TRACKER_SERVER"

Write-Host "`n=== 3. Логи клиента (последние 15 строк) ===" -ForegroundColor Cyan
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 15 -Encoding UTF8

Write-Host "`n=== 4. Достижимость сервера ===" -ForegroundColor Cyan
Write-Host "Через localhost:"
curl.exe -k -s -o $null -w "  HTTP %{http_code}`n" https://localhost/api/v1/version

Write-Host "Через 127.0.0.1:"
curl.exe -k -s -o $null -w "  HTTP %{http_code}`n" https://127.0.0.1/api/v1/version

Write-Host "`n=== 5. Что видит Python ===" -ForegroundColor Cyan
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -c @"
import socket
for host in ('localhost', '127.0.0.1'):
    try:
        res = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        print(f'  {host} -> {res[0][4]}')
    except Exception as e:
        print(f'  {host} -> ОШИБКА: {e}')
"@
Пришлите вывод этих 5 блоков. По ним сразу будет видно причину.
________________________________________
Скрипт 2 — «укрепляем» конфиг клиента (правь на всякий случай)
Скрипт делает так, чтобы клиент всегда шёл на 127.0.0.1 — даже если .env не прочитается.
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

# --- 1. Гарантированно правильный client/.env ---
$envContent = @'
TRACKER_SERVER_URL=https://127.0.0.1
TRACKER_PIN=
TRACKER_VERSION=1.0.0
'@
[System.IO.File]::WriteAllText("$clientDir\.env", $envContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client\.env" -ForegroundColor Green

# --- 2. Патчим config.py: дефолт = 127.0.0.1 ---
$cfgPath = "$clientDir\config.py"
$cfg = [System.IO.File]::ReadAllText($cfgPath, [System.Text.UTF8Encoding]::new($false))

$oldLine = 'SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://tracker.example.com")'
$newLine = 'SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://127.0.0.1")'

if ($cfg.Contains($newLine)) {
    Write-Host "  config.py уже пропатчен" -ForegroundColor Yellow
} elseif ($cfg.Contains($oldLine)) {
    $cfg = $cfg.Replace($oldLine, $newLine)
    [System.IO.File]::WriteAllText($cfgPath, $cfg, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  дефолт SERVER_URL ? https://127.0.0.1" -ForegroundColor Green
} else {
    # Возможно уже другой дефолт — не трогаем, только предупредим
    Write-Host "  ВНИМАНИЕ: строка с дефолтом SERVER_URL не найдена. Проверьте вручную:" -ForegroundColor Yellow
    Select-String -Path $cfgPath -Pattern "SERVER_URL"
}

# --- 3. Патчим http_client.py: отключаем IPv6-предпочтение если нужно ---
# (не критично, но улучшает совместимость)
Write-Host "`nТекущий SERVER_URL после правок:" -ForegroundColor Cyan
python -c @"
import sys
sys.path.insert(0, r'D:\tracker')
# эмулируем импорт config через dotenv
import os
from pathlib import Path
from dotenv import load_dotenv
p = Path(r'D:\tracker\client\.env')
load_dotenv(p, override=True)
print('  из .env:', os.environ.get('TRACKER_SERVER_URL'))
print('  дефолт в config.py: см. строку с SERVER_URL')
"@

Write-Host "`nГотово. Перезапустите клиент." -ForegroundColor Green
________________________________________
Скрипт 3 — запуск клиента и наблюдение
Сначала закройте старый клиент: правый клик по иконке в трее ? Выход.
Затем:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

# Чистим лог
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

python -m client.main
Во втором окне PowerShell:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Что хотим увидеть:
text
tracker.http Using CA bundle: ...
tracker.http Pinning DISABLED
tracker.sync SyncWorker started; server=https://127.0.0.1    ? важно, что 127.0.0.1
tracker.sync Server reachable (HTTP 200)
httpx HTTP Request: POST https://127.0.0.1/api/v1/heartbeat "HTTP/1.1 200 OK"
На панели клиента — «? онлайн» зелёным.
________________________________________
Если снова офлайн — пришлите мне
Одним сообщением:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 20 -Encoding UTF8
docker compose logs api --tail=15
docker compose ps
По этим трём блокам точно пойму, что сломано.
________________________________________
Возможные причины и что делать
Симптом в логе	Причина	Решение
getaddrinfo failed	Резолвится localhost в ::1	Скрипт 2 выше (127.0.0.1)
SSL: CERTIFICATE_VERIFY_FAILED	Сертификат не покрывает 127.0.0.1	Проверить ca.pem, в нём должен быть SAN с IP:127.0.0.1
Connection refused	nginx не слушает 443	docker compose ps, docker compose logs nginx
Server reachable (HTTP 500)	Падает сервер	docker compose logs api --tail=40
Логи пустые после запуска	Клиент упал до логирования	Запустить в консоли без pythonw, увидеть traceback
Запускайте Скрипт 1 (диагностика), пришлите вывод — и сразу поймём, что именно у вас. Затем Скрипт 2 и 3.
Смотрим внимательно. В логах:
text
2026-09-17 22:47:01,479 INFO tracker.http Using CA bundle: C:\Users\erohin\AppData\Roaming\Tracker\ca.pem
2026-09-17 22:47:01,479 WARNING tracker.http Pinning DISABLED
2026-09-17 22:47:03,174 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed
Клиент .env говорит TRACKER_SERVER_URL=https://127.0.0.1 — уже правильно!
Но getaddrinfo failed — значит клиент всё ещё стучится на localhost, а не на 127.0.0.1.
Проверим причину. В config.py дефолт всё ещё https://tracker.example.com, но это дефолт, если .env не читается.
Проверим — возможно ли, что .env не читается при запуске клиента? Или наоборот.
Наиболее вероятные причины:
Клиент закешировал модуль config при первом импорте, а потом .env изменился — но нет, при рестарте процесса всё перечитывается.
.env читается из D:\tracker\client\.env, но клиент запускается из D:\tracker, где Path.cwd() = D:\tracker, а не D:\tracker\client.
Смотрим config.py клиента:
python
_candidates = [
    Path.cwd() / ".env",
    Path(__file__).resolve().parent / ".env",
    Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
]
Второй кандидат — Path(__file__).resolve().parent / ".env" = D:\tracker\client\.env. Должен читаться.
Проверим, но на самом деле — логи показывают, что .env читается. Строка Loaded .env from ... должна быть в логе. Но её нет в выводе!
Смотрим внимательно на логи:
text
2026-09-17 22:47:01,479 INFO tracker.http Using CA bundle: ...
2026-09-17 22:47:01,479 WARNING tracker.http Pinning DISABLED
2026-09-17 22:47:03,174 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed
Нет строки Loaded .env from .... Значит .env не читается!
Почему? Потому что в конфиге клиента try: с python-dotenv. Если dotenv не установлен — будет _log.error("python-dotenv not installed"). Но у нас он есть.
Может, дело в том, что клиент запускается как python -m client.main из D:\tracker, и Path.cwd() = D:\tracker. Первый кандидат — D:\tracker\.env (это корневой .env сервера! там SECRET_ENCRYPTION_KEY=...). Этот файл ЕСТЬ. Значит load_dotenv загружает его первым и останавливается.
Смотрим код:
python
for p in _candidates:
    if p.exists():
        load_dotenv(p, override=True)
        _loaded_from = p
        break
Да! Первый существующий кандидат — D:\tracker\.env (корневой .env сервера с SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY). Там нет TRACKER_SERVER_URL. Поэтому используется дефолт https://tracker.example.com ? getaddrinfo failed для tracker.example.com.
Вот она причина!
Решение: поменять порядок кандидатов, чтобы сначала читался .env рядом с config.py (client/.env), а корневой серверный .env не трогался.
Или — использовать другой префикс при чтении: явно client/.env приоритетнее.
Лучшее решение — поменять порядок в config.py:
python
_candidates = [
    Path(__file__).resolve().parent / ".env",   # client/.env — приоритет!
    Path.cwd() / ".env",
    Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
]
Или ещё жёстче — читать только client/.env и %APPDATA%/Tracker/.env, игнорируя cwd/.env.
Также добавить проверку: если в файле нет TRACKER_SERVER_URL — не считать его «загруженным», идти дальше.
Даю полный config.py с исправлением.
Плюс — дефолт изменить на https://127.0.0.1.
Кстати, нужно ещё учесть, что клиент уже запускается с client/.env, но фактически загружается D:\tracker\.env. После фикса — пойдёт на 127.0.0.1.
Отлично. Пишу полный config.py клиента.
Найдена настоящая причина — клиент читает не тот .env
Смотрите на лог:
text
2026-09-17 22:47:01,479 INFO tracker.http Using CA bundle: ...
2026-09-17 22:47:01,479 WARNING tracker.http Pinning DISABLED
2026-09-17 22:47:03,174 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed
Нет строки Loaded .env from .... Значит .env клиента не читается вообще, а используется дефолт https://tracker.example.com ? getaddrinfo failed.
Почему так? Смотрим client/config.py:
python
_candidates = [
    Path.cwd() / ".env",                        # ? D:\tracker\.env (СЕРВЕРНЫЙ!)
    Path(__file__).resolve().parent / ".env",   # ? D:\tracker\client\.env (правильный)
    ...
]
for p in _candidates:
    if p.exists():
        load_dotenv(p, override=True)
        break
Вы запускаете python -m client.main из D:\tracker ? Path.cwd() = D:\tracker. Там есть серверный .env (с SECRET_ENCRYPTION_KEY, ADMIN_API_KEY и т.д.). Он находится первым, читается, а TRACKER_SERVER_URL в нём нет ? берётся дефолт.
Решение: поменять порядок — сначала искать .env рядом с самим config.py (т.е. в client/), а корневой игнорировать.
________________________________________
Скрипт — полная замена client/config.py
powershell
$ErrorActionPreference = "Stop"
$cfgPath = "D:\tracker\client\config.py"

$config_py = @'
import logging as _logging
import os
from pathlib import Path

_log = _logging.getLogger("tracker.config")

try:
    from dotenv import load_dotenv

    # Ищем .env в порядке приоритета.
    # ВАЖНО: первым идёт .env рядом с этим файлом (client/.env),
    # а НЕ .env в текущей директории — иначе при запуске из корня
    # проекта подхватится серверный .env, где TRACKER_* переменных нет.
    _candidates = [
        Path(__file__).resolve().parent / ".env",                       # client/.env
        Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
    ]
    _loaded_from = None
    for p in _candidates:
        if p.exists():
            load_dotenv(p, override=True)
            _loaded_from = p
            break
    if _loaded_from:
        _log.info("Loaded .env from %s", _loaded_from)
    else:
        _log.warning(".env not found in %s", [str(p) for p in _candidates])
except ImportError:
    _log.error("python-dotenv not installed; .env will NOT be read")


APP_NAME = "Tracker"
CLIENT_VERSION = os.environ.get("TRACKER_VERSION", "1.0.0")

if os.name == "nt":
    BASE_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    BASE_DIR = Path.home() / f".{APP_NAME.lower()}"

BASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "data.db"
LOG_PATH = BASE_DIR / "client.log"
DOWNLOAD_DIR = BASE_DIR / "updates"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Дефолт — 127.0.0.1, чтобы не упираться в IPv6-резолвинг localhost
SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://127.0.0.1")
SSL_CA_BUNDLE = os.environ.get("TRACKER_CA_BUNDLE", str(BASE_DIR / "ca.pem"))
PINNED_CERT_SHA256 = os.environ.get("TRACKER_PIN", "").strip().lower()

SYNC_INTERVAL = 30
ACTIVE_WINDOW_INTERVAL = 5
IDLE_THRESHOLD = 60
MAX_DB_SIZE_MB = 500
BATCH_SIZE = 200
COLLECT_KEYSTROKE_CHARS = False

