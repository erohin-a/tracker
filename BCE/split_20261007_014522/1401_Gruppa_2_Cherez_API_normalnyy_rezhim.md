<!-- Часть 1401 из 1409 -->
# Группа 2. Через API (нормальный режим)
*Хлебные крошки:* ============================================================ / Группа 2. Через API (нормальный режим)

[◀ Группа 1. Напрямую (аварийный режим)](1400_Gruppa_1_Napryamuyu_avariynyy_rezhim.md) | [Оглавление](00_BCE_INDEX.md) | [Группа 3. Опционально (если решим расширять) ▶](1402_Gruppa_3_Optsionalno_esli_reshim_rasshiryat.md)

---

## Группа 2. Через API (нормальный режим)

| Действие | Эндпоинт |
|---|---|
| Выпуск bootstrap-токена | `POST /api/v1/admin/bootstrap-tokens` (заголовок `x-admin-token`) |
| Выпуск re-registration-токена | `POST /api/v1/admin/computers/{uid}/re-registration-token` |
| Список ПК для выбора | чтение БД напрямую либо через admin API |
| Диагностика api | `GET /api/v1/version` |
| Диагностика БД | `SELECT count(*) FROM task_runs WHERE status='failed' AND started_at > now() - interval '24 hours'` |
| Диагностика контейнеров | `docker compose ps` → парсинг, статус в UI |

