<!-- Часть 29 из 1409 -->
# Просмотр данных (SQL)
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 6. Ежедневная работа / Просмотр данных (SQL)

[◀ Автозапуск клиента (Windows)](028_Avtozapusk_klienta_Windows.md) | [Оглавление](00_BCE_INDEX.md) | [7. Проблемы, которые мы преодолели ▶](030_7_Problemy_kotorye_my_preodoleli.md)

---

### Просмотр данных (SQL)

```powershell
# Количество записей
docker compose exec db psql -U tracker -d tracker -c "SELECT count(*) FROM records;"

# Список ПК
docker compose exec db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at FROM computers;"

# Сессии за сегодня
docker compose exec db psql -U tracker -d tracker -c "SELECT c.hostname, ws.session_start, ws.session_end FROM work_sessions ws JOIN computers c ON c.id = ws.computer_id WHERE ws.session_start >= CURRENT_DATE;"

# Активность за час
docker compose exec db psql -U tracker -d tracker -c "SELECT DATE_TRUNC('hour', client_ts) AS hour, SUM((data::json->>'keys')::int) FROM records WHERE kind='activity' AND client_ts >= NOW() - INTERVAL '24 hours' GROUP BY 1 ORDER BY 1;"
```

---

