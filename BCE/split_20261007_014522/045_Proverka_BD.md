<!-- Часть 45 из 1409 -->
# Проверка БД
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 9. Диагностика и логи / Проверка БД

[◀ Логи сервера](044_Logi_servera.md) | [Оглавление](00_BCE_INDEX.md) | [10. Что делать при типовых сбоях ▶](046_10_Chto_delat_pri_tipovyh_sboyah.md)

---

### Проверка БД

```powershell
# Все компьютеры
docker compose exec db psql -U tracker -d tracker -c "SELECT id, computer_uid, hostname, last_seen_at FROM computers;"

# Все сессии
docker compose exec db psql -U tracker -d tracker -c "SELECT * FROM work_sessions ORDER BY id DESC LIMIT 10;"

# Bootstrap-токены
docker compose exec db psql -U tracker -d tracker -c "SELECT id, LEFT(token_hash,12), expires_at, used_at FROM bootstrap_tokens ORDER BY id DESC LIMIT 10;"

# Аудит
docker compose exec db psql -U tracker -d tracker -c "SELECT created_at, actor, action, entity FROM audit_log ORDER BY id DESC LIMIT 20;"
```

---

