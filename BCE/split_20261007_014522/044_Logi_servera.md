<!-- Часть 44 из 1409 -->
# Логи сервера
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 9. Диагностика и логи / Логи сервера

[◀ Логи клиента](043_Logi_klienta.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка БД ▶](045_Proverka_BD.md)

---

### Логи сервера

```powershell
cd D:\tracker
docker compose logs api --tail=50
docker compose logs nginx --tail=50
docker compose logs db --tail=20
```

**Что искать:**
- `Registered uid=...` — регистрация прошла.
- `Ingest: comp=... accepted=N rejected=M` — батч обработан.
- `Bad signature for ...` — HMAC не сошлась.
- `POST /api/v1/computers/register HTTP/1.1" 401` — ошибка регистрации.

