<!-- Часть 1042 из 1409 -->
# Вычитаем время паузы (если есть)
*Хлебные крошки:* Вычитаем время паузы (если есть)

[◀ В _analyze_session после цикла:](1041_V_analyze_session_posle_tsikla.md) | [Оглавление](00_BCE_INDEX.md) | [full_duration = от первой до последней РЕАЛЬНОЙ активности ▶](1043_full_duration_ot_pervoy_do_posledney_REALNOY_aktivnosti.md)

---

# Вычитаем время паузы (если есть)
pause_sec = int(getattr(ws, "pause_seconds", 0) or 0)
if pause_sec > 0:
    effective_duration = max(0, effective_duration - pause_sec)

