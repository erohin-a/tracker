<!-- Часть 1232 из 1409 -->
# 11. Известные проблемы и решения
*Хлебные крошки:* Трекер — учёт рабочего времени. Handoff-документ / 11. Известные проблемы и решения

[◀ 10. Что не доделано](1231_10_Chto_ne_dodelano.md) | [Оглавление](00_BCE_INDEX.md) | [12. Стиль работы в проекте ▶](1233_12_Stil_raboty_v_proekte.md)

---

## 11. Известные проблемы и решения

| Проблема | Решение |
|---|---|
| `getaddrinfo failed` в Python | Использовать `https://127.0.0.1` вместо `localhost` (IPv6 vs IPv4) |
| `.env` читается не тот | Клиент ищет сначала `client/.env`, потом `%APPDATA%/Tracker/.env` |
| `create_all` не мигрирует | Alembic с `include_object` (исключает партиции) |
| Алерт `500` на batch | Дубликаты record_uid от разных ПК — ищем по всей таблице |
| `409` на sessions | Сессия принадлежит другому ПК — возвращаем 200 |
| PDF с крокозябрами | DejaVuSans.ttf в `server/fonts/` |
| `NameError: WorkSession` в tasks.py | Добавить в импорт внутри функции |
| `audit_log.entity_id` переполнялся | Кладём только первый UUID, всё в new_value |
| PowerShell here-string >30 строк | Использовать Python-патчеры |
| Тёмная тема не покрывает панель | Убрать inline-стили, использовать `setObjectName` + QSS |
| `pause_seconds > total_sec` | Обрезка в `close_stale_sessions`, не вычитать дважды |

---

