<!-- Часть 1219 из 1409 -->
# Отрезаем всё от <script> после CDN до </script>
*Хлебные крошки:* Отрезаем всё от <script> после CDN до </script>

[◀ Удаляем ненужный теперь fieldLabels (или оставим, не мешает)](1218_Udalyaem_nenuzhnyy_teper_fieldLabels_ili_ostavim_ne_meshaet.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ▶](1220_Proverka.md)

---

# Отрезаем всё от <script> после CDN до </script>
$marker_start = $content.IndexOf('<script>' + "`n" + '// ============================================================' + "`n" + '// Форматирование секунд')
if ($marker_start -lt 0) {
    # Альтернативный поиск — по ключевой функции
    $marker_start = $content.IndexOf('// Форматирование секунд')
    if ($marker_start -gt 0) {
        $marker_start = $content.LastIndexOf('<script>', $marker_start)
    }
}
$marker_end = $content.IndexOf('</script>', $marker_start)

if ($marker_start -lt 0 -or $marker_end -lt 0) {
    Write-Host "ERROR: не найден блок script" -ForegroundColor Red
    exit 1
}

$newScript = @'
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
// Кастомный агрегатор "Сумма (время)" через шаблон.
// PivotTable.js сам вызовет его с именем поля из vals.
// ============================================================
$.pivotUtilities.aggregatorTemplates.durationSum = function() {
  return function(dimension) {
    return function(data, rowKey, colKey) {
      return {
        sum: 0,
        push: function(record) {
          const v = record[dimension];
          if (typeof v === 'number' && !isNaN(v)) this.sum += v;
        },
        value: function() { return this.sum; },
        format: function(x) { return fmtDuration(x); },
        label: 'Сумма (время)',
        numInputs: 0
      };
    };
  };
};

// Аналогично для среднего
$.pivotUtilities.aggregatorTemplates.durationAvg = function() {
  return function(dimension) {
    return function(data, rowKey, colKey) {
      return {
        sum: 0, count: 0,
        push: function(record) {
          const v = record[dimension];
          if (typeof v === 'number' && !isNaN(v)) { this.sum += v; this.count += 1; }
        },
        value: function() { return this.count ? this.sum / this.count : 0; },
        format: function(x) { return fmtDuration(x); },
        label: 'Среднее (время)',
        numInputs: 0
      };
    };
  };
};

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

    // Регистрируем агрегаторы в объекте aggregators для pivotUI
    const aggregators = {
      "Сумма (время)": $.pivotUtilities.aggregatorTemplates.durationSum(),
      "Среднее (время)": $.pivotUtilities.aggregatorTemplates.durationAvg(),
      "Count": $.pivotUtilities.aggregators["Count"],
      "Count Unique Values": $.pivotUtilities.aggregators["Count Unique Values"],
      "List Unique Values": $.pivotUtilities.aggregators["List Unique Values"],
      "Sum": $.pivotUtilities.aggregators["Sum"],
      "Average": $.pivotUtilities.aggregators["Average"]
    };

    $('#pivot_output').pivotUI(data.rows, {
      rows: ['Отдел', 'Сотрудник'],
      cols: ['Месяц'],
      aggregatorName: 'Сумма (время)',
      vals: ['Отработано (сек)', 'Эффективно (сек)', 'Интенсивная (сек)', 'Пауза (сек)'],
      rendererName: 'Table',
      unusedAttrsVertical: false,
      autoSortUnusedAttrs: true,
      showUI: true,
      aggregators: aggregators
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
'@

$content = $content.Substring(0, $marker_start) + $newScript + $content.Substring($marker_end + '</script>'.Length)
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: JS-блок шаблона заменён ($($newScript.Length) символов)" -ForegroundColor Green

