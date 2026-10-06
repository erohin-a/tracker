<!-- Часть 56 из 1409 -->
# Бэкап
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 12. Ограничения и предупреждения / Бэкап

[◀ Производительность](055_Proizvoditelnost.md) | [Оглавление](00_BCE_INDEX.md) | [Контакты и ссылки ▶](057_Kontakty_i_ssylki.md)

---

### Бэкап

```powershell
# Дамп БД
docker compose exec db pg_dump -U tracker tracker > backup_$(Get-Date -Format yyyyMMdd).sql

# Восстановление
Get-Content backup_20260916.sql | docker compose exec -T db psql -U tracker -d tracker
```

---

