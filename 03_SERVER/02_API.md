# API
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\04_AUTH.md, 03_SERVER\03_MODELS.md

## Назначение
Описать все эндпоинты сервера «Трекер»: клиентские `/api/v1/*`, админские `/api/v1/admin/*`, веб-роуты `/admin/*` и служебные. Это карта для разработчика клиента и админки, а также для интеграций.

## Содержание

### Общие принципы
- Все эндпоинты — под префиксом `/api/v1/` (кроме веб-админки `/admin/`).
- Формат данных — JSON (кроме веб-страниц и файлов).
- Все timestamps — ISO 8601 с таймзоной (`YYYY-MM-DDTHH:MM:SS+00:00`).
- Аутентификация клиента — HMAC-SHA256 + заголовок `X-Computer-Uid`.
- Аутентификация админ API — заголовок `X-Admin-Token`.
- Веб-админка — сессия в cookie `tracker_admin`.
- Идемпотентность по `record_uid`, `session_uid`.

### Клиентские эндпоинты

#### 1. `POST /api/v1/computers/register`
Регистрация нового ПК по bootstrap-токену.

**Запрос:**
```json
{
  "computer_uid": "uuid-v4",
  "hostname": "PC-BUH-01",
  "os_info": "Windows 10 Pro",
  "client_version": "1.0.0",
  "bootstrap_token": "xxxxx"
}
Ответ:

json
{
  "computer_uid": "uuid-v4",
  "client_secret": "yyyyy",
  "secret_version": 1
}
Логика:

Проверка bootstrap-токена (хеш в bootstrap_tokens, TTL, одноразовый).

Генерация client_secret, шифрование Fernet, сохранение в computers.client_secret_enc.

При повторной регистрации — обновление секрета, secret_version++.

Ошибки:

401 — невалидный/истёкший токен.

400 — некорректные данные.

2. POST /api/v1/sessions
Создание/обновление сессии.

Запрос:

json
{
  "session_uid": "uuid-v4",
  "session_start": "2026-10-02T09:00:00+00:00",
  "session_end": null,
  "abnormal_termination": false,
  "client_version": "1.0.0"
}
Ответ: {"status": "ok"}

Логика:

Идемпотентность по session_uid.

Если сессия принадлежит другому ПК — возвращаем 200 OK (не воюем).

Предохранитель: сессии > 24 ч обрезаются с записью в audit_log.

Ошибки:

400 — некорректный session_start.

401 — невалидная HMAC-подпись.

3. POST /api/v1/records/batch
Отправка пачки записей.

Запрос:

json
{
  "records": [
    {
      "record_uid": "uuid-v4",
      "session_uid": "uuid-v4",
      "kind": "activity",
      "data": {"keys": 5, "clicks": 3, "scroll": 1},
      "client_ts": "2026-10-02T09:05:00+00:00",
      "signature": "hmac-sha256-hex"
    }
  ],
  "batch_signature": "hmac-sha256-hex"
}
Ответ:

json
{
  "accepted_uuids": ["uuid-1", "uuid-2"],
  "rejected_uuids": ["uuid-3"],
  "reasons": {"uuid-3": "duplicate"},
  "server_signature": "hmac-sha256-hex"
}
Логика:

Проверка HMAC каждой записи и батча.

Идемпотентность по record_uid (по всей таблице, не только по ПК).

Защита от IntegrityError (дубликаты).

Сохранение в records (партиционирована по client_ts).

До 500 записей в батче.

Ошибки:

400 — некорректный формат.

401 — bad_signature.

500 — ошибка вставки (обрабатывается).

4. POST /api/v1/heartbeat
«Я жив» — обновление last_seen_at.

Запрос: {}

Ответ: {"status": "ok"}

Логика: обновляет computers.last_seen_at = now().

5. GET /api/v1/client-config
Эффективные настройки для ПК.

Ответ:

json
{
  "reminder_enabled": true,
  "reminder_threshold_minutes": 15,
  "reminder_repeat_minutes": 10,
  "reminder_max_per_day": 5,
  "end_of_day_hour": 19,
  "end_of_day_minute": 0,
  "source_reminder": "global",
  "source_end_of_day": "global"
}
Логика:

Мерж глобальных (AppSetting) и персональных (employee_settings).

Персональные перекрывают глобальные.

6. PUT /api/v1/client-settings
Приём изменений от клиента.

Запрос: те же поля, что в client-config.

Логика: server wins, при конфликте — глобальные значения.

7. DELETE /api/v1/client-settings
Сброс к глобальным.

Логика: удаление записи employee_settings.

8. GET /api/v1/version
Версия клиента для автообновления.

Ответ:

json
{
  "latest_version": "1.0.0",
  "download_url": "https://.../TrackerSetup.exe",
  "mandatory": false,
  "release_notes": "..."
}
Админские эндпоинты (/api/v1/admin/*)
Метод	Путь	Назначение
POST	/api/v1/admin/bootstrap-tokens	Выпуск bootstrap-токена
POST	/api/v1/admin/computers/{uid}/revoke	Отключить ПК
POST	/api/v1/admin/computers/{uid}/re-registration-token	Разрешить перерегистрацию
Аутентификация: заголовок X-Admin-Token: <ADMIN_API_KEY>.

Веб-админка (/admin/*)
Метод	Путь	Назначение
GET	/admin/login	Форма входа
POST	/admin/login	Вход
GET	/admin/logout	Выход
GET	/admin/setup	Первичная настройка
POST	/admin/setup	Создание первого админа
GET	/admin/set-lang/{code}	Переключение языка
GET	/admin	Дашборд
GET	/admin/employees	Сотрудники
POST	/admin/employees/create	Создание
POST	/admin/employees/{id}/edit	Редактирование
POST	/admin/employees/{id}/fire	Увольнение
POST	/admin/employees/{id}/restore	Восстановление
POST	/admin/employees/{id}/delete-forever	Удаление (152-ФЗ)
GET	/admin/departments	Отделы
POST	/admin/departments/create	Создание
POST	/admin/departments/{id}/rename	Переименование
POST	/admin/departments/{id}/delete	Удаление
GET	/admin/computers	ПК
POST	/admin/computers/{id}/assign	Привязка
POST	/admin/computers/{id}/revoke	Отключение
POST	/admin/computers/{id}/activate	Включение
POST	/admin/computers/bulk-assign	Массовая привязка CSV
POST	/admin/computers/{id}/assign-unattached	Привязка сессий без привязки
POST	/admin/computers/{id}/delete-unattached	Удаление сессий без привязки
POST	/admin/computers/{id}/soft-delete	В корзину
POST	/admin/computers/{id}/restore	Из корзины
POST	/admin/computers/{id}/delete-forever	Удаление навсегда
POST	/admin/computers/{id}/re-registration-token	Перерегистрация
GET	/admin/tokens	Bootstrap-токены
POST	/admin/tokens/issue	Выпуск
POST	/admin/tokens/{id}/delete	Удаление
GET	/admin/reports	Форма отчёта
POST	/admin/reports/generate	Генерация отчёта
GET	/admin/reports/pivot	Pivot-страница
POST	/admin/api/pivot-data	Данные для pivot
GET	/admin/sessions	Сессии
POST	/admin/sessions/delete-selected	Удаление выбранных
POST	/admin/sessions/delete-filtered	Удаление по фильтру
POST	/admin/sessions/{uid}/delete	Удаление одной
GET	/admin/calendar	Календарь
POST	/admin/calendar/save	Сохранение
POST	/admin/calendar/generate	Генерация
POST	/admin/calendar/reset	Сброс
GET	/admin/settings	Настройки
POST	/admin/settings/save	Сохранение
GET	/admin/scheduler	Планировщик
POST	/admin/scheduler/{name}/toggle	Вкл/выкл
POST	/admin/scheduler/{name}/trigger	Ручной запуск
POST	/admin/scheduler/{name}/edit	Изменение cron
POST	/admin/scheduler/reload	Перезагрузка
GET	/admin/users	Пользователи
GET	/admin/users/new	Форма создания
POST	/admin/users/new	Создание
GET	/admin/users/{id}/edit	Форма редактирования
POST	/admin/users/{id}/edit	Сохранение
POST	/admin/users/{id}/toggle-active	Вкл/выкл
GET	/admin/users/{id}/reset-password	Форма сброса пароля
POST	/admin/users/{id}/reset-password	Сброс
POST	/admin/users/{id}/delete	Удаление
GET	/admin/logins	История входов
GET	/admin/audit	Аудит
GET	/admin/trash	Корзина
POST	/admin/trash/restore	Восстановить
POST	/admin/trash/delete-forever	Удалить навсегда
POST	/admin/trash/empty	Очистить
GET	/admin/profile	Профиль
POST	/admin/profile/save	Сохранение
POST	/admin/profile/change-password	Смена пароля
GET	/admin/schedules	Графики
GET	/admin/schedules/new	Форма создания
POST	/admin/schedules/new	Создание
GET	/admin/schedules/{id}/edit	Форма редактирования
POST	/admin/schedules/{id}/edit	Сохранение
POST	/admin/schedules/{id}/delete	Удаление
GET	/admin/employees/{id}/settings	Персональные настройки
POST	/admin/employees/{id}/settings/save	Сохранение
POST	/admin/employees/{id}/settings/reset	Сброс
Форматы ответов
JSON — для API-эндпоинтов.

HTML — для веб-страниц (Jinja2).

StreamingResponse — для CSV/XLSX/PDF.

RedirectResponse — после POST-форм (PRG-паттерн).

Коды ошибок
Код	Значение
200	Успех
303	Редирект после POST
400	Некорректные данные
401	Не авторизован
403	Нет прав
404	Не найдено
409	Конфликт (устарело, заменено на 200)
500	Внутренняя ошибка
Идемпотентность
record_uid — уникальный, повторная отправка не создаёт дубликат.

session_uid — уникальный, повторная отправка обновляет.

Bootstrap-токен — одноразовый, повторное использование → 401.

HMAC-подпись
Canonical JSON: json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).

Подпись записи: HMAC-SHA256 от {record_uid, session_uid, kind, data, client_ts} с client_secret.

Подпись батча: HMAC-SHA256 от {records: [...]} с client_secret.

Ключевые решения
Все клиентские эндпоинты — под /api/v1/. Версионирование для совместимости.

HMAC на каждой записи. Целостность данных, офлайн-режим.

Идемпотентность везде. Повторная отправка безопасна.

409 → 200 для «чужих» сессий. Не блокируем клиента.

Bootstrap-токены — одноразовые. Хеш в БД, TTL.

Админ API — X-Admin-Token. Просто и достаточно для внутренних вызовов.

Веб-админка — сессия в cookie. SessionMiddleware, tracker_admin.

PRG-паттерн. После POST — редирект, чтобы избежать повторной отправки.

JSON для API, HTML для страниц. Не смешиваем.

Ссылки на код
запросить: server/main.py — все клиентские и админские API

запросить: server/web_admin.py — все веб-роуты

запросить: server/schemas.py — Pydantic-схемы запросов/ответов

запросить: server/security.py — HMAC, canonical_json

запросить: server/security_passwords.py — bcrypt, роли

запросить: server/nginx.conf — проксирование

Открытые вопросы / чего не хватает
нет данных: OpenAPI/Swagger документация — FastAPI генерирует автоматически, но не описана.

нет данных: версионирование API — есть /api/v1/, но нет политики.

нет данных: rate limiting — не реализован.

нет данных: пагинация в API — не реализована (в веб-админке — limit 500).

не решено: нужен ли отдельный эндпоинт для логов клиента.

не решено: нужны ли webhooks для интеграций.

не решено: как быть с CORS — пока не настроен.

не решено: нужна ли аутентификация для /api/v1/version — сейчас открыт.

не решено: добавлять ли /api/v2/ при breaking changes.

Готово. Один файл выше. Следующий по индексу — 03_SERVER\03_MODELS.md.