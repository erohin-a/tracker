# Step 1: Split events into "continuous sessions of activity"

*Часть 81 из 100. Источник: `BCE.md`.*

[◀ Копируем внутрь контейнера и запускаем](080_Kopiruem_vnutr_konteynera_i_zapuskaem.md) | [Оглавление](00_BCE_INDEX.md) | [At the end — close last window at last event ▶](082_At_the_end_close_last_window_at_last_event.md)

---

# Step 1: Split events into "continuous sessions of activity" 
# where each session has no gap > gap_minutes

# Step 2: Within each continuous session, walk windows and assign time

current_window = None
current_window_start = None
last_ts = None
gap_threshold = timedelta(minutes=gap_minutes)

for ev in events:
    if last_ts is not None and (ev.ts - last_ts) > gap_threshold:
        # Long gap — reset current window
        if current_window is not None and current_window_start is not None:
            dur = int((last_ts - current_window_start).total_seconds())
            if dur > 0:
                app_stats[current_window]["seconds"] += dur
            current_window_start = None  # waiting for a new activity
    
    if ev.kind == "window":
        # Close previous window (if active)
        if current_window is not None and current_window_start is not None:
            dur = int((ev.ts - current_window_start).total_seconds())
            if dur > 0:
                app_stats[current_window]["seconds"] += dur
        current_window = ev.app
        # Only start counting if there was activity recently (this window event itself is an activity marker)
        # But — opening a window is an action, count it as start of active interval
        current_window_start = ev.ts
    elif ev.kind == "activity":
        if current_window is not None:
            if current_window_start is None:
                # Resume after idle — start counting now
                current_window_start = ev.ts
            keys = ev.data.get("keys", 0)
            clicks = ev.data.get("clicks", 0)
            scroll = ev.data.get("scroll", 0)
            if keys > 0:
                app_stats[current_window]["keyboard"] += 5
            if clicks + scroll > 0:
                app_stats[current_window]["mouse"] += 5
            # For интенсивная работа: (B) — union window
    
    last_ts = ev.ts

