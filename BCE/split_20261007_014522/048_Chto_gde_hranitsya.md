<!-- Часть 48 из 1409 -->
# Что где хранится
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 11. Безопасность и ротация секретов / Что где хранится

[◀ 11. Безопасность и ротация секретов](047_11_Bezopasnost_i_rotatsiya_sekretov.md) | [Оглавление](00_BCE_INDEX.md) | [Ротация `ADMIN_API_KEY` ▶](049_Rotatsiya_ADMIN_API_KEY.md)

---

### Что где хранится

| Секрет | Где | Кто использует |
|---|---|---|
| `SECRET_ENCRYPTION_KEY` | `.env` в корне | `client_secret_enc` в БД |
| `JWT_SECRET` | `.env` | резерв (не используется) |
| `ADMIN_API_KEY` | `.env` | эндпоинты `/api/v1/admin/*` |
| `client_secret` | keyring на ПК | HMAC-подпись записей |
| TLS-приватный ключ | `certs/privkey.pem` | nginx |

