<!-- Часть 49 из 1409 -->
# Ротация `ADMIN_API_KEY`
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 11. Безопасность и ротация секретов / Ротация `ADMIN_API_KEY`

[◀ Что где хранится](048_Chto_gde_hranitsya.md) | [Оглавление](00_BCE_INDEX.md) | [Ротация `SECRET_ENCRYPTION_KEY` ▶](050_Rotatsiya_SECRET_ENCRYPTION_KEY.md)

---

### Ротация `ADMIN_API_KEY`

```powershell
# 1. Остановить
cd D:\tracker
docker compose down

# 2. Новый ключ
python -c "import secrets; print(secrets.token_urlsafe(48))"

# 3. Заменить в .env через notepad
notepad .env

# 4. Запустить
docker compose up -d
docker compose exec api printenv ADMIN_API_KEY
```

