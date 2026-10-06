<!-- Часть 1182 из 1409 -->
# Что	Приоритет
*Хлебные крошки:* Что	Приоритет

[◀ 2. _render_pdf — только строки ПОСЛЕ 60-й (то, что не видели)](1181_2_render_pdf_tolko_stroki_POSLE_60_y_to_chto_ne_videli.md) | [Оглавление](00_BCE_INDEX.md) | [--- Утилита: заменяем функцию целиком по имени --- ▶](1183_Utilita_zamenyaem_funktsiyu_tselikom_po_imeni.md)

---

#	Что	Приоритет
1	Кнопка «Вчера» — ставит только date_from	??
2	Кнопки «7 дней», «30 дней» — тоже могут быть кривые	??
3	Сохранение фильтров отчёта в localStorage	??
4	Экспорт CSV/XLSX/PDF — старые колонки (без Интенсивная/Пауза)	??
5	XLSX не готов к сводной таблице	??
6	Кнопки «Свернуть всё / Развернуть всё»	??
7	Сортировка по столбцам	??
8	Иерархия: отдел ? сотрудник ? день ? программа	??
9	Отчёт «Отделы ? Программы»	??
10	Матрица «сотрудник ? программа»	??
11	Экспорт XLSX с несколькими листами	??
12	Экспорт отчёта по расписанию (по понедельникам на почту)	??
13	Графики активности по часам (Chart.js)	??
?? Особые требования к XLSX для pivot table
Чтобы Excel принял файл как источник сводной, нужно:
Одна строка заголовка — без склеенных ячеек и без двухэтажных шапок.
Никаких пустых строк между данными (ИТОГО в конце ломает pivot).
Типизированные значения:
дата — как datetime.date (не строка!), с форматом DD.MM.YYYY;
длительности — как timedelta с форматом [HH]:MM:SS;
числовые — как int (без строк).
Уникальные имена колонок без пробелов/точек (Excel сам их чинит, но лучше заранее: Рабочий_день, С_трекером и т.д.).
Отдельный лист для сводки «ИТОГО», если она нужна.
Дополнительные полезные колонки для pivot: «Год», «Месяц №» (число 1–12), «День недели» — чтобы группировать в сводной по ним.
________________________________________
2. Рекомендуемая очерёдность
Чтобы не переделывать по 2–3 раза — идём так:
Шаг A (сейчас). Кнопки периодов + localStorage.
Это HTML/JS, не трогает бэкенд. Заканчиваем UI-часть формы.
Шаг B. Обновление CSV/XLSX/PDF с новыми колонками.
Здесь мы уже будем знать точный набор фильтров и формат отчёта, чтобы не переделывать.
Шаг C. XLSX под pivot table.
Отдельные листы, типизированные значения, Месяц №.
Шаг D. Иерархия + Свернуть/развернуть.
Это большой UI-рефактор report_result.html, но бэкенд уже готов.
Шаг E. Отчёты по программам (Отделы ? Программы, матрица).
Логика: сначала то, что не требует переделки бэкенда и может быть закончено одним куском. Потом — то, что требует согласованного формата данных.
________________________________________
3. Шаг A — сейчас: кнопки периодов + localStorage
Даю полную замену reports.html. Этот шаблон теперь:
Правильно ставит обе даты во всех кнопках.
Сохраняет все фильтры (период, TZ, группировка, отделы, сотрудники, ПК, чекбоксы) в localStorage.
Восстанавливает их при открытии страницы.
Содержит маленькую кнопку «Сбросить фильтры».
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$template = @'
{% extends "base.html" %}
{% block title %}Отчёты{% endblock %}
{% block content %}
<h3 class="mb-4">Отчёты</h3>
<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/reports/generate" id="reportForm">
      <div class="mb-3">
        <label class="form-label fw-bold">Период</label>
        <div class="d-flex flex-wrap gap-2 mb-2">
          <button type="button" class="btn btn-sm btn-outline-secondary" data-period="today">Сегодня</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-period="yesterday">Вчера</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-period="last7">7 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-period="last30">30 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-period="thisMonth">Этот месяц</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-period="lastMonth">Прошлый месяц</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-period="thisYear">Этот год</button>
          <button type="button" class="btn btn-sm btn-link text-decoration-none" id="btnResetFilters"
                  title="Сбросить сохранённые фильтры">? Сбросить</button>
        </div>
        <div class="row g-2">
          <div class="col-md-3">
            <input class="form-control" type="date" name="date_from" id="date_from" required value="{{ today }}">
          </div>
          <div class="col-md-3">
            <input class="form-control" type="date" name="date_to" id="date_to" required value="{{ today }}">
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-3">
          <label class="form-label">
            Отделы
            <span class="hint" data-bs-toggle="tooltip" title="Если ничего не выбрано — все отделы. При выборе одного или нескольких — сотрудники фильтруются автоматически.">?</span>
          </label>
          <input type="text" class="form-control form-control-sm mb-1" placeholder="Поиск отдела…"
                 oninput="filterOptions('departments_select', this.value)">
          <select name="department_ids" id="departments_select" class="form-select multi-select" multiple
                  onchange="onDepartmentsChanged()">
            {% for d in departments %}
            <option value="{{ d.id }}" data-name="{{ d.name }}">{{ d.name }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">
            Сотрудники
            <span class="hint" data-bs-toggle="tooltip" title="Список автоматически фильтруется по выбранным отделам. Ctrl + клик — выбрать несколько.">?</span>
          </label>
          <input type="text" class="form-control form-control-sm mb-1" placeholder="Поиск по ФИО или 1C ID…"
                 oninput="filterOptions('employees_select', this.value)">
          <select name="employee_ids" id="employees_select" class="form-select multi-select" multiple>
            {% for e in employees %}
            <option value="{{ e.id }}"
                    data-dept="{{ e.department_id or '' }}"
                    data-name="{{ e.full_name }} {{ e.external_id or '' }}">
              {{ e.full_name }}{% if e.external_id %} ({{ e.external_id }}){% endif %}
            </option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Компьютеры</label>
          <input type="text" class="form-control form-control-sm mb-1" placeholder="Поиск ПК…"
                 oninput="filterOptions('computers_select', this.value)">
          <select name="computer_ids" id="computers_select" class="form-select multi-select" multiple>
            {% for c in computers %}
            <option value="{{ c.id }}" data-name="{{ c.hostname or '' }} {{ c.computer_uid }}">
              {{ c.hostname or c.computer_uid[:20] }}
            </option>
            {% endfor %}
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Группировка</label>
          <select name="group_by" id="group_by" class="form-select">
            <option value="days" selected>Рабочие дни ? Сотрудник</option>
            <option value="months">Месяц ? Сотрудник</option>
            <option value="employees">По сотрудникам</option>
            <option value="departments">По отделам</option>
            <option value="computers">По компьютерам</option>
            <option value="sessions">Детально — каждая сессия</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Формат</label>
          <select name="fmt" class="form-select">
            <option value="html">Просмотр</option>
            <option value="xlsx">Excel (XLSX)</option>
            <option value="csv">CSV</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
      </div>

      <div class="mt-3">
        <label class="form-label fw-bold">Что показывать</label>
        <div class="d-flex flex-wrap gap-4">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_apps" id="show_apps" checked>
            <label class="form-check-label" for="show_apps">Топ-программы</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_abnormal" id="show_abnormal" checked>
            <label class="form-check-label" for="show_abnormal">Пометки аварийных</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="expand_details" id="expand_details">
            <label class="form-check-label" for="expand_details">Разворачивать детали</label>
          </div>
        </div>
      </div>

      <div class="alert alert-secondary py-2 small mt-3 mb-0">
        Часовой пояс, начало дня, порог паузы — в <a href="/admin/settings">Настройках</a>.<br>
        TZ = <strong>{{ cfg.report_timezone }}</strong>,
        начало дня = <strong>{{ '%02d' % cfg.workday_start_hour }}:00</strong>,
        порог паузы = <strong>{{ cfg.activity_gap_minutes }} мин</strong>.
      </div>

      <button class="btn btn-primary mt-3">Сформировать отчёт</button>
    </form>
  </div>
</div>

<script>
(function() {
  const STORAGE_KEY = "tracker_report_filters_v1";
  const EMP_DEPT_MAP = {{ emp_dept_map | tojson }};

  // ---------- Утилиты ----------
  function fmt(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return y + '-' + m + '-' + dd;
  }
  function setRange(fromDate, toDate) {
    document.getElementById('date_from').value = fmt(fromDate);
    document.getElementById('date_to').value = fmt(toDate);
  }
  function getSelectedValues(id) {
    const sel = document.getElementById(id);
    if (!sel) return [];
    return Array.from(sel.options).filter(o => o.selected).map(o => o.value);
  }
  function setSelectedValues(id, values) {
    const sel = document.getElementById(id);
    if (!sel) return;
    const wanted = new Set((values || []).map(String));
    for (const o of sel.options) o.selected = wanted.has(String(o.value));
  }
  function check(id) { const el = document.getElementById(id); return el && el.checked; }
  function setChecked(id, v) { const el = document.getElementById(id); if (el) el.checked = !!v; }
  function getSelect(id) { const el = document.getElementById(id); return el ? el.value : ''; }
  function setSelect(id, v) { const el = document.getElementById(id); if (el && v) el.value = v; }

  // ---------- Периоды ----------
  function periodToday() { const n = new Date(); setRange(n, n); }
  function periodYesterday() { const d = new Date(); d.setDate(d.getDate() - 1); setRange(d, d); }
  function periodLastNDays(n) {
    const to = new Date(); const from = new Date();
    from.setDate(from.getDate() - (n - 1));
    setRange(from, to);
  }
  function periodThisMonth() {
    const now = new Date();
    setRange(new Date(now.getFullYear(), now.getMonth(), 1),
             new Date(now.getFullYear(), now.getMonth() + 1, 0));
  }
  function periodLastMonth() {
    const now = new Date();
    setRange(new Date(now.getFullYear(), now.getMonth() - 1, 1),
             new Date(now.getFullYear(), now.getMonth(), 0));
  }
  function periodThisYear() {
    const now = new Date();
    setRange(new Date(now.getFullYear(), 0, 1),
             new Date(now.getFullYear(), 11, 31));
  }

  const PERIOD_HANDLERS = {
    today: periodToday,
    yesterday: periodYesterday,
    last7: () => periodLastNDays(7),
    last30: () => periodLastNDays(30),
    thisMonth: periodThisMonth,
    lastMonth: periodLastMonth,
    thisYear: periodThisYear,
  };

  document.querySelectorAll('button[data-period]').forEach(btn => {
    btn.addEventListener('click', function() {
      const key = this.dataset.period;
      const h = PERIOD_HANDLERS[key];
      if (h) h();
    });
  });

  // ---------- Зависимая фильтрация: отделы ? сотрудники ----------
  window.onDepartmentsChanged = function() {
    const depsSel = document.getElementById('departments_select');
    const selectedDeps = new Set();
    for (const o of depsSel.options) if (o.selected) selectedDeps.add(String(o.value));
    const empSel = document.getElementById('employees_select');
    for (const opt of empSel.options) {
      const edp = String(opt.dataset.dept || '');
      const show = selectedDeps.size === 0 || (edp && selectedDeps.has(edp));
      opt.hidden = !show;
      if (!show) opt.selected = false;
    }
  };

  window.filterOptions = function(selectId, query) {
    const sel = document.getElementById(selectId);
    const q = (query || '').toLowerCase().trim();
    for (const opt of sel.options) {
      const txt = (opt.dataset.name || opt.textContent).toLowerCase();
      opt.hidden = q ? !txt.includes(q) : false;
    }
  };

  // ---------- Сохранение / восстановление ----------
  function saveFilters() {
    try {
      const data = {
        date_from: getSelect('date_from'),
        date_to: getSelect('date_to'),
        group_by: getSelect('group_by'),
        fmt: getSelect('fmt'),
        department_ids: getSelectedValues('departments_select'),
        employee_ids: getSelectedValues('employees_select'),
        computer_ids: getSelectedValues('computers_select'),
        show_apps: check('show_apps'),
        show_abnormal: check('show_abnormal'),
        expand_details: check('expand_details'),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
      console.warn('saveFilters failed', e);
    }
  }

  function loadFilters() {
    let data;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      data = JSON.parse(raw);
    } catch (e) {
      console.warn('loadFilters failed', e);
      return;
    }
    // Период
    if (data.date_from) document.getElementById('date_from').value = data.date_from;
    if (data.date_to) document.getElementById('date_to').value = data.date_to;
    // Группировка и формат
    if (data.group_by) setSelect('group_by', data.group_by);
    if (data.fmt) setSelect('fmt', data.fmt);
    // Мультиселекты
    setSelectedValues('departments_select', data.department_ids);
    // После восстановления отделов — пересчитать видимость сотрудников
    onDepartmentsChanged();
    setSelectedValues('employees_select', data.employee_ids);
    setSelectedValues('computers_select', data.computer_ids);
    // Чекбоксы
    if (typeof data.show_apps === 'boolean') setChecked('show_apps', data.show_apps);
    if (typeof data.show_abnormal === 'boolean') setChecked('show_abnormal', data.show_abnormal);
    if (typeof data.expand_details === 'boolean') setChecked('expand_details', data.expand_details);
  }

  function resetFilters() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
    location.reload();
  }

  // Сохраняем при отправке формы
  const form = document.getElementById('reportForm');
  form.addEventListener('submit', saveFilters);

  // Сброс
  document.getElementById('btnResetFilters').addEventListener('click', resetFilters);

  // Восстанавливаем при загрузке
  loadFilters();
})();
</script>
{% endblock %}
'@

[System.IO.File]::WriteAllText("D:\tracker\server\templates\reports.html", $template, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: reports.html переписан ($($template.Length) символов)" -ForegroundColor Green
Проверка
Пересборка:
powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose logs api --tail=10
Открой /admin/reports. Должно работать:
Кнопки периодов: нажми «Вчера» — обе даты станут вчерашними.
«7 дней» — диапазон 7 дней.
Поставь какие-нибудь фильтры, нажми «Сформировать», вернись на /admin/reports — фильтры должны восстановиться.
Кнопка «? Сбросить» — очищает сохранённые фильтры.
Пришли скриншот формы — убедимся, что всё на месте. Потом перейдём к шагу B (экспорт CSV/XLSX/PDF) и шагу C (XLSX для pivot).
всё работает
Отлично, всё работает. Пользователь подтвердил, что кнопки периодов и localStorage теперь работают (на скриншоте видно, что даты 24.09.2026 в обоих полях, то есть "Вчера" отработал).
Теперь переходим к следующему шагу по плану. Я расписывал:
Шаг A (кнопки периодов + localStorage) — сделано ?
Шаг B — обновление CSV/XLSX/PDF с новыми колонками
Шаг C — XLSX под pivot table
Шаг D — иерархия + Свернуть/развернуть
Шаг E — отчёты по программам
Пользователь также писал: "XLSX должен быть подготовлен к работе со сводной таблицей." и "Например период вчера мы так и не исправили, но я сейчас предлагаю вообще их исправить, мы не сделали сохранение настроек в отчёте."
Он хочет сразу сделать:
Экспорт CSV/XLSX/PDF с новыми колонками
XLSX под pivot table
Давай объединю это в один шаг. Нам нужно:
Обновить _render_csv:
Заголовки: добавить "С трекером", "Интенсивная", "Пауза"
ИТОГО тоже обновить
Обновить _render_xlsx:
Заголовки + новые колонки
Типизированные значения для pivot
Уникальные имена колонок (без пробелов, для pivot)
Добавить колонки "Год", "Месяц №" (число), "День недели"
Отдельный лист "ИТОГО" чтобы не мешать
Формат длительностей [HH]:MM:SS
Обновить _report_row_to_list — добавить 3 колонки
Обновить _report_row_to_xlsx — то же
Обновить _render_pdf — новые колонки в таблице
_pdf_table_data — тоже надо посмотреть и обновить.
Мне нужно узнать текущий код _pdf_table_data. Он упоминался в _render_pdf на строке 98: headers, rows = _pdf_table_data(report, styles).
Давай сначала попрошу показать _pdf_table_data, чтобы не гадать. Или могу сразу написать патч, который использует существующие функции-хелперы, и если что-то пойдёт не так — посмотрим.
На самом деле, для правильной последовательности — сначала дам патч, который обновит:
_render_csv (заголовки + ИТОГО)
_report_row_to_list (3 колонки)
_report_row_to_xlsx (3 колонки)
_render_xlsx (заголовки + формат колонок + pivot-friendly структура)
_pdf_table_data (заголовки + данные)
Но я не видел _pdf_table_data. Давай сначала попрошу диагностику этой функции — она короткая. Или могу сделать патч, который сам найдёт её и обновит по маркерам, но это рискованно.
Лучше сначала диагностика — одна короткая команда. Потом — один большой патч.
На самом деле, чтобы не затягивать, дам патч без pdf. То есть:
Сначала сделаем CSV+XLSX с pivot-friendly структурой.
PDF трогаем отдельно, когда увидим _pdf_table_data.
А лучше сразу посмотреть _pdf_table_data в этом же сообщении. Давай дам команду диагностики + сразу обещание патча, но патч напишу после вывода. Хотя пользователь хочет прогресс — дам сразу патч для CSV/XLSX, а PDF отложу.
Или — сделаю по-другому: сначала диагностика _pdf_table_data, потом один большой патч на всё (CSV, XLSX, PDF). Один заход.
Думаю, лучше так: дам диагностику _pdf_table_data (быстро) и параллельно поясню план патча для CSV/XLSX. Пользователь запустит диагностику, пришлёт вывод — и я дам один полный патч.
Давай так.
Ключевые решения для XLSX под pivot:
Формат заголовков: для pivot table в Excel имена колонок не должны содержать пробелов/точек. Обычно рекомендуют заменять пробелы на _. Но Excel 2016+ и так нормально работает с пробелами. А вот . и [ ] — проблемные.
В нашем случае колонки: "Рабочий день", "Год", "Месяц", "Число", "Сотрудник", "1C ID", "Отдел", "Компьютер", "Сессий", "Отработано", "С трекером", "Интенсивная", "Эффективно", "Пауза".
Пробелы можно оставить, pivot сам обработает. Но лучше избегать — сделаю через _, чтобы точно работало:
Рабочий_день
С_трекером
и т.д.
Хотя с точки зрения UI это выглядит странно. Excel всё равно покажет с подчёркиваниями. Хм.
Решение: оставить заголовки с пробелами, pivot работает и так. Excel автоматически преобразует названия в pivot. Главное — не дублировать и не делать очень длинных.
Дополнительные колонки для pivot:
Год (2026)
Месяц_номер (9) — число
Месяц (Сентябрь) — название
Число (24) — день месяца
День_недели (Четверг) — для группировки по дням недели
Это даст пользователю удобную базу для pivot.
Структура XLSX:
Лист "Данные" — одна строка = одна группа (без ИТОГО)
Лист "ИТОГО" — сводка по фильтру отдельным листом
Это стандартный подход, чтобы ИТОГО не мешал сводной.
Формат данных:
Дата — datetime.date с форматом DD.MM.YYYY
Длительность — timedelta с форматом [HH]:MM:SS
Числовые — int
Хорошо. Пишу ответ.
Стоит также подумать: текущие функции _report_row_to_list и _report_row_to_xlsx возвращают разные наборы для разных группировок. Если мы добавляем "Год/Месяц/Число/День недели", то для "sessions" это будет дата сессии, для "days" — дата дня, для "months" — месяц, для "employees" — пусто (не применимо), для "departments" — пусто, для "computers" — пусто.
Хм. Для pivot таблицы лучше, чтобы структура была унифицирована. Но не для всех группировок. Например, "По сотрудникам" — там нет одной даты, там период. Можно заполнить "Год" как год начала периода, "Месяц" как месяц. Но это не точно.
Давай так:
В режиме "days" и "sessions" — полная дата (Год, Месяц_номер, Месяц, Число, День_недели)
В режиме "months" — Год + Месяц_номер + Месяц (Число и День_недели пустые)
В режиме "employees", "departments", "computers" — все пустые (нет одной даты)
Для pivot по сотрудникам пользователь сможет использовать фильтры "Сотрудник", "Отдел", "Сессий", "Отработано" и т.д.
Ок. Пишу ответ.
Также стоит добавить в шапку XLSX "Автофильтр" — чтобы сразу можно было фильтровать в Excel.
Пишу.
Длина ответа должна быть умеренной — даю диагностику и план. При следующем сообщении будет патч.
Хотя пользователь ждёт прогресс. Давай сразу:
Диагностика _pdf_table_data (одна команда)
И одновременно дам патч для CSV+XLSX (без PDF), чтобы пользователь начал делать это, пока мы ждём.
Хм, но если делать патч для CSV+XLSX, то _report_row_to_list и _report_row_to_xlsx изменятся — а PDF использует _pdf_table_data, не эти функции. Так что можно смело патчить.
Давай так и сделаю: диагностика _pdf_table_data + патч для CSV/XLSX.
Хотя — патч длинный. Может лучше сделать по частям:
Сначала патч _report_row_to_list и _report_row_to_xlsx (добавить 3 колонки)
Потом патч заголовков в _render_csv и _render_xlsx
Потом — XLSX под pivot (отдельный патч)
PDF отдельно
Это 3-4 патча. Пользователь устанет. Лучше один большой патч с заменой функций целиком.
Давай — один патч, который перезапишет целиком:
_report_row_to_list
_report_row_to_xlsx
_render_csv
_render_xlsx
А PDF — отдельно, после того как покажет _pdf_table_data.
Всё, пишу.
Отлично, кнопка «Вчера» и сохранение фильтров работают — на скриншоте обе даты 24.09.2026. Шаг A закрыт.
Переходим к шагу B+C одним заходом: обновляем CSV и XLSX (и сразу готовим XLSX под pivot table). PDF отложим — там нужна отдельная функция _pdf_table_data, её сначала покажем.
План этого шага
CSV — 14 колонок вместо 11: добавляем С трекером, Интенсивная, Пауза. Плюс Год / Месяц_номер / Месяц / Число / День_недели для аналитики.
XLSX — то же + типизированные значения:
дата как datetime.date с форматом DD.MM.YYYY
длительности как timedelta с форматом [HH]:MM:SS
числовые как int
отдельный лист «ИТОГО» — чтобы не мешал сводной
автофильтр на шапке — чтобы сразу фильтровать в Excel
pivot-friendly заголовки — с пробелами, Excel сам справится
Скрипт — полная замена функций
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\web_admin.py")
content = PATH.read_text(encoding="utf-8")

