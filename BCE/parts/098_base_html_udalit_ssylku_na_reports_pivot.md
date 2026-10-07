# base.html: удалить ссылку на /reports/pivot

*Часть 98 из 100. Источник: `BCE.md`.*

[◀ Делает бэкапы всех правленых файлов в D:\tracker\_backup_remove_pivot_pdf\<дата_время>\](097_Delaet_bekapy_vseh_pravlenyh_faylov_v_D_tracker_backup_remove_pivot_pd.md) | [Оглавление](00_BCE_INDEX.md) | [D:\tracker\tools\grep_pivot.py ▶](099_D_tracker_tools_grep_pivot_py.md)

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
# D:\tracker\tools\disable_pdf_button.py
# Удаляет форму PDF из report_result.html (целиком, вместе с hidden-полями).
# Плюс пробует убрать ссылку на pivot из шаблонов, если найдёт.
import re
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(r"D:\tracker")
BACKUP = ROOT / "_backup_disable_pdf" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    rel = path.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)
    print(f"  [bkp] {rel}")

# ============================================================
# 1. report_result.html — удалить <form>, внутри которой fmt=pdf
# ============================================================
print("\n=== server/templates/report_result.html ===")
p = ROOT / "server" / "templates" / "report_result.html"
backup(p)
c = p.read_text(encoding="utf-8")

removed = 0

def repl(m):
    global removed
    block = m.group(0)
    # Признак PDF-формы: hidden input fmt=pdf
    if 'name="fmt"' in block and 'value="pdf"' in block:
        removed += 1
        return ""
    return block

c = re.sub(r'<form\b[^>]*>.*?</form>', repl, c, flags=re.DOTALL)
# Чистим лишние пустые строки
c = re.sub(r'\n{3,}', '\n\n', c)
p.write_text(c, encoding="utf-8")
print(f"  [{'OK' if removed else 'WARN'}] PDF-форм удалено: {removed}")

# ============================================================
# 2. Убираем ссылки на /reports/pivot из всех HTML в templates/
# ============================================================
print("\n=== server/templates/*.html — ссылки на /reports/pivot ===")
tpl_dir = ROOT / "server" / "templates"
total_pivot = 0
for p in sorted(tpl_dir.glob("*.html")):
    c = p.read_text(encoding="utf-8")
    if "/reports/pivot" not in c:
        continue
    lines = c.splitlines(keepends=True)
    new_lines = []
    n = 0
    for ln in lines:
        # Удаляем целую строку, если в ней есть <a ... /reports/pivot
        if "<a" in ln and "/reports/pivot" in ln:
            n += 1
            continue
        # Или закомментированную строку меню с pivot — тоже убираем
        new_lines.append(ln)
    if n:
        backup(p)
        p.write_text("".join(new_lines), encoding="utf-8")
        total_pivot += n
        print(f"  [OK] {p.name}: удалено строк: {n}")
    else:
        print(f"  [INFO] {p.name}: /reports/pivot упомянут, но не в <a>-строке — оставил")

print(f"\nВсего удалено ссылок на pivot: {total_pivot}")
print(f"Бэкапы: {BACKUP}")
Запусти:

powershell
cd D:\tracker
python tools\disable_pdf_button.py
Ожидаю увидеть:

PDF-форм удалено: 1

по pivot — либо [OK] <файл>: удалено строк: 1, либо [INFO] ...: упомянут, но не в <a>-строке.

Шаг 3. Перезапуск и проверка
powershell
docker compose restart api
docker compose logs api --tail=15
Открой https://localhost/admin/reports → сгенерируй отчёт → внизу должно быть:

кнопка «← Новый отчёт» (остаётся),

кнопки «Скачать PDF» больше нет,

XLSX/CSV — как были.

Что прислать
Вывод Select-String ... reports/pivot (шаг 1).

Вывод патчера (шаг 2).

Скриншот страницы результата отчёта — убедиться, что кнопки PDF нет.

Дальше: если всё чисто, я соберу финальный KB-патчер (HANDOFF, INDEX, 03_PIVOT.md, 04_EXPORTS.md, KNOWN_ISSUES), и после update_site.bat зафиксируем удаление pivot и PDF. Потом перейдём к P0 #2 — cookie 401 → редирект на /admin/login.

cd D:\tracker
Select-String -Path "server\templates\*.html" -Pattern "reports/pivot" -Encoding UTF8 не работает
User says the command doesn't work. Let me think about why. Possibly because Select-String with wildcard in -Path and -Encoding UTF8 might fail in older PowerShell versions, or because no matches found. Let me provide alternatives.

Actually the most likely issue: PowerShell 5.1's Select-String -Encoding accepts "UTF8" but the wildcard might not expand if the file paths have issues, or maybe there are truly no matches and it silently returns nothing (which the user interprets as "not working").

Let me give a more robust command and also check other extensions.

Скорее всего, команда отработала, но вернула пусто — то есть reports/pivot в шаблонах просто нет (что хорошо). В PowerShell 5.1 Select-String с -Path "*.html" в чужой папке иногда ведёт себя странно с кодировкой и не печатает ничего — легко принять за «не работает».

Давай проверим надёжнее, с явным обходом файлов.

Вариант A — простой и надёжный
Выполни:

powershell
cd D:\tracker
Get-ChildItem server\templates -Filter *.html | Select-String -Pattern "pivot" -SimpleMatch | Format-Table Path, LineNumber, Line -AutoSize
Ожидаемо:

Если пусто — значит, ссылок на pivot в шаблонах нет. Отлично, шаг с base.html можно пропустить.

Если что-то нашлось — пришли мне вывод.

Вариант B — на всё, включая роуты в Python
Чтобы точно знать, где ещё «живёт» pivot:

powershell
cd D:\tracker
Write-Host "--- HTML ---"
Get-ChildItem server\templates -Filter *.html | Select-String -Pattern "pivot" -SimpleMatch
Write-Host "--- PY ---"
Get-ChildItem server -Filter *.py -Recurse | Select-String -Pattern "pivot" -SimpleMatch
Write-Host "--- DONE ---"
Если и это «не работает»
Тогда, вероятно, PowerShell пишет ошибку — пришли точный текст ошибки. Но есть ещё один вариант: используй Python, он точно сработает.

Создай D:\tracker\tools\grep_pivot.py:

python
