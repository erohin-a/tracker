<!-- Часть 1111 из 1409 -->
# Найдём начало и конец функции _analyze_session
*Хлебные крошки:* Найдём начало и конец функции _analyze_session

[◀ Проверим, не пропатчен ли уже](1110_Proverim_ne_propatchen_li_uzhe.md) | [Оглавление](00_BCE_INDEX.md) | [Проверки ▶](1112_Proverki.md)

---

# Найдём начало и конец функции _analyze_session
start_marker = "def _analyze_session("
end_marker = "def _build_flat_records("

start = content.find(start_marker)
end = content.find(end_marker, start)
if start < 0 or end < 0:
    print("ERROR: не найдены маркеры _analyze_session / _build_flat_records")
    raise SystemExit(1)

new_func = '''def _analyze_session(ws: WorkSession, recs, tz: ZoneInfo, gap_minutes: int) -> dict:
    """
    Считает метрики по одной сессии.

    Ключевые метрики:
    - full_duration: полная длительность сессии (session_end - session_start).
      Включает время нажатой «Паузы».
    - effective_duration: сумма интервалов активности окон.
      Каждое окно открывается при смене активного приложения, закрывается по:
        * смене приложения,
        * разрыву между событиями > gap_minutes,
        * событию idle.
      Паузы и простои в эффективное время НЕ попадают (во время них
      records не пишутся).
    - intensive_seconds: 5 секунд ? количество activity-событий
      с реальной активностью (keys>0 или clicks+scroll>0).
      Ограничено сверху effective_duration.
    - pause_seconds: сумма времени нажатой кнопки «Пауза» (из БД).
    """
    start_local = _to_local(ws.session_start, tz)
    end_local = _to_local(ws.session_end or _now(), tz)

    first_event_local = None
    last_event_local = None
    gap = timedelta(minutes=gap_minutes)

    # Разбивка по приложениям
    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    current_window = None
    current_window_started_local = None

    # Собираем все события, сортируем по времени
    events = []
    for r in recs:
        try:
            data = json.loads(r.data) if r.data else {}
        except Exception:
            data = {}
        events.append({
            "ts_local": _to_local(r.client_ts, tz),
            "kind": r.kind,
            "data": data,
        })
    events.sort(key=lambda x: x["ts_local"])

    intensive_count = 0  # сколько activity-событий с реальной активностью

    for i, ev in enumerate(events):
        ts = ev["ts_local"]
        if first_event_local is None:
            first_event_local = ts
        last_event_local = ts

        kind = ev["kind"]
        data = ev["data"]

        prev_ts = events[i - 1]["ts_local"] if i > 0 else None
        big_gap = False
        if prev_ts is not None:
            delta = (ts - prev_ts).total_seconds()
            if delta > gap.total_seconds():
                big_gap = True

        if kind == "window":
            # Момент закрытия старого окна: если был большой разрыв — 
            # закрываем на предыдущем событии, иначе — на текущем
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

            # Интенсивная работа: каждое activity-событие с активностью = 5 сек
            if keys > 0 or clicks > 0 or scroll > 0:
                intensive_count += 1

            # Если разрыв — закрываем окно на предыдущем событии
            if big_gap:
                if current_window is not None and current_window_started_local is not None:
                    dur = int((prev_ts - current_window_started_local).total_seconds())
                    if dur > 0:
                        app_stats[current_window]["seconds"] += dur
                current_window_started_local = ts

            # Клавиатура/мышь в разрезе текущего окна
            if current_window is not None:
                if keys > 0:
                    app_stats[current_window]["keyboard"] += 5
                if clicks + scroll > 0:
                    app_stats[current_window]["mouse"] += 5

        elif kind == "idle":
            # Пришёл idle — закрываем текущее окно сразу
            if current_window is not None and current_window_started_local is not None:
                dur = int((ts - current_window_started_local).total_seconds())
                if dur > 0:
                    app_stats[current_window]["seconds"] += dur
            current_window = None
            current_window_started_local = None

        elif kind == "idle_end":
            # Возврат из idle — начинаем новое окно
            current_window = "unknown"
            current_window_started_local = ts

    # Закрываем последнее окно на последнем событии (не на end_local!)
    if (current_window is not None
            and current_window_started_local is not None
            and last_event_local is not None):
        dur = int((last_event_local - current_window_started_local).total_seconds())
        if dur > 0:
            app_stats[current_window]["seconds"] += dur

    # Effective = сумма всех интервалов окон
    effective_duration = sum(v["seconds"] for v in app_stats.values())

    # Intensive = 5 сек ? количество активных activity-событий
    intensive_seconds = intensive_count * 5
    if intensive_seconds > effective_duration:
        intensive_seconds = effective_duration

    # Границы активности
    if first_event_local and last_event_local:
        activity_start_local = first_event_local
        activity_end_local = last_event_local
    else:
        activity_start_local = start_local
        activity_end_local = end_local

    # Full — полная длительность сессии
    full_duration = max(0, int((end_local - start_local).total_seconds()))

    # Пауза — из БД (нажатие кнопки «Пауза»)
    pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)

    # Топ приложений
    top_apps = sorted(
        [{"app": k, "seconds": v["seconds"],
          "keyboard": v["keyboard"], "mouse": v["mouse"]}
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


'''

content = content[:start] + new_func + content[end:]

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

