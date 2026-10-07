# close_session не меняем, оставляем для ручного закрытия

*Часть 71 из 100. Источник: `BCE.md`.*

[◀ Раньше: full_duration = session_end - session_start](070_Ranshe_full_duration_session_end_session_start.md) | [Оглавление](00_BCE_INDEX.md) | [full_duration = от первой до последней РЕАЛЬНОЙ активности ▶](072_full_duration_ot_pervoy_do_posledney_REALNOY_aktivnosti.md)

---

# close_session не меняем, оставляем для ручного закрытия

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
Но проблема: get_last_session_record_ts и close_session_at определены НИЖЕ в файле (в самом конце). А detect_abnormal_termination — выше. При вызове они должны быть доступны, Python это позволяет (функции определяются при вызове). Но надо убедиться, что они определены в модуле.
Смотрю db.py — да, get_last_session_record_ts и close_session_at определены в конце файла. Значит, при вызове detect_abnormal_termination() они будут доступны. ОК.
Также _now_iso определена в самом верху. ОК.
Хорошо, пишу патчер.
Теперь по main.py клиента.
_quit():
python
def _quit(self):
    log.info("Shutting down")
    ...
    if self.session_uid:
        try:
            db.close_session(self.session_uid, abnormal=True)
            log.info("Closed session %s on quit (abnormal=True)", self.session_uid)
        except Exception:
            log.exception("close_session on quit")
Меняем на:
python
if self.session_uid:
    try:
        last_act = db.get_last_session_record_ts(self.session_uid)
        if last_act:
            db.close_session_at(self.session_uid, last_act, abnormal=True)
            log.info("Closed session %s on quit at last activity %s",
                     self.session_uid, last_act)
        else:
            db.close_session(self.session_uid, abnormal=True)
            log.info("Closed session %s on quit (no records, closed now)",
                     self.session_uid)
    except Exception:
        log.exception("close_session on quit")
_handle_unclosed_session():
python
        if choice == "resume":
            self._resume_session(session_uid)
        elif choice == "close_last_activity":
            try:
                end_iso = last_act_iso or db.get_session_start(session_uid)
                db.close_session_at(session_uid, end_iso, abnormal=True)
            except Exception:
                log.exception("close_session_at failed")
        else:  # close_now
            try:
                db.close_session(session_uid, abnormal=True)
            except Exception:
                log.exception("close_session failed")
Меняем exception-handler сверху:
python
        except Exception:
            log.exception("UnclosedSessionDialog failed — closing as abnormal")
            choice = "close_now"
На:
python
        except Exception:
            log.exception("UnclosedSessionDialog failed — closing at last activity")
            choice = "close_last_activity"
Плюс — если choice == "close_now" — там оставляем, но это крайний случай.
Хм, ещё вариант — вообще убрать "close_now" из диалога. Но пользователь может его попросить. Оставим.
Также надо подумать — как диалог UnclosedSessionDialog показывает варианты? Он должен показывать:
"Продолжить" — resume
"Завершить по последней активности (рекомендуется)" — close_last_activity
"Завершить сейчас" — close_now
Если пользователь нажмёт "продолжить", но на самом деле он не работал — он вернётся в 18:05 (last_activity) но сессия продолжится с этой точки. При этом следующая запись будет с 09:00 утра. И в отчёте мы получим разрыв 15 часов. Union интервалов должен будет разорвать этот интервал.
Хм, но при resume сессия продолжается с тем же UID. И в отчётах полная длительность от первой записи до последней — будет опять 15 часов. Если записи "первая 17:55, следующая 09:00", а gap_minutes = 5, то _analyze_session должен разорвать этот разрыв.
Смотрю _analyze_session. Там есть проверка delta > gap.total_seconds() для activity. Если разрыв больше gap, то current_window_started_local = ts — обнуляет окно. Но full_duration считается от first_event_local до last_event_local. То есть не прерывается.
Это значит, что если сессия была продолжена после долгого перерыва, то full_duration всё равно покажет разрыв. Надо исправить.
Хорошо, это уже в шаге 3 — переделка full_duration в отчёте. Там я буду считать full_duration = сумма активных интервалов, а не просто last - first.
То есть: если сотрудник работал 15:08–15:20, потом не работал, потом работал 09:00–09:30, то full_duration = 12 мин + 30 мин = 42 мин. А не 18 часов.
Для этого надо перебрать все события в сессии, и суммировать интервалы, где разрыв <= gap_minutes.
Ок, это уже к шагу 3.
Итого, шаг 1 (клиент) — патчим db.py:
Улучшить detect_abnormal_termination.
Патч 2 (клиент) — патчим main.py:
_quit — использовать close_session_at с last_activity.
_handle_unclosed_session — exception ? close_last_activity.
Хм, но пользователь сказал «начинаем». Он ждёт конкретные скрипты. Давай дам Скрипт 1 (db.py) и Скрипт 2 (main.py) одним сообщением.
Также надо подумать про _resume_session. Если пользователь выбрал "продолжить", сессия продолжается. При этом в отчёте надо разорвать интервал. Это делается в шаге 3.
Ок, пишу.
Формат ответа:
Кратко: что делаем в этом шаге.
Скрипт 1: патч db.py.
Скрипт 2: патч main.py.
Проверка.
Не пишу весь длинный план заново, чтобы не раздувать ответ. Пользователь согласен, начинаем конкретику.
Начну.
Один момент — я вижу, что close_session_at в db.py уже определена:
python
def close_session_at(session_uid: str, end_iso: str, abnormal: bool = True):
    """Закрывает сессию конкретным timestamp (например, последней активности)."""
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=? AND session_end IS NULL",
        (end_iso, 1 if abnormal else 0, session_uid),
    )
    if get_meta("active_session") == session_uid:
        set_meta("active_session", "")
    log.info("Session %s closed at %s (abnormal=%s)", session_uid, end_iso, abnormal)
Есть. Хорошо.
И get_last_session_record_ts:
python
def get_last_session_record_ts(session_uid: str) -> str:
    """Timestamp последней записи в сессии (ISO UTC). Пусто если записей нет."""
    row = get_conn().execute(
        "SELECT MAX(client_ts) AS ts FROM records WHERE session_uid = ?",
        (session_uid,),
    ).fetchone()
    return row["ts"] if row and row["ts"] else ""
Есть.
Отлично, обе функции на месте. Просто используем.
Пишу патчеры.
Ещё нюанс: в патчере db.py я использую _now_iso() внутри нового detect_abnormal_termination. Она определена вверху — ок.
Также — смотрю close_session я не меняю. В патчере надо аккуратно — не заменять ничего, кроме detect_abnormal_termination.
Про main.py — _handle_unclosed_session есть в файле.
Хорошо. Пишу.
Один момент: я должен дать скрипты так, чтобы пользователь мог их запустить через PowerShell и через Python-патчер. Как обычно.
Начинаю писать финальный ответ.
Отлично, начинаем. Разбиваю на 6 шагов, скрипты идут по порядку. Каждый шаг — отдельные скрипты, проверим после каждого.
Порядок работ:
Клиент: detect_abnormal_termination — использует last_activity (сейчас)
Клиент: _quit и обработчик незакрытых сессий — тоже last_activity
Отчёты: full_duration — от первой до последней активности, а не session_end - session_start
Сервер: обрезка сессий > 24 часов — предохранитель
Сервер: задача close_stale_sessions + настройка в админке
Отчёты: union интервалов — по сотруднику за день
Начинаем с шагов 1–2 (клиент). Они короткие и не зависят от сервера.
________________________________________
Шаг 1 — Патч client/db.py
Меняем detect_abnormal_termination так, чтобы она закрывала сессию временем последней активности, а не «сейчас». Плюс добавляем приоритет источников: сначала MAX(client_ts) из records, потом meta.last_activity, потом session_start.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\client\db.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

# ---------- Замена detect_abnormal_termination ----------
if "closing at last activity" in content:
    print("SKIP: detect_abnormal_termination уже пропатчен")
else:
    old = '''def detect_abnormal_termination():
    active = get_meta("active_session")
    if not active:
        return
    last = get_meta("last_activity")
    try:
        last_dt = datetime.fromisoformat(last) if last else datetime.now(timezone.utc)
    except ValueError:
        last_dt = datetime.now(timezone.utc)
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - last_dt > timedelta(hours=12):
        log.warning("Abnormal termination of %s", active)
        close_session(active, abnormal=True)'''

    new = '''def detect_abnormal_termination():
    """
    Закрывает «висящую» сессию от прошлого запуска клиента.

    Ключевое отличие от старой версии: session_end ставится НЕ «сейчас»,
    а временем последней реальной активности. Это исправляет баг
    «17 часов работы за ночь» — когда сотрудник ушёл в 18:00, ПК
    выключили, а утром клиент запускается и закрывает сессию.

    Приоритет источников времени последней активности:
      1. MAX(client_ts) из таблицы records — самый надёжный
         (данные в БД, не зависят от meta-ключей).
      2. meta.last_activity — если по какой-то причине records пусты.
      3. session_start — крайний случай (длительность = 0 секунд).

    Если с последней активности прошло меньше 12 часов — ничего
    не делаем. Возможно, это тот же рабочий день и клиент просто
    перезапустился. Дадим пользователю решить через UnclosedSessionDialog.
    """
    active = get_meta("active_session")
    if not active:
        return

    # Источник 1: последняя запись в records
    last_record_ts = get_last_session_record_ts(active)

    # Источник 2: meta.last_activity
    if not last_record_ts:
        last = get_meta("last_activity")
        if last:
            try:
                last_dt = datetime.fromisoformat(last)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
                last_record_ts = last_dt.isoformat()
            except ValueError:
                pass

    # Источник 3: session_start
    if not last_record_ts:
        last_record_ts = get_session_start(active) or _now_iso()

    # Проверка давности
    try:
        end_dt = datetime.fromisoformat(last_record_ts)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        end_dt = datetime.now(timezone.utc)

    if datetime.now(timezone.utc) - end_dt < timedelta(hours=12):
        return

    log.warning(
        "Abnormal termination of %s — closing at last activity %s",
        active, last_record_ts,
    )
    close_session_at(active, last_record_ts, abnormal=True)
'''

    if old in content:
        content = content.replace(old, new, 1)
        print("OK: detect_abnormal_termination переписан")
    else:
        print("ERROR: старый detect_abnormal_termination не найден")
        raise SystemExit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_db_abnormal.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Запуск патчера db.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_db_abnormal.py
Что ожидаем:
text
OK: detect_abnormal_termination переписан
SYNTAX OK
________________________________________
Шаг 2 — Патч client/main.py
Два места:
_quit() — при выходе закрываем сессию временем last_activity.
_handle_unclosed_session() — в аварийном случае (если диалог упал) используем close_last_activity, а не close_now.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\main.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

# ============================================================
# Патч 1: _quit — закрытие сессии временем last_activity
# ============================================================
old_quit = '''        self._stop_collector()
        if self.session_uid:
            try:
                db.close_session(self.session_uid, abnormal=True)
                log.info("Closed session %s on quit (abnormal=True)", self.session_uid)
            except Exception:
                log.exception("close_session on quit")
            self.session_uid = None'''

new_quit = '''        self._stop_collector()
        if self.session_uid:
            # Закрываем сессию временем последней активности,
            # а не текущим временем. Иначе при выходе из клиента
            # через час после «последнего движения мыши» мы получим
            # лишний час «работы» в отчёте.
            try:
                last_act = db.get_last_session_record_ts(self.session_uid)
                if last_act:
                    db.close_session_at(self.session_uid, last_act, abnormal=True)
                    log.info(
                        "Closed session %s on quit at last activity %s",
                        self.session_uid, last_act,
                    )
                else:
                    # Записей в сессии нет — закрываем сейчас (длительность ~0)
                    db.close_session(self.session_uid, abnormal=True)
                    log.info(
                        "Closed session %s on quit (no records, closed now)",
                        self.session_uid,
                    )
            except Exception:
                log.exception("close_session on quit")
            self.session_uid = None'''

if old_quit in content:
    content = content.replace(old_quit, new_quit, 1)
    print("OK: _quit — использует close_session_at")
else:
    print("WARN: блок _quit не найден (возможно уже пропатчен)")

# ============================================================
# Патч 2: _handle_unclosed_session — exception ? close_last_activity
# ============================================================
old_exc = '''        try:
            dlg = UnclosedSessionDialog(
                session_uid, started_iso, last_act_iso, parent=self,
            )
            dlg.exec()
            choice = dlg.choice
        except Exception:
            log.exception("UnclosedSessionDialog failed — closing as abnormal")
            choice = "close_now"'''

new_exc = '''        try:
            dlg = UnclosedSessionDialog(
                session_uid, started_iso, last_act_iso, parent=self,
            )
            dlg.exec()
            choice = dlg.choice
        except Exception:
            # Если диалог не открылся — закрываем БЕЗОПАСНО:
            # временем последней активности, а не «сейчас».
            log.exception("UnclosedSessionDialog failed — closing at last activity")
            choice = "close_last_activity"'''

if old_exc in content:
    content = content.replace(old_exc, new_exc, 1)
    print("OK: _handle_unclosed_session — безопасный дефолт")
else:
    print("WARN: блок exception в _handle_unclosed_session не найден")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_main_quit.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Запуск патчера main.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_main_quit.py
Что ожидаем:
text
OK: _quit — использует close_session_at
OK: _handle_unclosed_session — безопасный дефолт
SYNTAX OK
________________________________________
Проверка после шагов 1–2
Убедимся, что всё на месте:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== db.py: ключевые маркеры ===" -ForegroundColor Cyan
$db = [System.IO.File]::ReadAllText("D:\tracker\client\db.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("closing at last activity", "get_last_session_record_ts", "close_session_at", "Приоритет источников")) {
    if ($db.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}

Write-Host "`n=== main.py: ключевые маркеры ===" -ForegroundColor Cyan
$mn = [System.IO.File]::ReadAllText("D:\tracker\client\main.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("on quit at last activity", "closing at last activity")) {
    if ($mn.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}

Write-Host "`n=== Импорт-тест ===" -ForegroundColor Cyan
client\.venv\Scripts\python.exe -c "from client import db, main; print('IMPORT OK')"
Что ожидаем:
text
=== db.py: ключевые маркеры ===
 OK: closing at last activity
 OK: get_last_session_record_ts
 OK: close_session_at
 OK: Приоритет источников

=== main.py: ключевые маркеры ===
 OK: on quit at last activity
 OK: closing at last activity

=== Импорт-тест ===
IMPORT OK
________________________________________
Что дальше
Шаги 1–2 — только клиент. Не пересобирать сервер не нужно, эти изменения локальные.
Запускай оба скрипта. Пришли вывод (сокращённо — только OK/SYNTAX строки и результаты проверки).
После этого переходим к шагу 3 — главный фикс отчётов (full_duration от первой до последней активности внутри сессии). Там уже нужны правки web_admin.py на сервере, потребуется docker compose restart api.
>> client\.venv\Scripts\python.exe -c "from client import db, main; print('IMPORT OK')" === db.py: ключевые маркеры === OK: closing at last activity OK: get_last_session_record_ts OK: close_session_at OK: Приоритет источников === main.py: ключевые маркеры === OK: on quit at last activity OK: closing at last activity === Импорт-тест === IMPORT OK
Both scripts ran successfully. All markers are in place. Now moving to step 3 — the main fix in web_admin.py: full_duration should use first/last activity instead of session_end - session_start.
Let me plan the patch for web_admin.py _analyze_session:
Current code:
python
    if first_event_local and last_event_local:
        effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
    else:
        effective_duration = 0

    # Вычитаем время паузы (если есть)
    pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)
    if pause_sec > 0:
        effective_duration = max(0, effective_duration - pause_sec)

    full_duration = max(0, int((end_local - start_local).total_seconds()))
Need to change full_duration to use first_event_local/last_event_local:
python
    # full_duration — «Отработано» в отчёте.
    # Считаем от первой до последней РЕАЛЬНОЙ активности, а не от
    # session_start до session_end. Это исключает «мусорные» часы,
    # когда сессия висела незакрытой (клиент упал, ПК выключили).
    if first_event_local and last_event_local:
        full_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
    else:
        # Если в сессии нет записей — показываем реальную разницу
        # между start и end (для полноты картины), но это редкий случай.
        full_duration = max(0, int((end_local - start_local).total_seconds()))
Wait, but this might change the meaning for normal sessions. Let's think:
Normal case: session_start=09:00, first_activity=09:00:30, last_activity=18:00:00, session_end=18:00:05.
Old full_duration = 9:00:05
New full_duration = 8:59:30
Difference is minor (5-30 sec). But for a session that ran 17h with only 30 min of activity:
Old full_duration = 17h
New full_duration = 30 min
That's the fix we want.
But there might be a concern: if sessions have large gaps in activity inside (e.g., lunch 13:00-14:00, then work 14:00-18:00), first_event=09:00, last_event=18:00, full_duration=9h. But effective would be less. That's fine — «Отработано» = 9h — это span от первой до последней активности, что разумно.
However — what if the user says "I worked 12 hours" and my span says 12 hours but there was a 2 hour break in between? Then span=12h and effective=10h. That's the same as today. Good.
OK. Let me write the patch.
Also, I need to think: should I also update _group_by_session which uses r["full_duration"] as worked_duration? Yes, it already uses full_duration. Since we're changing full_duration's meaning, _group_by_session will automatically use the new value. Good.
Now _split_by_day uses _span_of_sessions for worked_duration, and _aggregate_group sums up effective_duration. We'll handle union in step 6.
Also for step 4 — server-side cap on session duration. Need to modify upsert_session in server/main.py.
But let me be careful: I should do step 3 first (report fix), then step 4 (server cap), then step 5 (stale session task), then step 6 (union).
Let me write step 3 patch.
Also, one more thing: I should make a small improvement — since session_end is not reliable, maybe we should also track something like last_activity_at column in work_sessions. But that's a bigger change requiring migration. For now, computing from records is fine.
Let me write step 3.
Actually, I realize there's a subtle issue. _analyze_session sets:
first_event_local from the earliest event in records
last_event_local from the latest event in records
For window records, the client_ts is the moment the window was detected. So last_event_local is when the last window/activity was recorded. If user worked until 18:00 and closed the client at 18:00, the last event was around 18:00. Good.
For the pathological 17-hour case:
Session was started 15:08:24
User worked until ~15:20, then closed the client (killed process)
Client's last activity in the DB was at 15:20
Session_end was set the next morning at 08:45:05 (by our buggy detect_abnormal_termination)
After our fix, session_end would be 15:20 (by new detect_abnormal_termination)
But this specific old session already has session_end=08:45:05 in DB
So we still need to fix the report logic to guard against bad session_end. Using first/last activity is the right approach.
But also — for future correctness, once the client-side fix takes effect, session_end will be set correctly. So the report's full_duration computation using first_event_local/last_event_local is a defense-in-depth.
OK. Let me write step 3.
Approach: I'll patch _analyze_session in web_admin.py. Change full_duration computation.
Also, I should compute this once and store it. Let me check what full_duration is used for:
_group_by_session — as worked_duration for the row
_split_by_day uses _span_of_sessions(sessions) — that's min(start) to max(end) of sessions in day group. Hmm — this ALSO uses session_end. So it will pick up the 17-hour session and make the day span wrong.
Wait, let's check _span_of_sessions:
python
def _span_of_sessions(sessions: list) -> int:
    if not sessions:
        return 0
    first = min(s["start_local"] for s in sessions)
    last = max(s["end_local"] for s in sessions)
    return max(0, int((last - first).total_seconds()))
It uses s["end_local"] which is _to_local(ws.session_end or _now(), tz). So if session_end is 08:45 next morning, end_local would be next day 08:45, and span would be huge.
Hmm, actually for our problematic case: session started 15:08, ends 08:45 next morning. But the day-group is by start_local.date() with workday_start_hour adjustment. So the session belongs to 23.09. But its end_local is 24.09 08:45, which is > other sessions in that day (max ~15:20). So max(s["end_local"]) = 24.09 08:45. And first = 07:39 (earliest session). Span would be ~25 hours.
So for step 3, I need to fix BOTH:
_analyze_session — store the "activity end" (last_event_local) instead of end_local.
_span_of_sessions — use activity_end instead of end_local.
Let me do it this way:
In _analyze_session, add activity_end_local = last_event_local (or fallback to end_local if no events).
In _span_of_sessions, use s["activity_end_local"] instead of s["end_local"].
Same for full_duration — compute from first/last activity.
Let me also add activity_start_local for symmetry.
OK, let me write the patch.
python
# В _analyze_session после цикла:
if first_event_local and last_event_local:
    effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
    activity_start_local = first_event_local
    activity_end_local = last_event_local
else:
    effective_duration = 0
    activity_start_local = start_local
    activity_end_local = end_local  # fallback

# Вычитаем время паузы (если есть)
pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)
if pause_sec > 0:
    effective_duration = max(0, effective_duration - pause_sec)

