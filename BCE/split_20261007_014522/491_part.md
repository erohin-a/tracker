<!-- Часть 491 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Аудит](490_Audit.md) | [Оглавление](00_BCE_INDEX.md) | [Проверяем, не добавлен ли уже ▶](492_Proveryaem_ne_dobavlen_li_uzhe.md)

---

# ============================================================
"@

    if ($content.Contains($marker)) {
        $content = $content.Replace($marker, $calendarBlock.TrimEnd())
        [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK  календарь добавлен в web_admin.py" -ForegroundColor Green
    } else {
        Write-Host "НЕ НАЙДЕН маркер '# Аудит' — добавьте блок вручную" -ForegroundColor Red
        exit 1
    }
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт C4 — server/templates/calendar.html
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

$calendar_html = @'
{% extends "base.html" %}
{% block title %}Календарь {{ year }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h3 class="mb-0">Календарь {{ year }}</h3>
  <div class="d-flex gap-2 align-items-center">
    <form method="get" class="d-flex gap-2">
      <select name="year" class="form-select form-select-sm" onchange="this.form.submit()">
        {% for y in years %}
          <option value="{{ y }}" {% if y == year %}selected{% endif %}>{{ y }}</option>
        {% endfor %}
      </select>
    </form>
    <form method="post" action="/admin/calendar/generate" class="d-inline">
      <input type="hidden" name="year" value="{{ year }}">
      <button class="btn btn-sm btn-outline-primary"
              onclick="return confirm('Заполнить {{ year }} по дефолту? Все ручные правки этого года сбросятся.');">
        Сгенерировать год
      </button>
    </form>
    <form method="post" action="/admin/calendar/reset" class="d-inline">
      <input type="hidden" name="year" value="{{ year }}">
      <button class="btn btn-sm btn-outline-danger"
              onclick="return confirm('Удалить все правки за {{ year }}? Вернётся дефолт (Пн-Пт рабочие).');">
        Сбросить
      </button>
    </form>
  </div>
</div>

{% if saved %}
<div class="alert alert-success py-2">? Календарь сохранён.</div>
{% endif %}

<div class="alert alert-info py-2 small">
  <strong>Как это работает:</strong>
  По умолчанию <em>Пн–Пт — рабочие</em>, <em>Сб–Вс — выходные</em>.
  Отметьте или снимите галочку, чтобы переопределить конкретный день
  (например, сделать субботу рабочей или среду — праздником).
  Затем нажмите <strong>«Сохранить год»</strong>.
  <br>
  В {{ year }}: <strong>{{ working_days }}</strong> рабочих из {{ total_days }} дней.
</div>

<form method="post" action="/admin/calendar/save">
  <input type="hidden" name="year" value="{{ year }}">

  <div class="row g-3">
    {% for m in months %}
    <div class="col-md-4">
      <div class="card">
        <div class="card-header py-2 fw-bold">{{ m.name }}</div>
        <div class="card-body p-2">
          <table class="table table-sm table-bordered mb-0" style="table-layout:fixed;font-size:12px">
            <thead><tr>
              {% for wd in weekday_names %}
                <th class="text-center p-1 {% if wd in ('Сб', 'Вс') %}bg-warning-subtle{% endif %}">{{ wd }}</th>
              {% endfor %}
            </tr></thead>
            <tbody>
            {% for week in m.weeks %}
              <tr>
                {% for cell in week %}
                  {% if cell %}
                    <td class="text-center p-0 position-relative
                      {% if cell.weekday >= 5 %}bg-warning-subtle{% endif %}"
                      title="{{ cell.iso }} — {{ 'рабочий' if cell.is_working else 'нерабочий' }}">
                      <label class="d-block w-100 h-100 m-0 p-1"
                             style="cursor:pointer">
                        <input type="checkbox" name="day_{{ cell.iso }}"
                               {% if cell.is_working %}checked{% endif %}
                               style="position:absolute;top:2px;left:2px;transform:scale(0.7)">
                        <span style="display:block;padding:4px;font-weight:bold;
                          {% if not cell.is_working %}color:#aaa;text-decoration:line-through;{% endif %}">
                          {{ cell.date.day }}
                        </span>
                      </label>
                    </td>
                  {% else %}
                    <td class="p-0 bg-light"></td>
                  {% endif %}
                {% endfor %}
              </tr>
            {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>

  <div class="d-flex justify-content-between align-items-center mt-3 mb-4">
    <div class="text-muted small">
      <span class="badge bg-warning-subtle text-dark">жёлтый фон</span> — выходной по умолчанию (Сб/Вс)<br>
      <span style="text-decoration:line-through;color:#aaa">зачёркнуто</span> — нерабочий день
    </div>
    <button class="btn btn-primary btn-lg">?? Сохранить {{ year }} год</button>
  </div>
</form>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\calendar.html", $calendar_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  calendar.html" -ForegroundColor Green
________________________________________
Скрипт C5 — добавляем ссылку «Календарь» в base.html
powershell
$ErrorActionPreference = "Stop"
$basePath = "D:\tracker\server\templates\base.html"
$content = [System.IO.File]::ReadAllText($basePath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("/admin/calendar")) {
    Write-Host "Ссылка на календарь уже есть" -ForegroundColor Yellow
} else {
    $old = '<a class="nav-link {% if ''/settings'' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>'
    $new = $old + "`n        " + '<a class="nav-link {% if ''/calendar'' in request.url.path %}active{% endif %}" href="/admin/calendar">Календарь</a>'
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($basePath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  ссылка на календарь добавлена" -ForegroundColor Green
}
________________________________________
Скрипт C6 — патч web_admin.py для подсветки в отчётах
Добавляем определение типа дня в _build_flat_records. Подсветка отобразится только если в отчёте есть day_type.
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains('info["day_type"]')) {
    Write-Host "Подсветка уже добавлена" -ForegroundColor Yellow
} else {
    # Вставляем определение day_type в _build_flat_records после workday_date
    $old = @'
        info["computer_name"] = (comp.hostname or comp.computer_uid) if comp else "—"
        info["workday_date"] = _workday_date(info["start_local"], workday_start_hour)
        flat.append(info)
    return flat
'@

    $new = @'
        info["computer_name"] = (comp.hostname or comp.computer_uid) if comp else "—"
        info["workday_date"] = _workday_date(info["start_local"], workday_start_hour)
        # Тип дня по календарю
        info["day_type"] = _day_type(db, info["workday_date"])
        flat.append(info)
    return flat
'@

    if ($content.Contains($old)) {
        $content = $content.Replace($old, $new)
        [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK  day_type добавлен в _build_flat_records" -ForegroundColor Green
    } else {
        Write-Host "НЕ НАЙДЕН блок в _build_flat_records" -ForegroundColor Red
        exit 1
    }
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт C7 — патч шаблона report_result.html (подсветка дней)
powershell
$ErrorActionPreference = "Stop"
$path = "D:\tracker\server\templates\report_result.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("day_type")) {
    Write-Host "Подсветка уже есть" -ForegroundColor Yellow
} else {
    # Заменяем ячейку "Рабочий день" в группировке days
    $old = @'
          <tr>
            <td>{{ r.date.strftime('%d.%m.%Y') }}{% if r.date.weekday() >= 5 %} <span class="badge bg-secondary">вых</span>{% endif %}</td>
'@

    $new = @'
          <tr>
            <td class="{% if r.day_type == 'weekend' %}table-warning{% elif r.day_type == 'holiday' %}table-danger{% endif %}">
              {{ r.date.strftime('%d.%m.%Y') }}
              {% if r.day_type == 'weekend' %}<span class="badge bg-warning text-dark">вых</span>
              {% elif r.day_type == 'holiday' %}<span class="badge bg-danger">празд.</span>{% endif %}
            </td>
'@

    if ($content.Contains($old)) {
        $content = $content.Replace($old, $new)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK  подсветка добавлена" -ForegroundColor Green
    } else {
        Write-Host "Не найден блок — правьте вручную" -ForegroundColor Yellow
    }
}
________________________________________
Скрипт C8 — пересборка и проверка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

docker compose ps
Write-Host "`n--- Логи API ---" -ForegroundColor Cyan
docker compose logs api --tail=20

Write-Host "`nОткройте:" -ForegroundColor Green
Write-Host "  https://127.0.0.1/admin/calendar    — календарь"
Write-Host "  https://127.0.0.1/admin/reports     — отчёты с подсветкой" -ForegroundColor Green
________________________________________
Что проверить
/admin/calendar — откроется год по месяцам
Сб/Вс жёлтым фоном
Чекбоксы отражают текущее состояние
Измените пару дней, нажмите «Сохранить год» ? плашка «Календарь сохранён»
Проверьте: сделайте будний день нерабочим, обновите страницу — день остался зачёркнутым
/admin/reports — сформировать отчёт на период с Сб/Вс
Суббота/воскресенье — жёлтый фон + бейдж «вых»
Если вы сделали будний день нерабочим — красный фон + «празд.»
/admin/calendar/generate — пересоздать год по дефолту (Сб/Вс нерабочие)
/admin/calendar/reset — удалить все ручные правки, вернуться к дефолту
________________________________________
Если что-то не так
Пришлите docker compose logs api --tail=40 — по трейсбеку пойму быстро.
Возможные проблемы:
500 на /admin/calendar ? RU_MONTHS не определён? Проверьте, что он есть в начале web_admin.py.
500 на дашборде после правок ? не забыли CalendarDay в импортах?
________________________________________
Что дальше
Как только календарь заработает — пришлю Подблок C-часть 2: PDF-отчёт (reportlab + шрифт DejaVu уже скачан в C2). Кнопка «Скачать PDF» появится рядом с CSV/XLSX в форме отчёта.
Запускайте C1–C8 и скажите результат.
Ошибка ?
Пользователь пытался запустить скрипт, но получил ошибки PowerShell на этапе парсинга. Проблема — в строке:
powershell
if ($content.Contains("@router.get(\"/calendar\"")) {
В PowerShell внутри двойных кавычек нельзя экранировать двойные кавычки через \" — нужно использовать `" (обратная кавычка) или одинарные кавычки.
Правильно:
powershell
if ($content.Contains('@router.get("/calendar"')) {
Или через блок здесь-строки. Также в файле web_admin.py может быть уже частично применён патч — надо проверить.
Давайте дам простой и надёжный скрипт. Он:
Проверит, есть ли уже календарь — если есть, ничего не делает
Если нет — допишет блок прямо в конец файла (перед последним ' который уже не нужен — вообще, допишем в самый конец файла перед закрывающим блоком или просто в конец, ведь функции всё равно идут после основных)
Стоп, но у нас web_admin.py сейчас заканчивается функцией audit_page. Если дописать блок календаря в конец — все декораторы @router.get и @router.post будут работать. Это нормально!
Давайте так и сделаем — допишем в конец файла. Проще и надёжнее.
Но подождите — у нас уже может быть частично применённый патч от прошлых попыток. Нужно сначала проверить.
Скрипт:
Прочитать web_admin.py
Проверить, есть ли уже def calendar_page — если есть, выходим
Если нет — проверить, что в импортах есть CalendarDay, если нет — добавить
В конец файла добавить блок календаря
Сохранить
Проверить синтаксис
Пойдём. Также надо проверить, что модели.py был обновлён (скрипт C1, вероятно, прошёл успешно).
Дам простой скрипт без вложенных кавычек, чтобы не спотыкаться.
Проблема ещё в том, что пользователь видел вывод с "action="generate")" — обратите внимание, что при копировании из предыдущего сообщения некоторые строки потерялись! Смотрите:
text
>>         cur += timedelta(days=1)
>>                     action="generate"))
>>     db.commit()
Тут явно пропала часть. Значит скрипт не сработал полностью, парсинг провалился до выполнения. Хорошо, файл не повреждён.
Давайте напишу новый скрипт, который дописывает в конец файла. Так мы не будем зависеть от поиска маркеров.
Ошибка PowerShell — экранирование кавычек
Проблема в строке:
powershell
if ($content.Contains("@router.get(\"/calendar\"")) {
В PowerShell нельзя экранировать " через \" — надо либо одинарные кавычки, либо двойную кавычку в удвоенном виде, либо обратную кавычку.
Хорошая новость: файл web_admin.py не пострадал — парсинг скрипта упал ещё до выполнения, ничего не записалось.
Сделаем надёжнее: напишу скрипт, который просто дописывает блок календаря в конец web_admin.py. Так не надо искать маркеры внутри файла.
________________________________________
Скрипт — добавление календаря в web_admin.py (дописываем в конец)
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

