<!-- Часть 1025 из 1409 -->
# Итого
*Хлебные крошки:* В apply_theme — emit сигнала после установки stylesheet / Итого

[◀ Уточняющие вопросы](1024_Utochnyayuschie_voprosy.md) | [Оглавление](00_BCE_INDEX.md) | [Раньше: full_duration = session_end - session_start ▶](1026_Ranshe_full_duration_session_end_session_start.md)

---

## Итого

**Идея правильная.** Я её поддерживаю. Безопасная реализация — возможна:
- Ручная загрузка файла (не автоматом)
- Показ отпечатка для сверки
- Подтверждение
- Автооткат при ошибке SSL

**Готов начинать.** Скажи:
- Формат файлов (мой рекоменд: `.pem/.crt/.cer`)
- Делаем автопроверку обновления с сервера (мой рекоменд: пока нет)
- Начинаем с клиента или с SCP

Если скажешь «делаем как рекомендуешь» — начинаю с клиентской части сразу.


Сылка на этот чат https://chat.deepseek.com/share/yqamvxoi9jmfu6pm0d

 Сегодня 25.09.20226 14.34 закончился чат прикладываю его ниже

Продолжаем проект «Трекер». Рабочая папка D:\tracker. вся переписка из всех предыдущих чатов во вложении. в этот раз я не успел тебя попросить в прошлом чате собрать всю информацию для перехода в новый чат. тебе придётся провести глубокий анализ файла во вложении и продолжить нашу разработку проекта «Трекер» если у тебя есть такая возможность, нужно отслеживать на заранее когда закончится очередной чат. также возникла проблема с отчётам там происходит накладка времени, но это после того как мы в новом чате сейчас разберемся что и как у нас сейчас в проекте «Трекер»
We need answer in Russian, continue project. Need analyze huge doc, understand current state. User asks: continue project, deep analysis, and there is problem with reports: time overlay. Need ask clarifying/offer plan. We have no access to files except content. Need respond with deep analysis and next steps. We should mention we see state: Sprint A client i18n/themes partially done, admin roles mostly done, cert UI in SCP. Last pending idea: client ca.pem replacement UI. Need note report time issue. Need propose diagnostic plan for report time overlay. We can't run scripts. Need be useful: outline current state, propose next actions, ask for specific files/logs. Should be comprehensive but not too long? Desired 5. We need maybe identify likely cause of report time overlay: timezone handling (UTC vs local), workday_start_hour, session crossing midnight, report grouping by day, pause_seconds, client_ts parsing. Need propose checks. Could also mention previous known: local time display, workday_start_hour, timezone setting. User says problem with reports: "накладка времени" maybe overlapping sessions? Could be duplicate records, sessions overlapping, timezone, session_start/end mixing. Need ask: what exactly overlays? screenshots? sample data? In new chat, they likely want start. We should say we need to see current state. But maybe we can proceed with cert UI? User mentions report issue after understanding project. Priority likely report bug. We can propose diagnosis.
Need include:
Brief "я изучил файл, вижу контекст".
Current state summary.
Immediate next steps: 1) report time bug diagnosis, 2) continue client ca.pem replacement, 3) SCP BuildTab/AdminTab, 4) finish client i18n/theme.
For report bug: likely causes and diagnostics scripts.
Ask for data: screenshots, SQL queries, sample records/sessions, logs.
Mention commands to run: check server timezone settings, workday_start_hour, sessions overlaps, records with client_ts, duplicate sessions. Provide SQL queries.
Also mention previous known report time issues: UTC storage, local display, workday_start_hour, session crossing midnight, pause_seconds. Need maybe "накладка" means double counting? If sessions overlap due to pauses? If client sends multiple sessions for same period? Need explain.
Could propose implementing check: in report generation, use effective_duration, exclude deleted records, filter is_deleted false, cap pause_seconds, handle sessions crossing workday boundary. Maybe bug is from multiple sessions on same day overlapping? Buttons start/stop, pause? Need see.
Since user says after new chat we'll figure out, we can propose first steps.
Also need "нужно отслеживать на заранее когда закончится очередной чат" — maybe warn about length? We can say I will watch context and if nearing limit, prepare handoff.
Let's craft answer in Russian.
Need maybe offer to create a handoff file? We can propose at start of new chat to gather summary. But currently they provided all. We can start with analysis.
Let's structure:
Кратко: я разобрался, проект на стадии ~90%, текущие ветки.
Что сделано (сжато): сервер/админка, клиент, i18n/темы, cert UI, SCP.
Где остановились: клиентская замена ca.pem, BuildTab/AdminTab SCP, отчетная проблема.
Приоритет: сначала отчетная накладка времени.
Диагностика отчётов: какие данные нужны, SQL, проверки.
Возможные причины и решения.
План дальнейших шагов после фикса.
Просьба: прислать конкретные данные.
Need not provide code? Could provide SQL and commands. Maybe small snippets.
Let's write.
Понял, контекст из файла я разобрал. Проект «Трекер» сейчас находится в состоянии «почти готов к выдаче», но есть незакрытые ветки: клиентская замена ca.pem, доработка SCP (BuildTab, AdminTab), i18n/темы клиента и — сейчас важнее — накладка времени в отчётах. Давай сначала разберёмся с отчётами, потому что это влияет на доверие к данным.
________________________________________
1. Где мы сейчас
Сервер и админка
FastAPI + PostgreSQL + Alembic + nginx + Docker.
75+ роутов админки, роли (admin, operator, hr, manager, viewer), пользователи, входы, аудит.
Отчёты: 6 группировок, мультифильтры, экспорт HTML/CSV/XLSX/PDF.
Партиционирование records по месяцам, планировщик задач, агрегация daily_stats.
Есть сертификаты, SCP (control/gui.py) с вкладками, включая CertificateTab.
Клиент (PyQt6)
Регистрация по bootstrap-токену, трей, сбор активности, сессии, пауза, напоминания.
Синхронизация, heartbeat, офлайн-режим, автообновление.
Сделана базовая i18n (client/i18n.py), темы (client/themes.py), начат рефакторинг settings_dialog.py.
В процессе: замена ca.pem через UI на вкладке «Регистрация».
Что осталось из ближайшего
Клиентская замена ca.pem + автооткат при ошибке SSL.
SCP: BuildTab (сборка установщика), AdminTab (сброс пароля/ADMIN_API_KEY).
Дочистить i18n и retranslate главного окна.
Разобраться с накладкой времени в отчётах.
________________________________________
2. Проблема: накладка времени в отчётах
Ты говоришь «накладка времени». Это может быть несколько разных багов:
Двойной учёт — одна и та же сессия или записи попадают в отчёт дважды.
Смещение часового пояса — UTC в БД, а отображение не в том поясе.
Пересечение сессий — две сессии идут одновременно (после перерегистрации, паузы, краша).
Неправильное определение рабочего дня — сессия через полночь относится не к тому дню.
Ошибка в pause_seconds — пауза вычитается дважды или не вычитается.
Дубли записей из-за повторной отправки батча (хотя идемпотентность есть, но могли остаться старые данные).
Ошибка в партиционировании — записи из разных партиций суммируются неверно.
Что нужно от тебя, чтобы точно диагностировать
Пришли, пожалуйста:
Скриншот отчёта, где видна накладка (например, «Отработано» больше 24 часов или время начала/конца не бьётся).
Параметры отчёта: группировка, период, выбранные сотрудники/ПК, часовой пояс, начало рабочего дня.
SQL-выборку по проблемной сессии:
sql
SELECT id, session_uid, computer_id, employee_id,
       session_start, session_end, abnormal_termination,
       pause_seconds, created_at
FROM work_sessions
WHERE employee_id = <ID>
ORDER BY session_start DESC
LIMIT 20;
SQL-выборку по записям этой сессии:
sql
SELECT kind, client_ts, data
FROM records
WHERE session_uid = '<UID>'
ORDER BY client_ts
LIMIT 50;
Настройки отчётов: /admin/settings — какие значения report_timezone, workday_start_hour, activity_gap_minutes, count_weekends.
Логи API за момент формирования отчёта:
powershell
docker compose logs api --tail=80
Быстрые проверки, которые можно сделать прямо сейчас
Проверить, нет ли пересекающихся сессий у одного сотрудника:
sql
SELECT a.session_uid AS a_uid, b.session_uid AS b_uid,
       a.session_start, a.session_end,
       b.session_start, b.session_end
FROM work_sessions a
JOIN work_sessions b
  ON a.employee_id = b.employee_id
 AND a.id < b.id
 AND a.session_start < b.session_end
 AND b.session_start < a.session_end
WHERE a.employee_id = <ID>;
Проверить сумму эффективного времени за день:
sql
SELECT date_trunc('day', session_start AT TIME ZONE 'Europe/Moscow') AS d,
       COUNT(*), SUM(EXTRACT(EPOCH FROM (session_end - session_start))) AS full_sec,
       SUM(pause_seconds) AS pause_sec
FROM work_sessions
WHERE employee_id = <ID>
  AND session_start >= '2026-09-01'
GROUP BY 1
ORDER BY 1;
Проверить, не дублируются ли записи:
sql
SELECT record_uid, COUNT(*)
FROM records
GROUP BY record_uid
HAVING COUNT(*) > 1;
Если дубли есть — это признак того, что идемпотентность где-то обошлась.
________________________________________
3. Где чаще всего ломается время в подобных системах
Судя по нашему коду, самые вероятные причины:
Часовой пояс. В БД всё в UTC, отображение — через ZoneInfo(settings.report_timezone). Если в настройках стоит UTC, а админ думает, что смотрит Москву — будет смещение. Проверь /admin/settings ? report_timezone.
workday_start_hour. Если начало дня = 6:00, сессия, начавшаяся в 02:00, относится к предыдущему дню. Если админ ожидает календарный день — будет «накладка» в отчёте по дням.
Сессия через полночь. Сессия 23:00–08:00 может попасть в два дня. В _split_by_day она относится к дню старта, но в отчёте по месяцам может выглядеть странно. Нужно проверить.
pause_seconds. Если пауза началась в одной сессии, а закончилась в другой (после краша), может вычитаться неверно. У нас уже был баг pause_seconds > total_sec, его чинили, но могли остаться старые данные.
abnormal_termination. Если сессия закрыта автоматически, session_end может быть равен времени последней активности, а не текущему. Это правильно, но если админ ждёт «до конца дня», будет расхождение.
Партиционирование. Если запрос идёт по records без учёта партиций (например, через db.query(Record)), PostgreSQL сам маршрутизирует, но если в коде есть прямой SQL без фильтра по client_ts, может сканировать всё.
Дубли записей. Если клиент после сбоя повторно отправил батч, а сервер принял как новые (например, из-за смены client_secret или record_uid), будет двойной учёт.
________________________________________
4. Что делать дальше — предлагаемый порядок
Сначала диагностика отчётов. Пришли данные из раздела 2. Я посмотрю и скажу, где именно ломается.
Потом фикс. В зависимости от причины:
если часовой пояс — поправим настройки или логику;
если дубли — почистим БД и усилим идемпотентность;
если pause_seconds — поправим расчёт;
если пересечение сессий — добавим проверку при создании сессии.
Затем вернёмся к клиенту. Доделаем замену ca.pem через UI (идея правильная, я поддерживаю).
Потом SCP. BuildTab + AdminTab.
В конце — i18n/темы до полной готовности.
________________________________________
5. Про перенос в новый чат
Я буду следить за длиной контекста. Если увижу, что мы близко к лимиту, я сразу предложу собрать handoff-сводку: что сделано, что осталось, какие файлы и команды. Ты сможешь скопировать её в новый чат.
Сейчас не нужно ничего копировать — мы продолжим здесь, пока есть место. Но если захочешь, я могу в любой момент сделать компактную сводку для переноса.
________________________________________
6. Что мне прислать прямо сейчас
Чтобы начать чинить отчёты, пришли:
Скриншот проблемного отчёта.
Параметры отчёта (группировка, период, TZ, начало дня).
SQL-выборку по work_sessions и records для проблемного сотрудника/сессии.
Вывод /admin/settings (или скриншот).
Логи API за момент формирования.
Как только увижу данные — сразу скажу, в чём причина и как исправить.
ок давай я сначала расскажу что я заметил. сегодня зашёл в отчёты и был удивлен что я за вчерашний день отработал 24 час 7 минут 31 секунду. Ошибка получилась в сессии где я якобы отработал 17 часов 36 минут 41 секунду. мы вчера с тобой много раз перерегистрировались и одна сессия оказалась вероятно зависшая. если я правильно понимаю остановка сессии происходит на стороне клиента и если клиент не послал команду сессия всё считается не закрытая? А ещё у меня возник интересный вопрос а что будет если сотрудник зарегистрировался на двух компьютерах и если одновременно их включит время будет суммироваться? как здесь быть? столько вопросов появляется надо детально всё проанализировать, проанализируй весь чат и всю нашу переписку из всех чатов которую я тебе прикладывал. разрывать тоже нельзя представь сотрудник программист работает на двух компьютерах и клиентская часть постоянно разрывает на одном и просит подключиться на другом это будет раздражать. Как быть?
The user has found a real bug: 24 hours worked in one day. Looking at the XLSX, one session shows "17:36:41" (17 hours 36 min 41 sec) which is clearly wrong. This is the session shown with the red arrow in the screenshot: Начало 15:08:24, Конец 08:45:05, Отработано 17:36:41.
Wait — 15:08:24 to 08:45:05 next day would be 17:36:41. So it spans overnight. That's the bug.
The user is asking important architectural questions:
Session close is client-side only — if client doesn't send close, session stays open forever? (this is the 17h bug — session started yesterday, never closed, and next day when client connected again, the server closed it by some rule but as a 17h span)
What if employee is registered on two computers and turns on both simultaneously? Time will sum?
Splitting sessions is bad UX (programmer on 2 PCs, client keeps splitting and asking to reconnect on another — annoying)
Let me think carefully about this.
The 17-hour session bug:
Looking at the report: session Начало 15:08:24 — Конец 08:45:05, Отработано 17:36:41, Эффективно 00:28:30.
So a session started at 15:08 yesterday. Then something happened — the client was closed/crashed/re-registered. Then the client was started again this morning at 08:45, and it closed the old session at 08:45:05 (the time the new client connected). Wait, but 15:08 to 08:45 next day = 17:36:41. Yes.
Actually looking at the report — the session_end was set to 08:45:05. That's probably when the new client registered or connected this morning. The client's detect_abnormal_termination or the auto-close logic set session_end to some time.
Wait, looking at our code — auto_close_idle_session sets session_end to last activity time, not to now. And detect_abnormal_termination closes if inactive > 12 hours, setting session_end to last_activity.
Hmm, 17 hours... Let me think. If the client was closed at 15:08 (last activity), and the new client started at 08:45 next day (17h later), then:
detect_abnormal_termination at startup: active=old_session_uid, last_activity=15:08 yesterday, now=08:45 today, diff=17h36min. Since 17h36 > 12h threshold ? closes as abnormal with session_end = last_activity = 15:08.
Then session_end would be 15:08 — span = 0 seconds. Not 17h.
But the report shows 17:36:41 which is exactly the difference between 15:08:24 and 08:45:05. So the session was closed with session_end = 08:45:05 (the new client's connect time), not with last_activity.
Why? Look at close_session in db.py — it always sets session_end = _now_iso() (current time), not last activity. So:
Old session started 15:08 yesterday.
Client crashed / closed without ending session.
New client started at 08:45 today.
detect_abnormal_termination should have been called before start... wait, in main.py we call db.detect_abnormal_termination() right after db.init_db().
But detect_abnormal_termination sets end = last_activity — let me re-check the code... Actually in the newer version:
python
def detect_abnormal_termination():
    active = get_meta("active_session")
    if not active:
        return
    last = get_meta("last_activity")
    ...
    if datetime.now(timezone.utc) - last_dt > timedelta(hours=12):
        log.warning("Abnormal termination of %s", active)
        close_session(active, abnormal=True)
And close_session:
python
def close_session(uid: str, abnormal: bool = False):
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?",
        (_now_iso(), 1 if abnormal else 0, uid),
    )
So close_session sets session_end = NOW, not last_activity! That's the bug. The auto-close should set session_end = last_activity, not now.
Wait, but there's also auto_close_idle_session which does set end = last activity. Let me re-check:
python
def auto_close_idle_session(idle_minutes: int = 30) -> str | None:
    ...
    end_iso = last_dt.isoformat()
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=1, synced=0 "
        "WHERE session_uid=? AND session_end IS NULL",
        (end_iso, active),
    )
    ...
Yes, auto_close_idle_session correctly sets end = last activity. But close_session(abnormal=True) used by detect_abnormal_termination sets end = NOW.
So there's a bug in detect_abnormal_termination ? it uses close_session which uses NOW. Should use last activity.
That's the root cause of the 17h bug. Fix: detect_abnormal_termination should set session_end = last_activity, not NOW.
Also on the server side, there should be a sanity check — reject sessions where (session_end - session_start) > reasonable max (e.g., 24h or 16h). Or cap it at last known activity.
Second question: employee on two computers simultaneously
Currently:
Each PC has its own computer_uid, own session, own employee_id (if bound).
Server sums sessions by employee_id.
So if two PCs both work simultaneously, they both create sessions with the same employee_id.
Report sums them ? double count of time.
Solutions:
Report-level dedup: In reports, when grouping by employee, detect overlapping sessions and count union of intervals, not sum.
Server-level prevention: When a new session starts for an employee (via any PC), if there's already an active session on another PC, either close the old one (idle timeout) or reject the new one.
Client-level prevention: Client A sends heartbeat; when client B is started, it detects the same employee is active on another PC and asks user "Продолжить здесь или завершить там?"
The user says splitting is bad UX. So option 2/3 need refinement.
Third question: splitting is annoying
Right — programmer works on two PCs, doesn't want to be bothered. But we can't count time twice.
Best solution:
Union of intervals in reports — dedup by time overlap. If two sessions overlap in time for one employee, take union of their intervals. Total = union length, not sum.
Client-side hint only once: When client B starts, if the server sees an active session for the same employee on another PC within last N minutes — send a soft notification "Вы работаете на другом ПК (PC-A). Здесь будет считаться только разница во времени." No blocking.
Or simpler: on the report side, count union. No client-side complexity.
Also user's question about "session закрывается только на клиенте" — yes, but:
We have auto-close by idle (30 min threshold).
We have detect_abnormal_termination at startup.
But we don't have server-side auto-close. If a client crashes and never comes back, the session stays open forever in the DB.
Server-side auto-close: A scheduled task that every hour closes sessions with no activity for > 2 hours (configurable). Sets session_end = last_activity.
Actually, we already have auto_close_idle_session — but it's on the client side only. Need a server-side equivalent in tasks.py.
Also, on the "double time" bug — another angle:
Looking at report: Сотрудник Ерохин, компьютер ws147. 23 sessions on 23.09.2026. Sum 24:07:31. But we know from the report that today he worked less. But it's counting sessions from yesterday too?
Wait, the report is for 23.09.2026 only. But the session 15:08:24 ? 08:45:05 (next day, 24.09.2026, morning) is being included because session_start is 23.09.2026.
Yes! The report filter is WorkSession.session_start >= start_utc AND session_start < end_utc — so sessions starting on 23.09 are included even if they end on 24.09.
That's correct behavior for "sessions started today", but if the session spans midnight, its duration gets counted in the day it started. So the "17:36:41" is a session started yesterday 15:08, ended today 08:45 (17h later), and the whole 17h gets counted in 23.09.
That's the visible bug — but the underlying problem is that session_end was set to the wrong time.
Plan for the answer:
Acknowledge the bug and explain what happened
Explain the mechanism (session started 15:08, client crashed, next day at 08:45 the detect_abnormal_termination fired and set session_end = now, not last_activity)
Propose fixes:
Fix 1 (client): detect_abnormal_termination should set end = last_activity
Fix 2 (client): cap session duration at N hours (e.g., 16) when closing — if last_activity > 16h ago, use start + reasonable_max
Fix 3 (server): add server-side auto-close task — every hour, close sessions with last activity > 2h
Fix 4 (server): on session ingest, if session_end - session_start > MAX_SESSION_HOURS (e.g., 16), either reject or cap
Fix 5 (reports): if a session crosses midnight, decide how to count it — split by days or count in day of start
Answer second question:
Two PCs simultaneous ? double count. Solution: union of intervals in reports.
Client-side: soft hint, not blocking.
Answer third question:
No splitting — use union of intervals in reports.
Proposed code changes.
Let me write it up.
Actually, I should be careful — I don't have the current code in front of me. I'm working from the summary in the file. Let me acknowledge that and propose a plan, and ask for the relevant files.
Actually, looking at the summary, I know:
client/db.py has auto_close_idle_session, close_session, detect_abnormal_termination
server/tasks.py has scheduled tasks
server/main.py has /api/v1/sessions endpoint
Let me write a thorough response. I'll start with analysis, then propose the fix in phases.
I should also mention that the report shows "Сессий 23" and one of them is 17h — so this is the culprit.
Let me also note: 14 abnormal terminations out of 23 sessions — that's a lot. This suggests many sessions were closed abnormally (client crashes). Need to look at that too.
Let me structure the response:
Разбор проблемы (что вижу)
Как это произошло (механизм)
Что делать — план из 3 уровней (клиент, сервер, отчёты)
Ответ на вопрос про 2 ПК
Ответ на вопрос про разрыв
Предложение: что делать сначала
I'll write in Russian, thorough but structured.
Отличный вопрос, и ты нашёл реальный баг. Давай разберу по порядку — сначала причину «24 часов», потом твои архитектурные вопросы про 2 ПК и разрыв, а в конце — план фиксов.
________________________________________
1. Разбор бага «24 часа за день»
Смотрю на отчёт и вижу виновника:
Начало	Конец	Отработано
15:08:24	08:45:05	17:36:41
Это сессия, которая началась 23.09 в 15:08, а «закрылась» 24.09 в 08:45. Разница 17 ч 36 мин — и она целиком попала в отчёт за 23.09, потому что фильтр в отчёте session_start в диапазоне 23.09, а не session_end.
Почему это произошло
Смотри цепочку:
23.09 в 15:08 клиент стартовал сессию. Мы с тобой вчера много раз перерегистрировались — и в какой-то момент клиент закрылся/упал/был убит без нажатия «Конец работы». В SQLite на ПК осталась запись active_session = <uid>, last_activity = 15:08:24.
24.09 утром ты запустил клиент заново. Сработал detect_abnormal_termination().
Смотрим его логику: проверяет now - last_activity > 12 часов ? да, 17ч36мин > 12ч ? вызывает close_session(uid, abnormal=True).
А close_session в client/db.py ставит session_end = _now_iso() — то есть текущее время клиента, а не время последней активности. Вот отсюда session_end = 08:45:05 вместо 15:08:24.
Смотри client/db.py:
python
def close_session(uid: str, abnormal: bool = False):
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?",
        (_now_iso(), 1 if abnormal else 0, uid),   # ? _now_iso() — вот баг
    )
А auto_close_idle_session (который срабатывает раз в минуту, если сессия активна) — правильно ставит session_end = last_activity. Но он работает только если клиент запущен. Если клиент был выключен ночью — не сработал. И утром сработал detect_abnormal_termination, который «закрывает сейчас».
Ответ на твой вопрос
остановка сессии происходит на стороне клиента и если клиент не послал команду сессия всё считается не закрытая?
Да, именно так. Сейчас:
Сессия закрывается только клиентом — либо кнопкой «Конец работы», либо auto_close_idle_session (когда клиент жив и видит, что 30+ мин нет активности), либо detect_abnormal_termination при следующем запуске.
На сервере нет автоматического закрытия. Если клиент упал и больше не включится — сессия висит в БД навсегда.
Плюс detect_abnormal_termination ставит end = «сейчас», а не «last_activity» — отсюда 17 часов.
Это надо чинить в 3 уровнях (клиент / сервер / отчёты), я напишу ниже.
________________________________________
2. Что делать — план фиксов
Уровень 1. Клиент — правильное закрытие сессии
Фикс 1.1. detect_abnormal_termination должен ставить session_end = last_activity, а не now. Если последняя активность была 15:08 — сессия закрывается 15:08, длительность = 0 секунд (или несколько секунд, что реалистично — человек ушёл, ПК ушёл в сон, клиент умер).
Фикс 1.2. Добавить глобальный «потолок» на длительность сессии. Даже если клиент воскрес через 3 дня — сессия не может быть длиннее MAX_SESSION_HOURS (например, 16 часов). Всё, что больше — обрезается по start + MAX_SESSION_HOURS или по last_activity, что больше.
Фикс 1.3. При старте клиента — если есть незакрытая сессия, не закрывать её «сейчас», а показать диалог UnclosedSessionDialog (он уже есть в проекте, судя по сводке) — с тремя вариантами:
Продолжить — продлить сессию (если разрыв < 2 часов).
Завершить по последней активности — правильный вариант по умолчанию.
Завершить сейчас — если сотрудник реально работал всё это время (редкий случай).
Уровень 2. Сервер — защита от «зависших» сессий
Фикс 2.1. Задача планировщика close_stale_sessions — раз в час:
Находит все work_sessions, где session_end IS NULL и last_activity_ts < now - 2 часа (нужно либо новое поле last_activity_at, либо вычислять через MAX(client_ts) из records).
Закрывает их: session_end = last_activity, abnormal_termination = True.
Пишет в аудит.
Фикс 2.2. Серверная валидация при приёме сессии в /api/v1/sessions:
Если session_end - session_start > MAX_SESSION_HOURS — отклонить с 422 и попросить клиента перепроверить.
Или принять, но обрезать session_end = session_start + MAX_SESSION_HOURS и записать в аудит.
Уровень 3. Отчёты — корректный подсчёт
Фикс 3.1. В отчётах по умолчанию считать эффективное время (без простоев > 5 мин), а не session_end - session_start. Это уже частично сделано, но Отработано показывается как полная длительность. Нужно решить, что важнее:
Если Отработано = span — там будут «мусорные» часы ночью.
Если Отработано = last_activity - first_activity (внутри сессии) — это честнее.
Мой рекоменд: Отработано = от first_activity до last_activity внутри сессии. То есть если сотрудник начал в 15:08, а последняя активность 15:20, то Отработано = 12 минут, а не 17 часов. А в 08:45 следующего утра — новая сессия.
Фикс 3.2. Если сессия пересекает полночь — сейчас она попадает в день старта. Это неверно. Нужно либо:
Считать сессию по дню session_start (как сейчас) — но тогда длинные сессии искажают.
Или разделять сессии по дням: сессия 23:00–08:00 даст 1 час в первый день и 8 часов во второй.
Второй вариант правильнее для табеля, но сложнее в реализации.
________________________________________
3. Два ПК у одного сотрудника — что делать
что будет если сотрудник зарегистрировался на двух компьютерах и если одновременно их включит время будет суммироваться?
Сейчас: да, будет суммироваться. У каждого ПК свой computer_uid и своя work_session с одинаковым employee_id. В отчёте обе сессии попадут в строки по этому сотруднику и сложатся.
Как быть — три подхода
Подход A. «Union интервалов» в отчётах (рекомендую).
В отчёте, когда группируем по сотруднику/дню, вместо суммы длительностей сессий считаем объединение временных интервалов. Если Иванов работал:
PC-A с 09:00 до 18:00
PC-B с 12:00 до 15:00
то сумма = 12 часов, а union = 9 часов. Это честно.
Плюс: не мешает сотруднику (нет блокировок, нет раздражающих диалогов).
Минус: сложнее SQL — нужно реализовать алгоритм объединения интервалов в Python (не в SQL). У нас уже есть _analyze_session и _build_flat_records — туда это добавится небанально, но реализуемо.
Подход B. «Один активный ПК» на уровне клиента.
Когда клиент стартует, он пингует сервер /api/v1/heartbeat с X-Computer-Uid. Сервер проверяет: есть ли другой активный ПК у того же employee_id? Если да — возвращает флаг parallel_session=true и имя ПК. Клиент не блокирует, но один раз показывает тост: «Вы также работаете на PC-B (12 мин назад). Время будет считаться как объединение. Спросить администратора, если это ошибка».
Плюс: не блокирует.
Минус: сотрудник может дважды нажать «Старт» на двух ПК «по привычке».
Подход C. «Только один активный ПК с автозакрытием на другом».
Если ПК-A уже работает, а ПК-B стартует — сервер закрывает сессию на ПК-A с session_end = last_activity, а на ПК-B создаёт новую. session_uid будет другим.
Плюс: не будет пересечений.
Минус: если сотрудник переключился на 5 минут — сессия на A закрывается, а потом он вернётся — надо опять стартовать. Раздражает.
Что рекомендую
Подход A (union интервалов). Это единственный, который не раздражает пользователя и корректно считает время. Подход B — как «мягкое уведомление», опционально. Подход C — не надо.
________________________________________
4. Разрыв сессии между ПК — почему не надо
представь сотрудник программист работает на двух компьютерах и клиентская часть постоянно разрывает на одном и просит подключиться на другом это будет раздражать
Полностью согласен. Разрывов не делаем. Никаких «вы должны работать только на одном ПК». У нас union интервалов на уровне отчёта — вопрос закрыт. Пусть работает на двух, на трёх, на десяти — время посчитается честно.
Единственное — при первом параллельном запуске показать один раз информационный тост, что мол «обнаружен второй ПК, время будет считаться объединением, для разделения — не работайте одновременно». Но не блокировать, не закрывать, не мешать.
________________________________________
5. Что вижу в отчёте (побочно)
14 аварийных из 23 — очень много. Это значит, что клиент много раз падал / выключался без «Конец работы». Скорее всего — результат наших вчерашних перерегистраций. Но если это повторится в реальной работе — надо разбираться отдельно.
Много коротких сессий (0:00:02, 0:00:03, 0:00:04) — это странно. Похоже, клиент часто перезапускался. Опять-таки — вчерашние тесты.
3:20:10 в конце — похоже на реальную работу.
Но! Пока мы не починим auto-close и не пересчитаем отчёты, эти данные — «мусор». После фиксов я бы советовал обнулить БД и начать чисто (мы уже это делали через docker compose down -v).
________________________________________
6. Порядок фиксов — что делаем сначала
Предлагаю такой план:
Спринт «Корректное время» (сегодня-завтра)
Клиент — фикс close_session (30 мин).
detect_abnormal_termination использует last_activity, не now.
Добавить MAX_SESSION_HOURS в config.py.
В close_session — обрезать по start + MAX_SESSION_HOURS.
Сервер — задача close_stale_sessions (1 час).
Раз в час закрывает сессии, где last_activity > 2ч, ставит end = last_activity.
Добавить last_activity_at в work_sessions (новая миграция Alembic).
Или вычислять через MAX(client_ts) из records.
Отчёты — «Отработано» по last_activity (1 час).
В _analyze_session уже есть first_event_local, last_event_local. Использовать их для worked_duration, а не session_end - session_start.
Только если last_event_local вообще есть.
Отчёты — union интервалов по сотруднику (2 часа).
В _split_by_day и _group_by_employee — вместо суммы effective_duration считать длину объединения интервалов.
Реализуется в Python: собрать все сессии сотрудника за день ? построить union ? вычислить длину.
Тест — обнулить БД, заново прогнать 1 день работы, проверить отчёт.
Спринт «Два ПК» (после)
Heartbeat-ответ с флагом parallel_session (30 мин).
Тост в клиенте один раз за сессию (30 мин).
Потом уже клиентский ca.pem и SCP
Их отложим до того, как разберёмся с корректностью учёта времени. Потому что фича с ca.pem — это когда «всё работает», а сейчас есть баг, влияющий на доверие к системе.
________________________________________
7. Что мне нужно от тебя
Чтобы я мог дать точные патчи, пришли:
client/db.py (полностью) — там ключевые функции close_session, auto_close_idle_session, detect_abnormal_termination. Хочу видеть их как есть сейчас.
client/main.py — кусок, где вызывается detect_abnormal_termination и close_session при старте.
server/web_admin.py — функции _analyze_session, _split_by_day, _group_by_employee.
server/main.py — эндпоинт /api/v1/sessions (upsert_session).
server/tasks.py — есть ли уже задачи, куда добавить close_stale_sessions.
Также скажи:
Максимум сессии — сколько часов ставим потолком? 12? 16? 24?
Порог last_activity для серверного автозакрытия — 1 час? 2 часа? 4 часа?
Разделять ли сессии через полночь по дням, или оставить «день старта»?
Union интервалов — делаем сейчас или отложим до следующей итерации?
И главное — готов ли ты обнулить БД (docker compose down -v) после фиксов, чтобы тестовые записи не путались с реальными? Данных пока немного, но дубли из-за перерегистраций уже накопились.
Как ответишь — дам патчи по порядку.
Максимум сессии — сколько часов ставим потолком? 12? 16? 24? я думаю не трогаем так как сейчас их много действительно потому что мы сейчас усердно работаем и перерегистрируемся Порог last_activity для серверного автозакрытия — 1 час? 2 часа? 4 часа? я думаю как настройку нужно вынести в это в админскую часть по умолчанию поставить 2 час и свободно менять час 1,2,3,4 и так далее. Разделять ли сессии через полночь по дням, или оставить «день старта»? мы ранее с тобой этот момент обсуждали посмотри всю нашу переписку прикрепляю скриншот выделил красным называется начало рабочего дня, об этом же идёт речь? Union интервалов — делаем сейчас или отложим до следующей итерации? Ты имеешь в виду про "Подход A. «Union интервалов» в отчётах (рекомендую)." наверное сразу всё делаем. И главное — готов ли ты обнулить БД (docker compose down -v) после фиксов, чтобы тестовые записи не путались с реальными? Да готов. У нас с тестовая разработка и ещё не кому не чего не устанавливали. Но прошу ещё раз очень детально проработать, проанализировать, правильно ли мы решили поступить? мы проделали огромный путь и по характеристикам наша программа ушла далеко своих аналогов и учитывая что я не программист, а сотрудник планово экономическо отдела с медицинским образованием это колоссальная проделанная работа. хочется что бы было и работало всё правильно.
Пользователь дал развёрнутый ответ на мои вопросы. Разберу его по пунктам и дам финальный план фиксов. Он прав — мы прошли огромный путь, и теперь надо аккуратно довести до ума.
Мои рекомендации по его ответам:
MAX_SESSION_HOURS (потолок сессии) — пользователь говорит «не трогаем». Правильно, но нужен предохранитель на уровне сервера: если клиент присылает сессию с длительностью > 24 часов, отклонять (422) или обрезать. Это защита от багов, а не ограничение нормальной работы. Отдельная настройка «макс. длительность сессии» — по умолчанию 24 часа, настраивается.
Порог last_activity для автозакрытия — пользователь хочет настраиваемым, по умолчанию 2 часа, диапазон 1-4+. Согласен. Добавим stale_session_hours в AppSetting.
Разделение через полночь — пользователь подтверждает, что это про «начало рабочего дня» (workday_start_hour на скриншоте). НО! Это две разные вещи:
workday_start_hour — определяет, к какому рабочему дню отнести сессию (для табеля).
Разделение сессии через полночь на два дня — это другая логика, для отчёта «по календарным дням».
Пользователь прав, что не надо путать. Я предложу: оставить workday_start_hour как есть (сессия относится к «рабочему дню» по нему), но добавить отдельную настройку «Показывать разбивку по календарным дням» (опционально). Или проще — оставить как есть, но правильно обрезать длительность.
Union интервалов — делаем сейчас.
БД обнуляем — да.
Теперь к сути. Разберу по шагам, что делаем.
Понимание проблемы
Смотрим на отчёт:
Сессия 15:08:24 ? 08:45:05 следующего дня = 17:36:41
Она попала в день 23.09, потому что фильтр в отчёте session_start в 23.09.
Правильное поведение:
Такая сессия не должна существовать в принципе — клиент должен был её закрыть по last_activity (15:08 + сколько-то минут).
Если она всё же существует (клиент умер окончательно) — сервер должен её закрыть по last_activity.
В отчёте «Отработано» должно быть = last_activity - first_activity внутри сессии (эффективно), а не session_end - session_start.
Точный план фиксов
Фикс 1. Клиент — detect_abnormal_termination использует last_activity
Файл client/db.py, функция detect_abnormal_termination. Сейчас ставит end = now. Надо end = last_activity.
Но! У пользователя уже есть close_session_at(session_uid, end_iso, abnormal) — оно ставит end явно. Так что достаточно вызвать его.
Фикс 2. Клиент — close_session при quit (не по кнопке)
_quit вызывает db.close_session(self.session_uid, abnormal=True) — это ставит end = now. Это неправильно, если клиент закрывают без «Конец работы» вечером — но здесь мы можем поставить end = last_activity. Или ещё лучше — не менять close_session, а добавить close_session_at с last_activity.
Фикс 3. Клиент — _handle_unclosed_session — уже работает правильно
Там три варианта, включая close_last_activity — это правильно. Но _start() вызывает db.get_active_session_uid() и потом _handle_unclosed_session — а это уже диалог. Хорошо. Но если пользователь выбрал «продолжить», то session_start остаётся, и потом будет длинная сессия. Тут нужен либо потолок (MAX_SESSION), либо на сервере проверка.
Фикс 4. Сервер — задача close_stale_sessions
Раз в час: находит сессии с session_end IS NULL и session_start < now - stale_hours (или лучше по last_activity). Закрывает end = last_activity (или session_start, если last_activity нет).
Как определить last_activity на сервере? У нас нет last_activity_at в work_sessions. Варианты:
Добавить поле last_activity_at в work_sessions, обновлять при каждом ingest.
Или вычислять MAX(client_ts) из records для session_uid — это медленно, но для «зависших» сессий сработает (их не много).
Проще: MAX(client_ts) через subquery. Для 100 висящих сессий это ок.
Фикс 5. Сервер — upsert_session защита от длинных сессий
Если end - start > MAX_SESSION_HOURS (например, 24) — обрезать end = start + MAX или отклонить. По умолчанию — обрезать, с записью в audit_log. Или отклонить с 422, чтобы клиент не смог даже залить такое.
Моя рекомендация: отклонить с 422. Клиент при попытке отправить такую сессию получит ошибку — но это неважно, потому что такие сессии не должны появляться. Если появились — это баг, который надо разбирать.
Но! Если клиент всё же отправит — сессия потеряется. Лучше обрезать до MAX + вернуть в ответе пометку. Клиент залогирует. Админ увидит в аудите.
Ещё вариант — отклонить, но не удалять. Клиент при ретрае попробует снова, снова ошибка. Зацикливание.
Финальное решение: принимать, но обрезать session_end = min(session_end, session_start + MAX_SESSION_HOURS) и записать в audit_log. Это компромисс, который не ломает клиент.
Но всё это не нужно, если клиент правильно закрывает сессию. Поэтому — сначала клиент, потом сервер-предохранитель.
Фикс 6. Отчёты — «Отработано» = last_activity - first_activity
Сейчас worked_duration = full_duration = session_end - session_start.
Надо: если в сессии есть записи (events), то worked_duration = last_event_local - first_event_local. Если записей нет — 0.
Это уже частично есть — effective_duration использует first/last. Надо применить и к worked_duration.
Но! Мы уже обсуждали: Отработано = span (от старта первой до конца последней сессии за день), а Эффективно = сумма эффективных. Пользователь не так давно подтвердил эту логику.
Хм. Итак, есть два уровня:
Уровень 1 (одна сессия): full_duration (session_end - session_start) и effective_duration (last_event - first_event).
Уровень 2 (день): worked_duration (span между сессиями) = last_end - first_start за день, и effective_duration (сумма эффективных за день).
Проблема: если одна сессия 17 часов (из-за бага), то worked_duration за день = 17 часов.
Правильно:
full_duration сессии = last_event - first_event (а не session_end - session_start). Потому что если в сессии есть события только 15:08-15:20, то реально работа была 12 минут, а 17 часов — это «сессия висела открытой».
worked_duration (span) за день = min(first_start) — max(last_end) по сессиям с реальной активностью.
Тогда:
23.09: одна сессия с активностью 15:08-15:20 = 12 мин.
Ещё есть короткие сессии 07:39-10:59 = 3:20 (это реальная работа).
Итого за день: 07:39 — 15:20 = 7:41 (span).
Или надо считать span между сессиями, где есть реальная активность.
Это моё предложение. Но! Может быть сотрудник начал работать, потом долго сидел в простое, потом опять работал. Тогда last_event - first_event внутри сессии = реальная длительность (с учётом простоя). А pause_seconds (кнопка «Пауза») — отдельно вычитается.
Хм, но если реально 8 часов работа, с обедом — first_event - last_event даст 8 часов, а effective_duration (с паузами > 5 мин) даст 6:30.
Итак, фикс для отчётов:
full_duration = last_event - first_event (а не session_end - session_start)
Если events нет — 0.
effective_duration = как сейчас.
Это решает проблему с 17-часовой сессией.
Фикс 7. Union интервалов
Для роли manager / для отчётов по сотруднику, когда у него 2 ПК. Нужно объединять интервалы сессий одного сотрудника за день. Если 2 ПК работают параллельно:
PC-A: 09:00-18:00 (полные интервалы, не last_event — важно!)
PC-B: 12:00-15:00
Union: 09:00-18:00 = 9 часов.
Важно: для union надо использовать полные интервалы сессий (session_start — session_end по last_event), а не first_event-last_event, потому что иначе получаются «дырки» внутри.
Хм, на самом деле для union нужно использовать интервалы активности — [first_event, last_event] каждой сессии. А не session_start/session_end. Потому что session_end может быть «сейчас» при висящей сессии.
Итак, для union собираем интервалы [first_event, last_event] всех сессий сотрудника за день и объединяем.
Реализация в Python: sorted intervals, merge overlapping, sum lengths.
Фикс 8. Настройка «Порог автозакрытия зависших сессий» на сервере
Новая настройка stale_session_hours в AppSetting. По умолчанию 2, диапазон 1-24.
Задача close_stale_sessions каждые 30 минут:
Находит work_sessions с session_end IS NULL и session_start < now - stale_hours.
Вычисляет last_activity через SELECT MAX(client_ts) FROM records WHERE session_uid = ...
Если last_activity > 0, ставит end = last_activity, abnormal = True.
Если last_activity = 0 (совсем нет записей), ставит end = session_start.
Фикс 9. Отключение автоопределения работы на 2 ПК — НЕ делаем
Пользователь согласился с моим подходом — union интервалов на уровне отчёта, без блокировок.
Приоритеты
Фикс клиента — detect_abnormal_termination и _quit используют last_activity. (30 мин)
Фикс клиента — close_session_at использовать везде, где нужно закрыть с конкретным end. (уже есть, надо применить)
Фикс отчётов — full_duration = last_event - first_event. (30 мин)
Фикс сервера — upsert_session обрезает сессии > MAX_SESSION_HOURS. (15 мин)
Фикс сервера — задача close_stale_sessions + настройка stale_session_hours. (1 час)
Фикс отчётов — union интервалов по сотруднику за день. (1 час)
Тест — обнулить БД, заново отработать 1 день.
Что я забыл?
Про разделение через полночь. Пользователь правильно понял — это про workday_start_hour. Сессия 23:00-08:00 с workday_start_hour=06:00:
По текущей логике _workday_date — start_local.hour = 23 >= 6, значит это день 23.09.
span сессии = 9 часов.
В отчёт «23.09» попадёт 9 часов.
Это правильно для табеля! Сотрудник начал работу 23.09, отработал 9 часов, его рабочий день = 23.09.
Другое дело — если сессия 22:00 (23.09) ? 06:00 (24.09), то:
start_local.hour = 22 >= 6, значит день 23.09.
Это тоже правильно — ночная смена 23.09.
А сессия 02:00-10:00 (24.09):
start_local.hour = 2 < 6, значит день = 23.09.
Это правильно, если работа ночью после дня 23.09.
Хм, всё логично. Так что «разделять через полночь» — не надо. workday_start_hour уже решает эту задачу.
Финальный план
Ок, теперь пишу ответ. Разделю на:
Разбор ответов пользователя + мои рекомендации (2 мин чтения).
Что НЕ делаем и почему.
План фиксов в 5 шагов.
Скрипты.
Учитывая размер — разобью на 2 сообщения:
Это сообщение: анализ + первые 3 фикса (клиент + отчёты).
Следующее: задача сервера + union интервалов + обнуление БД.
Начинаю писать.
Для клиента — патч в db.py:
detect_abnormal_termination — использовать last_activity.
Заменить вызов close_session(active, abnormal=True) на close_session_at(active, end_iso, abnormal=True) где end_iso = last_activity.
Для _quit в main.py — тоже использовать last_activity. Но там close_session тоже подойдёт, если мы изменим close_session чтобы он брал last_activity. Но это неверно для кнопки «Конец работы» — там end = now, потому что сотрудник сам нажал.
Значит, нужны две функции:
close_session_now(uid, abnormal) — end = now (для кнопки «Конец работы»).
close_session_at(uid, end_iso, abnormal) — end = указанный (для auto-close, detect, quit).
У нас сейчас close_session = «now», close_session_at = «end_iso». Ок.
Значит:
_on_stop_work использует close_session (now) — оставить.
_quit должен использовать close_session_at с last_activity.
detect_abnormal_termination уже использует close_session — исправить на close_session_at.
Также важно: если _quit вызывается при завершении работы вечером с активной сессией — что ставить? Логично — last_activity. Потому что если сотрудник ушёл в 18:00 и выключил ПК через 5 минут, то last_activity = 17:58 (например), это конец рабочего дня. Если он в 18:00 нажал «Конец работы», потом _quit без активной сессии — ок.
Если _quit при активной сессии — это либо краш, либо «закрыл окно и забыл». В любом случае правильнее = last_activity.
Теперь для отчётов.
В _analyze_session:
python
if first_event_local and last_event_local:
    effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
else:
    effective_duration = 0
А full_duration = max(0, int((end_local - start_local).total_seconds())).
Надо изменить:
python
