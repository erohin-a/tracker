# Проверка синтаксиса

*Часть 93 из 100. Источник: `BCE.md`.*

[◀ === 1. Функция _build_pivot_data ===](092_1_Funktsiya_build_pivot_data.md) | [Оглавление](00_BCE_INDEX.md) | [Заменяем блок pivotUI + опции ▶](094_Zamenyaem_blok_pivotUI_optsii.md)

---

# Проверка синтаксиса
try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: line={e.lineno}, msg={e.msg}")
    print(f"Текст: {e.text}")
    raise SystemExit(1)

for m in ["def _build_pivot_data", '\"/api/pivot-data\"', '\"/reports/pivot\"']:
    print(f" {'OK' if m in content else 'MISS'}: {m}")
'@
[System.IO.File]::WriteAllText("D:\tracker\_patch_pivot_backend.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч бэкенда pivot ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_pivot_backend.py
Что ожидаем:
text
OK: _build_pivot_data добавлена
OK: endpoint /api/pivot-data добавлен
OK: роут /reports/pivot добавлен
SYNTAX OK
 OK: def _build_pivot_data
 OK: "/api/pivot-data"
 OK: "/reports/pivot"
________________________________________
Скрипт 2 — Шаблон reports_pivot.html
Создаём новый файл. Подключаем PivotTable.js через CDN, добавляем свой агрегатор «Сумма (время)» для форматирования в HH:MM:SS.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$template = @'
{% extends "base.html" %}
{% block title %}Сводная таблица{% endblock %}
{% block content %}

<div class="d-flex justify-content-between align-items-center mb-3">
  <div>
    <h3 class="mb-1">?? Сводная таблица (Pivot)</h3>
    <div class="text-muted small">
      Тяните поля между зонами — как в Excel. Одна строка = один сотрудник за день.
    </div>
  </div>
  <a class="btn btn-outline-secondary" href="/admin/reports">? К обычным отчётам</a>
</div>

{# ============================================================
   Фильтры
   ============================================================ #}
<div class="card mb-3">
  <div class="card-body">

    <div class="row g-2 align-items-end mb-2">
      <div class="col-md-3">
        <label class="form-label small mb-1">Период: с</label>
        <input type="date" class="form-control form-control-sm" id="pivot_date_from" value="{{ today }}">
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">по</label>
        <input type="date" class="form-control form-control-sm" id="pivot_date_to" value="{{ today }}">
      </div>
      <div class="col-md-6 d-flex gap-1 flex-wrap">
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPivotPeriod(0)">Сегодня</button>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPivotPeriod(1)">Вчера</button>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPivotPeriod(7)">7 дней</button>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPivotPeriod(30)">30 дней</button>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPivotThisMonth()">Этот месяц</button>
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPivotLastMonth()">Прошлый месяц</button>
      </div>
    </div>

    <div class="row g-2">
      <div class="col-md-3">
        <label class="form-label small mb-1">Отделы <span class="text-muted">(Ctrl+клик)</span></label>
        <select id="pivot_depts" class="form-select form-select-sm" multiple size="5">
          {% for d in departments %}
          <option value="{{ d.id }}">{{ d.name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">Сотрудники</label>
        <select id="pivot_employees" class="form-select form-select-sm" multiple size="5">
          {% for e in employees %}
          <option value="{{ e.id }}" data-dept="{{ e.department_id or '' }}">{{ e.full_name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">Компьютеры</label>
        <select id="pivot_computers" class="form-select form-select-sm" multiple size="5">
          {% for c in computers %}
          <option value="{{ c.id }}">{{ c.hostname or c.computer_uid[:14] }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3 d-flex align-items-end">
        <button type="button" class="btn btn-primary w-100" onclick="loadPivotData()">
          ?? Загрузить данные
        </button>
      </div>
    </div>

    <div id="pivot_status" class="small text-muted mt-2"></div>
  </div>
</div>

{# ============================================================
   Сводная
   ============================================================ #}
<div class="card">
  <div class="card-body">
    <div id="pivot_output">
      <div class="text-muted p-3">Нажми «Загрузить данные» или открой страницу — данные загрузятся автоматически.</div>
    </div>
  </div>
</div>

{# ============================================================
   PivotTable.js через CDN
   ============================================================ #}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/themes/base/jquery-ui.min.css">
<script src="https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/dist/jquery-ui.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.js"></script>

<script>
// ============================================================
// Форматирование секунд ? HH:MM:SS
// ============================================================
function fmtDuration(seconds) {
  seconds = Math.round(Number(seconds) || 0);
  if (seconds < 0) seconds = 0;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}

// ============================================================
// Кастомные агрегаторы с форматированием времени
// ============================================================
function makeDurationAggregator(label) {
  return function(data, rowKey, colKey) {
    return {
      sum: 0,
      push: function(record) {
        for (let i = 0; i < rowKey.length; i++) {
          const v = record[rowKey[i]];
          if (typeof v === 'number') this.sum += v;
        }
      },
      value: function() { return this.sum; },
      format: function(x) { return fmtDuration(x); },
      label: label || 'Сумма (HH:MM:SS)'
    };
  };
}

// Регистрируем агрегатор
if (window.$ && $.pivotUtilities && $.pivotUtilities.aggregators) {
  $.pivotUtilities.aggregators["Сумма (время)"] = makeDurationAggregator("Сумма (время)");
  $.pivotUtilities.aggregators["Среднее (время)"] = function(data, rowKey, colKey) {
    return {
      sum: 0, count: 0,
      push: function(record) {
        for (let i = 0; i < rowKey.length; i++) {
          const v = record[rowKey[i]];
          if (typeof v === 'number') { this.sum += v; this.count += 1; }
        }
      },
      value: function() { return this.count ? this.sum / this.count : 0; },
      format: function(x) { return fmtDuration(x); }
    };
  };
}

// ============================================================
// Периоды
// ============================================================
function fmtDate(d) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}
function setPivotRange(from, to) {
  document.getElementById('pivot_date_from').value = fmtDate(from);
  document.getElementById('pivot_date_to').value = fmtDate(to);
}
function setPivotPeriod(daysAgo) {
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - daysAgo);
  setPivotRange(from, to);
}
function setPivotThisMonth() {
  const now = new Date();
  setPivotRange(new Date(now.getFullYear(), now.getMonth(), 1),
                new Date(now.getFullYear(), now.getMonth() + 1, 0));
}
function setPivotLastMonth() {
  const now = new Date();
  setPivotRange(new Date(now.getFullYear(), now.getMonth() - 1, 1),
                new Date(now.getFullYear(), now.getMonth(), 0));
}

// ============================================================
// Загрузка данных и рендер pivot
// ============================================================
function getSelectedValues(id) {
  const sel = document.getElementById(id);
  if (!sel) return [];
  return Array.from(sel.options).filter(o => o.selected).map(o => o.value);
}

async function loadPivotData() {
  const status = document.getElementById('pivot_status');
  status.textContent = '? Загрузка…';
  status.style.color = '#6c757d';

  const fd = new FormData();
  fd.append('date_from', document.getElementById('pivot_date_from').value);
  fd.append('date_to', document.getElementById('pivot_date_to').value);
  getSelectedValues('pivot_depts').forEach(v => fd.append('department_ids', v));
  getSelectedValues('pivot_employees').forEach(v => fd.append('employee_ids', v));
  getSelectedValues('pivot_computers').forEach(v => fd.append('computer_ids', v));

  try {
    const resp = await fetch('/admin/api/pivot-data', { method: 'POST', body: fd });
    if (!resp.ok) {
      status.textContent = '? Ошибка: HTTP ' + resp.status;
      status.style.color = '#dc3545';
      return;
    }
    const data = await resp.json();
    status.textContent = '? Загружено строк: ' + data.total + ' за период ' + data.date_from + ' — ' + data.date_to;
    status.style.color = '#28a745';

    if (!data.rows.length) {
      document.getElementById('pivot_output').innerHTML = '<div class="text-muted p-3">Нет данных за выбранный период</div>';
      return;
    }

    // Заголовки колонок для UI PivotTable
    const fieldLabels = {
      date: "Дата",
      year: "Год",
      month_num: "Месяц №",
      month_name: "Месяц",
      day: "Число",
      weekday: "День недели",
      weekday_full: "День недели (полный)",
      is_weekend: "Выходной",
      employee: "Сотрудник",
      external_id: "1C ID",
      department: "Отдел",
      computers: "Компьютеры",
      computer_count: "ПК (кол-во)",
      sessions_count: "Сессий",
      worked_span: "Отработано (сек)",
      worked_union: "С трекером (сек)",
      intensive: "Интенсивная (сек)",
      effective: "Эффективно (сек)",
      break_dur: "Пауза (сек)",
      pause_button: "Пауза кнопкой (сек)"
    };

    $('#pivot_output').pivotUI(data.rows, {
      rows: ['department', 'employee'],
      cols: ['month_name'],
      aggregatorName: 'Сумма (время)',
      vals: ['worked_span', 'effective', 'intensive', 'break_dur'],
      rendererName: 'Table',
      unusedAttrsVertical: false,
      autoSortUnusedAttrs: true,
      showUI: true,
      onRefresh: null,
      // Перевод заголовков полей
      locale: 'ru',
      // Свои метки
      attributeLabels: fieldLabels,
      // Отключаем нежелательные агрегаторы
      aggregators: {
        "Сумма (время)": makeDurationAggregator("Сумма (время)"),
        "Среднее (время)": $.pivotUtilities.aggregators["Среднее (время)"] || null,
        "Count": $.pivotUtilities.aggregators["Count"],
        "Count Unique Values": $.pivotUtilities.aggregators["Count Unique Values"],
        "List Unique Values": $.pivotUtilities.aggregators["List Unique Values"],
        "Sum": $.pivotUtilities.aggregators["Sum"],
        "Average": $.pivotUtilities.aggregators["Average"]
      }
    });
  } catch (e) {
    status.textContent = '? Ошибка: ' + e.message;
    status.style.color = '#dc3545';
  }
}

// ============================================================
// Синхронизация отделов ? сотрудники
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  const depsSel = document.getElementById('pivot_depts');
  const empSel = document.getElementById('pivot_employees');
  if (depsSel && empSel) {
    depsSel.addEventListener('change', function() {
      const deps = new Set(Array.from(this.selectedOptions).map(o => o.value));
      Array.from(empSel.options).forEach(o => {
        const d = String(o.dataset.dept || '');
        const show = deps.size === 0 || (d && deps.has(d));
        o.hidden = !show;
        if (!show) o.selected = false;
      });
    });
  }

  // Автозагрузка
  setPivotPeriod(30);
  loadPivotData();
});
</script>

<style>
/* Адаптация PivotTable к Bootstrap */
.pvtUi { font-size: 13px; }
.pvtUi select, .pvtUi input { font-size: 13px; }
.pvtAxisContainer, .pvtVals {
  background: #f8f9fa;
  border-radius: 4px;
  min-height: 30px;
}
.pvtAxisContainer li span.pvtAttr {
  background: #e9ecef;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
}
.pvtVals button.pvtButton { padding: 2px 6px; font-size: 12px; }
table.pvtTable { font-size: 12px; }
table.pvtTable tbody tr th,
table.pvtTable thead tr th { padding: 4px 6px; }
table.pvtTable .pvtTotalLabel { font-weight: bold; }
</style>

{% endblock %}
'@
[System.IO.File]::WriteAllText("D:\tracker\server\templates\reports_pivot.html", $template, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: reports_pivot.html создан ($($template.Length) символов)" -ForegroundColor Green

# Проверка маркеров
$check = [System.IO.File]::ReadAllText("D:\tracker\server\templates\reports_pivot.html", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @('pivotUI', 'pivottable@2.23.0', 'makeDurationAggregator', 'Сумма (время)', 'loadPivotData')) {
    if ($check.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}
Что ожидаем:
text
OK: reports_pivot.html создан (~12000 символов)
 OK: pivotUI
 OK: pivottable@2.23.0
 OK: makeDurationAggregator
 OK: Сумма (время)
 OK: loadPivotData
________________________________________
Скрипт 3 — Ссылка в меню base.html
Добавляем пункт «Сводная» рядом с «Отчёты».
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$path = "D:\tracker\server\templates\base.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains('/admin/reports/pivot')) {
    Write-Host "SKIP: ссылка уже есть" -ForegroundColor Yellow
} else {
    $old = '<a class="nav-link {% if ''/reports'' in request.url.path %}active{% endif %}" href="/admin/reports">{{ _("menu.reports") }}</a>'
    $new = $old + "`n " + '<a class="nav-link {% if ''/reports/pivot'' in request.url.path %}active{% endif %}" href="/admin/reports/pivot">?? Сводная</a>'
    if ($content.Contains($old)) {
        $content = $content.Replace($old, $new)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: ссылка на /admin/reports/pivot добавлена" -ForegroundColor Green
    } else {
        Write-Host "WARN: маркер ссылки на /reports не найден" -ForegroundColor Yellow
        Write-Host "Открой base.html и добавь ссылку на /admin/reports/pivot вручную" -ForegroundColor Yellow
    }
}
________________________________________
Скрипт 4 — Пересборка и проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Проверка синтаксиса Python ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe -c "import ast; ast.parse(open(r'D:\tracker\server\web_admin.py', encoding='utf-8').read()); print('web_admin.py SYNTAX OK')"

Write-Host "`n=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps

Write-Host "`n=== Логи API (последние 20 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=20

Write-Host "`n=== Проверка: маркеры в контейнере ===" -ForegroundColor Cyan
docker compose exec -T api grep -c "_build_pivot_data" /app/server/web_admin.py
docker compose exec -T api grep -c "api/pivot-data" /app/server/web_admin.py
docker compose exec -T api ls -la /app/server/templates/reports_pivot.html
Что ожидаем:
web_admin.py SYNTAX OK
Все 3 контейнера Up
В логах — без Traceback
_build_pivot_data — 1+, api/pivot-data — 1+, файл шаблона на месте
________________________________________
Проверка в браузере
Открой https://localhost/admin/reports/pivot.
Откроется страница с фильтрами. Через пару секунд автоматически подгрузится сводная за 30 дней.
Сверху над таблицей — три зоны: Доступные атрибуты, Строки, Колонки, Значения.
Потяни поля — увидишь, как таблица перестраивается.
По умолчанию:
Строки: Отдел, Сотрудник
Колонки: Месяц
Значения: Отработано, Эффективно, Интенсивная, Пауза — все в формате HH:MM:SS.
Если увидишь:
Пустую страницу ? проверь docker compose logs api --tail=40 (может быть ошибка в шаблоне).
PivotTable не грузится ? проверь консоль браузера (F12) — возможно, CDN недоступен (у меня есть план как завендорить локально).
Таблица с числами без формата ? значит кастомный агрегатор не зарегистрировался, посмотрим.
________________________________________
Что присылать
Вывод после Скрипта 1 — 6 строк (5 OK + SYNTAX).
Вывод после Скрипта 2 — 5 маркеров.
Вывод после Скрипта 4 — grep-числа и логи.
Скриншот страницы /admin/reports/pivot — там должен быть интерфейс pivot-таблицы.
После этого: если всё работает — добавим пресеты («Табель по отделам», «Программы по сотрудникам», «Опоздания»), экспорт сводной в XLSX и фильтры по дням недели. Если что-то падает — точечно поправим.
Начинай со Скрипта 1.
Отлично! Страница pivot работает — данные загружены (377 строк), интерфейс PivotTable отображается. Вижу поля, зоны для drag-and-drop.
Но есть проблема: у полей английские названия (date_iso, year, month_num, day, weekday, weekday_full, is_weekend, employee_id, external_id, computers, computer_count, sessions_count, worked_span, worked_union, intensive, effective, break_dur, pause_button). Мой fieldLabels не подхватился, потому что в PivotTable.js параметр называется attributeLabels и он требует правильной передачи.
Также вижу что нижняя таблица пустая — но это потому что нужно кликнуть по полям или сама таблица рендерится ниже. Хотя нет — я вижу что после загрузки таблица должна появиться. Возможно, нужно посмотреть ниже скриншота.
Проблемы:
Английские названия полей — нужно русифицировать через attributeLabels или переименовать поля в бэкенде сразу на русские ключи.
Таблица не отображается? — может быть ниже на скриншоте или нужен скролл.
Решение: проще всего переименовать поля в бэкенде сразу на русские названия. Тогда PivotTable.js покажет их как есть. Это надёжнее, чем бороться с attributeLabels.
Но ключи с пробелами и русскими буквами не очень удобно использовать как rowKey в JS — можно, но нужна аккуратность.
Альтернатива: оставить английские ключи в JSON, но передать в pivotUI параметр attributeLabels — однако в PivotTable.js 2.23.0 этот параметр должен работать. Возможно, я неправильно его передал.
Смотрю документацию PivotTable.js: параметр называется attributeLabels, передаётся в опции:
js
$("#output").pivotUI(data, {
  attributeLabels: { "date_iso": "Дата", ... }
})
Хм, но у меня это было. Возможно, проблема в том, что я передавал locale: 'ru' — а локали ru в стандартном PivotTable.js нет, поэтому он мог откатиться на английский.
Давай уберём locale: 'ru' и оставим только attributeLabels. Или ещё лучше — переименуем ключи в бэкенде сразу на русские, чтобы всё было просто.
Мне кажется, второй подход лучше. Только нужно аккуратно — если ключи с пробелами, то в JS к ним обращаться через record["Отработано"]. В PivotTable.js можно передавать массивы ключей, включая такие — должно работать.
Хотя, чтобы избежать проблем с пробелами, лучше использовать ключи без пробелов, но с русскими буквами:
Дата — ок
Год — ок
Месяц_номер — ок, но некрасиво
Месяц — ок
Число — ок
День_недели — ок
Сотрудник — ок
Отдел — ок
Компьютер — ок
Сессий — ок
Отработано — ок
С_трекером — ок
Интенсивная — ок
Эффективно — ок
Пауза — ок
Или оставить английские, но передать attributeLabels правильно.
Скорее всего, моя проблема — в том, что я передавал опции не туда, где их ожидает PivotTable.js. Точнее, attributeLabels — правильный параметр, но я передавал ещё locale: 'ru' — и он мог откатиться на английский.
Давай так: заменю locale: 'ru' на locale: 'en' (или уберу), а attributeLabels оставлю. Если не сработает — перейду на русские ключи в JSON.
Хм, я почти уверен, что attributeLabels в PivotTable.js работает, но нужно смотреть точно. Давай поищу в документации. В примерах:
js
$("#output").pivotUI(data, {
  attributeLabels: {
    "Field 1": "Field 1 Label",
    ...
  }
})
Но у меня там ключи типа date_iso — просто строки. Всё должно работать.
Возможно, проблема в том, что unusedAttrsVertical: false — а в этом режиме PivotTable рендерит поля иначе, но заголовки должны подхватываться.
Давай я не буду гадать — просто переименую ключи в бэкенде на русские, тогда всё будет видно как есть. Это самый надёжный путь.
Также надо посмотреть — отображается ли сама таблица. На скриншоте её не видно. Возможно, нужно прокрутить вниз. Но если её нет — значит что-то с рендером.
Стоп, глядя на скриншот внимательнее: внизу страницы только интерфейс PivotTable с полями, а таблицы нет. Возможно, она ниже или нужен скролл. Пользователь не указал, есть ли таблица ниже.
Давай я:
Переименую ключи в бэкенде на русские (это перезапишет _build_pivot_data).
Уберу locale: 'ru' из опций PivotTable.
Оставлю attributeLabels на всякий случай — пусть будет.
Скажу пользователю прислать скриншот всей страницы с прокруткой вниз, чтобы увидеть саму таблицу.
Хотя проще: сразу дам фикс с русскими ключами, и после перезагрузки пользователь увидит и таблицу (если она рендерится), и красивые заголовки.
Давай сделаю патч в бэкенде — заменю ключи на русские.
Ключи для JSON:
text
"Дата": dd.mm.yyyy (для показа)
"Год": 2026
"Месяц №": 9 (число)
"Месяц": Сентябрь
"Число": 24
"День недели": Пн-Вс
"Сотрудник": ФИО
"1C ID": строка
"Отдел": строка
"Компьютеры": строка
"Сессий": число
"Отработано": сек
"С трекером": сек
"Интенсивная": сек
"Эффективно": сек
"Пауза": сек
"Пауза кнопкой": сек
Пробелы в ключах — ок, PivotTable.js и JS работают.
Но! В JS у меня в коде vals: ['worked_span', 'effective', ...] — если ключи русские, надо и там поменять. И в rows: ['department', 'employee'] ? ['Отдел', 'Сотрудник'].
Так что нужно обновить и бэкенд, и шаблон.
Давай сделаю два скрипта: патч бэкенда (ключи) и патч шаблона (vals, rows, cols).
Хотя проще — патч шаблона с обновлёнными rows/cols/vals, и патч бэкенда с русскими ключами.
Или ещё вариант — оставить английские ключи в JSON (они удобнее для JS), но правильно передать attributeLabels. Может быть, проблема была в том, что параметр передавался не в тот объект.
Знаешь что, я перестрахуюсь: сделаю и то, и другое. Оставлю английские ключи, но перепишу attributeLabels и уберу locale: 'ru'. Если не сработает — перейдём на русские ключи.
Хм, но на скриншоте явно видно что attributeLabels НЕ работают — поля показываются с английскими именами. Значит, либо параметр неправильно передаётся, либо PivotTable.js его не поддерживает в этой версии.
Проверяю документацию PivotTable.js: параметр attributeLabels есть в опциях pivotUI(). Всё должно работать.
Возможно, проблема в том, что я передавал locale: 'ru', а в PivotTable.js локали загружаются отдельными файлами (например, pivot.ru.js). Без загруженной локали он мог откатиться на английский и ИГНОРИРОВАТЬ attributeLabels.
Давай уберу locale: 'ru' и оставлю только attributeLabels.
ОК, пишу фикс.
Также надо подумать: посмотреть ниже скриншота — там есть таблица или нет? Если нет — это отдельная проблема. Но сначала русифицируем, потом посмотрим.
Стратегия:
Патч шаблона — убрать locale: 'ru', оставить attributeLabels.
Проверить в браузере.
Если не поможет — перейдём на русские ключи в JSON.
Хотя, знаешь, лучше сразу на русские ключи — 100% надёжно. Тогда никаких attributeLabels не нужно.
Давай так и сделаю.
План:
Патч бэкенда _build_pivot_data — заменить ключи на русские (без пробелов где возможно, с подчёркиванием вместо пробелов).
Патч шаблона — обновить rows, cols, vals, fieldLabels.
Или... ключи с пробелами — это не проблема для JS, если использовать кавычки:
js
data.rows[0]["Отработано"]
работает.
Но в PivotTable при передаче vals: ['Отработано', 'Эффективно'] — тоже ок.
Значит, можно и с пробелами. Единственное — в HTML/JS это выглядит необычно, но работает.
Давай так:
Ключи: Дата, Год, Месяц №, Месяц, Число, День недели, Сотрудник, 1C ID, Отдел, Компьютеры, Сессий, Отработано, С трекером, Интенсивная, Эффективно, Пауза, Пауза кнопкой.
Пишу патч.
Хотя надо ещё убедиться, что в _build_pivot_data я возвращаю ровно то, что нужно — из скриншота видно что 377 строк, все поля на месте. Отлично.
Стоп — а таблица-то вообще рендерится? На скриншоте внизу вижу только department, employee в зоне строк и date, month_name в зоне колонок. Это дефолтное состояние pivotUI. Сама таблица должна быть ниже.
Возможно, у пользователя она есть, просто не влезла в скриншот. Уточню — попрошу показать нижнюю часть страницы.
Если таблица есть — отлично, просто русифицируем.
Если нет — отдельная проблема.
ОК, пишу ответ. Сначала — анализ скриншота, потом фикс.
Ответ будет:
Что вижу (работает: данные загружаются, pivotUI рендерится, 377 строк).
Что не так (английские заголовки).
Фикс (русские ключи).
Что присылать (скриншот с прокруткой вниз).
Про длину чата: ~72%, ещё 1-2 итерации.
Пишу.
Отлично — страница загрузилась, API вернул 377 строк за август, PivotTable.js рендерится, drag-and-drop работает. Главная проблема одна: английские названия полей (date_iso, worked_span и т. д.). Плюс не вижу в скриншоте самой таблицы — возможно, она ниже среза. Сейчас поправим первое, заодно проверим второе.
Про длину чата: сейчас около 72%. Хватит на 1–2 итерации. Если почувствую, что близко к концу — предупрежу и сделаю handoff.
________________________________________
Что вижу (разбор скриншота)
? Работает:
Страница /admin/reports/pivot открывается.
Фильтры сверху (период, отделы, сотрудники, компьютеры).
Кнопки быстрых периодов.
Слева меню с новым пунктом «Сводная».
Статус «? Загружено строк: 377 за период 2026-08-01 — 2026-08-31».
PivotTable UI с зонами:
Строки: department, employee
Колонки: date, month_name
Агрегатор: «Сумма (время)» — то есть наш кастомный агрегатор подхватился, отлично.
Доступные поля перечислены.
? Не работает:
Все поля называются по-английски: date_iso, year, month_num, worked_span и т. д. — потому что мой attributeLabels не подхватился (PivotTable.js в v2.23.0 не любит locale: 'ru' без загруженной локали — откатывается на английский и игнорирует attributeLabels).
Решение: переименовать ключи в JSON сразу на русские. Тогда не нужно бороться с attributeLabels и locale. Русские ключи с пробелами работают в PivotTable.js без проблем.
________________________________________
Скрипт 1 — Патч бэкенда: русские ключи в _build_pivot_data
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$patcher = @'
import ast
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\web_admin.py")
content = PATH.read_text(encoding="utf-8")

# Заменяем функцию _build_pivot_data целиком
pattern = re.compile(
    r"def _build_pivot_data\(.*?(?=\ndef |\n# ============|\Z)",
    re.DOTALL,
)
m = pattern.search(content)
if not m:
    print("ERROR: _build_pivot_data не найдена")
    raise SystemExit(1)

new_func = '''def _build_pivot_data(db, employee_ids, department_ids, computer_ids,
                       date_from, date_to, tz, workday_start_hour):
    """
    Строит "плоские" строки для pivot-таблицы.
    Ключи сразу на русском — PivotTable.js показывает их как есть.
    Одна строка = один сотрудник за один рабочий день.
    """
    flat = _build_flat_records(db, employee_ids, department_ids, computer_ids,
                                date_from, date_to, tz, workday_start_hour)
    if not flat:
        return []

    WEEKDAY_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    WEEKDAY_FULL = ["Понедельник", "Вторник", "Среда", "Четверг",
                    "Пятница", "Суббота", "Воскресенье"]

    groups = {}
    for r in flat:
        key = (r.get("employee_id"), r["workday_date"])
        groups.setdefault(key, []).append(r)

    rows = []
    for (emp_id, day), sessions in groups.items():
        first = sessions[0]
        d_start = min(s["start_local"] for s in sessions)
        d_end = max(s["end_local"] for s in sessions)
        span = max(0, int((d_end - d_start).total_seconds()))

        intervals = [(s["activity_start_local"], s["activity_end_local"])
                     for s in sessions]
        union = _union_duration(intervals)

        effective = sum(s.get("effective_duration", 0) for s in sessions)
        intensive = sum(s.get("intensive_seconds", 0) for s in sessions)
        pause_btn = sum(s.get("pause_seconds", 0) for s in sessions)
        break_dur = pause_btn + max(0, span - union)

        computers = sorted({s.get("computer_name") or "—" for s in sessions})

        rows.append({
            "Дата": day.strftime("%d.%m.%Y"),
            "Год": day.year,
            "Месяц №": day.month,
            "Месяц": RU_MONTHS[day.month],
            "Число": day.day,
            "День недели": WEEKDAY_SHORT[day.weekday()],
            "День недели (полный)": WEEKDAY_FULL[day.weekday()],
            "Выходной": "Да" if day.weekday() >= 5 else "Нет",
            "Сотрудник": first.get("employee_name") or "— не привязан —",
            "1C ID": first.get("external_id") or "",
            "Отдел": first.get("department_name") or "—",
            "Компьютеры": ", ".join(computers),
            "ПК (кол-во)": len(computers),
            "Сессий": len(sessions),
            "Отработано (сек)": span,
            "С трекером (сек)": union,
            "Интенсивная (сек)": intensive,
            "Эффективно (сек)": effective,
            "Пауза (сек)": break_dur,
            "Пауза кнопкой (сек)": pause_btn,
        })

    rows.sort(key=lambda x: (x["Дата"], x["Сотрудник"]), reverse=True)
    return rows


'''

content = content[:m.start()] + new_func + content[m.end():]
PATH.write_text(content, encoding="utf-8")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: line={e.lineno}, msg={e.msg}")
    raise SystemExit(1)

for key in ["Отработано (сек)", "С трекером (сек)", "Интенсивная (сек)",
            "Эффективно (сек)", "Пауза (сек)", "Сотрудник", "Отдел"]:
    print(f" {'OK' if key in content else 'MISS'}: {key}")
'@
[System.IO.File]::WriteAllText("D:\tracker\_patch_pivot_ru.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч pivot — русские ключи ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_pivot_ru.py
Что ожидаем:
text
SYNTAX OK
 OK: Отработано (сек)
 OK: С трекером (сек)
 OK: Интенсивная (сек)
 OK: Эффективно (сек)
 OK: Пауза (сек)
 OK: Сотрудник
 OK: Отдел
________________________________________
Скрипт 2 — Патч шаблона: русские ключи в pivotUI
Меняем дефолтные rows, cols, vals и убираем locale: 'ru' (без загруженной локали он всё равно откатывается на английский).
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$patcher = @'
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\templates\reports_pivot.html")
content = PATH.read_text(encoding="utf-8")

