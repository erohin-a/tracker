<!-- Часть 1109 из 1409 -->
# At the end — close last window at last event
*Хлебные крошки:* At the end — close last window at last event

[◀ Step 2: Within each continuous session, walk windows and assign time](1108_Step_2_Within_each_continuous_session_walk_windows_and_assign_time.md) | [Оглавление](00_BCE_INDEX.md) | [Проверим, не пропатчен ли уже ▶](1110_Proverim_ne_propatchen_li_uzhe.md)

---

# At the end — close last window at last event
if current_window is not None and current_window_start is not None and last_ts is not None:
    dur = int((last_ts - current_window_start).total_seconds())
    if dur > 0:
        app_stats[current_window]["seconds"] += dur
Wait, this has an issue. If window event triggers a new window AND we count it as start of active, but the window is opened and immediately user walks away — we'd count 0 because next event is far away (session_end is not an event, so last event is the window event — duration = 0). Good.
But if user opens window, sits idle 10 min (no activity), then moves mouse ? activity event at +10 min. Gap = 10 min > 5 min ? reset. current_window_start = None. Then activity event ? current_window_start = ev.ts. So counting starts from +10 min. The initial 10 min idle ? not counted. Good.
But wait — the window event itself IS last_ts initially. Then the 10 min gap. So we already closed... hmm let me re-trace.
text
t=0: window event — current_window=1C, current_window_start=0, last_ts=0
t=10min: activity event
  gap = 10 min > 5 min ? close current window: dur = last_ts - current_window_start = 0 - 0 = 0. Set current_window_start=None.
  kind=activity ? current_window_start = 10min. keys=1 ? keyboard += 5
  
last_ts = 10min

... (user works 20 min with activity every 5 sec)

t=30min: window event (switch)
  gap = 5 sec < 5 min ? don't reset.
  kind=window ? close current: dur = 30min - 10min = 20 min. app_stats[1C].seconds += 20 min. Good — counted only 20 min of actual work.
  current_window = new app, current_window_start = 30min.
So the 1C program got 20 min instead of 30 min. Correct!
Good, the algorithm works.
Now edge case: what if gap is exactly at boundary? Let's say user works, then idles 5 min exactly. Gap = 5 min, threshold = 5 min. > gap_threshold means not triggered. So 5 min of idle passes as "active". Next event at 5min+5sec. Then window continues. Hmm. OK, minor. Could use >= instead. Let's use > gap_threshold to be a bit lenient. Or > gap_threshold with gap = 5 min as > — user must idle > 5 min to break.
Fine.
Now let's think about the "Интенсивная работа" metric with union approach.
For variant (B): union of {keys>0} intervals and {clicks>0} intervals within activity events.
Simplest: for each activity event (5 sec window):
if keys > 0 OR clicks > 0 OR scroll > 0 ? count this 5-sec interval once
интенсивная = count * 5
That's the union of "any activity" intervals. Simple and correct — because each activity event represents a 5-sec interval, and it either has activity or not.
Total интенсивная ? С трекером always (since activity events only occur during session).
But user said "их сумма не должна превышать время работы в программе". Actually — интенсивная ? эффективная (время в программах) — because activity events are only assigned to the current window. If there's no window (idle, pause), activity events... hmm, actually they can occur anywhere in the session.
Wait — should keyboard activity count toward "intensive work" if there's no window (no program is active)? On Windows there's always some active window. So this edge case is rare. But to be safe: интенсивная counts activity events regardless of window, then capped at эффективная.
Actually — hmm. Let me re-think. In a real scenario, if user types something, some window is active. So keyboard/clicks happen inside some window. Which means: интенсивная ? эффективная naturally.
But there's a subtle case: user clicks on desktop (no active window) — that's a click inside no app. But desktop is technically "explorer.exe" window. So it still falls under a program.
OK, let's just compute интенсивная as "sum of 5-sec intervals where any activity was registered", and it will naturally be ? эффективная.
Now — the user's question again:
если сотрудник запустит окно программы на весь день на 9 часов подходя раз к примеру в 45 минут шевеля мышкой что бы экран не потух она так и посчитает что он работал в программ 9 часов?
Answer with the new algorithm:
Pure mouse movement is NOT tracked by client (only keys, clicks, scroll).
If they use a jiggler — pure movement — no activity events. Session has only the initial window event. Gap is huge. Window duration = 0. Correct: not counted.
If they click occasionally (or press key) every 4 min — gap is 4 min < 5 min ? window continues. So effectively they're "walking" 9 hours of presence at the PC. Hmm. In this case:
Эффективно = 9 hours (because window wasn't reset)
Интенсивная = 4 events * 5 sec = 20 sec
Аналогично для кадровика: "Эффективно 9:00, Интенсивно 0:20" — сразу видно, что человек не работал.
That's actually the right behavior. "Эффективно" measures "программа была активна и была какая-то жизнь", "Интенсивная" measures "реально нажимал". Разница между ними показывает "присутствовал у экрана, но не работал".
So the answer to the user: NO, разовое шевеление мышкой не спасёт. И даже если раз в 4 минуты чуть-чуть пошевелит — Эффективно посчитается, но Интенсивная покажет ~0, и кадровик сразу увидит разницу.
Alternative approach — event-based idle detection.
Actually, we could also detect "idle" periods differently: client could send idle events (from pynput-based idle detection). Looking at collector:
If idle for > IDLE_THRESHOLD (60 sec), it writes idle event
Then when activity resumes, idle_end event
Hmm, we do have idle events. Let me use those too.
Wait — do we write idle events? From collector:
text
def _emit_window(self):
    if self._is_idle():
        if not self._was_idle:
            self._write("idle", {"type": "idle"})
            self._was_idle = True
        return
    if self._was_idle:
        self._write("idle_end", {"type": "idle_end"})
        self._was_idle = False
So idle is sent when idle threshold (60 sec) is exceeded. Then idle_end when user returns.
So we could use idle events to know exactly when the user was idle. Even better!
Combined logic:
When we see idle event ? close current window immediately (last activity was before idle started)
When we see idle_end event ? don't count until next window/activity
But — during pause (button pause), does client emit idle events? Pause stops the collector, so no idle events during pause. Good.
The gap-based approach and idle-based approach are complementary. Idle is more precise (60 sec threshold), gap is fallback for missing idle events.
Actually — simplest robust: use BOTH. Cut window at idle_start event AND at gaps > gap_minutes. Whichever is more aggressive.
OK. I have a full picture now. Let me write the response.
Response structure:
Direct answer to the user's question: NO, won't count 9 hours. Explain why.
Explain the algorithm — cut on gaps and idle events.
Confirm intensity = union approach, capped by effective.
Confirm overall metric set.
Ask if ready to proceed to implementation.
Let me write clearly and concisely. Not too long.
Отличный вопрос — он вскрывает ключевую деталь, которую надо проговорить до кода. Отвечаю прямо.
Короткий ответ на твой кейс
Нет, 9 часов не засчитает. Даже если сотрудник открыл окно 1С на весь день и раз в 45 минут двигал мышкой — программа ему не «поверит».
Причины две:
Причина 1. Наш клиент не отслеживает движение мыши. Смотрим collector.py:
text
self._pending = {"keys": 0, "clicks": 0, "scroll": 0}
_on_key ? keys += 1
_on_click ? clicks += 1
_on_scroll ? scroll += 1
Чистое движение мыши (без клика и скролла) не считается вообще. Это защита от «mouse jiggler» — софта, который двигает курсор, чтобы экран не потух. У нас от такого софта защиты нет — потому что мы его и не видим.
Причина 2. Окно рвётся по «тишине» — gap-механизм.
Как конкретно считается «Эффективно» (window-time)
Алгоритм в _analyze_session работает так:
Все события (window + activity) складываются в один список, сортируются по времени.
Идём по списку. Держим «текущее окно» и момент, когда оно стало активным.
Ключевое правило: если между двумя соседними событиями разрыв > activity_gap_minutes (сейчас 5 мин) — текущее окно закрывается в момент последнего события. Отсчёт начинается заново только когда придёт новое событие.
Дополнительно: если клиент прислал idle — окно закрывается сразу, не дожидаясь gap.
Разбираю на твоём кейсе:
text
t=0:00   window 1C  ? current_window = 1C, отсчёт от 0:00
t=0:45   ничего нет (юзер просто двигал мышью — 0 записей)
...
t=9:00   конец сессии
Что получает «1С»: 0 секунд. Потому что после window-события в 0:00 — больше ничего не пришло. Разрыв 9 часов > 5 мин ? окно закрывается сразу в момент последнего события (в 0:00). Длительность = 0.
Что получает «Эффективно» за день: 0:00.
А если сотрудник нажмёт клавишу раз в 4 минуты?
Хитрый сценарий. Тогда:
t=0:00 — window 1C
t=0:04 — activity keys=1
t=0:08 — activity keys=1
...
до 9:00
Разрывы по 4 минуты < 5 мин ? окно 1C не закрывается. «Эффективно» = 9:00.
Но. В том же подсчёте у нас есть второй показатель — «Интенсивная». Он считает не окна, а 5-секундные интервалы, где реально были keys/clicks/scroll.
В этом сценарии: 135 раз нажатий (каждые 4 мин за 9 часов) = 135 ? 5 сек = 11 минут интенсивной работы.
И в отчёте кадровик сразу видит:
Эффективно	Интенсивная
9:00	0:11
Разница в 100 раз. Дальше — вопрос к сотруднику.
«Интенсивная работа» = вариант (B), финально
Считаем как union «5-секундных окон с любой активностью»:
Каждое activity-событие = 5 секунд.
Если в этих 5 секундах есть keys>0 или clicks+scroll>0 — засчитываем эти 5 секунд.
Никакого удвоения при одновременной клаве + мыши.
Ограничение: сумма всегда ? «Эффективно». В норме — потому что activity-события идут только внутри активного окна.
Пример: 135 нажатий ? 135 activity-событий с keys=1 ? 135 ? 5 = 11:15. Ни больше ни меньше.
Итоговый набор метрик — 5 чисел
Метрика	Формула	Отвечает на вопрос
Отработано	span от 1-й до конца последней сессии	«сколько по табелю»
С трекером	union интервалов сессий	«сколько у нас данных»
Эффективно	суммарное время активных окон (с обрезкой по gap и idle)	«сколько был в работе в приложениях»
Интенсивная	сумма 5-секундных окон с реальной активностью	«сколько реально стучал»
Пауза	pause_seconds + (Отработано ? С трекером)	«сколько официально отдыхал + перерывов между сессиями»
Всё связано границами:
Интенсивная ? Эффективно (события идут только внутри активного окна)
Эффективно ? С трекером (окна пишутся только во время сессии)
С трекером ? Отработано (перерыв между сессиями не входит в «С трекером»)
Что нужно доработать в бэкенде
Gap-обрезка окон — сейчас в _analyze_session есть логика обрезки по gap только для activity, для window — надо перепроверить и дописать так, чтобы окно закрывалось при большом разрыве между любыми событиями.
Idle-события — должны разрывать окно сразу, чтобы не ждать gap.
Метрика «Интенсивная» — новое поле в _analyze_session и в totals.
Метрика «Пауза» — переделать с Отработано ? Эффективно на pause_seconds + (Отработано ? С трекером).
Проверка верхней границы — если по какой-то причине сумма activity превысила сумму окон, обрезать до эффективной.
Готов начинать
С этого момента мы точно и однозначно определили все 5 метрик. Начинаю с этапа 1:
Убираю верхние карточки ? строка контекста.
Добавляю столбцы Дней, Интенсивная, Пауза (переопределённую).
Убираю столбец «Аварийные» ? иконка ? на строке.
Делаю блок «? Без привязки» внизу с раскрытием и кнопками.
Один момент, который хочу уточнить до старта: порог activity_gap_minutes меняем с 5 на 2 или оставляем 5? С одной стороны — 2 мин честнее (быстрее отсечёт «окно открыто, человека нет»). С другой — 5 мин не режет короткие паузы (отойти за кофе — не считается простоем). Кадровики обычно смотрят на обе цифры, так что можно оставить 5 как более «мягкий» порог. Как решишь — начинаю.
у нас в настройках по умолчанию сейчас стоит 5 секунд пукай остаётся так у нас есть инструмент когда будет большой тест тогда будет понятно, править или нет. проверь длину чата и начинаем
The user wants me to check chat length and start working. They've confirmed gap stays at 5 seconds. Let me be concise and start delivering the code.
Wait — they say "5 секунд" but the setting says "5 минут" (activity_gap_minutes). And there's also "Период опроса активного окна = 5 секунд". The screenshot shows "Порог паузы для «Эффективно»: 5 минут". That's activity_gap_minutes = 5. Keep as is.
They want me to:
Check chat length — I should estimate we're around 60-70% full based on the massive input.
Start working — begin with Step 1: remove top cards, add "Дней" and "Пауза" columns, "Интенсивная" column, remove "Аварийные" column, add "? Без привязки" block.
Actually wait — I need to be careful. The user said "проверь длину чата и начинаем". Let me be brief on chat length and get to work.
Chat length estimate: This is a long conversation with huge file attachments. We're probably at 50-60% of context. Should plan for handoff around next big sprint.
Let me start with the code. I need to:
Backend changes in web_admin.py:
Remove upper cards logic (well, keep totals but change what we compute)
Add "intensive_seconds" metric
Fix "Пауза" = pause_seconds + (worked_span - worked_union)
Add days_count for month grouping
Template changes:
Remove top 4 cards, add context string
Change table columns
Add "? Без привязки" block
Let me structure this carefully. The first step should be backend — since without correct metrics the frontend won't show correct data.
Actually let me be smart — first thing is to check what's currently in _analyze_session and _build_report to give a precise patch. But I don't have the current file content — I have from the handoff notes.
Based on the handoff:
worked_span_duration — уже есть
worked_duration — union, есть
effective_duration — есть
_compute_effective_seconds — есть
break_duration — добавили в последнем патче (но не проверяли)
idle_duration — добавили в последнем патче
Now we need:
intensive_seconds — новое
Переопределить break_duration = pause_seconds + (span - union). Сейчас оно = span - union. Плюс pause_seconds.
Wait, actually pause_seconds уже вычитается из сессии? Let me think about this. When the user presses "Пауза", the client:
Stops collector
Sets pause_start in meta
When unpaused, pause_seconds += delta
Does the session_end get affected? No. Does it split the session? No.
So session_end - session_start = full session wall time, включая нажатые паузы.
pause_seconds — это сколько времени внутри сессии была кнопка нажата.
Now worked_span_duration = span от первой до последней сессии за день.
worked_duration (union) = union интервалов сессий.
effective_duration = сумма времени в активных окнах.
Отсюда:
Между сессиями пропуск = worked_span_duration - worked_duration
Кнопки паузы внутри сессий = ? pause_seconds
Общая пауза = (worked_span_duration - worked_duration) + ? pause_seconds
Good. So break_duration = (worked_span_duration - worked_duration) + ? pause_seconds.
But wait — are pause_seconds вычтены из worked_duration? Because during pause, no records are written, but the session is still "open". Let me check.
Looking at how records work: during pause, client stops collector. But session_end - session_start включает паузу. So union интервалов [start, end] включает pause time.
Hmm, that's a problem. If we count union = [8:00, 17:00] = 9 hours, но сессия 2 имеет паузу 13:30-14:30, тогда union включит эти 1 час. А "С трекером" должно быть = 8 часов (без паузы).
So we need to SUBTRACT pause_seconds from worked_duration for it to be accurate.
Actually no — "С трекером" как мы определили выше = "сколько времени клиент был в активной сессии". Это спорно — во время паузы клиент в сессии, но не собирает данные.
Hmm, this needs clarity. Let me think about what makes sense:
"С трекером" = времени, когда клиент фактически что-то собирал (не на паузе). То есть из union интервалов сессий надо вычесть pause_seconds.
Alternative: считать интервалы [start, pause_start] ? [pause_end, end] внутри сессии. Это сложнее.
Simpler: worked_duration_with_pause = union(intervals) — wait, but if pause_seconds is already subtracted, then "с трекером" уменьшится.
Let me look at the user's example again:
Сессия 1: 8:00-12:00 (4:00)
Перерыв: 12:00-13:00 (1:00)
Сессия 2: 13:00-17:00, пауза 13:30-14:30 (1:00)
Expected:
Отработано = 9:00 (span)
С трекером = 8:00 (4 + 4, где 4 = 13:00-17:00 = 4, но с паузой? или без?)
Hmm. User says "С трекером 8:00". But session 2 has pause 1 hour. Does that mean:
Option A: С трекером = 9 - 1 (перерыв) = 8:00 — то есть С ТРЕКЕРОМ включает паузу
Option B: С трекером = 9 - 1 (перерыв) - 1 (пауза) = 7:00 — С ТРЕКЕРОМ без паузы
User said 8:00. So it's Option A. С трекером включает время нажатой паузы.
Then:
Эффективно = 7:00 (4:00 + 3:00)
Пауза = 9:00 - 7:00 = 2:00? Or something else?
Wait user said: "Пауза = «Паузу» + время без трекера между рабочими сессиями"
Пауза = 1:00 (кнопка) + 1:00 (перерыв) = 2:00
And it matches my "worked_span - effective" formula coincidentally in this example. Let me verify:
worked_span - effective = 9:00 - 7:00 = 2:00 ?
But this formula is not always equal! Consider:
Сессия 8:00-17:00 без пауз, без простоев больше 5 минут
Эффективно = 9:00
Пауза = 0
worked_span - effective = 9 - 9 = 0 ?
Another case:
Сессия 8:00-17:00, внутри было много тихих простоев (не нажатых)
Скажем, человек уходил в кино на 3 часа, ничего не нажимал
gap обрежет — эффективно = 6:00
worked_span - effective = 3:00
Но "Пауза" (по определению пользователя) = 0 кнопок + 0 перерывов = 0!
So the formulas are different. The user's definition is:
Пауза = ? pause_seconds + (worked_span - worked_union)
Where worked_union = union интервалов сессий (включая время нажатой паузы, потому что сессия не закрыта).
Let me redo example:
worked_span = 9:00
worked_union = 8:00 (4 + 4, где вторая сессия включает 1 час паузы)
? pause_seconds = 1:00
Пауза = 1:00 + (9:00 - 8:00) = 1:00 + 1:00 = 2:00 ?
Good.
And Эффективно = 7:00 — это сумма времени активных окон. Внутри паузы окон нет, поэтому из 8 часов сессии 2 только 3 часа в окнах.
So:
Отработано = span
С трекером = union сессий (включая время пауз)
Эффективно = сумма активных окон
Интенсивная = union 5-сек окон с активностью
Пауза = ? pause_seconds + (span - union)
But wait, actually is that OK that С трекером включает паузу? Yes because "С трекером" = "запущено приложение и сессия открыта". Даже если сотрудник нажал паузу, приложение работает и сессия "открыта".
OK. I need to make sure the code uses this definition.
Also: worked_union включает pause_seconds — то есть в union мы не вычитаем паузы. Это надо проверить в коде — вероятно там сейчас union [start, end] без вычета паузы. Хорошо, что так.
Actually wait — a pause might create a records gap. Но если во время pause records не пишутся, то activity_end_local = last_event_local может не покрывать всю сессию. Значит в _analyze_session interval [activity_start, activity_end] может не включать паузу.
Hmm. Let me think carefully.
Actually in _analyze_session, we have:
start_local = начало сессии
end_local = конец сессии
first_event_local = первое событие (activity/window)
last_event_local = последнее событие
activity_start_local = first_event_local (или start если нет событий)
activity_end_local = last_event_local (или end если нет событий)
For pause case:
Session start 13:00
Pause 13:30-14:30 (no records during)
Session end 17:00
Records: 13:00-13:30, 14:30-17:00
first_event_local = 13:00
last_event_local = 17:00
So activity_start = 13:00, activity_end = 17:00. Interval = 4 hours. Includes pause.
OK, so union интервалов будет включать паузу, если она внутри одной сессии. Хорошо.
But wait — did we subtract pause_seconds anywhere? Looking at _analyze_session:
text
if pause_sec > 0:
    effective_duration = max(0, effective_duration - pause_sec)
Hmm — we're subtracting pause_seconds from effective_duration. But effective is meant to be "сумма активных окон", which should already exclude pause (no records during pause). So subtracting pause_seconds again — это двойное вычитание.
Actually let me think again. In _analyze_session:
effective_duration изначально = last_event - first_event = 4:00 (для сессии 2)
Но inside this interval, pause 13:30-14:30 есть. Записи не пишутся.
effective_duration = 4:00 (по старой формуле).
Но правильное "эффективно" = сумма окон с активным приложением = 3:00.
Тогда нужно посчитать эффективно как сумму длительностей интервалов активных окон, а не last_event - first_event.
Разница именно в этом. Текущий код считает эффективно как "от первого события до последнего", а надо "сумма окон активности".
Но с учётом gap — если gap 5 мин, и пауза 60 мин, то окно 1С закрывается в момент последнего events до паузы (13:30), потом снова открывается когда приходит новое событие (14:30). Значит эффективно = 30 мин + 2:30 = 3:00.
Использовать первый проход через events — вычислять сумму активных интервалов. Это как раз то что нужно.
OK. Это уже большая правка в _analyze_session. Надо её аккуратно делать.
Given complexity — давайте разобью работу:
Этап 1.A — только бэкенд: переделать _analyze_session с правильно посчитанным effective (сумма активных интервалов) и intensive. Плюс переопределить break_duration.
Этап 1.B — только шаблон: убрать карточки, добавить столбцы, добавить блок "без привязки".
Это два разных этапа. Начну с A, потом B.
Хотя может проще всё сразу. Пользователь хочет идти. Плюс у нас есть тестовые данные.
Дай подумаю о chat length. Мы уже в очень длинной сессии (огромные документы). Наверное 60-70%. Стоит предупредить, что следующая итерация может быть последней.
Let me start with a clear plan message and then do the first script.
Actually the user asked to "check chat length and start". So:
Short mention of chat length
Start with first script
Let me structure:
Chat length: около 60-70%, хватит на 2-3 крупных итерации
План этапа 1: 2 подэтапа — бэкенд + шаблон
Скрипт 1 — переделка _analyze_session (правильный effective + intensive + break)
Let me carefully write the backend patch. Looking at current _analyze_session (from handoff):
python
def _analyze_session(ws, recs, tz, gap_minutes):
    start_local = _to_local(ws.session_start, tz)
    end_local = _to_local(ws.session_end or _now(), tz)
    first_event_local = None
    last_event_local = None
    gap = timedelta(minutes=gap_minutes)
    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    current_window = None
    current_window_started_local = None
    events = []
    for r in recs:
        try:
            data = json.loads(r.data) if r.data else {}
        except Exception:
            data = {}
        events.append({"ts_local": _to_local(r.client_ts, tz), "kind": r.kind, "data": data})
    events.sort(key=lambda x: x["ts_local"])
    for i, ev in enumerate(events):
        ts = ev["ts_local"]
        if first_event_local is None:
            first_event_local = ts
        last_event_local = ts
        kind = ev["kind"]
        data = ev["data"]
        if kind == "window":
            if current_window is not None and current_window_started_local is not None:
                dur = int((ts - current_window_started_local).total_seconds())
                if dur > 0:
                    app_stats[current_window]["seconds"] += dur
            app = data.get("app") or data.get("title") or "unknown"
            current_window = app
            current_window_started_local = ts
        elif kind == "activity":
            keys = int(data.get("keys", 0) or 0)
            clicks = int(data.get("clicks", 0) or 0)
            scroll = int(data.get("scroll", 0) or 0)
            if i > 0:
                delta = (ts - events[i - 1]["ts_local"]).total_seconds()
                if delta > gap.total_seconds():
                    if current_window is not None and current_window_started_local is not None:
                        dur = int((events[i - 1]["ts_local"] - current_window_started_local).total_seconds())
                        if dur > 0:
                            app_stats[current_window]["seconds"] += dur
                    current_window_started_local = ts
            if current_window is not None:
                if keys > 0:
                    app_stats[current_window]["keyboard"] += 5
                if clicks + scroll > 0:
                    app_stats[current_window]["mouse"] += 5
    if current_window is not None and current_window_started_local is not None and last_event_local is not None:
        dur = int((last_event_local - current_window_started_local).total_seconds())
        if dur > 0:
            app_stats[current_window]["seconds"] += dur
    if first_event_local and last_event_local:
        effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
        activity_start_local = first_event_local
        activity_end_local = last_event_local
    else:
        effective_duration = 0
        activity_start_local = start_local
        activity_end_local = end_local
    pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)
    if pause_sec > 0:
        effective_duration = max(0, effective_duration - pause_sec)
    full_duration = max(0, int((activity_end_local - activity_start_local).total_seconds()))
    top_apps = sorted(...)
    return {
        "session_uid": ws.session_uid,
        ...
        "full_duration": full_duration,
        "effective_duration": effective_duration,
        "activity_start_local": activity_start_local,
        "activity_end_local": activity_end_local,
        "pause_seconds": pause_sec,
        ...
    }
OK, so the current logic is:
effective_duration = last_event - first_event (не правильно, там дырки)
Плюс потом минус pause_seconds (двойное вычитание — если пауза внутри интервала)
full_duration = last_event - first_event (не то, что надо)
Need to change:
effective_duration = сумма (current_window интервалов, обрезанных по gap)
full_duration = end - start (это то, что я ранее переименовал в activity_end... на самом деле должно быть = Отработано за сессию, но не нужно — есть worked_span_duration)
intensive_seconds = сумма 5-секундных интервалов, где activity с keys>0 или clicks+scroll>0
Пусть:
effective_duration = сумма app_stats[app]["seconds"] (уже вычислено в конце!)
intensive_seconds = 5 ? количество activity-событий с keys>0 OR clicks+scroll>0
pause_seconds = как есть из БД
full_duration = end_local - start_local (это просто длительность сессии)
Wait — но effective_duration не должна включать паузы, а она не включает по определению (окна не пишутся во время pause). Отлично, значит формула правильная, просто взять сумму app_stats.
Ok, that's much cleaner.
For gap — надо чтобы gap-проверка применялась к ЛЮБЫМ событиям, не только activity. Тогда:
Между двумя activity с разрывом > 5 мин ? окно закрывается на моменте последнего activity.
Между activity и window (или window и activity) с разрывом > 5 мин ? тоже закрывается.
Но window — это edge-triggered, они появляются когда меняется окно. Если окно не менялось 5 минут, то window-событий не будет. Значит текущее окно не закрывается просто потому что 5 минут прошло — а надо закрыть по fact того, что окно было активно 5 минут назад.
Хмм. Проблема: если окно 1С открыто, и за 9 часов не менялось, но пользователь раз в 4 минуты отправлял activity с keys=1 — окно 1С закрывается по факту последнего activity (9:00), и продолжается с 9:00. Длина окна = 9:00. Правильно.
Но если окно 1С открыто 9 часов без активности вообще (ни keys, ни clicks) — тогда window-событие было только в 0:00. Last_event = 0:00. Окно закроется в 0:00. Length = 0. Правильно.
Ок, значит логика "закрываем окно по последнему activity" уже работает. Но что если пришёл activity в 0:05, а потом ничего до 9:00? Окно 1С длится 0:00-0:05 = 5 минут. Правильно.
А если пришёл activity в 0:05 (keys=1), потом в 0:10 (keys=1) и так далее каждые 5 минут? Каждое событие возобновляет окно. В итоге окно 1С длится от 0:00 до 9:00 = 9 часов. Правильно.
Хм, но это не gap logic — это gap logic для повторных событий. Смотрим на текущий код:
text
if delta > gap.total_seconds():
    # закрыть окно
    current_window_started_local = ts
Значит если delta > 5 мин между двумя activity — окно закрывается (до предыдущего), и открывается с нового места. Но если delta <= 5 мин, окно продолжается.
Стоп, но это же влияет только на activity. Для window-событий такой логики нет! Если приходит window в 10:00 (смена на Chrome), а предыдущее событие было в 9:00 (last activity), то duration = 1 час — окно 1С длилось 1 час. Но фактически последняя активность была в 9:00, а потом тишина. Значит окно должно было закрыться в 9:05 (или при следующем событии — момент 9:00).
Надо добавить проверку на gap и для window-событий.
Actually текущий код закрывает окно перед открытием нового при window-событии:
text
if kind == "window":
    if current_window is not None and current_window_started_local is not None:
        dur = int((ts - current_window_started_local).total_seconds())
        if dur > 0:
            app_stats[current_window]["seconds"] += dur
Это закрывает окно 1С в момент window-события (10:00). Duration = 1 час. Это не правильно — должно быть 9:00-9:05 или 9:00-9:00.
Fix: при window-событии, перед закрытием старого окна, проверить gap: если delta от предыдущего события > gap, то old_window закрывается на предыдущем событии, а не на текущем.
text
if kind == "window":
    # Определяем момент закрытия старого окна
    prev_ts = events[i-1]["ts_local"] if i > 0 else None
    close_ts = ts
    if prev_ts is not None:
        delta = (ts - prev_ts).total_seconds()
        if delta > gap.total_seconds():
            close_ts = prev_ts  # окно закрылось ещё тогда
    if current_window is not None and current_window_started_local is not None:
        dur = int((close_ts - current_window_started_local).total_seconds())
        if dur > 0:
            app_stats[current_window]["seconds"] += dur
    ...
Yes, this should work.
For activity with gap logic — нужно тоже аккуратно:
text
elif kind == "activity":
    keys, clicks, scroll = ...
    if i > 0:
        delta = (ts - events[i-1].ts_local).total_seconds()
        if delta > gap.total_seconds():
            if current_window is not None and current_window_started_local is not None:
                # окно закрылось на предыдущем событии
                dur = int((events[i-1].ts_local - current_window_started_local).total_seconds())
                if dur > 0:
                    app_stats[current_window]["seconds"] += dur
                current_window_started_local = ts
    ...
Yes that's what's in the code.
But there's a subtle issue with last_event_local — this variable is updated for every event, but the final closing uses it:
text
if current_window is not None and current_window_started_local is not None and last_event_local is not None:
    dur = int((last_event_local - current_window_started_local).total_seconds())
For "1C window open, user opens 9 hours, one event at 0:00, no more events", last_event = 0:00. Duration = 0:00 - 0:00 = 0. Правильно.
OK, so with the gap-fix on window events, the algorithm is correct.
But we still have the issue of effective_duration = last_event - first_event. This needs to become sum of window intervals. Given that app_stats already has this data, it's easy — just sum them all up.
python
effective_duration = sum(v["seconds"] for v in app_stats.values())
And intensive_seconds:
python
intensive_seconds = 0
for ev in events:
    if ev["kind"] == "activity":
        d = ev["data"]
        keys = int(d.get("keys", 0) or 0)
        clicks = int(d.get("clicks", 0) or 0)
        scroll = int(d.get("scroll", 0) or 0)
        if keys > 0 or clicks > 0 or scroll > 0:
            intensive_seconds += 5
Wait — the current client sends activity records every 5 seconds. So each activity = 5 sec. If in those 5 sec there was any input, count it.
But wait — the client sends ONE activity record per 5 sec only if there was activity. Let me check collector.py:
text
def _flush(self):
    with self._lock:
        counts = dict(self._pending)
        self._pending.update({"keys": 0, "clicks": 0, "scroll": 0})
    if any(counts.values()):
        self._write("activity", {"type": "activity", "counts"})
So it only writes activity records if there was some input. Each activity = 5 sec interval with input.
Then intensive_seconds = 5 ? count(activity events). Simple.
But — careful — this could exceed effective_seconds in edge cases. Cap it at effective_seconds.
Or better — only count activity events that fall inside a valid window interval. Simple approach: cap at effective_seconds.
Actually if the client uses a different polling interval (e.g., 10 sec), this breaks. For now assume 5 sec (ACTIVE_WINDOW_INTERVAL = 5 in client config).
Actually let me not overthink — use constant 5.
OK, this is the plan. Now let me write the patch for _analyze_session.
Let me write the full replacement for _analyze_session since it's complex.
Actually let me carefully check what the current code looks like — I don't have the exact current version. I'll patch key parts.
Approach: I'll give a Python patcher that replaces specific blocks. Let me identify what needs to change:
In the window branch — add gap check for closing old window.
After the loop — compute effective = sum of app seconds; intensive = 5 ? activity count; remove the effective_duration - pause_sec line.
Add intensive_seconds to return dict.
OK let me write it.
Actually the safest way — replace the whole _analyze_session function. Let me use a Python patcher that finds def _analyze_session and replaces until def _build_flat_records.
Let me construct the new function:
python
def _analyze_session(ws: WorkSession, recs, tz: ZoneInfo, gap_minutes: int) -> dict:
    """
    Считает метрики по одной сессии.
    Возвращает:
      - full_duration: session_end - session_start (полная длительность сессии, включая pause)
      - effective_duration: сумма интервалов активных окон (без пауз и простоев)
      - intensive_seconds: 5 ? количество activity-событий с реальной активностью
      - activity_start_local / activity_end_local: границы активности
      - top_apps: разбивка по программам
    """
    start_local = _to_local(ws.session_start, tz)
    end_local = _to_local(ws.session_end or _now(), tz)
    first_event_local = None
    last_event_local = None
    gap = timedelta(minutes=gap_minutes)
    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    current_window = None
    current_window_started_local = None
    events = []
    for r in recs:
        try:
            data = json.loads(r.data) if r.data else {}
        except Exception:
            data = {}
        events.append({"ts_local": _to_local(r.client_ts, tz), "kind": r.kind, "data": data})
    events.sort(key=lambda x: x["ts_local"])
    
    intensive_count = 0  # сколько activity-событий с реальной активностью
    
    for i, ev in enumerate(events):
        ts = ev["ts_local"]
        if first_event_local is None:
            first_event_local = ts
        last_event_local = ts
        kind = ev["kind"]
        data = ev["data"]
        
        # Вычислим, был ли разрыв с предыдущим событием
        prev_ts = events[i - 1]["ts_local"] if i > 0 else None
        big_gap = False
        if prev_ts is not None:
            delta = (ts - prev_ts).total_seconds()
            if delta > gap.total_seconds():
                big_gap = True
        
        if kind == "window":
            # Если был большой разрыв — окно уже закрылось на предыдущем событии
            close_ts = prev_ts if big_gap else ts
            if current_window is not None and current_window_started_local is not None:
                dur = int((close_ts - current_window_started_local).total_seconds())
                if dur > 0:
                    app_stats[current_window]["seconds"] += dur
            app = data.get("app") or data.get("title") or "unknown"
            current_window = app
            current_window_started_local = ts
        elif kind == "activity":
            keys = int(data.get("keys", 0) or 0)
            clicks = int(data.get("clicks", 0) or 0)
            scroll = int(data.get("scroll", 0) or 0)
            # Интенсивная работа: 5 секунд за каждое событие с реальной активностью
            if keys > 0 or clicks > 0 or scroll > 0:
                intensive_count += 1
            # Если разрыв больше gap — окно закрывается на предыдущем событии
            if big_gap:
                if current_window is not None and current_window_started_local is not None:
                    dur = int((prev_ts - current_window_started_local).total_seconds())
                    if dur > 0:
                        app_stats[current_window]["seconds"] += dur
                current_window_started_local = ts
            # Учёт клавиатуры/мыши в разрезе текущего окна
            if current_window is not None:
                if keys > 0:
                    app_stats[current_window]["keyboard"] += 5
                if clicks + scroll > 0:
                    app_stats[current_window]["mouse"] += 5
        elif kind == "idle":
            # Пришёл idle — окно закрывается на текущем событии
            if current_window is not None and current_window_started_local is not None:
                dur = int((ts - current_window_started_local).total_seconds())
                if dur > 0:
                    app_stats[current_window]["seconds"] += dur
            current_window = None
            current_window_started_local = None
        elif kind == "idle_end":
            # Возврат из idle — начнём новое окно
            current_window = "unknown"
            current_window_started_local = ts
    
    # Закрываем последнее окно по последнему событию (не по end_local!)
    if current_window is not None and current_window_started_local is not None and last_event_local is not None:
        dur = int((last_event_local - current_window_started_local).total_seconds())
        if dur > 0:
            app_stats[current_window]["seconds"] += dur
    
    # Effective = сумма всех окон
    effective_duration = sum(v["seconds"] for v in app_stats.values())
    
    # Intensive = 5 ? количество событий с активностью
    intensive_seconds = intensive_count * 5
    # Ограничение сверху: не больше effective
    if intensive_seconds > effective_duration:
        intensive_seconds = effective_duration
    
    # Границы активности
    if first_event_local and last_event_local:
        activity_start_local = first_event_local
        activity_end_local = last_event_local
    else:
        activity_start_local = start_local
        activity_end_local = end_local
    
    # Full = end - start (полная длительность сессии)
    full_duration = max(0, int((end_local - start_local).total_seconds()))
    
    # Pause — из БД (нажат ли кнопка pause)
    pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)
    
    # Top apps
    top_apps = sorted(
        [{"app": k, "seconds": v["seconds"], "keyboard": v["keyboard"], "mouse": v["mouse"]}
         for k, v in app_stats.items()],
        key=lambda x: x["seconds"], reverse=True,
    )[:15]
    
    return {
        "session_uid": ws.session_uid,
        "start_local": start_local,
        "end_local": end_local,
        "date_local": start_local.date(),
        "full_duration": full_duration,
        "effective_duration": effective_duration,
        "intensive_seconds": intensive_seconds,
        "activity_start_local": activity_start_local,
        "activity_end_local": activity_end_local,
        "pause_seconds": pause_sec,
        "keyboard": sum(v["keyboard"] for v in app_stats.values()),
        "mouse": sum(v["mouse"] for v in app_stats.values()),
        "abnormal": bool(ws.abnormal_termination),
        "top_apps": top_apps,
        "employee_id": ws.employee_id,
        "computer_id": ws.computer_id,
    }
Wait — the client's activity interval is 5 seconds only if ACTIVE_WINDOW_INTERVAL = 5 (which is the current collector interval). Actually looking at collector.py more carefully:
text
def run(self):
    ...
    while self._running:
        self._emit_window()
        self._flush()
        end = time.time() + ACTIVE_WINDOW_INTERVAL
        while self._running and time.time() < end:
            time.sleep(0.2)
So it flushes every 5 seconds ? each activity record = 5 sec interval. Good.
Also note: kb and mouse counters in app_stats already work correctly — if keys > 0: keyboard += 5. The same "5 sec" logic.
Now, I need to update the aggregate functions to compute totals:
intensive_seconds should sum in _build_report totals
break_duration should be ?(pause_seconds) + (worked_span - worked_union)
Let me also update _build_report. But wait — the aggregate is done per-row (per day, per employee, etc.). Let me look at the current version.
Hmm I don't have the current version in front of me. Let me think about what needs to change:
In _split_by_day (or whatever): for each session, sum effective_duration, intensive_seconds, pause_seconds. That's simple.
For worked_span_duration — already computed via span.
For worked_duration (union) — computed via _union_duration.
For break_duration per row:
text
break_duration = pause_seconds_sum + (worked_span_duration - worked_duration)
Where pause_seconds_sum is ? pause_seconds across all sessions in this row.
OK. Let me look at the totals for the whole report. There should be a _build_report function that has totals.
Actually I'm getting into a large refactor. Let me be strategic — I'll write a patcher that:
Replaces _analyze_session with the new version.
Updates _build_report to compute the totals correctly.
But I need to see the current code first. Let me be conservative — do a targeted patch of just the _analyze_session and add the fields, and let the existing aggregates pick them up (if they exist).
Hmm — hard to do without seeing the file. Let me ask the user to send the current version of _analyze_session and the aggregation functions, or I'll write a patcher that operates on known anchors.
Actually, from the handoff, the aggregation functions include:
_split_by_day
_split_by_month
_group_by_employee
_group_by_department
_group_by_computer
_group_by_session
_build_report
And inside each, they use effective_duration, keyboard, mouse, top_apps, abnormal, worked_duration, worked_span_duration.
I need to add intensive_seconds and pause_seconds to those aggregations.
Let me write a patcher that:
Adds intensive_seconds and pause_seconds sum to _aggregate_group.
Replaces _analyze_session.
The _aggregate_group helper (from handoff):
python
def _aggregate_group(sessions: list, extra_fields: dict) -> dict:
    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    for s in sessions:
        _merge_apps(app_stats, s["top_apps"])
    result = {
        **extra_fields,
        "sessions_count": len(sessions),
        "effective_duration": sum(s["effective_duration"] for s in sessions),
        "keyboard": sum(s["keyboard"] for s in sessions),
        "mouse": sum(s["mouse"] for s in sessions),
        "abnormal": any(s["abnormal"] for s in sessions),
        "worked_duration": _span_of_sessions(sessions),
        "top_apps": _apps_to_list(app_stats),
        "sessions": sessions,
    }
    return result
I need to add:
python
"intensive_seconds": sum(s["intensive_seconds"] for s in sessions),
"pause_seconds": sum(s["pause_seconds"] for s in sessions),
"break_duration": sum(s["pause_seconds"] for s in sessions) + max(0, _span_of_sessions(sessions) - result_union),
Hmm — but break_duration needs both span and union. Span already computed via _span_of_sessions. Union is via _union_duration(intervals).
Let me define:
worked_span_duration = span of sessions (min start ? max end)
worked_duration = union of activity intervals
Currently worked_duration = _span_of_sessions(sessions) = span. But per the handoff, _span_of_sessions was replaced with union. So:
worked_duration (union) = _span_of_sessions(sessions) — now computes union
But we need span separately for worked_span_duration.
Wait — from the handoff: "web_admin.py — _span_of_sessions = union интервалов (без пересечений при 2 ПК)". So _span_of_sessions returns union. Then how is worked_span_duration computed?
Looking at handoff: "web_admin.py — новая метрика worked_span_duration (табель: от 1-й до последней)". So there must be a separate function or computation.
OK, I don't have enough info. Let me ask the user to send the current state of these functions, OR I'll assume and patch carefully.
Given the user wants to move fast, let me just write a patcher that:
Replaces _analyze_session — that's the main change
Adds new metrics to _aggregate_group and _build_report — I'll write those with checks, if the block isn't found, skip and log
Let me not overthink. I'll write the patcher, tell the user to run it, and if something doesn't match, I'll see the output.
Let me write it now. Actually, first let me be honest about chat length, then start.
Chat length: около 65-70%. Осталось на 2-3 крупные итерации.
Plan:
Этап 1.A: бэкенд — _analyze_session (правильный effective + intensive)
Этап 1.B: бэкенд — агрегаты (break_duration, intensive_seconds в totals)
Этап 1.C: шаблон — убрать карточки, новые столбцы
Этап 1.D: шаблон — блок "без привязки" + кнопки
Let me start with A. I'll ask user to send me the current function if my patch fails.
OK writing now. Let me be concise but complete.
Actually, let me give the patcher for _analyze_session and ask user to run it. Short message. Then if we confirm, next step.
Let me also warn: after this patch, existing test data (which we just created) might show different numbers, since current data doesn't have accurate pause_seconds/records patterns. But that's OK.
Let me write.
Длина чата
Оценочно ~65% заполнено. Осталось места на 2–3 крупные итерации. После первого этапа сделаю handoff-сводку, чтобы точно не потерять контекст.
gap_minutes = 5 оставляем как есть — согласен, инструмент покажет когда править.
План этапа 1
Разбиваю на 4 скрипта:
1.A — бэкенд: переделка _analyze_session (правильный effective + новый intensive)
1.B — бэкенд: агрегаты (пересчёт break_duration, добавление intensive_seconds в totals)
1.C — шаблон: убираем карточки, новые столбцы
1.D — шаблон: блок «? Без привязки» внизу
Начинаю с 1.A — это ядро. Без правильного effective остальное не имеет смысла.
Скрипт 1.A — переделка _analyze_session
Что меняется в логике:
Effective = сумма интервалов всех окон (а не last_event ? first_event). Раньше этот интервал включал паузы и простои — теперь каждое окно закрывается по правилам gap/idle, и их длительности суммируются.
Gap-проверка для window-событий. Раньше gap применялся только к activity. Теперь — ко всем: если между двумя событиями разрыв > 5 мин, окно закрывается на момент предыдущего события, а не на текущее. Это чинит кейс «открыл 1С на 9 часов, отошёл, вернулся — окно не должно считать все 9 часов».
idle / idle_end обрабатываются явно. Пришёл idle — окно закрывается сразу. Пришёл idle_end — начинается новое окно с unknown до первой смены.
pause_seconds больше не вычитается из effective. Во время паузы клиент не пишет records, значит эффективное время и так не включает паузу. Убираем двойное вычитание.
Новое поле intensive_seconds = 5 ? (количество activity-событий с keys>0 OR clicks+scroll>0). Ограничение сверху: не больше effective.
full_duration = end_local ? start_local (полная длительность сессии, включая паузы). Это для справки, не для отчёта.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

