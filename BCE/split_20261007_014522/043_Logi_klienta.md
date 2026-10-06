<!-- Часть 43 из 1409 -->
# Логи клиента
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 9. Диагностика и логи / Логи клиента

[◀ 9. Диагностика и логи](042_9_Diagnostika_i_logi.md) | [Оглавление](00_BCE_INDEX.md) | [Логи сервера ▶](044_Logi_servera.md)

---

### Логи клиента

```powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 50 -Encoding UTF8
```

**Что искать:**
- `Loaded .env from ...` — .env подхватился.
- `Registered as ...` — регистрация прошла.
- `Sync: accepted=N rejected=0` — данные уходят.
- `Registration failed` — ошибка регистрации (с traceback).
- `sync failed` — проблема с сервером.

