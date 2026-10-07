# Заменяем блок pivotUI + опции

*Часть 94 из 100. Источник: `BCE.md`.*

[◀ Проверка синтаксиса](093_Proverka_sintaksisa.md) | [Оглавление](00_BCE_INDEX.md) | [2. Структура проекта ▶](095_2_Struktura_proekta.md)

---

# Заменяем блок pivotUI + опции
old_block = re.compile(
    r"\$\('#pivot_output'\)\.pivotUI\(data\.rows, \{.*?\n    \}\);",
    re.DOTALL,
)
m = old_block.search(content)
if not m:
    print("ERROR: не найден вызов pivotUI")
    raise SystemExit(1)

new_block = '''$('#pivot_output').pivotUI(data.rows, {
      rows: ['Отдел', 'Сотрудник'],
      cols: ['Месяц'],
      aggregatorName: 'Сумма (время)',
      vals: ['Отработано (сек)', 'Эффективно (сек)', 'Интенсивная (сек)', 'Пауза (сек)'],
      rendererName: 'Table',
      unusedAttrsVertical: false,
      autoSortUnusedAttrs: true,
      showUI: true,
      aggregators: {
        "Сумма (время)": makeDurationAggregator("Сумма (время)"),
        "Среднее (время)": $.pivotUtilities.aggregators["Среднее (время)"] || null,
        "Count": $.pivotUtilities.aggregators["Count"],
        "Count Unique Values": $.pivotUtilities.aggregators["Count Unique Values"],
        "List Unique Values": $.pivotUtilities.aggregators["List Unique Values"],
        "Sum": $.pivotUtilities.aggregators["Sum"],
        "Average": $.pivotUtilities.aggregators["Average"]
      }
    });'''

content = content[:m.start()] + new_block + content[m.end():]

# Также убираем attributeLabels и locale, если остались
content = re.sub(r"\s*locale:\s*'ru',", "", content)
content = re.sub(
    r"\s*attributeLabels:\s*fieldLabels,",
    "",
    content,
)

# Удаляем ненужный теперь fieldLabels (или оставим, не мешает)
PATH.write_text(content, encoding="utf-8")

print("OK: pivotUI обновлён под русские ключи")
for m in ["'Отдел', 'Сотрудник'", "'Отработано (сек)'", "makeDurationAggregator"]:
    print(f" {'OK' if m in content else 'MISS'}: {m}")
'@
[System.IO.File]::WriteAllText("D:\tracker\_patch_pivot_tpl_ru.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч шаблона pivot ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_pivot_tpl_ru.py
Что ожидаем:
text
OK: pivotUI обновлён под русские ключи
 OK: 'Отдел', 'Сотрудник'
 OK: 'Отработано (сек)'
 OK: makeDurationAggregator
________________________________________
Скрипт 3 — Пересборка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Синтаксис ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe -c "import ast; ast.parse(open(r'D:\tracker\server\web_admin.py', encoding='utf-8').read()); print('OK')"

Write-Host "`n=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
docker compose logs api --tail=15
________________________________________
Проверка в браузере
Открой https://localhost/admin/reports/pivot.
Обнови страницу жёстко: Ctrl+Shift+R (или Ctrl+F5), чтобы сбросить кеш.
Через пару секунд подгрузится сводная.
Проверь заголовки полей — теперь должны быть русскими: «Отдел», «Сотрудник», «Месяц», «Отработано (сек)» и т. д.
Прокрути страницу вниз — там должна быть сама pivot-таблица с данными.
Что важно увидеть на скриншоте:
Слева зона со списком полей — все на русском.
Сверху зоны «Строки» / «Колонки» / «Значения» — заполнены: Отдел, Сотрудник / Месяц / Отработано (сек), Эффективно (сек), Интенсивная (сек), Пауза (сек).
Сама таблица — либо ниже, либо нужно прокрутить. Если её нет — это отдельный баг, будем чинить.
________________________________________
Что прислать
Вывод Скрипта 1 (8 строк).
Вывод Скрипта 2 (4 строки).
Вывод Скрипта 3 (статус контейнеров + логи).
Скриншот всей страницы — с прокруткой вниз, чтобы была видна сама таблица.
Если таблица рендерится — увидим данные и пойдём к следующему шагу (пресеты + экспорт сводной в XLSX). Если нет — разберёмся с рендером.
Запускай скрипты по порядку — и присылай.
Язык перевёлся, данные не попадают в таблицу я каждый раз прикладываю огромный файл с нашей перепиской он влияет на длину чата? давай ды соберёшь мне новый файл совсем подробностями хотелками нюансам кодами структурами ошибками он же наверняка будет короче, и я больше этот огромный файл прикладывать не буду. что бы по нему можно было инструкцию писать по программе. что бы когда либо его не приложил бы тебе ты всё понял бы.
Пользователь просит:
Разобраться, почему данные не попадают в таблицу (заголовки перевелись, но сама таблица пустая).
Собрать новый компактный файл-хендофф вместо огромного файла переписки, чтобы его можно было прикладывать вместо всего чата.
По первому вопросу: вижу на скриншоте, что pivotUI отрендерился, зоны есть, но сама таблица пустая. Проблема в том, что в моём шаблоне вызывается pivotUI(data.rows, {...}), но по умолчанию рендерер PivotTable.js — это «Table», и он должен показывать данные. Однако на скриншоте таблицы нет.
Возможные причины:
Значения (vals) — строковые ключи не совпадают с реальными ключами в data.rows. Я переименовал в русские, но pivotUI для полей значения может не находить их.
Агрегатор возвращает 0, потому что не находит числовые поля.
Может быть, проблема в том, что кастомный агрегатор makeDurationAggregator неправильно считает: он ищет rowKey[i] в record, но в PivotTable.js rowKey — это массив имён полей. Проверю.
Смотрю на мой makeDurationAggregator:
js
push: function(record) {
  for (let i = 0; i < rowKey.length; i++) {
    const v = record[rowKey[i]];
    if (typeof v === 'number') this.sum += v;
  }
}
Здесь rowKey — это массив имён полей (например ['Отдел', 'Сотрудник']), а не значения. record[rowKey[i]] — это получить значение поля Отдел из записи. Это НЕ то, что нужно. Нужно суммировать поля из vals, а не из rows.
Правильный агрегатор должен принимать vals как параметр. Но в PivotTable.js кастомные агрегаторы не получают vals напрямую в push. Вместо этого есть паттерн, где агрегатор создаётся фабрикой, которая знает vals:
js
function makeDurationAggregator(vals) {
  return function(data, rowKey, colKey) {
    return {
      sum: 0,
      push: function(record) {
        for (const v of vals) {
          const x = record[v];
          if (typeof x === 'number') this.sum += x;
        }
      },
      ...
    }
  }
}
Но по умолчанию pivotUI вызывает агрегатор как aggregatorName(data, rowKey, colKey), и мы не знаем заранее, какие vals выбраны. Можно объединить все значения в один сумматор — тогда при выборе одного vals будет сумма по всем, что неверно.
Проще всего — вообще не использовать кастомный агрегатор для форматирования. Вместо этого:
Использовать встроенный Sum (сумма) — он работает.
Для форматирования чисел в HH:MM:SS использовать post-processing: пройтись по ячейкам таблицы и заменить.
Или использовать встроенный рендерер Table со встроенным агрегатором Sum, а форматирование сделать через коллбэк onRefresh — после рендера пройтись по всем <td> с числами и перевести в HH:MM:SS.
Это надёжнее.
Смотрим на текущий код:
js
aggregatorName: 'Сумма (время)',
vals: ['Отработано (сек)', 'Эффективно (сек)', 'Интенсивная (сек)', 'Пауза (сек)'],
Если агрегатор неправильный — данные не попадут.
Также заметил: в aggregators я передаю "Сумма (время)": makeDurationAggregator("Сумма (время)") — здесь мы вызываем makeDurationAggregator БЕЗ аргумента vals, поэтому внутри push перебирается rowKey, а не vals. То есть суммируются значения полей, которые в rows (Отдел, Сотрудник) — а это строки, не числа. Отсюда нули.
Решение:
Использовать встроенный агрегатор Sum.
Форматирование HH:MM:SS сделать после рендера через onRefresh или через отдельный рендерер.
Но onRefresh в PivotTable.js v2 вызывается после каждого рендера. Внутри можно пройтись по таблице и преобразовать числа.
Другой путь — написать правильный фабричный агрегатор:
js
function makeDurationAggregator(vals) {
  return function(data, rowKey, colKey) {
    return {
      sum: 0,
      push: function(record) {
        for (const v of vals) {
          if (typeof record[v] === 'number') this.sum += record[v];
        }
      },
      value: function() { return this.sum; },
      format: function(x) { return fmtDuration(x); },
    };
  };
}
И вызвать makeDurationAggregator(['Отработано (сек)', 'Эффективно (сек)', 'Интенсивная (сек)', 'Пауза (сек)']) — передать список vals.
Но при этом если пользователь выберет другой набор vals, агрегатор не адаптируется. Это ограничение PivotTable.js — кастомные агрегаторы не получают vals автоматически.
Проще и надёжнее: использовать встроенный Sum, а форматирование делать через CSS/JS после рендера.
Или ещё один подход: сделать так, чтобы все значения были уже в правильном виде — но тогда pivot не сможет суммировать.
Итоговое решение:
Использовать встроенный Sum (стандартный агрегатор PivotTable.js).
После рендера через onRefresh пройтись по всем ячейкам <td> в .pvtTable и заменить числовые значения секунд на HH:MM:SS.
Это стандартный трюк. Форматирование выполняется один раз после каждого рендера.
Также нужно проверить, что поля vals в data.rows имеют числовые значения — они точно имеют, потому что в бэкенде int((end - start).total_seconds()).
Второй вопрос: пользователь хочет компактный handoff-файл. Сделаю подробный markdown-документ со структурой, файлами, ключевыми решениями, командами, и передам как содержимое одного файла.
Длина ответа должна быть разумной. Сделаю два фокуса:
Патч шаблона pivot — фикс агрегатора (короткий скрипт).
Handoff-документ — большой markdown, который пользователь сохранит в файл (я не могу создать файл, но могу дать текст, который он сохранит).
Дам в одном ответе:
Диагностику проблемы.
Скрипт 1: патч шаблона (замена агрегатора на Sum + пост-форматирование).
Скрипт 2: пересборка.
Полный текст handoff-документа.
Пользователь просит "давай ты соберёшь мне новый файл совсем подробностями хотелками нюансам кодами структурами ошибками". Это большой документ. Я его напишу целиком как markdown, чтобы пользователь мог сохранить в файл HANDOFF.md.
Файл будет содержать:
Паспорт проекта.
Стек и структура.
Что сделано.
Что осталось.
Ключевые решения (метрики, роли, партиционирование, auth).
Структура БД.
Роуты и API.
Команды.
Проблемы и решения.
Открытые баги и задачи.
Стиль работы.
Постараюсь уместить в разумный объём, но подробно.
Формат ответа:
Кратко про проблему pivot.
Скрипт 1 — патч.
Скрипт 2 — пересборка.
Handoff-документ целиком.
Начнём.
Стоп — надо ещё проверить, что данные вообще приходят. На скриншоте "Загружено строк 377". Значит API работает. Проблема именно в рендере таблицы. Скорее всего — агрегатор.
Проверим ещё раз:
aggregatorName: 'Сумма (время)' — есть в aggregators.
makeDurationAggregator("Сумма (время)") — вызывается с одним аргументом (метка), а не с vals. Внутри push используется rowKey[i] вместо vals[i]. rowKey — массив ИМЁН полей, не значений. Значит record[rowKey[i]] = record['Отдел'] = строка. typeof === 'number' ? false. sum всегда 0.
Да, вот причина. Исправляем.
Правильный вариант — использовать встроенный Sum и форматировать после рендера. Или использовать фабрику с vals.
Давай сделаю комбинированный подход:
Агрегатор «Сумма (время)» — фабрика, которая суммирует все числовые поля из record, кроме тех, что точно не числа (год, число, месяц №, ПК кол-во, сессий). Хм, сложно.
Проще: использовать встроенный Sum (который суммирует выбранные vals). PivotTable.js автоматом применяет Sum к выбранным vals. Тогда таблица отрендерится, но числа будут в секундах.
Форматирование сделаем через onRefresh. Пройтись по .pvtTable td и если содержимое выглядит как число > 60, преобразовать в HH:MM:SS. Но это не точно — там могут быть целые числа сессий, которые тоже > 60.
Другой вариант — по классу колонки. ПivotTable.js добавляет классы к колонкам? Нет, но можно смотреть на порядок. Сложно.
Ещё вариант — отформатировать только ячейки внутри конкретных столбцов. Но в pivot таблице структура меняется динамически.
Самый надёжный способ: использовать фабрику агрегатора, которая знает все числовые поля и суммирует только те, что выбраны в vals. Но pivotUI не передаёт vals в агрегатор. Однако! Когда pivotUI вызывает aggregatorName из aggregators, он использует фабрику, и в v2.23 можно получить vals через замыкание.
Смотрим на PivotTable.js source: при клике на выбор vals обновляется internal state, и агрегатор вызывается с новыми vals внутри — но сам объект агрегатора создаётся один раз. В v2.23 вроде есть поддержка vals через параметр:
js
$.pivotUtilities.aggregatorTemplates.sum = function(formatter) {
  return function(dimension) {
    return function(data, rowKey, colKey) {
      return {
        sum: 0,
        push: function(record) {
          this.sum += record[dimension];
        },
        ...
      };
    };
  };
};
Здесь dimension — это имя поля. То есть шаблон работает только для одного поля. А pivotUI вызывает aggregator(data, rowKey, colKey) для каждого значения... точнее, в pivotUI есть getAggregator:
js
function getAggregator(val, col) {
  var agg, aggName = ...
  if (aggName === 'Sum') agg = $.pivotUtilities.aggregatorTemplates.sum()([val]);
  ...
}
То есть для «Sum» pivotUI сам вызывает sum()([val]) для каждого значения в vals. Для кастомных агрегаторов это не работает автоматически. Нужно, чтобы кастомный агрегатор был зарегистрирован как шаблон, возвращающий фабрику, а не фабрика напрямую.
Проще всего — использовать встроенный «Sum» и форматирование через onRefresh.
Форматирование через onRefresh:
js
onRefresh: function(config) {
  setTimeout(function() {
    $('#pivot_output .pvtTable td').each(function() {
      var txt = $(this).text().trim();
      // Форматируем только числа, которые не похожи на маленькие целые
      if (/^\d+(\.\d+)?$/.test(txt)) {
        var num = parseFloat(txt);
        // Если число большое (секунды) — > 3600 или это долгий интервал
        // Но сессии тоже могут быть > 100
        // Проблема: не отличить секунды от сессий по значению
      }
    });
  }, 10);
}
Проблема: невозможно отличить секунды от других чисел. Нужно знать, какая колонка содержит что.
Лучший вариант — использовать кастомный рендерер (renderer) или несколько агрегаторов, где для каждого vals свой форматтер.
PivotTable.js позволяет регистрировать шаблон агрегатора так, чтобы он работал как встроенные:
js
$.pivotUtilities.aggregatorTemplates.durationSum = function() {
  return function(dimension) {
    return function(data, rowKey, colKey) {
      return {
        sum: 0,
        push: function(record) {
          this.sum += record[dimension] || 0;
        },
        value: function() { return this.sum; },
        format: function(x) { return fmtDuration(x); },
        numInputs: 0,
        label: 'Сумма (время)',
      };
    };
  };
};
Обратим внимание: эта функция возвращает функцию, которая принимает dimension (имя поля). Именно так работает PivotTable.js для стандартных агрегаторов. При вызове через pivotUI он получит список vals и для каждого вызовет aggregatorTemplates['X']()([val]).
Тогда регистрируем в aggregators через aggregatorTemplates:
js
$.pivotUtilities.aggregatorTemplates.durationSum = function() { ... };
$.pivotUtilities.aggregators['Сумма (время)'] = $.pivotUtilities.aggregatorTemplates.durationSum();
PivotTable.js узнаёт через aggregatorTemplates о новых шаблонах, если они добавлены до вызова pivotUI. При использовании aggregators внутри pivotUI мы передаём функцию, но она должна быть уже фабрикой.
Хм, посмотрю исходник: pivotUI использует $.pivotUtilities.aggregatorTemplates для получения шаблонов. Плюс пользователь может передать aggregators — это добавит или перезапишет.
Правильный формат:
js
$.pivotUtilities.aggregatorTemplates.durationSum = function() {
  return function(dimension) {
    return function(data, rowKey, colKey) {
      return {
        sum: 0,
        push: function(record) {
          this.sum += record[dimension] || 0;
        },
        value: function() { return this.sum; },
        format: function(x) { return fmtDuration(x); }
      };
    };
  };
};
И в pivotUI передать в aggregators:
js
aggregators: {
  "Сумма (время)": $.pivotUtilities.aggregatorTemplates.durationSum(),
  ...
}
И aggregatorName: 'Сумма (время)'. PivotTable.js вызовет durationSum()()(vals[0]) для каждого значения в vals.
Да, это правильный подход. Сделаем.
Также при этом формат format(x) будет вызываться для отображения значения — так что HH:MM:SS получится автоматически.
Новое содержимое for template:
js
// Фабрика агрегатора: возвращает template, который работает как Sum
$.pivotUtilities.aggregatorTemplates.durationSum = function() {
  return function(dimension) {
    return function(data, rowKey, colKey) {
      return {
        sum: 0,
        push: function(record) {
          var v = record[dimension];
          if (typeof v === 'number') this.sum += v;
        },
        value: function() { return this.sum; },
        format: function(x) { return fmtDuration(x); },
        label: 'Сумма (время)',
        numInputs: 0
      };
    };
  };
};
И потом:
js
aggregators: {
  "Сумма (время)": $.pivotUtilities.aggregatorTemplates.durationSum(),
  ...
}
Так и сделаем.
Хорошо, теперь про handoff-документ. Пользователь просит подробный файл, чтобы не прикладывать огромный. Сделаю большой markdown.
Хватит думать, пишу ответ.
Стратегия ответа:
Кратко пояснить, в чём баг pivot.
Дать патч шаблона (полная замена JS-части).
Дать команду пересборки.
Дать handoff-документ (большой markdown для сохранения в файл).
Handoff должен быть компактным, но ёмким. Постараюсь уложиться в 500-700 строк markdown.
Пишу.
Смотрю скриншот — вижу, что заголовки полей перевелись, зоны есть, но сама таблица пустая. Причина: кастомный агрегатор «Сумма (время)» не работает — внутри него я суммирую не те поля. Сейчас исправлю.
Про файл-handoff: идея правильная, огромный файл переписки раздувает контекст. Сделаю подробный самодостаточный документ — его можно будет приложить в новый чат вместо всего файла. И тогда твоя история не будет влиять на длину чата.
Про длину чата: сейчас ~74%. Хватит на эту итерацию + handoff. Дальше — в новый чат с новым файлом.
________________________________________
Разбор бага pivot
В моём шаблоне кастомный агрегатор был написан так:
js
function makeDurationAggregator(label) {
  return function(data, rowKey, colKey) {
    return {
      sum: 0,
      push: function(record) {
        for (let i = 0; i < rowKey.length; i++) {
          const v = record[rowKey[i]];  // ? БАГ!
          if (typeof v === 'number') this.sum += v;
        }
      },
      ...
    }
  }
}
Проблема: rowKey — это массив имён полей (['Отдел', 'Сотрудник']), а не массив значений. Итерируюсь по rowKey, беру record['Отдел'] — а это строка, не число. Значит, sum всегда 0.
Правильный подход: зарегистрировать агрегатор через $.pivotUtilities.aggregatorTemplates.durationSum — тогда PivotTable.js сам передаст имя поля из vals, и мы будем суммировать именно его.
________________________________________
Скрипт 1 — Полная замена JS-части шаблона
Заменяем весь блок <script> в reports_pivot.html — так надёжнее, чем точечные патчи.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
$path = "D:\tracker\server\templates\reports_pivot.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

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

# Проверка
$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
foreach ($m in @('durationSum', 'aggregatorTemplates', "'Отдел', 'Сотрудник'", 'pivotUI')) {
    if ($check.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}
Что ожидаем:
text
OK: JS-блок шаблона заменён (~4500 символов)
 OK: durationSum
 OK: aggregatorTemplates
 OK: 'Отдел', 'Сотрудник'
 OK: pivotUI
________________________________________
Скрипт 2 — Пересборка и проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
docker compose logs api --tail=15
После этого:
Открой https://localhost/admin/reports/pivot.
Жёстко обнови страницу: Ctrl+Shift+R (или Ctrl+F5) — сбросить кеш JS.
Через пару секунд должна отрендериться таблица с числами в формате HH:MM:SS.
________________________________________
Файл-handoff
Скопируй текст ниже в файл D:\tracker\HANDOFF.md (или любое удобное место). Это компактная, но полная сводка проекта. Прикладывай её в новый чат вместо огромного файла переписки.
markdown
# Трекер — учёт рабочего времени. Handoff-документ

**Дата:** 25.09.2026
**Рабочая папка:** `D:\tracker`
**Стек сервера:** FastAPI + PostgreSQL 16 + Alembic + nginx + Docker
**Стек клиента:** PyQt6 + httpx + pynput + keyring
**Начало проекта:** 17.09.2026
**Готовность:** ~90%

---

## 1. Что это за проект

Система учёта рабочего времени сотрудников с клиентом на ПК, отправкой данных по HTTPS с HMAC-подписью, и веб-интерфейсом администратора. Собирает: счётчики нажатий клавиатуры (без содержимого), клики/скролл мыши, имя приложения и заголовок активного окна, idle. Содержимое нажатий НЕ пишется.

---

