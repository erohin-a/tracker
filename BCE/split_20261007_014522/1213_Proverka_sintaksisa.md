<!-- Часть 1213 из 1409 -->
# Проверка синтаксиса
*Хлебные крошки:* Проверка синтаксиса

[◀ ============================================================](1212_part.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка маркеров ▶](1214_Proverka_markerov.md)

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

