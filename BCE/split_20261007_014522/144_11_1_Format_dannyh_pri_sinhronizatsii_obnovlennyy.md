<!-- Часть 144 из 1409 -->
# 11.1. Формат данных при синхронизации (обновлённый)
*Хлебные крошки:* Техническое задание на разработку системы учёта рабочего времени удалённых сотрудников «Трекер» (расширенная версия) / 11. Приложения / 11.1. Формат данных при синхронизации (обновлённый)

[◀ 11. Приложения](143_11_Prilozheniya.md) | [Оглавление](00_BCE_INDEX.md) | [11.2. Схема данных (ER-диаграмма, обновлённая) ▶](145_11_2_Shema_dannyh_ER_diagramma_obnovlennaya.md)

---

### 11.1. Формат данных при синхронизации (обновлённый)

**Запрос клиента:**

```json
{
  "computer_id": "550e8400-e29b-41d4-a716-446655440000",
  "employee": {
    "last_name": "Иванов",
    "first_name": "Иван",
    "middle_name": "Иванович"
  },
  "records": [
    {
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "type": "session",
      "session_start": "2026-09-15T09:00:00+03:00",
      "session_end": "2026-09-15T18:00:00+03:00",
      "pc_boot_time": "2026-09-15T08:55:00+03:00",
      "pc_shutdown_time": null
    },
    {
      "uuid": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "type": "program_usage",
      "session_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "process_name": "pycharm64.exe",
      "window_title": "PyCharm — my_project",
      "usage_seconds": 7200,
      "started_at": "2026-09-15T09:00:00+03:00"
    },
    {
      "uuid": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "type": "activity",
      "session_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "activity_type": "keyboard",
      "active_seconds": 1800,
      "recorded_at": "2026-09-15T09:00:00+03:00"
    }
  ]
}
```

**Ответ сервера:**

```json
{
  "status": "ok",
  "accepted_uuids": [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "c3d4e5f6-a7b8-9012-cdef-123456789012"
  ],
  "rejected_uuids": [],
  "server_time": "2026-09-15T12:00:00+03:00"
}
```

