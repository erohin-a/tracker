<!-- Часть 1158 из 1409 -->
# Проверка ключевых маркеров
*Хлебные крошки:* Проверка ключевых маркеров

[◀ Вырезаем функцию и смотрим — не должно быть override](1157_Vyrezaem_funktsiyu_i_smotrim_ne_dolzhno_byt_override.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1159_part.md)

---

# Проверка ключевых маркеров
$check = [System.IO.File]::ReadAllText("D:\tracker\server\templates\report_result.html", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @('intensive_seconds', 'break_duration', 'unattached', 'report.stats', 'worked_span_duration')) {
    if ($check.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}
Что нужно ещё в бэкенде (следующим шагом)
Шаблон ссылается на два новых поля, которых в _build_report пока нет:
report.stats.employees_count / report.stats.departments_count — счётчики для строки контекста
report.unattached — список ПК без привязки
report.all_employees — список сотрудников для выпадающего списка в блоке «Без привязки»
Это 1.D — небольшой патч в _build_report. Дам его сразу после того, как убедимся, что 1.C не сломал страницу.
Порядок
Скрипт 1.C — замена шаблона. Пришли вывод (OK + 5 маркеров).
Пересборка:
powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose logs api --tail=15
Открой /admin/reports, сформируй отчёт за август. Пришли скриншот.
На скриншоте должны увидеть:
Без верхних карточек — вместо них строка с контекстом и итоговая плашка
Столбцы: Рабочий день | Сотрудник | 1C ID | Отдел | Сессий | Отработано | С трекером | Интенсивная | Эффективно | Пауза
Столбца «Аварийные» нет, но у аварийных строк — иконка ? справа
Внизу — блок «? X ПК без привязки» (пока может быть пустым, потому что report.unattached в шаблоне undefined ? блок просто не покажется — это нормально, докрутим в 1.D)
Запускай 1.C и пересборку. Пришли скриншот. Если что-то упадёт (500 или пустая страница) — пришли docker compose logs api --tail=40.
Пользователь запустил скрипт 1.C — шаблон переписан, все маркеры на месте. Отлично.
Теперь нужен патч 1.D — добавить в бэкенд _build_report:
report.stats.employees_count / report.stats.departments_count
report.unattached — список ПК без привязки
report.all_employees — список сотрудников
Плюс нужно добавить роуты:
POST /admin/computers/{computer_id}/assign-unattached — привязать непривязанные сессии ПК к сотруднику
POST /admin/computers/{computer_id}/delete-unattached — удалить непривязанные сессии ПК
Давай сделаю это одним скриптом.
Что нужно:
В _build_report добавить:
Собрать статистику по flat: сколько уникальных employees, сколько уникальных departments
Собрать unattached — список ПК, у которых есть сессии без employee_id в выбранном периоде
Передать all_employees — список сотрудников для dropdown
Добавить два роута в web_admin.py.
Давай подумаю про unattached логику. У нас есть flat — список сессий с полями employee_id, computer_id, employee_name. Сессии без привязки имеют employee_id = None и employee_name = '— не привязан —'. Но также нам нужен hostname ПК и его computer_uid.
Для этого надо:
Собрать уникальные computer_id из flat, где employee_id is None
Для каждого такого computer_id получить: hostname, computer_uid, sessions_count, worked_span_duration, first_session_local, last_session_local
Логику лучше сделать после формирования rows, но с доступом к flat.
Также надо передать all_employees — список активных сотрудников для dropdown. Это просто db.query(Employee).filter(Employee.fired_at.is_(None)).all().
Также надо в _build_report передать stats: employees_count (уникальных сотрудников в flat), departments_count (уникальных отделов).
Пишу скрипт.
Для роутов:
POST /admin/computers/{computer_id}/assign-unattached — принять employee_id, обновить все work_sessions с этим computer_id и employee_id IS NULL, проставить employee_id. Также обновить Computer.employee_id.
POST /admin/computers/{computer_id}/delete-unattached — принять date_from, date_to, удалить сессии (и records) в периоде, где employee_id IS NULL.
Запишу это всё в патчер.
Стоп — но надо проверить, что _build_report уже импортирует нужное. И где он возвращает dict — там надо добавить поля.
Давай напишу патчер через Python — найду в _build_report блок с return { и добавлю туда stats, unattached, all_employees.
Также надо посмотреть, есть ли у нас _now() в web_admin.py — да, есть.
Пишу.
Также важно: report.unattached в шаблоне использует u.computer_id для формы. Хорошо.
Пишу патчер.
Отлично, шаблон на месте — 5 из 5 маркеров OK, report_result.html переписан.
Теперь 1.D — патч бэкенда: добавить в _build_report три недостающих поля (stats, unattached, all_employees) + два роута для блока «Без привязки».
Скрипт 1.D
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

changes = []

