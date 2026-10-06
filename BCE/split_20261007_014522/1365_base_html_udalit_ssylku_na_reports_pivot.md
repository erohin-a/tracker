<!-- Часть 1365 из 1409 -->
# base.html: удалить ссылку на /reports/pivot
*Хлебные крошки:* base.html: удалить ссылку на /reports/pivot

[◀ Очистим лишние пустые строки](1364_Ochistim_lishnie_pustye_stroki.md) | [Оглавление](00_BCE_INDEX.md) | [D:\tracker\tools\disable_pdf_button.py ▶](1366_D_tracker_tools_disable_pdf_button_py.md)

---

# base.html: удалить ссылку на /reports/pivot
p = ROOT / "server" / "templates" / "base.html"
if p.exists():
    backup(p)
    c = p.read_text(encoding="utf-8")
    lines = c.splitlines(keepends=True)
    new_lines = []
    pivot_removed = 0
    for ln in lines:
        if '<a' in ln and '/reports/pivot' in ln:
            pivot_removed += 1
            continue
        new_lines.append(ln)
    c = "".join(new_lines)
    p.write_text(c, encoding="utf-8")
    print(f"base.html: ссылок pivot удалено: {pivot_removed}")
    if not pivot_removed:
        print("  [WARN] не нашли pivot в base.html — покажи вывод Select-String")
Ок. Также стоит понять, есть ли pivot в другом шаблоне. Пользователь показывал в файле 00_INDEX: "reports.html" и другие. Надо найти через Select-String.

Давай дам команду для проверки.

Также важно: пользователь должен подтвердить, что в report_result.html именно ОДНА форма с PDF, чтобы патчер зацепил её. На скриншоте — да.

Ещё: возможно, выше в файле есть формы для фильтров (они НЕ содержат fmt=pdf, значит не удалятся).

Ок, готовлю ответ.

Ещё вопрос: пользователь просил проверить длину чата. Я ответил в прошлый раз, но он не подтвердил. Сейчас я уже ответил "8-12%". Теперь ему нужно просто прислать результаты патча.

Дам компактный ответ:

Что вижу на скриншоте.

Что делать (патчер).

Что проверить в base.html через Select-String.

Так, чтобы не раздувать.

Отлично, теперь вижу структуру. На скриншоте — одна форма для PDF (строки 314–325), внутри неё только hidden-параметры и кнопка «Скачать PDF». Удалять надо всю форму целиком, а не по строчкам — иначе останутся висячие hidden inputs.

Что я вижу в report_result.html
html
{# Кнопки внизу #}
<div class="d-flex gap-2 mt-3 ...">
    <form method="post" action="/admin/reports/generate" class="d-inline">
        ...6 hidden inputs (employee_ids, department_ids, computer_ids,
                            date_from, date_to, group_by)...
        <input type="hidden" name="fmt" value="pdf">     ← признак PDF
        ...2 условных hidden (show_apps, show_abnormal)...
        <button class="btn btn-outline-danger">📄 Скачать PDF</button>
    </form>
    <a class="btn btn-outline-secondary" href="/admin/reports">← Новый отчёт</a>
</div>
Значит, XLSX/CSV-кнопок тут нет — они либо на странице reports.html, либо отсутствуют вовсе. Это ок, задачу не меняет.

Шаг 1. Проверь base.html на pivot
Выполни:

powershell
cd D:\tracker
Select-String -Path "server\templates\*.html" -Pattern "reports/pivot" -Encoding UTF8
Пришли мне результат (это 5–10 строк). Если найдётся — я покажу, какую строку удалить. Если нет — pivot уже нигде не упомянут в меню (и это нормально, раз страница и так была отдельной).

Шаг 2. Патчер — удаление формы PDF целиком
Создай D:\tracker\tools\disable_pdf_button.py:

python
