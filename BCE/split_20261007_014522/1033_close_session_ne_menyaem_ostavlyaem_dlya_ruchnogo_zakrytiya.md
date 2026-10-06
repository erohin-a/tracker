<!-- Часть 1033 из 1409 -->
# close_session не меняем, оставляем для ручного закрытия
*Хлебные крошки:* close_session не меняем, оставляем для ручного закрытия

[◀ 2. Обновляем close_session — добавляем safety cap на длительность](1032_2_Obnovlyaem_close_session_dobavlyaem_safety_cap_na_dlitelnost.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Замена detect_abnormal_termination ---------- ▶](1034_Zamena_detect_abnormal_termination.md)

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

