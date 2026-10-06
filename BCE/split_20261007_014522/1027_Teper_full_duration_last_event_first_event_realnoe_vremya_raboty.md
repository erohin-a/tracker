<!-- Часть 1027 из 1409 -->
# Теперь: full_duration = last_event - first_event (реальное время работы)
*Хлебные крошки:* Теперь: full_duration = last_event - first_event (реальное время работы)

[◀ Раньше: full_duration = session_end - session_start](1026_Ranshe_full_duration_session_end_session_start.md) | [Оглавление](00_BCE_INDEX.md) | [effective_duration всё ещё first-last минус паузы... ▶](1028_effective_duration_vse_esche_first_last_minus_pauzy.md)

---

# Теперь: full_duration = last_event - first_event (реальное время работы)
if first_event_local and last_event_local:
    full_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
else:
    full_duration = 0

