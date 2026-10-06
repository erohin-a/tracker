<!-- Часть 1041 из 1409 -->
# В _analyze_session после цикла:
*Хлебные крошки:* В _analyze_session после цикла:

[◀ ============================================================](1040_part.md) | [Оглавление](00_BCE_INDEX.md) | [Вычитаем время паузы (если есть) ▶](1042_Vychitaem_vremya_pauzy_esli_est.md)

---

# В _analyze_session после цикла:
if first_event_local and last_event_local:
    effective_duration = max(0, int((last_event_local - first_event_local).total_seconds()))
    activity_start_local = first_event_local
    activity_end_local = last_event_local
else:
    effective_duration = 0
    activity_start_local = start_local
    activity_end_local = end_local  # fallback

