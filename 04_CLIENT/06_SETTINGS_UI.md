# Окно настроек клиента
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 04_CLIENT\01_ARCHITECTURE.md, 04_CLIENT\05_REMINDERS.md, 04_CLIENT\07_THEMES_I18N.md, 04_CLIENT\09_REGISTRATION.md

## Назначение
Описать окно настроек клиента Tracker: какие вкладки, какие поля, что делают кнопки, как связано с i18n и темами. Это карта для разработчика, который дорабатывает UI, и для администратора, который объясняет сотруднику, где что настроить.

## Содержание

### Общее
- Класс: `SettingsDialog` (`client/settings_dialog.py`).
- Открывается из главного окна кнопкой «⚙ Настройки».
- Одно окно, **три вкладки** (`QTabWidget`).
- При смене языка вызывает `language_changed`, `SettingsDialog._on_language_changed` делает retranslate всех вкладок.
- При смене темы вызывает `themes.apply_theme(app)`.
- Кнопка «Закрыть» внизу.

### Вкладка 1: «Напоминание» (`ReminderTab`)

**Назначение:** настройки напоминаний о старте работы и конце дня.

**Группа «Напоминание о старте»:**
| Поле | Тип | По умолчанию | Подсказка ⓘ |
|---|---|---|---|
| `reminder_enabled` | QCheckBox | вкл | Включить напоминание |
| `reminder_threshold_minutes` | QSpinBox | 15 | Минут активности без сессии |
| `reminder_repeat_minutes` | QSpinBox | 10 | Через сколько повторять |
| `reminder_max_per_day` | QSpinBox | 5 | Максимум в день |

**Группа «Конец дня»:**
| Поле | Тип | По умолчанию | Подсказка ⓘ |
|---|---|---|---|
| `end_of_day_hour` | QSpinBox | 19 | Час (0 = выключено) |
| `end_of_day_minute` | QSpinBox | 0 | Минуты |

**Статус источника:**
- `reminder.status.personal` — «Персональные» (если `source_reminder = personal`).
- `reminder.status.global` — «Как у всех» (если `source_reminder = global`).

**Кнопки:**
- «Сбросить к общим» (`reminder.btn.reset_to_global`) — с подтверждением.
- Тултип: `reminder.btn.reset_to_global.tooltip`.

**Логика сброса:**
1. Показать `QMessageBox` с `reminder.reset.confirm_title` / `reminder.reset.confirm_text`.
2. При подтверждении — `DELETE /api/v1/client-settings`.
3. Обновить поля из `client-config`.
4. Статус → `reminder.status.global`.

**Ошибки сброса:**
- `reminder.reset.not_registered` — ПК не зарегистрирован.
- `reminder.reset.not_linked` — сотрудник не привязан.
- `reminder.reset.unauth` — 401/403.
- `reminder.reset.server_error` — 500.
- `reminder.reset.success` — успех.
- `reminder.reset.partial` — частичный успех.

**Иконка ⓘ (`_hint()`):**
- Возвращает иконку ⓘ только если есть перевод для ключа `*.hint`.
- При наведении — `QToolTip` с переводом.

**Ключи i18n:**
- `reminder.source.personal`, `reminder.source.global`.
- `reminder.group.start`, `reminder.group.eod`.
- `reminder.enabled`, `reminder.threshold`, `reminder.threshold.hint`.
- `reminder.repeat`, `reminder.repeat.hint`.
- `reminder.max_per_day`, `reminder.max_per_day.hint`.
- `reminder.eod_hour`, `reminder.eod_minute`, `reminder.eod.hint`.
- `reminder.eod_hour.zero` — «0 = выключено».
- `reminder.btn.reset_to_global`, `reminder.btn.reset_to_global.tooltip`.
- `reminder.reset.confirm_title`, `reminder.reset.confirm_text`.
- `reminder.status.local_only`, `reminder.status.synced`, `reminder.status.server_refused`, `reminder.status.not_authorized`, `reminder.status.server_error`, `reminder.status.net_error`.

### Вкладка 2: «Общие» (`GeneralTab`)

**Назначение:** базовые настройки клиента: автозапуск, тема, язык, сервер, уведомления.

**Группа «Автозапуск»:**
| Поле | Тип | Что делает |
|---|---|---|
| `autostart` | QCheckBox | Вкл/выкл автозапуск при входе в систему |

- `general.autostart.hint` — подсказка.
- `general.autostart.error` — ошибка при записи в реестр.

**Группа «Внешний вид»:**
| Поле | Тип | Значения |
|---|---|---|
| `theme` | QComboBox | light / dark / system |

- `general.theme.light`, `general.theme.dark`, `general.theme.system`.
- `general.theme.hint`.

**Группа «Язык»:**
| Поле | Тип | Значения |
|---|---|---|
| `lang` | QComboBox | ru / en |

- `general.lang.hint`.
- `general.lang.restart_title`, `general.lang.restart_text` — предупреждение о необходимости перезапуска.

**Группа «Связь»:**
| Поле | Тип | Что делает |
|---|---|---|
| `server_url` | QLineEdit | Адрес сервера |
| `cert_fingerprint` | QLineEdit | Отпечаток сертификата (SHA-256) |

**Кнопки:**
- «Проверить соединение» (`general.btn.check_connection`).
- «Сохранить адрес» (`general.btn.save_server`).

**Статусы проверки:**
- `general.conn.checking` — «Проверка...».
- `general.conn.ok` — «Соединение установлено».
- `general.conn.fail` — «Ошибка».
- `general.conn.no_server` — «Сервер недоступен».
- `general.conn.saved` — «Сохранено».

**Группа «Уведомления»:**
| Поле | Тип | Что делает |
|---|---|---|
| `notif.offline` | QCheckBox | Уведомлять о потере связи |
| `notif.eod` | QCheckBox | Уведомлять о конце дня |

- `general.notif.offline.hint`, `general.notif.eod.hint`.

**Ключи i18n:**
- `general.group.autostart`, `general.autostart`, `general.autostart.hint`, `general.autostart.error`.
- `general.group.appearance`, `general.theme`, `general.theme.hint`, `general.theme.light`, `general.theme.dark`, `general.theme.system`.
- `general.group.language`, `general.lang`, `general.lang.hint`, `general.lang.restart_title`, `general.lang.restart_text`.
- `general.group.connectivity`, `general.server_url`, `general.server_url.hint`, `general.cert_fingerprint`, `general.cert_fingerprint.hint`.
- `general.btn.check_connection`, `general.btn.save_server`.
- `general.conn.checking`, `general.conn.ok`, `general.conn.fail`, `general.conn.no_server`, `general.conn.saved`.
- `general.group.notifications`, `general.notif.offline`, `general.notif.offline.hint`, `general.notif.eod`, `general.notif.eod.hint`.

### Вкладка 3: «Регистрация» (`RegistrationTab`)

**Назначение:** информация о текущей регистрации ПК + возможность перерегистрации.

**Группа «Информация»:**
| Поле | Тип | Что показывает |
|---|---|---|
| `uid` | QLabel | `computer_uid` (не редактируется) |
| `hostname` | QLabel | Имя ПК |
| `server` | QLabel | Текущий URL сервера |

**Группа «Сервер»:**
| Поле | Тип | Что делает |
|---|---|---|
| `server_url` | QLineEdit | Адрес сервера |
| `cert_fingerprint` | QLineEdit | Отпечаток сертификата |
| `bootstrap_token` | QLineEdit | Bootstrap-токен для перерегистрации |

**Кнопки:**
- «Сохранить адрес» (`reg.btn.save_server`).
- «Проверить соединение» (`reg.btn.check_connection`).
- «Перерегистрировать» (`reg.reregister`).

**Статусы:**
- `reg.server.saved`, `reg.server.checking`, `reg.server.ok`, `reg.server.fail`.

**Перерегистрация:**
1. Предупреждение `reg.reregister.warn`.
2. Подтверждение `reg.reregister.confirm_title` / `reg.reregister.confirm_text`.
3. Вызов `registration.register_with_token(token)`.
4. При успехе — `reg.reregister.done_title` / `reg.reregister.done_text`.
5. При отсутствии UID — `reg.reregister.no_uid`.
6. При ошибке — `reg.reregister.error`.

**Ключи i18n:**
- `reg.group.info`, `reg.uid`, `reg.hostname`, `reg.server`.
- `reg.group.server`, `reg.server_url`, `reg.server_url.hint`.
- `reg.cert_fingerprint`, `reg.cert_fingerprint.hint`.
- `reg.bootstrap_token`, `reg.bootstrap_token.hint`.
- `reg.btn.save_server`, `reg.btn.check_connection`.
- `reg.server.saved`, `reg.server.checking`, `reg.server.ok`, `reg.server.fail`.
- `reg.reregister`, `reg.reregister.warn`, `reg.reregister.confirm_title`, `reg.reregister.confirm_text`.
- `reg.reregister.done_title`, `reg.reregister.done_text`, `reg.reregister.no_uid`, `reg.reregister.error`.

### Общие кнопки

| Кнопка | Ключ i18n | Что делает |
|---|---|---|
| Сохранить | `btn.save` | Сохранить изменения вкладки |
| Закрыть | `btn.close` | Закрыть окно настроек |
| Отмена | `btn.cancel` | Отменить изменения (в отдельных случаях) |

### Retranslate (смена языка)

**Проблема:** переключение языка требует перезапуска (в текущей реализации).

**Что делается:**
1. Пользователь меняет язык в `GeneralTab` → `general.lang`.
2. Показывается предупреждение `general.lang.restart_title` / `general.lang.restart_text`.
3. Язык сохраняется в `config.json` → `language`.
4. При следующем запуске клиента — интерфейс на новом языке.

**Что планируется:**
- `retranslateUi()` в `MainWindow` и `SettingsDialog`.
- При смене языка — вызвать retranslate без перезапуска.

**Известные ограничения:**
- Главное окно (`main.py`) — частично хардкод по-русски, i18n не подключён полностью.
- `SettingsDialog` — retranslate работает для вкладок (`ReminderTab`, `GeneralTab`, `RegistrationTab`).
- Диалоги (`RegistrationDialog`, `UnclosedSessionDialog`) — retranslate не реализован.

### Темы

**Как применяется:**
1. Пользователь выбирает тему в `GeneralTab` → `general.theme`.
2. Сохраняется в `config.json` → `theme`.
3. Вызывается `themes.apply_theme(app, code)`.
4. `theme_signals.theme_changed.emit(code)` — уведомляет подписчиков.

**Значения:**
- `light` — светлая, по умолчанию.
- `dark` — тёмная.
- `system` — системная (пока применяется как light).

**Что покрыто QSS:**
- `QMainWindow`, `QDialog`.
- `QFrame#infoPanel`.
- Кнопки `#btnStart`, `#btnStop`, `#btnPause`, `#btnResume`, `#btnSettings`.
- `QTabWidget`, `QTabBar`.
- `QMenu`, `QToolTip`.
- `QLineEdit`, `QSpinBox`, `QComboBox`, `QCheckBox`, `QGroupBox`.
- `QMessageBox`.

**Что НЕ покрыто (требует доработки):**
- Title bar окна (тёмная тема только для клиентской области).
- Некоторые таблицы и списки.
- Иконки трея (не зависят от темы).

### Взаимодействие с сервером

**`GET /api/v1/client-config`** — раз в 5 минут:
- `reminder_enabled`, `reminder_threshold_minutes`, `reminder_repeat_minutes`, `reminder_max_per_day`.
- `end_of_day_hour`, `end_of_day_minute`.
- `source_reminder`, `source_end_of_day`.

**`PUT /api/v1/client-settings`** — при сохранении персональных настроек:
- Отправляет выбранные поля.
- Сервер сохраняет в `employee_settings`.

**`DELETE /api/v1/client-settings`** — при сбросе к глобальным:
- Удаляет запись `employee_settings`.
- Клиент возвращается к глобальным значениям.

**`GET /api/v1/version`** — проверка обновлений (в `updater.py`).

### Локальное хранение

**`config.json`** (`%APPDATA%\Tracker\config.json`):
- `language` — ru/en.
- `theme` — light/dark/system.
- `autostart_enabled` — bool.
- `server_url` — переопределение.
- `cert_fingerprint` — переопределение.
- `notifications` — `{offline: bool, eod: bool}`.

**`meta` SQLite:**
- Настройки напоминаний (`reminder_settings.py`).

### Известные проблемы и решения

| Проблема | Причина | Решение |
|---|---|---|
| Переключение языка требует перезапуска | Нет retranslate главного окна | В планах |
| Тёмная тема не покрывает title bar | QSS не работает с системным title bar | WinAPI `DwmSetWindowAttribute` (опционально) |
| Автозапуск не срабатывает | Нет прав на реестр | Запуск от пользователя |
| Сброс к общим не работает | 401/403 | Проверить регистрацию ПК |
| Server URL не сохраняется | Неправильный порядок чтения `.env` | `client/.env` в приоритете |
| Отпечаток не проверяется | Не задан `TRACKER_PIN` | Опционально, для pinning |

### Логи
2026-10-02 09:20:00 INFO tracker.settings Settings dialog opened
2026-10-02 09:20:05 INFO tracker.themes Applied dark theme
2026-10-02 09:20:10 INFO tracker.settings Theme saved: dark
2026-10-02 09:20:15 INFO tracker.settings Language saved: ru
2026-10-02 09:20:20 INFO tracker.settings Server URL saved: https://127.0.0.1

text

## Ключевые решения
- **Три вкладки:** Напоминание, Общие, Регистрация. Логичное разделение.
- **Настройки напоминаний — персональные + глобальные.** Мерж с сервером.
- **Статус источника** (`personal` / `global`) — прозрачность.
- **Кнопка «Сбросить к общим»** — быстрое возвращение к глобальным.
- **Язык — с перезапуском.** В планах — retranslate.
- **Тема — сразу.** Без перезапуска, через `theme_signals`.
- **Автозапуск — checkbox.** Просто.
- **Server URL — в настройках.** Можно переопределить.
- **Отпечаток сертификата — в настройках.** Для pinning.
- **Перерегистрация — на вкладке «Регистрация».** Все данные в одном месте.

## Ссылки на код
- запросить: `client/settings_dialog.py` — `SettingsDialog`, `ReminderTab`, `GeneralTab`, `RegistrationTab`
- запросить: `client/main.py` — открытие настроек, обработка `language_changed`, `theme_changed`
- запросить: `client/themes.py` — `apply_theme`, `theme_signals`
- запросить: `client/i18n.py` — ключи `settings.*`, `reminder.*`, `general.*`, `reg.*`, `btn.*`
- запросить: `client/reminder_settings.py` — `get_all`, `set_many`
- запросить: `client/config.py` — `get_setting`, `set_setting`, `get_server_url`, `get_cert_fingerprint`, `get_language_code`, `get_theme_code`
- запросить: `client/registration.py` — `register_with_token`, `is_registered`
- запросить: `client/autostart.py` — `set_autostart`
- запросить: `server/main.py` — `GET /api/v1/client-config`, `PUT /api/v1/client-settings`, `DELETE /api/v1/client-settings`

## Открытые вопросы / чего не хватает
- нет данных: полный список полей `ReminderTab` — возможно, есть скрытые.
- нет данных: реализован ли `snooze` в UI.
- нет данных: есть ли валидация ввода server_url.
- нет данных: как показывается ошибка при сохранении.
- не решено: нужен ли звук при сохранении.
- не решено: должен ли `SettingsDialog` быть модальным.
- не решено: нужна ли кнопка «Сбросить все настройки».
- не решено: как быть с настройками, если сервер недоступен.
- не решено: должен ли `RegistrationTab` показывать статус `revoked`.
- не решено: нужна ли проверка отпечатка сертификата при сохранении.
- не решено: как показывать «Обновление доступно» в настройках (обсуждалось).
- не решено: retranslate главного окна — когда будет реализовано.
- не решено: темная тема title bar — нужна ли.

Готово. Один файл выше. Следующий по индексу — 04_CLIENT\07_THEMES_I18N.md.