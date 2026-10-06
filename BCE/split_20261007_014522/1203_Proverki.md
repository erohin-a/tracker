<!-- Часть 1203 из 1409 -->
# Проверки
*Хлебные крошки:* Проверки

[◀ Проверка синтаксиса](1202_Proverka_sintaksisa.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1204_part.md)

---

# Проверки
for m in ["def _build_pivot_data", '"/api/pivot-data"', '"/reports/pivot"']:
    print(f" {'OK' if m in content else 'MISS'}: {m}")
Now the template. Let me design it:
html
{% extends "base.html" %}
{% block title %}Сводная таблица{% endblock %}
{% block content %}
<h3 class="mb-3">Сводная таблица (Pivot)</h3>

<div class="card mb-3">
  <div class="card-body">
    <div class="row g-2 align-items-end">
      <div class="col-md-3">
        <label class="form-label small mb-1">Период: с</label>
        <input type="date" class="form-control form-control-sm" id="pivot_date_from" value="{{ today }}">
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">по</label>
        <input type="date" class="form-control form-control-sm" id="pivot_date_to" value="{{ today }}">
      </div>
      <div class="col-md-2">
        <button class="btn btn-sm btn-outline-secondary w-100" onclick="setPivotPeriod(0)">Сегодня</button>
      </div>
      <div class="col-md-2">
        <button class="btn btn-sm btn-outline-secondary w-100" onclick="setPivotPeriod(1)">Вчера</button>
      </div>
      <div class="col-md-2">
        <button class="btn btn-sm btn-outline-secondary w-100" onclick="setPivotPeriod(30)">30 дней</button>
      </div>
    </div>
    
    <div class="row g-2 mt-2">
      <div class="col-md-3">
        <label class="form-label small mb-1">Отделы (Ctrl+клик)</label>
        <select id="pivot_depts" class="form-select form-select-sm" multiple size="4">
          {% for d in departments %}
          <option value="{{ d.id }}">{{ d.name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">Сотрудники</label>
        <select id="pivot_employees" class="form-select form-select-sm" multiple size="4">
          {% for e in employees %}
          <option value="{{ e.id }}" data-dept="{{ e.department_id or '' }}">{{ e.full_name }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label small mb-1">Компьютеры</label>
        <select id="pivot_computers" class="form-select form-select-sm" multiple size="4">
          {% for c in computers %}
          <option value="{{ c.id }}">{{ c.hostname or c.computer_uid[:14] }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="col-md-3 d-flex align-items-end">
        <button class="btn btn-primary w-100" onclick="loadPivotData()">Загрузить данные</button>
      </div>
    </div>
    
    <div id="pivot_status" class="small text-muted mt-2"></div>
  </div>
</div>

<div class="card">
  <div class="card-body">
    <div id="pivot_output"></div>
  </div>
</div>

{# ---- PivotTable.js via CDN ---- #}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/themes/base/jquery-ui.min.css">
<script src="https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jquery-ui@1.13.2/dist/jquery-ui.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pivottable@2.23.0/dist/pivot.ru.min.js"></script>

<script>
// Форматирование секунд в HH:MM:SS
function fmtDuration(seconds) {
  seconds = Math.round(seconds || 0);
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}

// Регистрируем кастомный агрегатор "Сумма (HH:MM:SS)"
if (window.$.pivotUtilities && $.pivotUtilities.aggregators) {
  // Кастомный агрегатор, который возвращает объект {seconds, formatted}
  $.pivotUtilities.aggregators["Сумма (время)"] = function(data, rowKey, colKey) {
    return {
      sum: 0,
      push: function(record) {
        for (var i = 0; i < rowKey.length; i++) {
          var v = record[rowKey[i]];
          if (typeof v === 'number') this.sum += v;
        }
      },
      value: function() { return this.sum; },
      format: function(x) { return fmtDuration(x); }
    };
  };
}

function getSelectedValues(id) {
  const sel = document.getElementById(id);
  return Array.from(sel.options).filter(o => o.selected).map(o => o.value);
}

function setPivotPeriod(daysAgo) {
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - daysAgo);
  const fmt = d => d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
  document.getElementById('pivot_date_from').value = fmt(from);
  document.getElementById('pivot_date_to').value = fmt(to);
}

async function loadPivotData() {
  const status = document.getElementById('pivot_status');
  status.textContent = 'Загрузка…';
  
  const formData = new FormData();
  formData.append('date_from', document.getElementById('pivot_date_from').value);
  formData.append('date_to', document.getElementById('pivot_date_to').value);
  getSelectedValues('pivot_depts').forEach(v => formData.append('department_ids', v));
  getSelectedValues('pivot_employees').forEach(v => formData.append('employee_ids', v));
  getSelectedValues('pivot_computers').forEach(v => formData.append('computer_ids', v));
  
  try {
    const resp = await fetch('/admin/api/pivot-data', { method: 'POST', body: formData });
    if (!resp.ok) {
      status.textContent = 'Ошибка: ' + resp.status;
      return;
    }
    const data = await resp.json();
    status.textContent = 'Загружено строк: ' + data.total;
    
    if (data.rows.length === 0) {
      document.getElementById('pivot_output').innerHTML = '<div class="text-muted p-3">Нет данных за выбранный период</div>';
      return;
    }
    
    $('#pivot_output').pivotUI(data.rows, {
      rows: ['department', 'employee'],
      cols: ['month_name'],
      aggregatorName: 'Sum',
      vals: ['worked_span', 'worked_union', 'effective', 'intensive', 'break_dur'],
      rendererName: 'Table',
      locale: 'ru',
      unusedAttrsVertical: false,
      renderers: $.extend(
        $.pivotUtilities.renderers,
        $.pivotUtilities.export_renderers || {}
      )
    });
  } catch (e) {
    status.textContent = 'Ошибка: ' + e.message;
  }
}

// Автозагрузка при открытии
document.addEventListener('DOMContentLoaded', () => {
  setPivotPeriod(30);
  loadPivotData();
});

// Синхронизация отделов ? сотрудники
document.getElementById('pivot_depts').addEventListener('change', function() {
  const deps = new Set(Array.from(this.selectedOptions).map(o => o.value));
  const empSel = document.getElementById('pivot_employees');
  Array.from(empSel.options).forEach(o => {
    const d = String(o.dataset.dept || '');
    const show = deps.size === 0 || (d && deps.has(d));
    o.hidden = !show;
    if (!show) o.selected = false;
  });
});
</script>

<style>
.pvtUi { font-size: 13px; }
.pvtAxisContainer, .pvtVals { background: #f8f9fa; border-radius: 4px; }
table.pvtTable { font-size: 12px; }
table.pvtTable tbody tr th, table.pvtTable thead tr th { padding: 4px 6px; }
</style>
{% endblock %}
Hmm — the pivottable.ru.min.js — let me check if that exists. Actually I think locales are separate files. Let me check... pivot.ru.js might not exist. Let me remove locale: 'ru' for now.
Actually pivottable has i18n. Let me check — from memory, they have separate files for locales in dist/. Let me just skip locale.
OK let me finalize.
Actually, a concern: pivottable 2.23.0 min is quite big. And jQuery UI. Total maybe 500KB. Loading via CDN is fine for now.
But wait — the CDN URL might not work. Let me use a more reliable one or use unpkg:
https://unpkg.com/jquery@3.7.1/dist/jquery.min.js
https://unpkg.com/jquery-ui@1.13.2/dist/jquery-ui.min.js
https://unpkg.com/pivottable@2.23.0/dist/pivot.min.js
Both jsdelivr and unpkg should work. Let me use jsdelivr.
OK let me write the response.
Structure:
План веб-pivot (короткий)
Скрипт 1 — backend patcher (function + endpoint + route)
Скрипт 2 — template reports_pivot.html
Скрипт 3 — nav link in base.html
Rebuild + test
Let me write.
Actually — I need to double-check that List is imported in web_admin.py. Let me check... From earlier context: from typing import Optional, List — yes it's there.
And date is imported from datetime — yes.
And RU_MONTHS is defined — yes.
OK writing.
One more thing: the pivottable min.css needs to be included. Yes.
Alright, let me write the response. Given the length, I'll split into this message being the plan + backend, and next message the template.
Actually — let me just do everything in one message. If it's too long, so be it.
No wait — the response could be 800+ lines with all scripts. Let me split:
Message 1 (this): Plan + backend patcher + instructions to test endpoint
Message 2 (next): Template + nav + rebuild
OK, first message.
Hmm, but user might be impatient. Let me do both in one message but be compact.
Let me write the backend first (most important), then template.
Final decision: give both in one message. Long but complete.
Let me write.
For chat length warning: I'll add a short note at top.
Let me go.
Отлично, делаем веб-pivot. По объёму — это 2–3 итерации: сначала бэкенд + API + страница, потом шаблон с PivotTable.js, потом пресеты и полировка. Начинаем с бэкенда, чтобы убедиться, что API отдаёт правильные данные, а потом уже рисовать UI.
Про длину чата: сейчас около 70%. Хватит на 1–2 крупные итерации. Если почувствую, что близко к лимиту — сразу предупрежу и сделаю handoff. Ты тоже, если увидишь, что чат тормозит, скажи.
________________________________________
План веб-pivot
Идея: страница /admin/reports/pivot — с фильтрами (период, отделы, сотрудники, компьютеры) и интерактивной сводной таблицей на PivotTable.js. Тянешь поля «Сотрудник», «Отдел», «Месяц», «День недели» — получаешь ту же логику, что в Excel-сводной.
Что нужно:
Backend — функция _build_pivot_data, которая выдаёт плоские строки (одна строка = один сотрудник за день) в JSON.
API-эндпоинт /admin/api/pivot-data — принимает фильтры, возвращает JSON.
Роут /admin/reports/pivot — отдаёт страницу с фильтрами.
Шаблон reports_pivot.html — с PivotTable.js.
Ссылка в меню.
________________________________________
Скрипт 1 — Backend: функция, API, роут
Что делает:
Добавляет _build_pivot_data(db, filters) — возвращает плоский список: одна строка = (сотрудник, рабочий день), с полями date, year, month_num, month_name, day, weekday, employee, external_id, department, computers, sessions_count, worked_span, worked_union, intensive, effective, break_dur, pause_button.
Добавляет POST /admin/api/pivot-data — принимает те же фильтры, что и отчёты, возвращает {rows, total, date_from, date_to}.
Добавляет GET /admin/reports/pivot — отдаёт страницу (пока пустую, шаблон сделаем следующим шагом).
Запускай:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$patcher = @'
import ast
from pathlib import Path

PATH = Path(r"D:\tracker\server\web_admin.py")
content = PATH.read_text(encoding="utf-8")

if "def _build_pivot_data" in content:
    print("SKIP: pivot уже есть")
    raise SystemExit(0)

