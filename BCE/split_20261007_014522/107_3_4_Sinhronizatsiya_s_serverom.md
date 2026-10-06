<!-- Часть 107 из 1409 -->
# 3.4. Синхронизация с сервером
*Хлебные крошки:* Техническое задание на разработку системы учёта рабочего времени удалённых сотрудников «Трекер» (расширенная версия) / 3. Клиентский модуль / 3.4. Синхронизация с сервером

[◀ 3.3. Локальное хранение данных](106_3_3_Lokalnoe_hranenie_dannyh.md) | [Оглавление](00_BCE_INDEX.md) | [3.5. Конфигурация ▶](108_3_5_Konfiguratsiya.md)

---

### 3.4. Синхронизация с сервером

#### 3.4.1. Алгоритм синхронизации

```
1. Проверить наличие интернет-соединения (GET /api/health с таймаутом 5 сек).
2. Если соединение есть:
   a. Выбрать все записи с is_synced = FALSE (батчами по 100 записей).
   b. Сформировать JSON-пакет.
   c. Отправить POST /api/sync с заголовком Authorization: Bearer <token>.
   d. Если ответ 200 OK:
      - Пометить записи из accepted_uuids как is_synced = TRUE, synced_at = NOW().
      - Обновить индикатор синхронизации.
   e. Если ответ 401 Unauthorized:
      - Обновить токен (refresh token).
      - Повторить попытку.
   f. Если ответ 5xx или таймаут:
      - Повторить с экспоненциальной задержкой (1, 2, 4, 8, 16 секунд; максимум 5 попыток).
3. Если соединения нет:
   - Ничего не делать. Повторить через 5 минут.
```

#### 3.4.2. Повторные попытки (Retry Policy)

Использовать библиотеку `tenacity`:

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    reraise=True
)
async def send_batch(batch: list[dict]) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{server_url}/api/sync",
            json={"computer_id": computer_id, "employee": employee, "records": batch},
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
```

**Обоснование:** Экспоненциальная задержка с джиттером предотвращает «забивание» сервера при массовых сбоях.

#### 3.4.3. Батчинг (пакетная отправка)

- **Размер батча:** 100 записей (настраивается).
- **Причина:** Уменьшение количества HTTP-запросов, снижение нагрузки на сервер и сеть.
- **Ограничение:** Общий размер JSON-пакета не должен превышать 1 МБ. При превышении — уменьшать батч.

#### 3.4.4. Идемпотентность

- Каждая запись имеет уникальный `uuid`.
- Сервер при получении записи с существующим `uuid` игнорирует её (не создаёт дубликат).
- Это позволяет безопасно повторять отправку при сбоях.

