<!-- Часть 50 из 1409 -->
# Ротация `SECRET_ENCRYPTION_KEY`
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 11. Безопасность и ротация секретов / Ротация `SECRET_ENCRYPTION_KEY`

[◀ Ротация `ADMIN_API_KEY`](049_Rotatsiya_ADMIN_API_KEY.md) | [Оглавление](00_BCE_INDEX.md) | [Что делать если `client_secret` утёк ▶](051_Chto_delat_esli_client_secret_utek.md)

---

### Ротация `SECRET_ENCRYPTION_KEY`

**Внимание:** при смене этого ключа старые `client_secret` перестанут расшифровываться, и все клиенты получат `bad_signature`. **Придётся перерегистрировать все ПК.**

Правильный путь:
```powershell
docker compose down -v   # обнуляет БД
# Сменить ключ в .env
docker compose up -d --build
# Перерегистрировать все ПК
```

