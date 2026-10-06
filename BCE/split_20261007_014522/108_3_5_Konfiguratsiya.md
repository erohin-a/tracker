<!-- Часть 108 из 1409 -->
# 3.5. Конфигурация
*Хлебные крошки:* Техническое задание на разработку системы учёта рабочего времени удалённых сотрудников «Трекер» (расширенная версия) / 3. Клиентский модуль / 3.5. Конфигурация

[◀ 3.4. Синхронизация с сервером](107_3_4_Sinhronizatsiya_s_serverom.md) | [Оглавление](00_BCE_INDEX.md) | [4. Серверный модуль ▶](109_4_Servernyy_modul.md)

---

### 3.5. Конфигурация

Файл `config.json` в директории пользователя:

```json
{
  "server_url": "https://server.company.ru/api",
  "auth_token": "",
  "refresh_token": "",
  "sync_interval_minutes": 5,
  "poll_interval_seconds": 5,
  "inactivity_timeout_seconds": 60,
  "batch_size": 100,
  "log_level": "INFO",
  "employee": {
    "last_name": "",
    "first_name": "",
    "middle_name": ""
  },
  "computer_id": "550e8400-e29b-41d4-a716-446655440000",
  "autostart_enabled": false,
  "tray_enabled": true
}
```

**Валидация конфигурации при запуске:**
- `server_url` должен быть валидным URL.
- `sync_interval_minutes` ? 1.
- `poll_interval_seconds` ? 1.
- `inactivity_timeout_seconds` ? 10.
- При отсутствии `computer_id` — сгенерировать и сохранить.

---

