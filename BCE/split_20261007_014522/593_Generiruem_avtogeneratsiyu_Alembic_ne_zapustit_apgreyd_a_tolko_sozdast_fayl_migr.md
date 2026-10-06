<!-- Часть 593 из 1409 -->
# Генерируем автогенерацию — Alembic не запустит апгрейд, а только создаст файл миграции
*Хлебные крошки:* Генерируем автогенерацию — Alembic не запустит апгрейд, а только создаст файл миграции

[◀ Запускаем api в фоне. Он упадёт, потому что миграций нет — но это ожидаемо.](592_Zapuskaem_api_v_fone_On_upadet_potomu_chto_migratsiy_net_no_eto_ozhidaemo.md) | [Оглавление](00_BCE_INDEX.md) | [server/i18n.py ▶](594_server_i18n_py.md)

---

# Генерируем автогенерацию — Alembic не запустит апгрейд, а только создаст файл миграции
docker compose exec -T api alembic revision --autogenerate -m "baseline"

Write-Host "`n=== Смотрим, что получилось ===" -ForegroundColor Cyan
if (Test-Path D:\tracker\server\alembic\versions) {
    Get-ChildItem D:\tracker\server\alembic\versions\*.py | Format-Table Name, Length
} else {
    Write-Host "Файлов нет — что-то пошло не так" -ForegroundColor Red
}
Что должно произойти:
В D:\tracker\server\alembic\versions\ появится файл вида abc123_baseline.py.
Внутри — все CREATE TABLE для наших 10 таблиц: computers, employees, departments, work_sessions, records, bootstrap_tokens, client_versions, audit_log, app_settings, calendar_days.
Проверим содержимое:
powershell
powershell
Get-ChildItem D:\tracker\server\alembic\versions\*.py | ForEach-Object {
    Write-Host "`n--- $($_.Name) ---" -ForegroundColor Cyan
    Get-Content $_.FullName | Select-Object -First 60
}
________________________________________
Скрипт D8 — применяем миграцию и перезапускаем
powershell
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

Write-Host "`n=== Перезапускаем api — теперь Alembic применит миграцию ===" -ForegroundColor Cyan
docker compose restart api
Start-Sleep -Seconds 12

Write-Host "`n=== Проверяем логи ===" -ForegroundColor Cyan
docker compose logs api --tail=30
Ожидаемые логи:
text
tracker.server INFO Применение миграций Alembic...
alembic.runtime.migration INFO Context impl PostgresqlImpl.
alembic.runtime.migration INFO Will assume transactional DDL.
alembic.runtime.migration INFO Running upgrade  -> abc123, baseline
tracker.server INFO Миграции Alembic успешно применены
Проверяем, что таблицы появились:
powershell
powershell
docker compose exec -T db psql -U tracker -d tracker -c "\dt"
Должно быть 11 таблиц:
text
public | alembic_version     | table | tracker
public | app_settings        | table | tracker
public | audit_log           | table | tracker
public | bootstrap_tokens    | table | tracker
public | calendar_days       | table | tracker
public | client_versions     | table | tracker
public | computers           | table | tracker
public | departments         | table | tracker
public | employees           | table | tracker
public | records             | table | tracker
public | work_sessions       | table | tracker
alembic_version — служебная таблица, в ней хранится текущая ревизия.
Проверяем версию:
powershell
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT * FROM alembic_version;"
Должно быть:
text
 version_num
--------------
 abc123...
________________________________________
Скрипт D9 — финальная проверка
powershell
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

Write-Host "`n=== Поднимаем всё ===" -ForegroundColor Cyan
docker compose up -d
Start-Sleep -Seconds 20
docker compose ps

Write-Host "`n=== Админка работает? ===" -ForegroundColor Cyan
curl.exe -k -s -o $null -w "HTTP %{http_code}`n" https://localhost/admin/login

Write-Host "`n=== Проверка, что Alembic на месте ===" -ForegroundColor Cyan
docker compose exec -T api alembic current
Должно быть HTTP 200 и текущая ревизия (abc123 (head)).
________________________________________
ЧАСТЬ D. Что мы получили
? Alembic настроен. Миграции хранятся в server/alembic/versions/.
? Baseline-миграция создана — описывает текущую схему.
? FastAPI при старте сам применяет миграции. Ручные ALTER TABLE больше не нужны.
? История версий — в таблице alembic_version.
? Откат возможен: alembic downgrade -1.
Что важно понять про Alembic:
Дальше работа идёт так:
Мы меняем модель в server/models.py (добавили поле, таблицу).
Генерируем миграцию:
powershell
docker compose exec api alembic revision --autogenerate -m "add roles table"
Проверяем сгенерированный файл в server/alembic/versions/.
Перезапускаем API — миграция применяется автоматически.
Больше никаких ручных ALTER TABLE.
Если миграция получилась битой:
alembic downgrade -1 — откат на один шаг.
Или docker compose down -v + docker compose up -d --build — полный сброс.
________________________________________
ЧАСТЬ E. Что дальше (Спринт 1.2)
После того как Alembic заработает, двигаемся в Спринт 1.2. Добавим через миграции:
Новые таблицы:
admin_users — пользователи админки с bcrypt-хешами
admin_logins — история входов
schedules — шаблоны графиков работы
scheduled_tasks — задачи планировщика
task_runs — история запусков
api_keys — для внешних интеграций
daily_stats — агрегаты по дням
backup_config — настройки бэкапов
Изменения существующих таблиц:
departments: добавить schedule_id
employees: добавить schedule_id, fired_at
computers: добавить last_heartbeat_at
records, work_sessions: добавить is_deleted, deleted_at, deleted_by
work_sessions: добавить pause_seconds (для кнопки Пауза)
Партиционирование records — отдельная миграция с op.execute(raw_sql).
Каждая таблица — с комментарием в миграции: «зачем нужна, как влияет».
________________________________________
ЧАСТЬ F. Что мне нужно от тебя
Перед тем как ты запустишь скрипты D1–D9, ответь на два вопроса:
Есть ли у тебя данные в БД, которые жалко? Если да — сначала дамп (pg_dump), потом сброс. Если нет — сбросим и пойдём чисто.
Готов ли ты, что клиенты после сброса потребуют перерегистрации? Bootstrap-токены сгорят, нужно будет выпустить новый, клиенты в keyring содержат старый client_secret — при попытке отправки получат 401 и уйдут в auth_failed. Нужно будет на клиентах удалить keyring и зарегистрироваться заново.
Если ты готов — запускай скрипты D1–D5, потом скажи «готово», и мы пройдём D6–D9 вместе, следя за логами.
Если что-то упадёт на любом шаге — присылай docker compose logs api --tail=40 и вывод Get-Content D:\tracker\server\alembic\env.py | Select-Object -First 20, разберём.
А сложно сейчас везде сделать переключатель на русский английский язык? если не сложно давай сделаем и начнём с Скрипт D1
The user wants to add i18n (internationalization) support for Russian/English. They ask if it's difficult, and want to start with Script D1.
Let me think about this carefully.
Is i18n hard? It depends on the approach:
Simple approach (hardcoded dicts in Python): Easy to implement but verbose.
gettext/Babel standard: More "correct" but requires .po/.mo files, compilation, and more setup.
Jinja2 + Babel: Complex but standard.
For this project, considering:
Server templates are Jinja2 (HTML)
Client is PyQt6 (Python code)
User wants to be able to switch between RU and EN
Realistic assessment: Adding i18n isn't hard but it's tedious. Every string needs to be extracted, translated, and the mechanism needs to be hooked into both Jinja2 (web) and PyQt6 (client). If we do it halfway (just Russian labels replaced with English sometimes), it becomes messy.
My recommendation:
For a project at this stage, adding full i18n before finishing the feature set is premature. There's a lot of new code coming (roles, schedules, scheduler, etc.), and every new string will need double translation.
BUT the user explicitly asked, and this is a "do it right from the start" project.
Compromise: set up the infrastructure now (i18n module, translation dict, hook into Jinja2 and Qt), but only translate the strings that already exist. New strings get added as we go.
Actually, the honest answer: yes it's a bit of work, but manageable. We can:
Create server/i18n.py with a translation dict + t(key, lang) function.
Create client/i18n.py with similar structure.
Hook Jinja2: pass _ function to templates, use {{ _("key") }} in templates.
Hook PyQt6: use self.tr() or a custom t() function.
Store language preference:
For web admin: in admin_users.language field (once we have users) or in cookie.
For client: in client/.env as TRACKER_LANG=ru or en.
The cost:
Setting up infrastructure: ~1-2 hours.
Translating existing strings: another 2-3 hours (there are ~500+ strings in web_admin + templates + client).
Ongoing cost: every new feature needs double strings.
My honest recommendation:
Set up the infrastructure now (i18n.py modules, Jinja2 hook, Qt hook).
Translate only the UI chrome (menus, buttons, status messages) initially.
For data and complex texts (help texts, descriptions), keep Russian as primary and add English as we finish features.
Or better: defer the full translation until the feature set stabilizes, but set up the infrastructure so we don't have to rewrite.
Let me be direct with the user about this trade-off. They asked "сложно ли" — answer honestly: не сложно, но долго. And there's a risk of doubling work if we do it now vs. after features are done.
However, they're the boss. If they want it, let's do it right.
Proposed approach:
I'll suggest a middle path:
Сейчас: настроить инфраструктуру i18n (модули, хуки, переключатель в UI). Перевести только то, что уже есть — но частично, самое важное (меню, кнопки).
Дальше: при разработке каждой новой фичи — сразу писать строки через i18n-функцию.
В конце: один проход по всем файлам — добить перевод.
This means we start with:
server/i18n.py — инфраструктура
client/i18n.py — инфраструктура
Hook in Jinja2 templates
Hook in PyQt6 widgets
Language switcher in client settings + admin login page
But wait — the user wants to start with Script D1 (requirements.txt) which was about Alembic. Do they want to:
A) Do i18n first, then Alembic
B) Do i18n + Alembic together
C) Restart from D1 which now also includes i18n deps?
Reading again: "А сложно сейчас везде сделать переключатель на русский английский язык? если не сложно давай сделаем и начнём с Скрипт D1"
So they want: first assess difficulty, then if feasible, add i18n, and start with the D1 script.
So D1 becomes: update requirements.txt with both alembic AND i18n-related packages (if any). Babel? gettext? Or just dict-based (no extra deps)?
For dict-based i18n — no extra dependencies. That's the simplest.
Python dict-based i18n: no deps.
Babel: heavy, needs .po files.
Flask-Babel: Flask-only.
I recommend dict-based. Simple, fast, no build steps, no .mo compilation.
So D1 = alembic only (no extra deps for i18n).
But we should set up the infrastructure as part of Sprint 1 or as a pre-step.
My plan for the response:
Honest assessment of i18n difficulty.
Recommend approach: dict-based, staged rollout.
Start with D1 (requirements.txt) — alembic only, no i18n deps needed.
Set up i18n infrastructure right after D1.
Actually, thinking more — the user might be worried that if we do Alembic first and then add i18n later, we'd have to touch every file again. But that's not true — Alembic is about DB, i18n is about strings. They're independent.
Let me structure the response:
Оценка сложности i18n — не сложно, но объёмно. Объясню подход.
Рекомендация: dict-based, поэтапно.
Пересматриваем план: добавить шаг "i18n infrastructure" в Спринт 1.
Скрипт D1 — с alembic и подготовкой к i18n.
Скрипт D1.1 (новый) — создать server/i18n.py и client/i18n.py — но это уже в Спринте 1.
Hmm, but the user said "начнём с Скрипт D1" — meaning let's start with D1. So I should give them D1 first, then we proceed.
Let me keep it clean:
Give assessment
Give recommendation
Give D1 (as originally planned, maybe with a note about i18n)
Actually, let me reconsider. Should I add anything to requirements.txt for i18n?
If we use simple dict-based i18n — no. Pure Python.
If we use gettext — need to manage .po files, compile to .mo. Overkill.
If we want to use Babel for locale-aware formatting (dates, numbers) — maybe. But that's separate concern.
Decision: dict-based i18n, no extra deps.
So D1 stays as is: just alembic.
But we should plan i18n as part of the same sprint. Let me outline:
Спринт 1.1 (обновлённый):
D1: requirements.txt (+alembic)
D1.5 (new): i18n infrastructure setup
server/i18n.py — RU/EN dictionaries + t() function
client/i18n.py — same
Hook in Jinja2 (via globals)
Hook in PyQt6 (via global function)
Language field in AppSetting
D2–D9: Alembic setup
Actually, better to keep Alembic and i18n separate. Let me do:
D1: requirements.txt + alembic (as before)
D2–D9: Alembic setup
Then E1–E5: i18n setup
But the user asked to start with D1 and to include i18n. Let me just do:
Assessment of i18n
Recommendation
D1: update requirements.txt — I'll make it minimal, just alembic. Because i18n doesn't need deps.
Then explain that after D1, we'll set up i18n infrastructure (Scripts E1-E5) before or alongside D2.
Hmm, actually, if we're going to do i18n, we should do it BEFORE we write all the new admin pages (roles, schedules, etc.). Otherwise we'll have to redo every template.
So the order should be:
D1: requirements.txt
E1–E3: i18n infrastructure (modules, Jinja2 hook, Qt hook)
D2–D9: Alembic setup (unchanged)
Then start writing new features using i18n from the start.
That's the smart order.
Wait, but Alembic setup involves generating baseline migration. If we haven't touched the DB schema, we can do Alembic either before or after i18n — it doesn't matter.
Let me suggest:
D1: requirements.txt
E1–E5: i18n infrastructure
D2–D9: Alembic
Actually, thinking about it — i18n infrastructure is not big. Let me just combine: D1 = requirements.txt with alembic, then we set up i18n, then we continue with Alembic. But since the user said "начнём с Скрипт D1", let me just deliver D1 and prepare the ground.
Now, one big concern about i18n: DB-stored strings. Things like:
Department names (Сотрудники Бухгалтерии)
Employee full names (Иванов И.И.)
Schedule names (Стандартный)
Notes in calendar_days
Those are data, not UI strings. They can't be auto-translated. The user just needs to enter them in the desired language, or we don't translate them at all.
UI strings — menu items, buttons, table headers, error messages, tooltips — those get translated.
Rule of thumb:
UI chrome = translatable
Data = not translatable (user enters as-is)
This makes i18n much simpler.
Another concern: Jinja2 templates. Every {{ }} in templates needs a {{ _("") }} wrapper. That's mechanical work.
For PyQt6 client: every QLabel("Начать работу") becomes QLabel(t("start_work")).
Total effort estimation:
Infrastructure: ~2 hours
Initial translation of existing strings: ~4 hours
Ongoing: minimal, just use t() everywhere
Acceptable. Let's do it.
My answer structure:
Honest assessment
Recommend dict-based approach
Explain what gets translated (UI) vs not (data)
Start with D1
Let me write this concisely and not overwhelm the user.
For D1 — just the alembic addition. Keep it simple. Then we'll talk i18n infrastructure.
Actually, re-reading once more: "если не сложно давай сделаем и начнём с Скрипт D1"
"if not difficult, let's do it and start with Script D1"
So: they want to do i18n, and they want to start with D1. So D1 should be the first step that includes i18n groundwork.
But D1 was originally just requirements.txt. For i18n we don't need new packages. So D1 stays the same. But we should tell the user: "D1 не меняется, но сразу после него мы сделаем настройку i18n (шаги E1-E5) перед тем как продолжим с Alembic".
Or we could add a step E0 that updates requirements.txt to include everything at once (alembic + whatever i18n needs).
Let me just be practical:
D1 stays as is (requirements.txt + alembic). Then we have a small note: "i18n не требует новых пакетов — делаем на чистом Python".
Then next scripts (E1-E5) set up i18n. THEN we return to Alembic (D2-D9).
Actually wait — the user asked to "start with Script D1". So they want D1 as their action item now. So give them D1, explain i18n plan, tell them to run D1 and report back.
Let me write this.
One more thing — the user asked: "сложно сейчас везде сделать переключатель?"
Answer honestly:
Не сложно.
Но объёмно — нужно пройти по всем файлам (шаблоны + клиент), обернуть строки в t("key"), создать словари RU/EN.
Риск: если сделать наполовину, будет каша. Лучше сделать инфраструктуру сейчас, а строки переводить по мере разработки.
Let me write the response now. Should be concise, honest, and give D1.
Format:
Краткая оценка i18n
Решение по подходу
Правила (что переводим, что нет)
Скрипт D1
План после D1
Length: medium. Not too long.
Про i18n (RU/EN) — честная оценка
Прежде чем давать D1, отвечу на главный вопрос: сложно ли?
Коротко: не сложно, но объёмно
Три фактора:
1. Инфраструктура — простая. Один Python-модуль с двумя словарями (RU/EN) и функцией t("key"). Не нужны никакие внешние библиотеки типа Babel/gettext. Полчаса работы.
2. Перевести существующие строки — вот это долго. У нас:
11 HTML-шаблонов в админке (пункты меню, заголовки таблиц, кнопки, тултипы)
~15 страниц админки в web_admin.py (сообщения об ошибках, audit_log, письма)
Клиент PyQt6 (~10 экранов, все надписи)
Всего порядка 500–700 строк. Если делать вручную — день работы. Но это механическая работа: обернуть строку в t("ключ") и добавить два перевода.
3. Поддержка при разработке — самое важное. Если мы сейчас добавим i18n, то все новые страницы (роли, расписания, планировщик) будем сразу писать с t(). Если не добавим — придётся потом проходить по ним заново.
Моя рекомендация
Делаем. Но по уму:
Сейчас — только инфраструктура. Модули server/i18n.py и client/i18n.py, хук в Jinja2, хук в PyQt6, переключатель языка в настройках.
Существующие строки — переведём не все сразу, а постепенно, при каждой следующей правке файла. Сегодня трогаем web_admin.py — заодно переводим. Завтра трогаем base.html — заодно переводим.
Данные НЕ переводим. Что такое «данные»:
Имена сотрудников («Иванов И.И.»)
Названия отделов («Бухгалтерия»)
Названия шаблонов графиков
Примечания в календаре
Топ-программы в отчётах (PyCharm, Chrome — они и так английские)
Что такое «UI-строки» (их переводим):
Пункты меню («Сотрудники», «Отчёты»)
Кнопки («Сохранить», «Удалить»)
Заголовки таблиц («Отработано», «Эффективно»)
Сообщения об ошибках и подсказки
Статусы («онлайн», «офлайн», «уволен»)
Язык по умолчанию — русский. Переключатель — маленькая кнопка RU/EN в правом верхнем углу админки и в настройках клиента. Выбор хранится:
В админке — в cookie (потом переедет в admin_users.language).
У клиента — в client/.env (TRACKER_LANG=ru).
Оценка по времени
Этап	Время
Инфраструктура (модули + хуки + переключатель)	1–1.5 ч
Перевод существующих строк (постепенно, при каждой правке)	«в фоне»
Полный перевод клиента (отдельным заходом)	2–3 ч
Полный перевод шаблонов (отдельным заходом)	2–3 ч
Итого: сразу тратим 1.5 часа, дальше всё делаем уже «с i18n в голове».
Технически — как это будет выглядеть
Сервер:
python
