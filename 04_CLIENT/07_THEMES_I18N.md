# Темы и i18n клиента
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 04_CLIENT\01_ARCHITECTURE.md, 04_CLIENT\06_SETTINGS_UI.md, 03_SERVER\08_I18N.md

## Назначение
Описать две связанные подсистемы клиента: темы оформления (QSS light/dark/system) и интернационализацию (RU/EN). Это карта для разработчика, который дорабатывает UI, и для администратора, который объясняет сотруднику, где переключить язык и тему.

## Содержание

### Часть 1: Темы

#### Что такое темы в клиенте
- **Light** — светлая, по умолчанию.
- **Dark** — тёмная.
- **System** — системная (пока применяется как light).
- Реализация — **QSS** (Qt Style Sheets) в `client/themes.py`.
- Применение — через `app.setStyleSheet(qss)`.

#### Классы и сигналы
```python
class _ThemeSignals(QObject):
    theme_changed = pyqtSignal(str)

theme_signals = _ThemeSignals()
theme_signals.theme_changed испускается при смене темы.

Подписчики (окна) могут реагировать на смену.

Константы
SUPPORTED_THEMES — список тем: light, dark, system.

_CUSTOM_LIGHT — QSS-строка для светлой темы.

_CUSTOM_DARK — QSS-строка для тёмной темы.

Функция apply_theme(app, code)
python
def apply_theme(app, code: str) -> bool:
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(_CUSTOM_DARK)
        theme_signals.theme_changed.emit("dark")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet(_CUSTOM_LIGHT)
        theme_signals.theme_changed.emit(code or "light")
        return True
    else:
        app.setStyleSheet(_CUSTOM_LIGHT)
        theme_signals.theme_changed.emit("light")
        return False
Что покрыто QSS
Обе темы:

QMainWindow, QMainWindow > QWidget, QDialog, QWidget.

QLabel.

QPushButton (все состояния: hover, pressed, disabled).

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit.

QComboBox QAbstractItemView.

QCheckBox (индикатор).

QGroupBox (рамка, заголовок).

QTabWidget::pane, QTabBar::tab, QTabBar::tab:selected, QTabBar::tab:hover:!selected.

QMenu, QMenu::item, QMenu::item:selected.

QToolTip.

QMessageBox.

QFrame#infoPanel — панель информации.

QLabel#panelTitle, QLabel#statusLabel, QLabel#sessionClock.

QLabel#serverLabel[state="online"], QLabel#serverLabel[state="offline"].

QPushButton#btnStart, #btnStop, #btnPause, #btnResume, #btnSettings.

Палитры
Светлая:

Элемент	Цвет
Фон	#ffffff
Текст	#212529
Границы	#ced4da / #dee2e6
Панель	#f8f9fa
Кнопка Старт	#28a745 (зелёная)
Кнопка Стоп	#dc3545 (красная)
Кнопка Пауза	#ffc107 (жёлтая)
Кнопка Настройки	#6c757d (серая)
Тёмная:

Элемент	Цвет
Фон	#2b2b2b
Текст	#e0e0e0
Границы	#555555
Панель	#3a3a3a
Кнопка Старт	#28a745
Кнопка Стоп	#dc3545
Кнопка Пауза	#ffc107
Кнопка Настройки	#6c757d
Онлайн	#34ce57
Офлайн	#ff6b6b
Известные проблемы
Inline-стили перебивают QSS. Например, setStyleSheet("#infoPanel { ... }") в main.py ломает тёмную тему. Решение: убрать inline-стили, использовать setObjectName + QSS.

Title bar окна остаётся светлым при тёмной теме — QSS не работает с системным заголовком. Решение: WinAPI DwmSetWindowAttribute (опционально).

Некоторые таблицы и списки могут быть не покрыты — нужно проверять.

Иконка в трее не зависит от темы (PNG/JPG).

Правила работы с темами
Не использовать inline-стили для элементов, которые должны менять тему.

Использовать setObjectName для кастомных элементов (#infoPanel, #btnStart, #btnPause).

Все стили — в themes.py (_CUSTOM_LIGHT, _CUSTOM_DARK).

Подписываться на theme_signals.theme_changed для динамических обновлений.

Проверять на обеих темах при добавлении новых элементов.

Как применить тему в коде
python
from .themes import apply_theme, theme_signals, SUPPORTED_THEMES

# Применить при старте
apply_theme(app, get_theme_code())

# Подписаться на смену
theme_signals.theme_changed.connect(self._on_theme_changed)
Как добавить новый стиль
Добавить в _CUSTOM_LIGHT блок для элемента.

Добавить в _CUSTOM_DARK соответствующий блок.

Использовать setObjectName для элемента в коде.

Проверить на обеих темах.

Часть 2: i18n (интернационализация)
Что такое i18n в клиенте
Простой словарь переводов без внешних библиотек (никаких Babel/gettext).

Все строки интерфейса — в client/i18n.py.

Два языка: RU (по умолчанию) и EN.

Язык хранится в config.json → language.

Переключение языка требует перезапуска (в планах — retranslate).

Структура client/i18n.py
python
DEFAULT_LANG = "ru"

SUPPORTED_LANGS = [
    {"code": "ru", "label": "Русский", "short": "RU"},
    {"code": "en", "label": "English", "short": "EN"},
]

TRANSLATIONS = {
    "btn.save": {"ru": "Сохранить", "en": "Save"},
    # ~85 ключей
}

def t(key: str, **kwargs) -> str:
    lang = get_language()
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text

def set_language(code: str) -> None:
    if code in {l["code"] for l in SUPPORTED_LANGS}:
        set_setting("language", code)

def get_language() -> str:
    return get_setting("language", "ru")
Ключевые моменты:

Ключи вида раздел.элемент: btn.save, settings.tab.reminder.

Fallback: запрошенный язык → DEFAULT_LANG → сам ключ.

Поддержка **kwargs для плейсхолдеров: t("sched.js_valid_simple", preview="...").

Количество ключей (~85)
Группы:

Префикс	Что описывает	Кол-во
btn.*	Кнопки (save, close, cancel, yes, no)	~5
settings.*	Окно настроек (title, tab.reminder, tab.general, tab.registration)	~5
reminder.*	Вкладка «Напоминание»	~25
general.*	Вкладка «Общие»	~20
reg.*	Вкладка «Регистрация»	~15
Итого: ~70–85 ключей.

Где используется
Файл	Что переведено
client/settings_dialog.py	Все три вкладки (ReminderTab, GeneralTab, RegistrationTab)
client/main.py	Частично — панель, трей, кнопки пока на русском хардкодом
client/registration_dialog.py	Не подключён — первый запуск на русском
client/unclosed_dialog.py	Не подключён — восстановление на русском
client/reminder.py	Частично — тексты напоминаний на русском
Полный список ключей
Кнопки:

btn.save — Сохранить / Save

btn.close — Закрыть / Close

btn.cancel — Отмена / Cancel

btn.yes — Да / Yes

btn.no — Нет / No

Окно настроек:

settings.title — Настройки / Settings

settings.tab.reminder — Напоминание / Reminder

settings.tab.general — Общие / General

settings.tab.registration — Регистрация / Registration

Напоминание:

reminder.source.personal — Персональные / Personal

reminder.source.global — Как у всех / Global

reminder.group.start — Напоминание о старте / Start reminder

reminder.enabled — Включить / Enable

reminder.threshold — Порог срабатывания / Threshold

reminder.threshold.hint — Минут активности без сессии / Minutes of activity without session

reminder.repeat — Интервал повторов / Repeat interval

reminder.repeat.hint — Через сколько минут повторять / Minutes between reminders

reminder.max_per_day — Максимум в день / Max per day

reminder.max_per_day.hint — Максимум напоминаний за день / Max reminders per day

reminder.group.eod — Конец дня / End of day

reminder.eod_hour — Час / Hour

reminder.eod_minute — Минуты / Minutes

reminder.eod.hint — Напоминание о завершении / Reminder to finish

reminder.eod_hour.zero — 0 = выключено / 0 = disabled

reminder.btn.reset_to_global — Сбросить к общим / Reset to global

reminder.btn.reset_to_global.tooltip — подсказка

reminder.reset.confirm_title — Подтверждение / Confirmation

reminder.reset.confirm_text — Текст подтверждения

reminder.status.local_only — Локальные / Local

reminder.status.synced — Синхронизированы / Synced

reminder.status.server_refused — Сервер отказал / Server refused

reminder.status.not_authorized — Не авторизован / Not authorized

reminder.status.server_error — Ошибка сервера / Server error

reminder.status.net_error — Ошибка сети / Network error

reminder.reset.not_registered — ПК не зарегистрирован

reminder.reset.not_linked — Сотрудник не привязан

reminder.reset.unauth — 401/403

reminder.reset.server_error — 500

reminder.reset.success — Успех

reminder.reset.partial — Частичный успех

Общие:

general.group.autostart — Автозапуск / Autostart

general.autostart — Автозапуск при входе / Autostart at login

general.autostart.hint — подсказка

general.autostart.error — Ошибка

general.group.appearance — Внешний вид / Appearance

general.theme — Тема / Theme

general.theme.hint — подсказка

general.theme.light — Светлая / Light

general.theme.dark — Тёмная / Dark

general.theme.system — Системная / System

general.group.language — Язык / Language

general.lang — Язык / Language

general.lang.hint — подсказка

general.lang.restart_title — Требуется перезапуск / Restart required

general.lang.restart_text — Текст

general.group.connectivity — Связь / Connectivity

general.server_url — Адрес сервера / Server URL

general.server_url.hint — подсказка

general.cert_fingerprint — Отпечаток сертификата / Certificate fingerprint

general.cert_fingerprint.hint — подсказка

general.btn.check_connection — Проверить соединение / Check connection

general.btn.save_server — Сохранить адрес / Save server

general.conn.checking — Проверка... / Checking...

general.conn.ok — Соединение установлено / Connection OK

general.conn.fail — Ошибка / Failed

general.conn.no_server — Сервер недоступен / Server unavailable

general.conn.saved — Сохранено / Saved

general.group.notifications — Уведомления / Notifications

general.notif.offline — Уведомлять о потере связи / Notify on offline

general.notif.offline.hint — подсказка

general.notif.eod — Уведомлять о конце дня / Notify at end of day

general.notif.eod.hint — подсказка

Регистрация:

reg.group.info — Информация / Info

reg.uid — UID / UID

reg.hostname — Hostname / Hostname

reg.server — Сервер / Server

reg.group.server — Сервер / Server

reg.server_url — Адрес сервера / Server URL

reg.server_url.hint — подсказка

reg.cert_fingerprint — Отпечаток сертификата / Certificate fingerprint

reg.cert_fingerprint.hint — подсказка

reg.bootstrap_token — Bootstrap-токен / Bootstrap token

reg.bootstrap_token.hint — подсказка

reg.btn.save_server — Сохранить адрес / Save server

reg.btn.check_connection — Проверить соединение / Check connection

reg.server.saved — Сохранено / Saved

reg.server.checking — Проверка... / Checking...

reg.server.ok — Соединение установлено / Connection OK

reg.server.fail — Ошибка / Failed

reg.reregister — Перерегистрировать / Re-register

reg.reregister.warn — Предупреждение

reg.reregister.confirm_title — Подтверждение

reg.reregister.confirm_text — Текст

reg.reregister.done_title — Готово

reg.reregister.done_text — Текст

reg.reregister.no_uid — Нет UID

reg.reregister.error — Ошибка

Как добавить новую строку
Придумать ключ по схеме раздел.элемент.

Добавить в TRANSLATIONS:

python
"btn.download": {"ru": "Скачать", "en": "Download"},
Использовать: from .i18n import t; label.setText(t("btn.download")).

Как добавить новый язык
Добавить в SUPPORTED_LANGS:

python
{"code": "de", "label": "Deutsch", "short": "DE"},
К каждому ключу добавить "de": "...".

Fallback: запрошенный → DEFAULT_LANG (ru) → сам ключ.

Retranslate (смена языка без перезапуска)
Текущее состояние: не реализован для главного окна. Требует перезапуска.

Что планируется:

retranslateUi() в MainWindow и SettingsDialog.

При смене языка — вызвать retranslate.

Обновить все строки (кнопки, метки, тултипы).

Что уже работает:

SettingsDialog._on_language_changed — делает retranslate всех вкладок.

Вызывается при смене языка в GeneralTab.

Что НЕ работает:

Главное окно (main.py) — строки хардкодом.

Трей — строки хардкодом.

RegistrationDialog — строки хардкодом.

UnclosedSessionDialog — строки хардкодом.

Связь с темами
Тема и язык — независимые настройки.

Обе хранятся в config.json.

Обе применяются при старте клиента.

Обе меняются через SettingsDialog → GeneralTab.

Известные проблемы и решения
Проблема	Причина	Решение
Тёмная тема не покрывает панель	Inline-стили	Убрать inline, setObjectName + QSS
Title bar светлый в тёмной теме	QSS не работает с системным заголовком	WinAPI DwmSetWindowAttribute
Переключение языка требует перезапуска	Нет retranslate главного окна	В планах
Некоторые строки не переводятся	Хардкод в main.py	Добавить ключи, использовать t()
Иконка ⓘ показывается без перевода	Нет проверки .hint	Показывать только если есть перевод
«Крокозябры» в QSS	Неверная кодировка файла	UTF-8 без BOM
Логи
text
2026-10-02 09:20:00 INFO tracker.themes Applied dark theme
2026-10-02 09:20:10 INFO tracker.i18n Language set to ru
2026-10-02 09:20:15 INFO tracker.settings Theme saved: dark
Ключевые решения
QSS для тем. Гибко, поддерживает кастомные элементы.

setObjectName + QSS. Не inline-стили.

theme_signals.theme_changed. Реакция на смену темы.

Свой словарь i18n. Без Babel/gettext.

Два языка: RU + EN. Достаточно.

Fallback на DEFAULT_LANG. Если перевода нет — русский.

Fallback на сам ключ. Дырки видны.

Retranslate только для SettingsDialog. Главное окно — в планах.

Хранение в config.json. Тема и язык — настройки клиента.

Иконка ⓘ только если есть перевод. Не показываем пустые тултипы.

Ссылки на код
запросить: client/themes.py — _CUSTOM_LIGHT, _CUSTOM_DARK, apply_theme, theme_signals, SUPPORTED_THEMES

запросить: client/i18n.py — TRANSLATIONS, t, set_language, get_language, SUPPORTED_LANGS

запросить: client/settings_dialog.py — использование t(), _on_language_changed, _hint()

запросить: client/main.py — применение темы, обработка theme_changed

запросить: client/config.py — get_theme_code, get_language_code, set_setting

запросить: client/registration_dialog.py — не использует i18n

запросить: client/unclosed_dialog.py — не использует i18n

запросить: client/reminder.py — частично использует i18n

Открытые вопросы / чего не хватает
нет данных: полный список ключей — только в client/i18n.py, ~85 штук.

нет данных: есть ли ещё ключи, добавленные после 22.09.2026.

нет данных: реализован ли retranslate в SettingsDialog — да, для вкладок.

нет данных: как показывается иконка ⓘ без перевода — не показывается.

не решено: нужен ли retranslate главного окна — да, в планах.

не решено: как быть с хардкодом в main.py, registration_dialog.py, unclosed_dialog.py.

не решено: нужен ли третий язык.

не решено: нужна ли тёмная тема для title bar.

не решено: как быть с иконками трея в тёмной теме.

не решено: должен ли язык клиента браться из client-config или из config.json.

не решено: писать ли автотест на «все ключи из кода есть в TRANSLATIONS».

не решено: как обрабатывать динамические строки (ошибки, сообщения).

не решено: нужна ли поддержка RTL-языков (арабский, иврит) — нет.

не решено: нужна ли поддержка множественного числа (plural) — нет.

Готово. Один файл выше. Следующий по индексу — 04_CLIENT\08_AUTOSTART_UPDATE.md.