<!-- Часть 110 из 1409 -->
# 4.1. Приём данных
*Хлебные крошки:* Техническое задание на разработку системы учёта рабочего времени удалённых сотрудников «Трекер» (расширенная версия) / 4. Серверный модуль / 4.1. Приём данных

[◀ 4. Серверный модуль](109_4_Servernyy_modul.md) | [Оглавление](00_BCE_INDEX.md) | [4.2. Хранение данных ▶](111_4_2_Hranenie_dannyh.md)

---

### 4.1. Приём данных

#### 4.1.1. Эндпоинты API

| Метод | Путь | Описание | Аутентификация |
|-------|------|----------|----------------|
| POST | `/api/sync` | Приём записей от клиента | Bearer JWT |
| GET | `/api/health` | Проверка доступности сервера | Нет |
| POST | `/api/auth/login` | Получение JWT по логину/паролю | Нет |
| POST | `/api/auth/refresh` | Обновление access token | Refresh token |
| GET | `/api/employees` | Список сотрудников | Bearer JWT |
| POST | `/api/employees` | Создание сотрудника | Bearer JWT |
| PUT | `/api/employees/{id}` | Редактирование сотрудника | Bearer JWT |
| DELETE | `/api/employees/{id}` | Удаление сотрудника | Bearer JWT |
| POST | `/api/employees/merge` | Объединение карточек | Bearer JWT |
| GET | `/api/computers` | Список компьютеров | Bearer JWT |
| PUT | `/api/computers/{id}` | Перепривязка компьютера | Bearer JWT |
| GET | `/api/records` | Записи с фильтрами | Bearer JWT |
| PUT | `/api/records/{id}` | Редактирование записи | Bearer JWT |
| DELETE | `/api/records/{id}` | Удаление записи | Bearer JWT |
| POST | `/api/reports/generate` | Генерация отчёта | Bearer JWT |
| GET | `/api/reports/{id}/download` | Скачивание отчёта | Bearer JWT |
| GET | `/api/sync-log` | Журнал синхронизации | Bearer JWT |

#### 4.1.2. Обработка POST /api/sync

```python
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional
import uuid

router = APIRouter()

class EmployeeSchema(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)

class RecordSchema(BaseModel):
    uuid: str = Field(..., description="UUID записи")
    type: str = Field(..., pattern="^(session|program_usage|activity)$")
    # ... остальные поля

class SyncRequest(BaseModel):
    computer_id: str
    employee: EmployeeSchema
    records: list[RecordSchema] = Field(..., max_length=500)

@router.post("/api/sync")
async def sync_data(
    request: SyncRequest,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Валидация токена
    token = authorization.replace("Bearer ", "")
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # 2. Проверка/создание сотрудника и компьютера
    employee = await get_or_create_employee(db, request.employee)
    computer = await get_or_create_computer(db, request.computer_id, employee.id)
    
    # 3. Обработка записей (идемпотентно)
    accepted_uuids = []
    for record in request.records:
        existing = await db.execute(
            select(Record).where(Record.uuid == record.uuid)
        )
        if existing.scalar_one_or_none():
            accepted_uuids.append(record.uuid)  # Уже существует — считаем принятой
            continue
        
        # Сохранение записи
        db_record = Record(
            uuid=record.uuid,
            type=record.type,
            computer_id=request.computer_id,
            employee_id=employee.id,
            data=record.model_dump_json()
        )
        db.add(db_record)
        accepted_uuids.append(record.uuid)
    
    await db.commit()
    
    return {
        "status": "ok",
        "accepted_uuids": accepted_uuids,
        "server_time": datetime.now(timezone.utc).isoformat()
    }
```

#### 4.1.3. Ограничения и защита

- **Максимальный размер запроса:** 10 МБ. При превышении — 413 Payload Too Large.
- **Максимальное количество записей в батче:** 500. При превышении — 422 Unprocessable Entity.
- **Rate limiting:** 100 запросов в минуту на один IP (для предотвращения DoS).
- **Валидация типов:** Pydantic автоматически отклоняет некорректные данные.

