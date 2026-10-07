# 4. Серверный модуль

*Часть 5 из 100. Источник: `BCE.md`.*

[◀ ?? Сертификаты `D:\tracker\certs\`](004_Sertifikaty_D_tracker_certs.md) | [Оглавление](00_BCE_INDEX.md) | [12. Заключение ▶](006_12_Zaklyuchenie.md)

---

## 4. Серверный модуль

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

### 4.2. Хранение данных

#### 4.2.1. Схема базы данных (обновлённая)

**Таблица `employees`:**

```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    "1c_id" TEXT UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `computers`:**

```sql
CREATE TABLE computers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    computer_id TEXT UNIQUE NOT NULL,
    employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    machine_name TEXT,
    mac_address TEXT,
    os_info TEXT,
    last_seen_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `work_sessions`:**

```sql
CREATE TABLE work_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    employee_id INTEGER REFERENCES employees(id),
    computer_id TEXT REFERENCES computers(computer_id),
    session_start TIMESTAMP NOT NULL,
    session_end TIMESTAMP,
    pc_boot_time TIMESTAMP,
    pc_shutdown_time TIMESTAMP,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_by TEXT,
    edited_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `program_usage`:**

```sql
CREATE TABLE program_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    session_id INTEGER REFERENCES work_sessions(id) ON DELETE CASCADE,
    process_name TEXT NOT NULL,
    window_title TEXT,
    usage_seconds INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `activity_log`:**

```sql
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    session_id INTEGER REFERENCES work_sessions(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('keyboard', 'mouse')),
    active_seconds INTEGER NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Таблица `sync_log`:**

```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    computer_id TEXT NOT NULL,
    employee_id INTEGER REFERENCES employees(id),
    records_count INTEGER NOT NULL,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT
);
```

**Таблица `audit_log`:**

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.2. Миграции

- Использовать **Alembic** для управления миграциями схемы.
- Все изменения схемы — только через миграции.
- При развёртывании: `alembic upgrade head`.

### 4.3. Объединение записей сотрудника

#### 4.3.1. Логика объединения карточек

При объединении двух карточек сотрудников (A ? B):

1. Все записи из `computers`, где `employee_id = A.id`, обновляются на `employee_id = B.id`.
2. Все записи из `work_sessions`, где `employee_id = A.id`, обновляются на `employee_id = B.id`.
3. Запись A помечается как `is_active = FALSE` и `merged_into = B.id`.
4. Создаётся запись в `audit_log`.

**Важно:** Объединение не должно терять данные. Все связанные записи (`program_usage`, `activity_log`) остаются привязанными к сессиям.

#### 4.3.2. Перепривязка компьютера

- При смене `employee_id` для компьютера все **новые** сессии будут привязаны к новому сотруднику.
- **Исторические данные** остаются привязанными к старому сотруднику.
- **Опция:** При перепривязке оператор может выбрать «Перенести все исторические данные» (тогда `employee_id` в `work_sessions` также обновляется).

### 4.4. Редактирование данных

| Операция | Описание | Ограничения |
|---------|----------|-------------|
| Редактирование ФИО | Изменение `last_name`, `first_name`, `middle_name` | Валидация символов |
| Объединение карточек | Слияние двух сотрудников | Необратимо; требует подтверждения |
| Перепривязка компьютера | Смена `employee_id` для `computer_id` | Опция переноса истории |
| Редактирование времени сеанса | Исправление `session_start` / `session_end` | `session_end` > `session_start` |
| Удаление записей | Удаление `program_usage` / `activity_log` | Каскадное удаление по `session_id` |
| Привязка к 1С | Заполнение `1c_id` | Уникальность `1c_id` |
| Удаление сотрудника | `is_active = FALSE` (мягкое удаление) | Каскадное удаление данных — по выбору |

**Все операции редактирования должны логироваться в `audit_log`.**

### 4.5. Формирование отчётов

#### 4.5.1. Параметры отчёта

| Параметр | Варианты | Обязательность |
|---------|----------|---------------|
| Сотрудник | Один / несколько / все | Да |
| Период | Дата начала — дата окончания | Да |
| Тип данных | По программам / по клавиатуре / по мыши / сводный | Да |
| Формат | Просмотр / TXT / PDF / XLS | Да |
| Группировка | По дням / по сотрудникам / по компьютерам | Нет (по умолчанию — по дням) |

#### 4.5.2. Виды отчётов

**Отчёт по программам:**
- Сотрудник, компьютер, дата.
- Список программ (по `process_name`) и суммарное время работы в каждой (секунды / ЧЧ:ММ:СС).
- Общее время работы за период.
- Топ-5 программ по времени.

**Отчёт по работе на клавиатуре:**
- Сотрудник, компьютер, дата.
- Время активной работы на клавиатуре (секунды / ЧЧ:ММ:СС).
- Общее время активной работы за период.

**Отчёт по работе на мыши:**
- Аналогично отчёту по клавиатуре.

**Сводный отчёт:**
- Сотрудник, компьютер, дата.
- Общее время сеанса.
- Время работы в программах (топ-5).
- Время работы на клавиатуре.
- Время работы на мыши.
- **Коэффициент активности:** `(keyboard_seconds + mouse_seconds) / 2 / session_duration`. Значения > 1.0 обрезаются до 1.0.

#### 4.5.3. Форматы экспорта

| Формат | Библиотека | Особенности |
|--------|-----------|-------------|
| TXT | Встроенный `open()` | Моноширинное выравнивание, разделители |
| PDF | `reportlab` | Кириллица (шрифт DejaVu Sans), таблицы, заголовки, итоги |
| XLS | `openpyxl` | Форматирование, фильтры, итоговые строки, автоширина |

**Требование:** Все отчёты должны корректно отображать кириллицу. Для PDF — использовать встроенный шрифт `DejaVuSans.ttf` или зарегистрировать системный шрифт.

### 4.6. Серверный интерфейс (веб)

#### 4.6.1. Технология

- **Backend:** FastAPI + Jinja2 (шаблоны).
- **Frontend:** Bootstrap 5 + минимальный JavaScript (без React/Vue, если не требуется).
- **Аутентификация:** Сессионная (cookie) для веб-интерфейса; JWT для API.

#### 4.6.2. Разделы

1. **Сотрудники:**
   - Список карточек с поиском и фильтрацией.
   - Добавление / редактирование / объединение.
   - Привязка к 1С.
   - Мягкое удаление.

2. **Компьютеры:**
   - Список зарегистрированных компьютеров.
   - Информация: `computer_id`, `machine_name`, MAC, ОС, последняя активность.
   - Перепривязка к сотрудникам.

3. **Данные:**
   - Таблица всех принятых записей с фильтрами:
     - По сотруднику.
     - По дате.
     - По типу записи.
     - По компьютеру.
   - Редактирование и удаление.

4. **Отчёты:**
   - Форма параметров отчёта.
   - Предпросмотр в браузере.
   - Кнопки экспорта (TXT, PDF, XLS).

5. **Журнал синхронизации:**
   - История подключений клиентских модулей:
     - Когда.
     - С какого `computer_id`.
     - Сколько записей передано.
     - IP-адрес.

6. **Аудит:**
   - Журнал всех действий операторов.
   - Фильтрация по дате, пользователю, типу действия.

---

## 5. Безопасность

### 5.1. Передача данных

- **HTTPS:** Обязательное использование TLS 1.2+.
- **Сертификат:** Let's Encrypt или корпоративный сертификат.
- **HSTS:** Заголовок `Strict-Transport-Security: max-age=31536000`.

### 5.2. Аутентификация и авторизация

- **Клиент ? Сервер:** JWT (access token) в заголовке `Authorization: Bearer <token>`.
  - Access token: срок жизни 1 час.
  - Refresh token: срок жизни 30 дней.
  - При истечении access token — автоматическое обновление через refresh token.
- **Веб-интерфейс:** Сессионная аутентификация (cookie с `HttpOnly`, `Secure`, `SameSite=Strict`).
- **Роли:**
  - `admin` — полный доступ.
  - `operator` — доступ к данным и отчётам, без управления пользователями.
  - `viewer` — только просмотр отчётов.

### 5.3. Защита персональных данных (152-ФЗ)

**Критически важно:** Система собирает и обрабатывает персональные данные сотрудников (ФИО, данные об активности). Это требует соблюдения Федерального закона № 152-ФЗ «О персональных данных».

**Меры:**
1. **Согласие сотрудника:** Работодатель обязан получить письменное согласие сотрудника на обработку персональных данных.
2. **Уведомление Роскомнадзора:** Работодатель должен уведомить Роскомнадзор об обработке персональных данных (если ещё не уведомлён).
3. **Цель обработки:** Данные собираются исключительно для учёта рабочего времени. Не допускается использование данных в иных целях.
4. **Минимизация данных:** Собираются только данные, необходимые для учёта рабочего времени. Содержимое нажатий клавиш **не записывается**.
5. **Хранение:** Данные хранятся на сервере компании. Доступ — только у авторизованных операторов.
6. **Уничтожение:** По истечении срока хранения (определяется внутренним регламентом) данные уничтожаются.
7. **Уведомление сотрудников:** Сотрудники должны быть уведомлены о том, что за их активностью ведётся наблюдение. Рекомендуется включить пункт в трудовой договор или ознакомить под подпись.

**Рекомендация:** Проконсультироваться с юристом перед внедрением системы.

### 5.4. Защита локальной базы данных

- **Права файловой системы:** `chmod 600` (Linux), права текущего пользователя (Windows).
- **Опционально:** Шифрование базы через SQLCipher или `apsw-sqlite3mc`. **Минус:** Усложняет сборку и может замедлить работу. **Рекомендация:** Использовать, если политика безопасности компании требует.

### 5.5. Защита серверной базы данных

- **PostgreSQL:** Аутентификация по паролю, SSL-соединение, ограничение доступа по IP.
- **SQLite:** Права файловой системы, регулярное резервное копирование.
- **Резервное копирование:** Ежедневно, с хранением за последние 30 дней. Автоматизация через `cron` или APScheduler.

---

## 6. Нефункциональные требования

| Параметр | Требование |
|---------|------------|
| Нагрузка (клиент) | До 50 сотрудников на один сервер |
| Период опроса активного окна | 5 секунд (настраивается) |
| Период синхронизации | 5 минут (настраивается) |
| Объём локальной базы | ~1–2 МБ на рабочий день одного сотрудника |
| Время запуска клиента | < 3 секунд |
| Время отклика API | < 200 мс (при нагрузке до 50 клиентов) |
| Доступность сервера | 99% в рабочее время |
| Резервное копирование | Раз в сутки, хранение 30 дней |
| Логирование | Уровень INFO по умолчанию; DEBUG — по требованию |
| Размер дистрибутива клиента | < 80 МБ (с PyInstaller) |

---

## 7. Проблемы и решения (расширенный анализ)

### 7.1. Проблемы с `pynput` и их решения

| Проблема | Решение |
|---------|---------|
| Требуются права root на Linux для `uinput` | Создать udev-правило: `SUBSYSTEM=="input", GROUP="input", MODE="0660"`. Добавить пользователя в группу `input`. |
| Wayland блокирует доступ к клавиатуре | Предупредить пользователя. Рекомендовать X11. Альтернатива: использовать `evdev` (требует прав). |
| macOS требует разрешений | Документировать в инструкции по установке. (macOS не является целевой ОС.) |
| Конфликт с другими приложениями, использующими хуки | Не использовать `suppress_event`; только мониторинг. |
| Высокое потребление CPU при частых событиях | Агрегировать события: считать не каждое событие, а количество событий за интервал (например, 5 секунд). |
| PyInstaller не включает `pynput` в сборку | Добавить `--hidden-import=pynput.keyboard._win32 --hidden-import=pynput.mouse._win32` (Windows) или `--hidden-import=pynput.keyboard._xorg` (Linux). |

### 7.2. Проблемы с PyInstaller и антивирусами

**Проблема:** Скомпилированные `.exe` часто помечаются антивирусами как подозрительные из-за:
- Использования UPX-сжатия.
- Отсутствия цифровой подписи.
- Эвристического анализа поведения (распаковка во временную папку).

**Решения:**
1. **Отключить UPX:** `upx=False` в `.spec`-файле. Это самое эффективное средство.
2. **Добавить метаданные PE:** Указать `company_name`, `product_name`, `file_description`, `legal_copyright` в `.spec`.
3. **Подписать `.exe`:** Использовать сертификат код-подписи (Code Signing Certificate). Это значительно снижает ложные срабатывания.
4. **Добавить в исключения Windows Defender:** Инструкция для пользователя: «Windows Security ? Virus & threat protection ? Manage settings ? Add or remove exclusions ? Add folder ? `%APPDATA%\Tracker`».
5. **Отправить в Microsoft:** Если файл всё ещё помечается, отправить его на анализ в Microsoft Defender.
6. **Использовать `--onedir` вместо `--onefile`:** `--onedir` создаёт папку с файлами, что меньше похоже на «самораспаковывающийся» архив и реже вызывает ложные срабатывания.

### 7.3. Проблемы с многопоточностью в GUI

**Проблема:** GIL в Python ограничивает параллельное выполнение потоков. GUI должен работать в главном потоке. Фоновые задачи (сбор данных, синхронизация) должны работать в отдельных потоках, но не блокировать GUI.

**Решение:**
- **PyQt6:** Использовать `QThread` + сигналы/слоты для взаимодействия с GUI. Все операции ввода-вывода — в фоновых потоках.
- **Tkinter:** Использовать `threading.Thread` для фоновых задач. Для обновления GUI из фонового потока использовать `root.after(0, callback)`.
- **Синхронизация:** Использовать `queue.Queue` для передачи данных между потоками.

### 7.4. Проблемы с SQLite и конкурентным доступом

**Проблема:** Одновременная запись из потока сбора данных и чтение из потока синхронизации может привести к блокировке.

**Решение:**
- Включить WAL-режим.
- Использовать отдельные соединения для каждого потока (SQLite не потокобезопасен при совместном использовании одного соединения).
- Установить `busy_timeout` = 5000 мс.
- Использовать `aiosqlite` для асинхронного доступа на сервере.

### 7.5. Проблемы с определением активного окна

**Проблема:** `pygetwindow.getActiveWindow().title` может возвращать пустую строку или заголовок, который часто меняется.

**Решение:** Использовать `win32gui` + `win32process` + `psutil` для получения имени процесса. Имя процесса (`process_name`) — стабильный идентификатор. Заголовок окна — дополнительный контекст.

### 7.6. Проблемы с автозапуском

**Проблема:** На Windows запись в реестр может быть заблокирована антивирусом или политиками безопасности.

**Решение:**
- Использовать `HKEY_CURRENT_USER` (не требует прав администратора).
- Предусмотреть альтернативу: ярлык в папке «Автозагрузка» (`shell:startup`).
- При отказе — показать сообщение об ошибке с инструкцией.

### 7.7. Проблемы с сетевыми запросами

**Проблема:** Сервер может быть недоступен, сеть может быть нестабильной.

**Решение:**
- Использовать `tenacity` для повторных попыток с экспоненциальной задержкой.
- Устанавливать таймауты (connect: 5 сек, read: 30 сек).
- Кэшировать данные локально и отправлять при первой возможности.
- Использовать `httpx` с `http2=True` для эффективности.

---

## 8. Тестирование

### 8.1. Модульное тестирование

- **Клиент:**
  - Тесты сбора данных (моки `pynput`, `win32gui`).
  - Тесты валидации конфигурации.
  - Тесты сериализации записей.
- **Сервер:**
  - Тесты API (pytest + httpx).
  - Тесты валидации Pydantic.
  - Тесты идемпотентности синхронизации.

### 8.2. Интеграционное тестирование

- Полный цикл: клиент ? синхронизация ? сервер ? база данных ? отчёт.
- Тестирование при разрыве соединения (эмуляция отключения сети).
- Тестирование при переполнении базы.

### 8.3. Нагрузочное тестирование

- Эмуляция 50 клиентов, одновременно отправляющих данные.
- Проверка времени отклика API.
- Проверка стабильности под нагрузкой.

### 8.4. Тестирование на целевых ОС

- Windows 10, Windows 11.
- Linux (Ubuntu 22.04, X11).
- Linux (Ubuntu 22.04, Wayland) — с ограничениями.

### 8.5. Тестирование антивирусами

- Проверить `.exe` на VirusTotal.
- Проверить на Windows Defender, Avast, Kaspersky.

---

## 9. Развёртывание и сопровождение

### 9.1. Развёртывание сервера

- **Docker:** Рекомендуется использовать Docker Compose для развёртывания (FastAPI + PostgreSQL + Nginx).
- **Nginx:** Обратный прокси с TLS-терминацией.
- **Gunicorn + Uvicorn Workers:** Для production-развёртывания FastAPI.
- **Миграции:** `alembic upgrade head` при старте контейнера.

### 9.2. Развёртывание клиента

- **Дистрибутив:** `.exe` (Windows) или бинарник + `.desktop` (Linux).
- **Установка:** Рекомендуется использовать Inno Setup (Windows) или `.deb`/`.rpm` пакеты (Linux).
- **Обновление:** Механизм автообновления через проверку версии на сервере (`GET /api/version`).

### 9.3. Мониторинг

- **Сервер:** Prometheus + Grafana для метрик (запросы/сек, время отклика, ошибки).
- **Клиент:** Отправка «heartbeat» на сервер каждые 5 минут (опционально).
- **Логи:** Централизованный сбор логов через `loguru` ? файл ? отправка на сервер (опционально).

### 9.4. Обновление и миграция данных

- При обновлении схемы БД — обязательные миграции Alembic.
- При обновлении клиента — обратная совместимость API.
- Версионирование API: `/api/v1/sync`, `/api/v2/sync`.

---

## 10. План разработки (уточнённый)

| Этап | Содержание | Результат | Оценка |
|------|-----------|----------|--------|
| 1 | Клиент: каркас GUI, профиль сотрудника, кнопки управления | Рабочий интерфейс | 1 неделя |
| 2 | Клиент: сбор данных (активное окно, клавиатура, мышь) | Накопление данных в локальную SQLite | 2 недели |
| 3 | Клиент: синхронизация с сервером, индикатор статуса | Отправка данных по HTTP | 1 неделя |
| 4 | Сервер: приём данных, хранение, модель данных | REST API + база данных | 2 недели |
| 5 | Сервер: интерфейс сотрудников и компьютеров, объединение | Веб-интерфейс редактирования | 2 недели |
| 6 | Сервер: отчёты, экспорт TXT/PDF/XLS | Готовые отчёты | 1.5 недели |
| 7 | Тестирование, упаковка (PyInstaller), документация | Дистрибутив | 1.5 недели |
| **Итого** | | | **11 недель** |

---

## 11. Приложения

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

### 11.2. Схема данных (ER-диаграмма, обновлённая)

```
employees (1) ???????< (N) computers
    ?                      ?
    ? (1)                  ? (1)
    ?                      ?
    ???< (N) work_sessions >???
              ?
              ? (1)
              ?
    ??????????????????????
    ?                    ?
    ? (N)                ? (N)
    ?                    ?
program_usage      activity_log

sync_log >??? computers
audit_log
```

### 11.3. Рекомендуемые библиотеки (полный список)

| Библиотека | Версия | Назначение |
|-----------|--------|-----------|
| fastapi | ?0.100 | Серверный фреймворк |
| uvicorn | ?0.23 | ASGI-сервер |
| sqlalchemy | ?2.0 | ORM |
| aiosqlite | ?0.19 | Асинхронный драйвер SQLite |
| asyncpg | ?0.29 | Асинхронный драйвер PostgreSQL |
| alembic | ?1.12 | Миграции |
| pydantic | ?2.0 | Валидация |
| pynput | ?1.7 | Сбор данных клавиатуры/мыши |
| pygetwindow | ?0.0.9 | Активное окно (Windows) |
| psutil | ?5.9 | Системная информация |
| pywin32 | ?306 | Win32 API (Windows) |
| httpx | ?0.25 | HTTP-клиент |
| tenacity | ?8.2 | Повторные попытки |
| loguru | ?0.7 | Логирование |
| reportlab | ?4.0 | PDF-экспорт |
| openpyxl | ?3.1 | XLS-экспорт |
| jinja2 | ?3.1 | Шаблоны |
| python-jose | ?3.3 | JWT |
| passlib | ?1.7 | Хеширование паролей |
| PyQt6 | ?6.5 | GUI (рекомендуемый) |
| pystray | ?0.19 | Системный трей (Tkinter) |
| Pillow | ?10.0 | Изображения |
| APScheduler | ?3.10 | Периодические задачи |
| pyinstaller | ?6.0 | Сборка дистрибутива |
| pytest | ?7.4 | Тестирование |
| pytest-asyncio | ?0.21 | Асинхронные тесты |

---

