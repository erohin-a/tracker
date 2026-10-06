<!-- Часть 929 из 1409 -->
# ...docstring...
*Хлебные крошки:* ...docstring...

[◀ Склейка](928_Skleyka.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](930_part.md)

---

# ...docstring...
import json
import logging
import socket

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (...)

from . import db, http_client, reminder_settings
from .autostart import set_autostart
from .config import (
    BASE_DIR, SERVER_URL,
    get_setting, set_setting,
    get_server_url, get_cert_fingerprint,
    get_language_code, get_theme_code,
)
from .i18n import t, SUPPORTED_LANGS, set_language, get_language
from .registration import get_computer_uid

log = logging.getLogger("tracker.settings_dialog")


class ReminderTab(QWidget):
    # ... логика с i18n и тултипами
Честно говоря, придётся много написать. Постараюсь быть эффективным.
Один момент: пользователь сказал "программа для других неизвестная и необходимо где это возможно и в клиентской части и в админской делать всплывающие окошки что это и для чего". Значит, добавляю tooltip через .setToolTip(t("...hint")) или, что лучше, добавляю helper-функцию hint_label(t_key) которая возвращает QLabel с ? и tooltip.
Хорошо. Пишу.
Также добавлю кнопку «Проверить соединение» — она делает GET на /api/v1/version и показывает результат. Нужно учесть, что URL может быть ещё не сохранён — тогда проверяем по введённому.
Пишу все три части.
Дам все три части в одном сообщении + патч main.py. Постараюсь быть компактным, но не в ущерб функциональности.
Также надо подумать — при смене языка в диалоге ставим в config.json новое значение и предлагаем перезапуск. А при смене темы — применяем сразу через themes.apply_theme (передаём QApplication.instance()).
Для этого settings_dialog получит доступ к app. Проще всего через QApplication.instance().
Пишу.
Насчёт длинны. Пусть будет так:
Скрипт 1: part1 (ReminderTab) — ~130 строк
Скрипт 2: part2 (GeneralTab) — ~200 строк
Скрипт 3: part3 (RegistrationTab + SettingsDialog) — ~250 строк
Скрипт 4: склейка + проверка
Скрипт 5: патч main.py
Начнём.
Также мне надо перепроверить сигнатуру reminder_settings.get_all() и .set_many() — они у нас есть в проекте, использовались в текущем settings_dialog.py. Значит, ок.
Двигаюсь.
Отлично, база для Спринта A готова. Теперь большой блок — переписываем settings_dialog.py целиком.
Почему частями: файл получится ~600 строк. По твоему опыту — большие here-string'и в PowerShell ломаются. Поэтому пишу в 3 .tmp файла, потом склеиваю. Если что-то пойдёт не так — увидим, какая часть поломалась.
________________________________________
Скрипт 1 — Часть 1: заголовок + ReminderTab
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$part1 = @'
