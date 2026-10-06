<!-- Часть 51 из 1409 -->
# Что делать если `client_secret` утёк
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 11. Безопасность и ротация секретов / Что делать если `client_secret` утёк

[◀ Ротация `SECRET_ENCRYPTION_KEY`](050_Rotatsiya_SECRET_ENCRYPTION_KEY.md) | [Оглавление](00_BCE_INDEX.md) | [12. Ограничения и предупреждения ▶](052_12_Ogranicheniya_i_preduprezhdeniya.md)

---

### Что делать если `client_secret` утёк

1. На сервере: `POST /api/v1/admin/computers/{uid}/revoke` с `X-Admin-Token`.
2. На ПК: удалить `%APPDATA%\Tracker\credentials.enc` и keyring-запись.
3. Выпустить новый bootstrap-токен, запустить клиент заново.

---

