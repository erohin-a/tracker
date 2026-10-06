# Настройки
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 03_SERVER\03_MODELS.md, 02_METRICS\01_METRICS.md, 02_METRICS\05_CALENDAR.md

## Назначение
Описать глобальные настройки приложения «Трекер»: где хранятся, какие есть, как меняются, на что влияют. Это карта для администратора, который настраивает систему, и для разработчика, который добавляет новую настройку.

## Содержание

### Где хранятся настройки
- **Таблица `app_settings`** — key/value, ключ `String(64)`, значение `Text`.
- Модель `AppSetting` в `server/models.py`.
- Редактирование — через страницу `/admin/settings`.
- Персональные настройки сотрудника — в `employee_settings` (nullable поля = «как у всех»).
- Секреты (`SECRET_ENCRYPTION_KEY`, `JWT_SECRET`, `ADMIN_API_KEY`) — в `.env`, не в БД.

### Полный список настроек

#### Отчёты
| Ключ | Тип | По умолчанию | Диапазон | Что влияет |
|---|---|---|---|---|
| `report_timezone` | str | `Europe/Moscow` | список TZ | Часовой пояс для отображения в отчётах |
| `workday_start_hour` | int | `6` | 0–23 | Час начала рабочего дня (сессии до него → предыдущий день) |
| `activity_gap_minutes` | int | `5` | 1–120 | Порог разрыва между событиями для «Эффективно» |
| `count_weekends` | bool | `True` | — | Учитывать ли выходные в отчётах |

#### Клиенты
| Ключ | Тип | По умолчанию | Диапазон | Что влияет |
|---|---|---|---|---|
| `idle_close_minutes` | int | `30` | 5–480 | Порог бездействия для авто-закрытия сессии на клиенте |
| `stale_session_hours` | int | `2` | 1–24 | Порог авто-закрытия «висящих» сессий на сервере |
| `sync_interval` | int | `30` | 5–3600 | Интервал синхронизации клиента (секунды) |
| `batch_size` | int | `200` | 10–1000 | Сколько записей клиент отправляет за раз |
| `active_window_interval` | int | `5` | 1–60 | Период опроса активного окна (секунды) |
| `idle_threshold` | int | `60` | 10–3600 | Порог бездействия, после которого клиент пишет `idle` (секунды) |

#### Напоминание о старте работы
| Ключ | Тип | По умолчанию | Диапазон | Что влияет |
|---|---|---|---|---|
| `reminder_enabled` | bool | `True` | — | Включить напоминание о старте |
| `reminder_threshold_minutes` | int | `15` | 1–480 | Минут активности без сессии до первого напоминания |
| `reminder_repeat_minutes` | int | `10` | 1–480 | Через сколько минут повторять, если проигнорировали |
| `reminder_max_per_day` | int | `5` | 1–100 | Максимум напоминаний за день |

#### Уведомление о конце рабочего дня
| Ключ | Тип | По умолчанию | Диапазон | Что влияет |
|---|---|---|---|---|
| `end_of_day_hour` | int | `19` | 0–23 | Час срабатывания EOD-напоминания (0 = выключено) |
| `end_of_day_minute` | int | `0` | 0–59 | Минуты EOD-напоминания |

### Хелперы для работы с настройками

**Чтение:**
```python
def get_app_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else default

def get_app_setting_int(db: Session, key: str, default: int, minv: int, maxv: int) -> int:
    try:
        return max(minv, min(maxv, int(get_app_setting(db, key, str(default)))))
    except (ValueError, TypeError):
        return default
Запись:

python
def set_app_setting(db: Session, key: str, value: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if row:
        row.value = value
    else:
        db.add(AppSetting(key=key, value=value))
Словарь всех настроек:

python
def get_settings_dict(db: Session) -> dict:
    return {
        "idle_close_minutes": get_app_setting_int(db, "idle_close_minutes", settings.idle_close_minutes, 5, 480),
        "workday_start_hour": get_app_setting_int(db, "workday_start_hour", settings.workday_start_hour, 0, 23),
        "activity_gap_minutes": get_app_setting_int(db, "activity_gap_minutes", settings.activity_gap_minutes, 1, 120),
        "report_timezone": get_app_setting(db, "report_timezone", settings.report_timezone),
        "sync_interval": get_app_setting_int(db, "sync_interval", 30, 5, 3600),
        "batch_size": get_app_setting_int(db, "batch_size", 200, 10, 1000),
        "active_window_interval": get_app_setting_int(db, "active_window_interval", 5, 1, 60),
        "idle_threshold": get_app_setting_int(db, "idle_threshold", 60, 10, 3600),
        "count_weekends": get_app_setting(db, "count_weekends", "1") == "1",
        "reminder_enabled": get_app_setting(db, "reminder_enabled", "1") == "1",
        "reminder_threshold_minutes": get_app_setting_int(db, "reminder_threshold_minutes", 15, 1, 480),
        "reminder_repeat_minutes": get_app_setting_int(db, "reminder_repeat_minutes", 10, 1, 480),
        "reminder_max_per_day": get_app_setting_int(db, "reminder_max_per_day", 5, 1, 100),
        "end_of_day_hour": get_app_setting_int(db, "end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": get_app_setting_int(db, "end_of_day_minute", 0, 0, 59),
        "stale_session_hours": get_app_setting_int(db, "stale_session_hours", 2, 1, 24),
    }
Страница /admin/settings
Форма POST /admin/settings/save:

Часовой пояс (report_timezone) — выпадающий список.

Начало рабочего дня (workday_start_hour) — int.

Порог паузы (activity_gap_minutes) — int.

Idle-порог (idle_close_minutes) — int.

Автозакрытие зависших сессий (stale_session_hours) — int.

Интервал синхронизации (sync_interval) — int.

Размер батча (batch_size) — int.

Период опроса активного окна (active_window_interval) — int.

Порог бездействия (idle_threshold) — int.

Учитывать выходные (count_weekends) — checkbox.

Напоминание: reminder_enabled, reminder_threshold_minutes, reminder_repeat_minutes, reminder_max_per_day.

EOD: end_of_day_hour, end_of_day_minute.

Валидация при сохранении:

python
new_vals = {
    "idle_close_minutes": max(5, min(480, int(idle_close_minutes))),
    "workday_start_hour": max(0, min(23, int(workday_start_hour))),
    "activity_gap_minutes": max(1, min(120, int(activity_gap_minutes))),
    # ...
}
Аудит: каждое изменение пишется в audit_log (actor, entity=app_setting, action=update, old_value, new_value).

Плашка «saved»: после успешного сохранения — ?saved=1.

Влияние настроек на систему
На отчёты
report_timezone — в каком поясе отображаются даты.

workday_start_hour — группировка по дням (сессия до 6:00 → предыдущий день).

activity_gap_minutes — «Эффективно» и «Пауза».

count_weekends — учитывать ли выходные в метриках.

На клиент
Клиент получает эффективные настройки через GET /api/v1/client-config (см. 03_SERVER\02_API.md):

reminder_enabled, reminder_threshold_minutes, reminder_repeat_minutes, reminder_max_per_day.

end_of_day_hour, end_of_day_minute.

Мерж глобальных и персональных:

Глобальные — из app_settings.

Персональные — из employee_settings.

Персональные перекрывают глобальные.

Поле source_* в ответе показывает, откуда взято значение (global или personal).

Клиенты подхватывают изменения в течение 5 минут (следующий цикл синхронизации).

На планировщик
stale_session_hours — используется в close_stale_sessions.

report_timezone, workday_start_hour, activity_gap_minutes — в aggregate_daily_stats.

На сервер
sync_interval, batch_size, active_window_interval, idle_threshold — только отдаются клиенту, на сервере не используются.

Персональные настройки (employee_settings)
Отдельная страница /admin/employees/{id}/settings.

Поля:

reminder_enabled (nullable).

reminder_threshold_minutes (nullable).

reminder_repeat_minutes (nullable).

reminder_max_per_day (nullable).

end_of_day_hour (nullable).

end_of_day_minute (nullable).

Логика:

NULL = «как у всех» (используется глобальное значение).

Не-NULL = персональное значение перекрывает глобальное.

Кнопка «Сбросить к общим» — удаляет запись employee_settings, возвращает к глобальным.

Права: admin, operator, hr.

Часовые пояса
Список поддерживаемых (_available_timezones):

Код	Метка
Europe/Moscow	Москва (UTC+3)
Europe/Kaliningrad	Калининград (UTC+2)
Europe/Samara	Самара (UTC+4)
Asia/Yekaterinburg	Екатеринбург (UTC+5)
Asia/Omsk	Омск (UTC+6)
Asia/Novosibirsk	Новосибирск (UTC+7)
Asia/Krasnoyarsk	Красноярск (UTC+7)
Asia/Irkutsk	Иркутск (UTC+8)
Asia/Yakutsk	Якутск (UTC+9)
Asia/Vladivostok	Владивосток (UTC+10)
UTC	UTC
Известные проблемы и решения
Проблема	Причина	Решение
Изменения не доходят до клиента	Клиент не синхронизировался	Подождать до 5 минут или trigger()
workday_start_hour меняет старые отчёты	Пересчёт идёт по текущей настройке	Нормальное поведение — отчёты пересчитываются
activity_gap_minutes не влияет на daily_stats	Агрегат не пересчитывается автоматически	Запустить aggregate_daily_stats вручную
Персональные настройки не применяются	Клиент не подтянул client-config	Проверить employee_settings в БД
count_weekends = False не исключает выходные	Проверить логику в _build_report	Убедиться, что фильтр применяется
Как добавить новую настройку
Добавить ключ в get_settings_dict (с дефолтом и диапазоном).

Добавить поле в форму settings.html.

Добавить параметр в settings_save (Form + валидация).

Если настройка влияет на клиент — добавить в client-config (в get_client_config).

Если настройка влияет на отчёты — использовать её в _build_report.

Записать в audit_log при изменении.

Ключевые решения
app_settings как key/value. Просто, гибко, без миграций для новых настроек.

Диапазоны валидации в коде. max(minv, min(maxv, value)) — защита от дурака.

Персональные перекрывают глобальные. NULL = «как у всех».

Клиенты подхватывают за 5 минут. Через client-config.

Все изменения — в audit_log. Полная история.

Часовой пояс — на уровне отчётов, не сервера. Сервер всегда UTC, отображение — по TZ.

count_weekends — глобальная настройка. Не может быть разной для разных отделов.

workday_start_hour = 6 по умолчанию. Компромисс для ночных смен.

Ссылки на код
запросить: server/models.py — модель AppSetting, EmployeeSettings

запросить: server/web_admin.py — get_app_setting, set_app_setting, get_app_setting_int, get_settings_dict

запросить: server/web_admin.py — роуты /admin/settings, /admin/settings/save

запросить: server/web_admin.py — роуты /admin/employees/{id}/settings, /save, /reset

запросить: server/templates/settings.html, employee_settings.html

запросить: server/main.py — GET /api/v1/client-config, PUT /api/v1/client-settings, DELETE /api/v1/client-settings

запросить: server/config.py — дефолты в Settings

Открытые вопросы / чего не хватает
нет данных: полный список app_settings в БД — только то, что описано выше.

нет данных: есть ли настройки, добавленные после 22.09.2026, но не описанные в KB.

нет данных: применяется ли count_weekends в daily_stats — нужно проверить.

не решено: нужна ли настройка retention_days для сырых records.

не решено: нужна ли настройка count_weekends на уровне отдела.

не решено: как быть с workday_start_hour при разных сменах (утро/ночь).

не решено: должны ли персональные настройки быть у всех сотрудников или только у некоторых.

не решено: нужна ли настройка «часовой пояс клиента» (не сервера).

не решено: нужна ли настройка stale_session_hours на уровне ПК.

не решено: как быть с миграцией настроек при обновлении (новые ключи не создаются автоматически).

Готово. Один файл выше. Следующий по индексу — 04_CLIENT\01_ARCHITECTURE.md.