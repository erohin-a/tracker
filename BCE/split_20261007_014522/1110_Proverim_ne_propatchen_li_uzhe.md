<!-- Часть 1110 из 1409 -->
# Проверим, не пропатчен ли уже
*Хлебные крошки:* Проверим, не пропатчен ли уже

[◀ At the end — close last window at last event](1109_At_the_end_close_last_window_at_last_event.md) | [Оглавление](00_BCE_INDEX.md) | [Найдём начало и конец функции _analyze_session ▶](1111_Naydem_nachalo_i_konets_funktsii_analyze_session.md)

---

# Проверим, не пропатчен ли уже
if "intensive_seconds" in content:
    print("SKIP: _analyze_session уже пропатчен (intensive_seconds есть)")
    raise SystemExit(0)

