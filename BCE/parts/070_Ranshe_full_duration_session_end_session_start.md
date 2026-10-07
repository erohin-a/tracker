# Раньше: full_duration = session_end - session_start

*Часть 70 из 100. Источник: `BCE.md`.*

[◀ Итого](069_Itogo.md) | [Оглавление](00_BCE_INDEX.md) | [close_session не меняем, оставляем для ручного закрытия ▶](071_close_session_ne_menyaem_ostavlyaem_dlya_ruchnogo_zakrytiya.md)

---

# Раньше: full_duration = session_end - session_start
# Теперь: full_duration = last_event - first_event (реальное время работы)
if first_event_local and last_event_local:
    full_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
else:
    full_duration = 0

# effective_duration всё ещё first-last минус паузы... 
# но подожди, если full = last-first, то effective тоже = last-first минус паузы? 
# Тогда они одинаковые будут без пауз.
Хм. Надо переосмыслить.
Что такое full_duration? Это «сколько сотрудник был у ПК, за исключением отсутствия, которое мы не можем посчитать». По сути, first_event - last_event для одной сессии. Раньше это было session_end - session_start, но там сессия может висеть.
Что такое effective_duration? Это «активная работа без пауз > 5 минут». Тоже от first_event до last_event, но с вычетом больших пауз.
Тогда:
full_duration = last_event - first_event.
effective_duration — как сейчас (сумма по событиям, с учётом gaps).
Разница: full = 8 часов, effective = 6 часов. Оба получены из events, а не из session_start/session_end.
Отлично. Тогда фикс простой.
Но! worked_duration (span за день) сейчас считается как max(end_local) - min(start_local) по сессиям. Надо:
Использовать end_local = last_event (а не session_end).
Тогда span тоже будет осмысленным.
Это требует, чтобы end_local в info был = last_event, а не session_end. Или хранить отдельно.
Проще: в info записывать session_start_ts = start_local и session_end_ts = last_event_local (или start_local если событий нет). А full_duration вычислять из этого.
Ок, финальная логика:
python
if first_event_local and last_event_local:
    end_local = last_event_local  # перезаписываем
else:
    end_local = start_local  # или оставить session_end?
full_duration = int((end_local - start_local).total_seconds())
Хм, но end_local используется в другом месте — в шаблоне для отображения «конец сессии». Там должно быть реальное время — либо session_end, либо last_event.
Компромисс:
end_local = session_end (для отображения в UI).
activity_end_local = last_event (для расчёта).
full_duration = activity_end - first_event, или 0 если нет событий.
Ок.
А для дня: worked_duration = max(activity_end) - min(activity_start) по всем сессиям дня.
Union интервалов
Для union надо объединить интервалы [activity_start, activity_end] всех сессий сотрудника за день.
python
def _union_duration(intervals: list[tuple[datetime, datetime]]) -> int:
    if not intervals:
        return 0
    sorted_iv = sorted(intervals)
    merged = [sorted_iv[0]]
    for start, end in sorted_iv[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return sum(int((e - s).total_seconds()) for s, e in merged)
Применить в _split_by_day, _group_by_employee, _split_by_month.
Сервер — задача close_stale_sessions
Новая задача в tasks.py + регистрация в TASKS_REGISTRY. По умолчанию выключена, cron = "*/30 * * * *" (каждые 30 минут). Настраиваемый порог stale_session_hours (AppSetting, default 2).
python
def close_stale_sessions(db, hours=None):
    if hours is None:
        hours = int(get_setting(db, "stale_session_hours", "2"))
    cutoff = _now() - timedelta(hours=hours)
    stale = db.query(WorkSession).filter(
        WorkSession.session_end.is_(None),
        WorkSession.session_start < cutoff,
    ).all()
    closed = 0
    for ws in stale:
        # last_activity из records
        last_ts = db.execute(text(
            "SELECT MAX(client_ts) FROM records WHERE session_uid = :uid"
        ), {"uid": ws.session_uid}).scalar()
        end_ts = last_ts or ws.session_start or cutoff
        ws.session_end = end_ts
        ws.abnormal_termination = True
        closed += 1
        db.add(AuditLog(
            actor="scheduler",
            entity="work_session",
            entity_id=ws.session_uid,
            action="auto_close_stale",
            new_value=f"end={end_ts}, threshold={hours}h",
        ))
    db.commit()
    return f"Закрыто зависших сессий: {closed} (порог: {hours}ч)"
Настройка в админке
На странице /admin/settings добавить поле «Порог автозакрытия зависших сессий (часы)».
Обнуление БД
После фиксов: docker compose down -v + up -d --build.
Ок, пишу ответ. Постараюсь компактно.
Сначала объясню логику, потом дам код. Начну с клиента (db.py) — это самое срочное. Потом отчёты. Потом сервер.
Учту, что пользователь не программист, объясню по-человечески.
Стиль — дружелюбный, но по делу. Плюс поясню, что мой «потолок 24ч» и «порог 2ч» — это разные вещи, чтобы не путался.
Отлично, разберу по порядку. Сначала отвечу на твои вопросы, потом предложу финальный план. Ты абсолютно прав, что надо аккуратно всё перепроверить — мы уже прошли огромный путь, и сейчас важно закрепить правильное поведение.
1. Про твои уточнения
Про «начало рабочего дня» на скриншоте — да, это оно, но не совсем то
workday_start_hour (сейчас у тебя 06:00) решает такую задачу: к какому рабочему дню отнести сессию. Если сессия началась в 05:00 — она относится к предыдущему дню. Если в 08:00 — к текущему. Это правильно и уже работает.
Что я имел в виду под «разделением через полночь» — это другая задача: сессия 22:00?06:00 длится 8 часов, но календарно она попадает в два дня. Вопрос: показывать её как 8 часов в первый день, или как «2 часа вчера + 6 часов сегодня».
Мой ответ: не надо делить. workday_start_hour уже решает эту задачу по-человечески: сессия целиком относится к своему рабочему дню. Так делают все табельные системы. Твоё текущее поведение — правильное.
Про «потолок сессии» и «порог автозакрытия» — это РАЗНЫЕ вещи
Я, кажется, слил их в один вопрос, извини. Разделим:
A. Порог автозакрытия зависших сессий (то, что ты хочешь в настройки). Это «если клиент молчит N часов, сервер закрывает сессию сам». По умолчанию 2 часа, диапазон 1–24. Настраивается в админке. Так и делаем.
B. Потолок длительности одной сессии (страховка от багов). Это защита от случая «клиент прислал сессию 17 часов». Не путать с реальной работой — реальная работа это 8–12 часов. Ставим жёсткий предел 24 часа на сервере — если сессия длиннее, сервер её режет и пишет в аудит. Это не настройка, это предохранитель. Так и делаем, значение 24 не трогаем (у нас 24 часа — это уже что-то экстремальное).
Union интервалов — да, сразу
Ты правильно понял. Делаем сразу. Это правильное решение для двух ПК.
2. Что делаем — план из 6 шагов
Шаг 1. Клиент: detect_abnormal_termination использует last_activity
Сейчас (в client/db.py):
python
def detect_abnormal_termination():
    ...
    if datetime.now(timezone.utc) - last_dt > timedelta(hours=12):
        log.warning("Abnormal termination of %s", active)
        close_session(active, abnormal=True)  # ? ставит end = СЕЙЧАС
Надо: end = last_activity, а не сейчас. У нас уже есть close_session_at() — используем её.
Шаг 2. Клиент: _quit тоже использует last_activity
Сейчас в client/main.py при выходе:
python
db.close_session(self.session_uid, abnormal=True)  # ? ставит end = СЕЙЧАС
Надо: end = last_activity сессии. Это правильнее, потому что если сотрудник выключил ПК через 5 минут после «последнего движения мыши» — время работы 5 минут, а не «пока ПК выключался».
Шаг 3. Отчёты: full_duration = от первой до последней активности, а не session_end - session_start
В web_admin.py, функция _analyze_session:
Сейчас:
python
full_duration = max(0, int((end_local - start_local).total_seconds()))
Надо:
python
if first_event_local and last_event_local:
    activity_end_local = last_event_local
    full_duration = max(0, int((activity_end_local - first_event_local).total_seconds()))
else:
    full_duration = 0
Смысл: если в сессии есть записи только за 12 минут (15:08–15:20), то «Отработано» = 12 минут, а не 17 часов.
Это главный фикс, который решит проблему из твоего XLSX.
Шаг 4. Сервер: обрезка сессий > 24 часов
В server/main.py, в upsert_session: если (end - start) > 24h — обрезать end = start + 24h, записать в audit_log. Клиент всё равно получит 200 OK.
Шаг 5. Сервер: задача close_stale_sessions + настройка
Новая задача в tasks.py, регистрируем в TASKS_REGISTRY. Запускается каждые 30 минут, читает настройку stale_session_hours из AppSetting (default = 2). Закрывает сессии, где session_end IS NULL и session_start < now - hours. end = MAX(client_ts) из records или session_start если записей нет.
В админке /admin/settings — новое поле «Порог автозакрытия зависших сессий (часы)».
Шаг 6. Отчёты: union интервалов по сотруднику за день
В _split_by_day, _split_by_month, _group_by_employee — вместо суммы длительностей сессий считаем объединение интервалов [first_event, last_event] всех сессий сотрудника за день.
Псевдокод:
python
def _union_duration(intervals):
    # intervals — список (start, end)
    if not intervals: return 0
    sorted_iv = sorted(intervals)
    merged = [sorted_iv[0]]
    for s, e in sorted_iv[1:]:
        ls, le = merged[-1]
        if s <= le:
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s, e))
    return sum(int((e - s).total_seconds()) for s, e in merged)
Применяем только к worked_duration (span). effective_duration (сумма эффективных) остаётся как есть — она уже не даст 17 часов.
3. Общая картина после фиксов
Пример: сотрудник 23.09 отработал на PC-A 07:39–10:59 (3:20) и на PC-B 09:00–15:20 (6:20), частично пересекаются.
Было:
Сумма = 3:20 + 6:20 = 9:40 (или, при баге с 17 часами, ещё хуже).
Станет:
Union интервалов [07:39–10:59] ? [09:00–15:20] = [07:39–15:20] = 7:41.
Именно union, потому что сотрудник один, и он не мог работать в двух местах одновременно.
Если бы у него были две сессии с перерывом (07:39–10:59, 12:00–18:00):
Union = (10:59–07:39) + (18:00–12:00) = 3:20 + 6:00 = 9:20 (перерыв 10:59–12:00 не считается).
Сумма длительностей = 9:20. Здесь разницы нет.
Union работает как надо в обоих случаях.
4. Про обнуление БД
Да, обнуляем после всех фиксов. Тестовые данные, которые накопились (25 сессий, 3699 записей), действительно мусорят. После обнуления — 0 сессий, 0 записей, начинаем чисто.
5. Мой вопрос к тебе перед началом
По шагу 6 (union) — я хочу убедиться, что мы правильно называем «полный рабочий день». Два варианта:
Вариант A (union — рекомендую). Отработано за день = «реально работал N часов, независимо от количества ПК». Если сотрудник работал на двух ПК параллельно, часы не удваиваются. Это правда.
Вариант B (сумма сессий). Отработано = сумма длительностей всех сессий. Проще, но если два ПК работают параллельно — часы удваиваются. Неправда.
Мой выбор — А. Согласен?
И ещё — effective_duration (эффективное время) сейчас считается как сумма эффективных длительностей по каждой сессии отдельно. Если два ПК параллельно, тоже удваивается. Тут тоже применять union? Я думаю — да, для консистентности. Но это сложнее: внутри интервала нужно ещё вычесть паузы, а они у каждой сессии свои. Компромисс — оставить effective как сумму (не union), а union применять только к worked_duration (span). Меньше путаницы.
Скажи: A + union только для worked_duration — согласен?
Если да — начну выдавать скрипты. Начну с клиента (Шаг 1), потому что это самое критичное: без этого фикса проблема с 17-часовой сессией будет повторяться.
со всем согласен начинаем
Пользователь согласен со всем планом. Начинаем с Шага 1 — фикс клиента. Он уже показал мне db.py и main.py.
Давай структурирую. План из 6 шагов:
Клиент: detect_abnormal_termination использует last_activity
Клиент: _quit использует last_activity
Отчёты: full_duration = от первой до последней активности
Сервер: обрезка сессий > 24 часов
Сервер: задача close_stale_sessions + настройка
Отчёты: union интервалов
Начну с шага 1 (клиент). Потом 2 (клиент). Потом 4, 5 (сервер). Потом 3, 6 (отчёты).
Смотрю db.py клиента. Там:
detect_abnormal_termination() — уже использует close_session (ставит end=now)
close_session_at() — уже есть и правильно закрывает по конкретному timestamp
get_last_session_record_ts() — уже есть
Итак, нужно:
Поправить detect_abnormal_termination — использовать get_last_session_record_ts или get_meta("last_activity"), и вызывать close_session_at() вместо close_session().
Проблема: detect_abnormal_termination использует last_activity из meta. Но это meta-ключ, который обновляется через touch_activity(), и он сбрасывается при старте новой сессии. Если приложение упало, meta-ключ last_activity остался бы. Но проблема в том, что при перезагрузке между запусками, last_activity может быть актуален (тот момент когда приложение ещё работало).
Однако есть более надёжный источник — MAX(client_ts) из records для этой сессии. Он не зависит от meta. Давай используем его.
Поправить main.py при выходе — вместо close_session(uid, abnormal=True) использовать close_session_at(uid, last_activity, abnormal=True).
Также надо поправить _handle_unclosed_session — там уже используется close_session_at для варианта "close_last_activity". А вариант "close_now" использует close_session. Оставляем — там пользователь сам выбрал «закрыть сейчас». Ок.
Хм, ещё вопрос — клиент сейчас в _handle_unclosed_session показывает диалог. Если пользователь выбирает "resume" — продолжает сессию. Если "close_last_activity" — закрывает по last activity. Если "close_now" — закрывает сейчас. Это хорошо.
Но detect_abnormal_termination (в db.py) вызывается ДО этого диалога? Смотрим main.py:
python
def _start(self):
    try:
        db.init_db()
    ...
    active = db.get_active_session_uid()
    if active:
        self._handle_unclosed_session(active)
Так что detect_abnormal_termination в db.py вообще не вызывается в _start(). А где вызывается? Поищем... Не вижу в main.py. Возможно, это legacy-функция, которая раньше вызывалась, а сейчас нет. Или вызывается внутри init_db?
Смотрю init_db():
python
def init_db():
    if DB_PATH.exists():
        ...
    conn = get_conn()
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    ...
    conn.executescript(SCHEMA)
    _migrate(conn)
Нет, detect_abnormal_termination не вызывается. Значит, она legacy. Тогда в main.py клиента — актуальный путь закрытия при выходе это _quit(). Смотрим:
python
def _quit(self):
    ...
    if self.session_uid:
        try:
            db.close_session(self.session_uid, abnormal=True)  # ? вот здесь
И _handle_unclosed_session — для случая «найдена незакрытая сессия при старте».
Так что правки:
detect_abnormal_termination — либо удалить, либо поправить на всякий случай (она не вызывается, но пусть будет правильной).
_quit — использовать close_session_at с last_activity.
_handle_unclosed_session — уже правильно для close_last_activity, для close_now оставляем.
Также важно: auto_close_idle_session уже правильно закрывает по last_activity. Она вызывается раз в минуту через _idle_timer. То есть если клиент жив и сотрудник ушёл — сессия закроется через 30 минут по last_activity. Это уже работает.
Но если клиент упал/выключился — сессия остаётся открытой в SQLite, и закрывается только при следующем запуске через _handle_unclosed_session. И вот там для close_last_activity уже правильно.
Проблема с 17-часовой сессией:
Клиент был открыт, сессия шла, потом клиент закрыли/убили.
При следующем запуске сработал _handle_unclosed_session.
Пользователь (или автоматически, если диалог не смог открыться) выбрал... "close_now".
close_session(uid, abnormal=True) поставил end = now.
При синхронизации эта сессия ушла на сервер с session_end = now (17 часов разницы).
Сервер принял, сохранил.
В отчёте: full_duration = end - start = 17 часов.
Правильно: если сотрудник не работал эти 17 часов, надо было закрыть по last_activity.
Так вот — close_now — это вообще неправильный вариант. Пользователь мог не понять, или диалог не смог открыться (exception). В _handle_unclosed_session при exception choice = "close_now".
Надо:
Убрать "close_now" из опций диалога — оставить "resume" и "close_last_activity".
Или — сделать "close_last_activity" дефолтом.
Или — в случае exception использовать close_session_at по last_activity.
Я думаю, лучше:
Вариант "close_now" оставить в диалоге (иногда реально надо — например, сотрудник работал, потом ушёл, ПК перезагрузился, но не выключился).
НО — на сервере добавить проверку: если session_end - session_start > MAX_SESSION_HOURS (24ч), то обрезать до start + 24ч или до MAX(last_event) — тут сервер не знает last_event, потому что записи могут быть ещё не отправлены. Значит сервер режет до start + 24ч.
Это предохранитель, а не основной механизм.
Основной механизм — изменить default в диалоге и при exception:
В _handle_unclosed_session при exception использовать close_session_at(uid, last_act_iso) вместо close_session.
В диалоге сделать "close_last_activity" вариантом по умолчанию (визуально выделенным).
Также в _quit():
Сейчас db.close_session(self.session_uid, abnormal=True) — end=now.
Надо last_act = db.get_last_session_record_ts(self.session_uid) — вернуть session_end = last_act если есть, иначе now.
Это даст: если клиент выключили в 18:00, но последняя активность была в 17:55 — сессия закроется в 17:55. Ну, 5 минут разницы. Приемлемо.
Хорошо, начинаю писать скрипты.
Скрипт 1.1 — Патч client/db.py:
Улучшить detect_abnormal_termination: использовать get_last_session_record_ts и close_session_at.
Добавить close_session_at (уже есть, но убедиться).
Скрипт 1.2 — Патч client/main.py:
_quit: использовать close_session_at с last_activity.
_handle_unclosed_session: при exception — close_session_at с last_activity.
(Опционально) — оставить диалог как есть, он уже правильный.
Начну с db.py. Это самый важный шаг. Патчер через Python.
Давай напишу патчер для db.py:
python
import ast
import re

PATH = r"D:\tracker\client\db.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

# 1. Заменяем detect_abnormal_termination на правильную версию
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
    Если при старте клиента обнаружена незакрытая сессия — закрываем
    её временем последней активности (а не текущим временем).

    Логика: почему не "сейчас"?
    Если сотрудник ушёл домой в 18:00, а ПК упал/выключили в 18:05,
    сессия в SQLite осталась открытой. Утром при следующем запуске
    закрываем её — но не временем "сейчас" (09:00 следующего дня,
    это дало бы 15 часов работы), а временем последней реальной
    активности (18:00).

    Fallback на "сейчас" — только если записей в сессии вообще нет
    (тогда длительность = 0 секунд).
    """
    active = get_meta("active_session")
    if not active:
        return

    # Приоритет 1: последняя запись активности в этой сессии (самый надёжный источник)
    last_record_ts = get_last_session_record_ts(active)

    # Приоритет 2: meta last_activity (если записей нет)
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

    # Приоритет 3: start_time сессии (если совсем ничего нет)
    if not last_record_ts:
        last_record_ts = get_session_start(active) or _now_iso()

    # Насколько давно это было?
    try:
        end_dt = datetime.fromisoformat(last_record_ts)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        end_dt = datetime.now(timezone.utc)

    # Если прошло меньше 12 часов — ничего не делаем (может, клиент
    # просто перезапустился и это та же сессия). Мы лишь страхуем
    # действительно «висящие» сессии.
    if datetime.now(timezone.utc) - end_dt < timedelta(hours=12):
        return

    log.warning("Abnormal termination of %s — closing at last activity %s",
                active, last_record_ts)
    close_session_at(active, last_record_ts, abnormal=True)
'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: detect_abnormal_termination заменён")
else:
    print("WARN: старый detect_abnormal_termination не найден — возможно уже пропатчен")

# 2. Обновляем close_session — добавляем safety cap на длительность
old_close = '''def close_session(uid: str, abnormal: bool = False):
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?",
        (_now_iso(), 1 if abnormal else 0, uid),
    )
    if get_meta("active_session") == uid:
        set_meta("active_session", "")'''

new_close = '''def close_session(uid: str, abnormal: bool = False):
    """
    Закрывает сессию текущим временем UTC.
    Для аварийного закрытия правильнее использовать close_session_at —
    передать время последней активности, а не «сейчас».
    """
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?",
        (_now_iso(), 1 if abnormal else 0, uid),
    )
    if get_meta("active_session") == uid:
        set_meta("active_session", "")'''

