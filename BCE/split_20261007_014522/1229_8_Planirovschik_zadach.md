<!-- Часть 1229 из 1409 -->
# 8. Планировщик задач
*Хлебные крошки:* Трекер — учёт рабочего времени. Handoff-документ / 8. Планировщик задач

[◀ 7. Роли пользователей](1228_7_Roli_polzovateley.md) | [Оглавление](00_BCE_INDEX.md) | [9. Что работает ▶](1230_9_Chto_rabotaet.md)

---

## 8. Планировщик задач

Реализован через APScheduler + advisory lock (только один воркер запускает задачи).

**Активные задачи:**
- `create_future_partitions` — cron `0 4 1 * *` — создаёт партиции `records_YYYY_MM` на 12 месяцев вперёд
- `aggregate_daily_stats` — cron `0 1 * * *` — агрегирует daily_stats
- `close_stale_sessions` — cron `*/30 * * * *` — закрывает сессии без `session_end` > `stale_session_hours` (по умолчанию 2ч)

**Отключены по умолчанию:**
- `cleanup_trash`, `vacuum_analyze_hot_tables`, `cleanup_old_admin_logins`, `cleanup_old_task_runs`

---

