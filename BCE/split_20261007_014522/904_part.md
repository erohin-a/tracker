<!-- Часть 904 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Словарь переводов](903_Slovar_perevodov.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](905_Proverka_sintaksisa.md)

---

# ============================================================
TRANSLATIONS = {
    # ---------- Общие ----------
    "btn.save": {"ru": "Сохранить", "en": "Save"},
    "btn.close": {"ru": "Закрыть", "en": "Close"},
    "btn.cancel": {"ru": "Отмена", "en": "Cancel"},
    "btn.yes": {"ru": "Да", "en": "Yes"},
    "btn.no": {"ru": "Нет", "en": "No"},

    # ---------- Окно настроек ----------
    "settings.title": {"ru": "Настройки Tracker", "en": "Tracker Settings"},
    "settings.tab.reminder": {"ru": "Напоминание", "en": "Reminders"},
    "settings.tab.general": {"ru": "Общие", "en": "General"},
    "settings.tab.registration": {"ru": "Регистрация", "en": "Registration"},

    # ---------- Напоминание ----------
    "reminder.source.personal": {
        "ru": "Источник: персональные настройки (заданы администратором)",
        "en": "Source: personal settings (set by administrator)",
    },
    "reminder.source.global": {
        "ru": "Источник: глобальные настройки (значения по умолчанию)",
        "en": "Source: global settings (default values)",
    },
    "reminder.group.start": {
        "ru": "Напоминание о старте работы",
        "en": "Start-of-work reminder",
    },
    "reminder.enabled": {"ru": "Включить напоминание", "en": "Enable reminder"},
    "reminder.threshold": {"ru": "Порог срабатывания:", "en": "Trigger threshold:"},
    "reminder.threshold.hint": {
        "ru": "Сколько минут активности без запущенной сессии должно пройти до первого напоминания",
        "en": "How many minutes of activity without an active session before the first reminder",
    },
    "reminder.repeat": {"ru": "Интервал повторов:", "en": "Repeat interval:"},
    "reminder.repeat.hint": {
        "ru": "Если проигнорировали напоминание — через сколько минут напомнить снова",
        "en": "If ignored — after how many minutes to remind again",
    },
    "reminder.max_per_day": {
        "ru": "Максимум напоминаний за день:",
        "en": "Max reminders per day:",
    },
    "reminder.max_per_day.hint": {
        "ru": "Защита от спама. При превышении — больше не напоминаем до следующего дня",
        "en": "Anti-spam. Above this limit — no reminders until next day",
    },
    "reminder.group.eod": {
        "ru": "Уведомление о конце рабочего дня",
        "en": "End-of-day notification",
    },
    "reminder.eod_hour": {"ru": "Час срабатывания:", "en": "Hour:"},
    "reminder.eod_minute": {"ru": "Минуты:", "en": "Minute:"},
    "reminder.eod.hint": {
        "ru": "В это время, если сессия ещё идёт, покажем уведомление «Не забыли завершить день?»",
        "en": "At this time, if a session is still running, show a «Did you forget to finish?» notification",
    },
    "reminder.eod_hour.zero": {"ru": "0 = выключено", "en": "0 = disabled"},
    "reminder.btn.reset_to_global": {
        "ru": "Сбросить к общим",
        "en": "Reset to global",
    },
    "reminder.btn.reset_to_global.tooltip": {
        "ru": "Удалить персональные настройки. Будут применены глобальные значения.",
        "en": "Delete personal settings. Global values will be applied.",
    },
    "reminder.reset.confirm_title": {"ru": "Сбросить к общим", "en": "Reset to global"},
    "reminder.reset.confirm_text": {
        "ru": "Будут удалены персональные настройки, заданные администратором.\n\nПосле этого применятся глобальные значения. Продолжить?",
        "en": "Personal settings set by administrator will be deleted.\n\nGlobal values will be applied. Continue?",
    },
    "reminder.status.local_only": {
        "ru": "Сохранено локально. ПК не зарегистрирован — на сервер не отправлено.",
        "en": "Saved locally. PC not registered — not sent to server.",
    },
    "reminder.status.synced": {
        "ru": "OK: Сохранено и синхронизировано с сервером.",
        "en": "OK: Saved and synced with server.",
    },
    "reminder.status.server_refused": {
        "ru": "Сохранено локально. Сервер отказал: {detail}",
        "en": "Saved locally. Server refused: {detail}",
    },
    "reminder.status.not_authorized": {
        "ru": "Сохранено локально. ПК не авторизован — обратитесь к администратору.",
        "en": "Saved locally. PC not authorized — contact administrator.",
    },
    "reminder.status.server_error": {
        "ru": "Сохранено локально. Сервер ответил {code}.",
        "en": "Saved locally. Server replied {code}.",
    },
    "reminder.status.net_error": {
        "ru": "Сохранено локально. Ошибка сети: {err}",
        "en": "Saved locally. Network error: {err}",
    },
    "reminder.reset.not_registered": {
        "ru": "ПК не зарегистрирован",
        "en": "PC not registered",
    },
    "reminder.reset.not_linked": {
        "ru": "ПК не привязан к сотруднику — обратитесь к администратору.",
        "en": "PC not linked to employee — contact administrator.",
    },
    "reminder.reset.unauth": {
        "ru": "ПК не авторизован — обратитесь к администратору.",
        "en": "PC not authorized — contact administrator.",
    },
    "reminder.reset.server_error": {
        "ru": "Сервер вернул {code}. Сброс не выполнен.",
        "en": "Server replied {code}. Reset failed.",
    },
    "reminder.reset.success": {
        "ru": "OK: Персональные настройки удалены. Применены глобальные.",
        "en": "OK: Personal settings deleted. Global applied.",
    },
    "reminder.reset.partial": {
        "ru": "Удалено, но не удалось загрузить настройки ({code})",
        "en": "Deleted, but failed to reload ({code})",
    },

    # ---------- Общие ----------
    "general.group.autostart": {"ru": "Автозапуск", "en": "Autostart"},
    "general.autostart": {
        "ru": "Запускать Tracker при входе в систему",
        "en": "Run Tracker on system startup",
    },
    "general.autostart.hint": {
        "ru": "Клиент запустится автоматически после входа пользователя в Windows",
        "en": "Client will launch automatically after user logs into Windows",
    },
    "general.autostart.error": {
        "ru": "Не удалось изменить автозапуск. Проверьте права доступа.",
        "en": "Failed to change autostart. Check permissions.",
    },
    "general.group.appearance": {"ru": "Внешний вид", "en": "Appearance"},
    "general.theme": {"ru": "Тема:", "en": "Theme:"},
    "general.theme.hint": {
        "ru": "Цветовая схема интерфейса клиента. Применяется мгновенно.",
        "en": "Client UI color scheme. Applied instantly.",
    },
    "general.theme.light": {"ru": "Светлая", "en": "Light"},
    "general.theme.dark": {"ru": "Тёмная", "en": "Dark"},
    "general.theme.system": {"ru": "Системная", "en": "System"},
    "general.group.language": {"ru": "Язык интерфейса", "en": "UI language"},
    "general.lang": {"ru": "Язык:", "en": "Language:"},
    "general.lang.hint": {
        "ru": "Язык надписей в клиенте. Для применения требуется перезапуск.",
        "en": "Language of client labels. Restart required to apply.",
    },
    "general.lang.restart_title": {
        "ru": "Перезапуск клиента",
        "en": "Restart client",
    },
    "general.lang.restart_text": {
        "ru": "Язык изменён на «{lang}».\n\nДля применения требуется перезапуск клиента. Перезапустить сейчас?",
        "en": "Language changed to «{lang}».\n\nRestart is required. Restart now?",
    },
    "general.group.connectivity": {"ru": "Подключение", "en": "Connection"},
    "general.server_url": {"ru": "Адрес сервера:", "en": "Server URL:"},
    "general.server_url.hint": {
        "ru": "Полный адрес сервера, включая https://. Например: https://tracker.company.ru",
        "en": "Full server URL including https://. For example: https://tracker.company.ru",
    },
    "general.cert_fingerprint": {
        "ru": "Отпечаток сертификата:",
        "en": "Certificate fingerprint:",
    },
    "general.cert_fingerprint.hint": {
        "ru": "SHA-256 отпечаток сертификата сервера (64 hex-символа). Оставьте пустым, если не требуется pinning. Администратор подскажет значение.",
        "en": "SHA-256 fingerprint of server certificate (64 hex chars). Leave empty if pinning is not required. Administrator will provide the value.",
    },
    "general.btn.check_connection": {
        "ru": "Проверить соединение",
        "en": "Check connection",
    },
    "general.btn.save_server": {
        "ru": "Сохранить адрес",
        "en": "Save server URL",
    },
    "general.conn.checking": {"ru": "Проверяем...", "en": "Checking..."},
    "general.conn.ok": {
        "ru": "OK: сервер отвечает, версия {version}",
        "en": "OK: server responds, version {version}",
    },
    "general.conn.fail": {
        "ru": "Ошибка: сервер недоступен ({err})",
        "en": "Error: server unavailable ({err})",
    },
    "general.conn.no_server": {
        "ru": "Укажите адрес сервера",
        "en": "Enter server URL",
    },
    "general.conn.saved": {
        "ru": "Адрес сохранён. Перезапустите клиент для применения.",
        "en": "URL saved. Restart client to apply.",
    },
    "general.group.notifications": {
        "ru": "Уведомления",
        "en": "Notifications",
    },
    "general.notif.offline": {
        "ru": "Показывать тост при потере связи с сервером",
        "en": "Show toast when connection lost",
    },
    "general.notif.offline.hint": {
        "ru": "Появится системное уведомление, если клиент не может связаться с сервером больше 2 циклов синхронизации",
        "en": "System notification appears if client cannot reach server for more than 2 sync cycles",
    },
    "general.notif.eod": {
        "ru": "Показывать напоминание о конце дня",
        "en": "Show end-of-day reminder",
    },
    "general.notif.eod.hint": {
        "ru": "В указанное время, если сессия ещё идёт, появится напоминание завершить рабочий день",
        "en": "At specified time, if session is still running, show end-of-day reminder",
    },

    # ---------- Регистрация ----------
    "reg.group.info": {
        "ru": "Информация о регистрации",
        "en": "Registration info",
    },
    "reg.uid": {"ru": "Computer UID:", "en": "Computer UID:"},
    "reg.hostname": {"ru": "Hostname:", "en": "Hostname:"},
    "reg.server": {"ru": "Сервер:", "en": "Server:"},
    "reg.group.server": {
        "ru": "Адрес сервера",
        "en": "Server address",
    },
    "reg.server_url": {"ru": "URL сервера:", "en": "Server URL:"},
    "reg.server_url.hint": {
        "ru": "Адрес сервера Tracker. Формат: https://host или https://IP. Если не указан — используется значение из файла .env",
        "en": "Tracker server address. Format: https://host or https://IP. If not set — value from .env is used",
    },
    "reg.cert_fingerprint": {
        "ru": "Отпечаток сертификата (опционально):",
        "en": "Certificate fingerprint (optional):",
    },
    "reg.cert_fingerprint.hint": {
        "ru": "SHA-256 отпечаток TLS-сертификата сервера (64 hex-символа). Оставьте пустым, если не нужен pinning. Админ выдаст значение командой на сервере.",
        "en": "SHA-256 fingerprint of the server TLS certificate (64 hex chars). Leave empty if pinning is not required. Admin will provide it.",
    },
    "reg.bootstrap_token": {
        "ru": "Bootstrap-токен:",
        "en": "Bootstrap token:",
    },
    "reg.bootstrap_token.hint": {
        "ru": "Одноразовый токен от администратора для регистрации ПК. Используется только при первой регистрации. Если ПК уже зарегистрирован — можно оставить пустым.",
        "en": "One-time token from administrator to register PC. Used only at first registration. If PC is already registered — leave empty.",
    },
    "reg.btn.save_server": {
        "ru": "Сохранить адрес",
        "en": "Save server URL",
    },
    "reg.btn.check_connection": {
        "ru": "Проверить соединение",
        "en": "Check connection",
    },
    "reg.server.saved": {
        "ru": "Адрес сохранён. Перезапустите клиент для применения.",
        "en": "URL saved. Restart client to apply.",
    },
    "reg.server.checking": {"ru": "Проверяем...", "en": "Checking..."},
    "reg.server.ok": {
        "ru": "OK: сервер отвечает, версия {version}",
        "en": "OK: server responds, version {version}",
    },
    "reg.server.fail": {
        "ru": "Ошибка: {err}",
        "en": "Error: {err}",
    },
    "reg.reregister": {
        "ru": "Перерегистрировать компьютер",
        "en": "Re-register computer",
    },
    "reg.reregister.warn": {
        "ru": "Перерегистрация удалит текущий ключ клиента. Понадобится новый bootstrap-токен от администратора.",
        "en": "Re-registration will delete the current client key. A new bootstrap token from administrator will be required.",
    },
    "reg.reregister.confirm_title": {
        "ru": "Перерегистрация",
        "en": "Re-registration",
    },
    "reg.reregister.confirm_text": {
        "ru": "Компьютер: {uid}...\n\nКлюч доступа будет удалён. UID компьютера сохранится, чтобы администратор мог разрешить перерегистрацию именно для этого ПК.\n\nПродолжить?",
        "en": "Computer: {uid}...\n\nAccess key will be deleted. Computer UID will be kept so administrator can allow re-registration for this specific PC.\n\nContinue?",
    },
    "reg.reregister.done_title": {"ru": "Готово", "en": "Done"},
    "reg.reregister.done_text": {
        "ru": "Ключ доступа удалён. UID компьютера сохранён.\n\nШаги для завершения перерегистрации:\n1. Попросите администратора в админке нажать «Разрешить перерегистрацию» для этого ПК.\n2. Закройте это окно и запустите Tracker заново.\n3. В появившемся окне введите новый токен от администратора.",
        "en": "Access key deleted. Computer UID kept.\n\nSteps to complete re-registration:\n1. Ask administrator to click «Allow re-registration» for this PC.\n2. Close this window and restart Tracker.\n3. In the appeared dialog, enter the new token from administrator.",
    },
    "reg.reregister.no_uid": {
        "ru": "Computer UID неизвестен. Обратитесь к администратору — требуется полная перерегистрация с нуля.",
        "en": "Computer UID unknown. Contact administrator — full re-registration required.",
    },
    "reg.reregister.error": {
        "ru": "Не удалось выполнить перерегистрацию: {err}",
        "en": "Failed to re-register: {err}",
    },
}


def set_language(code: str) -> bool:
    """Устанавливает текущий язык. Возвращает True при успехе."""
    global _current_lang
    if code in [l["code"] for l in SUPPORTED_LANGS]:
        _current_lang = code
        log.info("Language set to %s", code)
        return True
    return False


def get_language() -> str:
    """Возвращает текущий язык."""
    return _current_lang


def is_valid_lang(code: str) -> bool:
    """Проверяет поддержку языка."""
    return code in [l["code"] for l in SUPPORTED_LANGS]


def t(key: str, **kwargs) -> str:
    """
    Возвращает перевод по ключу.
    Если в строке есть {name} — подставит из kwargs.
    """
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(_current_lang) or entry.get("ru") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
'@

[System.IO.File]::WriteAllText("D:\tracker\client\i18n.py", $content, [System.Text.UTF8Encoding]::new($false))

Write-Host "OK: client/i18n.py создан" -ForegroundColor Green

