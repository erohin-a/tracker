<!-- Часть 35 из 1409 -->
# 8.4. Heartbeat
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 8. Что не реализовано / 8.4. Heartbeat

[◀ 8.3. Отчёты и экспорт](034_8_3_Otchety_i_eksport.md) | [Оглавление](00_BCE_INDEX.md) | [8.5. Ротация `client_secret` ▶](036_8_5_Rotatsiya_client_secret.md)

---

### 8.4. Heartbeat

Клиент обновляет `last_seen_at` при каждом `ingest`. Отдельного heartbeat-эндпоинта нет.

