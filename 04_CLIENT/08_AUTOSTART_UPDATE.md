# Автозапуск и обновление
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 04_CLIENT\01_ARCHITECTURE.md, 04_CLIENT\06_SETTINGS_UI.md, 06_DEPLOY\05_UPDATES.md, 06_DEPLOY\06_INSTALLER.md

## Назначение
Описать два связанных механизма клиента: автозапуск при входе в систему и автообновление версий. Это карта для администратора, который раскатывает обновления, и для разработчика, который дорабатывает инфраструктуру.

## Содержание

### Часть 1: Автозапуск

#### Зачем нужен
- Клиент должен запускаться автоматически при входе сотрудника в систему.
- Сотрудник не должен каждый раз вручную открывать Tracker.
- Трей-иконка сразу появляется в панели.

#### Управление
- Checkbox «Автозапуск при входе в систему» в главном окне.
- Дублирующий checkbox на вкладке «Общие» в `SettingsDialog`.
- Функция `set_autostart(enabled: bool)` в `client/autostart.py`.

#### Windows
**Механизм:** реестр, ветка `HKCU`.

**Ключ:**
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run

text

**Имя записи:** `Tracker` (или `TrackerClient`).

**Значение:** путь к исполняемому файлу:
- В dev-режиме: `python -m client.main` с полным путём к Python.
- В prod: `C:\Users\<user>\AppData\Local\Tracker\Tracker.exe`.

**Реализация:**
```python
import winreg

def set_autostart(enabled: bool) -> bool:
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE,
    )
    try:
        if enabled:
            winreg.SetValueEx(key, "Tracker", 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, "Tracker")
            except FileNotFoundError:
                pass
        return True
    finally:
        winreg.CloseKey(key)
Особенности:

HKCU — не требует прав администратора.

Работает для текущего пользователя.

Если сотрудник переустанавливает Windows — запись теряется.

Linux
Механизм: .desktop-файл в ~/.config/autostart/.

Путь: ~/.config/autostart/tracker.desktop.

Содержимое:

ini
[Desktop Entry]
Type=Application
Name=Tracker
Exec=/path/to/tracker
X-GNOME-Autostart-enabled=true
Hidden=false
Реализация:

python
from pathlib import Path

def set_autostart(enabled: bool) -> bool:
    desktop_file = Path.home() / ".config" / "autostart" / "tracker.desktop"
    if enabled:
        desktop_file.parent.mkdir(parents=True, exist_ok=True)
        desktop_file.write_text(desktop_content, encoding="utf-8")
    else:
        if desktop_file.exists():
            desktop_file.unlink()
    return True
macOS
Не реализовано. В планах — LaunchAgents.

Ошибки автозапуска
Ошибка	Причина	Решение
Запись не создаётся	Нет прав на реестр	Запуск от пользователя, не от admin
general.autostart.error	Исключение при записи	Показать сообщение
Автозапуск не срабатывает	Антивирус блокирует	Добавить в исключения
Путь к .exe неверный	Изменился путь установки	Переустановить клиент
Двойной запуск	Старая запись в реестре	Удалить вручную
Проверка автозапуска
Windows:

powershell
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" | Select-Object Tracker
Linux:

bash
cat ~/.config/autostart/tracker.desktop
Связь с UI
GeneralTab.autostart (QCheckBox).

При изменении — set_autostart(checked).

При ошибке — general.autostart.error через QMessageBox.

Состояние сохраняется в config.json → autostart_enabled.

При старте клиента состояние восстанавливается из config.json.

Часть 2: Обновление
Зачем нужно
Раскатывать новые версии клиента на все ПК.

Не ходить по каждому ПК вручную.

Обеспечить, чтобы все клиенты были на актуальной версии.

Компоненты
Компонент	Файл	Назначение
UpdateChecker	client/updater.py	Проверка версии через /api/v1/version
apply_update	client/updater.py	Скачивание и установка обновления
client_versions	server/models.py	Таблица версий на сервере
GET /api/v1/version	server/main.py	Эндпоинт для проверки
Форма публикации	/admin/...	Не реализована (P0)
Как работает проверка
Клиент при старте (и периодически) вызывает GET /api/v1/version.

Сервер отвечает:

json
{
  "latest_version": "1.1.0",
  "download_url": "https://server/downloads/TrackerSetup-1.1.0.exe",
  "mandatory": false,
  "release_notes": "Исправлен баг с ..."
}
Клиент сравнивает latest_version с CLIENT_VERSION (из .env или config.py).

Если новее — показывает уведомление.

Если mandatory = true — требует обновления.

client/updater.py
Класс UpdateChecker:

Проверяет версию.

Возвращает UpdateInfo или None.

Функция apply_update:

Скачивает файл обновления в DOWNLOAD_DIR (%APPDATA%\Tracker\updates\).

Проверяет целостность (размер, хеш).

Запускает установщик.

Завершает клиент для установки.

Логика скачивания:

httpx с теми же настройками (pinning, CA).

Прогресс-бар в UI (обсуждалось, не реализовано).

Retry при ошибках сети.

Таблица client_versions
Поле	Тип	Описание
id	Integer PK	
version	String(32), unique	«1.1.0»
release_date	DateTime	
download_url	String(512)	
mandatory	Boolean	Обязательное обновление?
release_notes	Text	Что нового
created_at	DateTime	
GET /api/v1/version
Возвращает последнюю версию из client_versions (по release_date DESC).

Если версий нет:

Возвращает текущую версию или 404.

Клиент не показывает уведомление.

UI-индикация
При старте: если версия новее — QMessageBox с latest_version и release_notes.

Если mandatory: кнопка «Позже» отсутствует, только «Обновить сейчас».

В настройках: на вкладке «Общие» (обсуждалось, не реализовано) — блок «Доступно обновление».

В трее: иконка с восклицательным знаком (обсуждалось, не реализовано).

Что НЕ реализовано
Публикация версий через UI — P0. Сейчас нужно вручную добавлять запись в client_versions через SQL.

Установщик клиента (Inno Setup) — P0. Без него нечего распространять.

Автоматическая установка — обсуждалась, не реализована.

Откат обновления — не реализован.

Проверка подписи .exe — не реализована.

Канареечное обновление (сначала на 1 ПК, потом на всех) — не реализовано.

Обновление через SCP — обсуждалось, не реализовано.

Планируемая форма публикации версий
Путь: /admin/versions/new.

Поля:

Загрузка .exe файла.

Версия (String, например «1.1.0»).

Mandatory (checkbox).

Release notes (textarea).

Логика:

Файл сохраняется в server/static/downloads/.

Запись создаётся в client_versions.

download_url формируется автоматически.

Клиенты при следующей проверке видят новую версию.

Проверка обновления на сервере
SQL:

sql
SELECT version, release_date, download_url, mandatory
FROM client_versions
ORDER BY release_date DESC
LIMIT 1;
Вручную добавить версию:

sql
INSERT INTO client_versions (version, release_date, download_url, mandatory, release_notes)
VALUES ('1.1.0', NOW(), 'https://server/downloads/TrackerSetup-1.1.0.exe', false, 'Исправлен баг ...');
Безопасность
HTTPS: скачивание только по HTTPS.

CA bundle: тот же ca.pem, что и для API.

Pinning: если задан TRACKER_PIN, применяется.

Подпись .exe: не проверяется (P1).

Хеш файла: не проверяется (P1).

Известные проблемы
Проблема	Причина	Решение
Уведомление не появляется	Нет записей в client_versions	Добавить вручную или через UI (P0)
Скачивание падает	Сертификат/сеть	Проверить ca.pem, retry
Установка не запускается	Нет прав	Запуск от пользователя
Клиент не перезапускается	Не реализован авто-перезапуск	Вручную
«Обновление доступно» каждый раз	Версия не обновляется после установки	Проверить CLIENT_VERSION в .env
CLIENT_VERSION
Читается из os.environ.get("TRACKER_VERSION", "1.0.0").

Указывается в client/.env.

Должна совпадать с версией в client_versions после установки.

Используется в /api/v1/computers/register (поле client_version).

Используется в client_versions на сервере.

Связь с SCP
BuildTab (в планах) — сборка .exe и установщика.

AdminTab (в планах) — публикация версий.

Текущая реализация — только просмотр сертификата.

Связь автозапуска и обновления
После установки обновления клиент должен перезапуститься.

Автозапуск гарантирует, что после перезагрузки клиент поднимется.

Если обновление mandatory — старый клиент должен перестать работать.

Логи
text
2026-10-02 09:00:00 INFO tracker.updater version check: current=1.0.0 latest=1.1.0
2026-10-02 09:00:01 INFO tracker.updater update available, mandatory=False
2026-10-02 09:00:05 INFO tracker.updater downloading to C:\Users\...\Tracker\updates\TrackerSetup-1.1.0.exe
2026-10-02 09:00:15 INFO tracker.updater download complete, size=12500000
2026-10-02 09:00:16 INFO tracker.updater launching installer
2026-10-02 09:00:16 INFO tracker.updater shutting down for update
Проверка версии вручную
powershell
curl.exe -k https://127.0.0.1/api/v1/version
Ожидаемый ответ:

json
{
  "latest_version": "1.0.0",
  "download_url": "",
  "mandatory": false,
  "release_notes": null
}
Если версий нет — поля пустые.

Ключевые решения
Реестр для Windows автозапуска. HKCU — без прав администратора.

.desktop для Linux. Стандартный механизм.

GET /api/v1/version для проверки. Просто и достаточно.

client_versions для хранения. Гибко, можно добавлять версии.

mandatory для обязательных обновлений. Контроль версий.

Скачивание в %APPDATA%\Tracker\updates\. Не требует прав.

Установка через внешний установщик. Клиент не сам себя обновляет.

Публикация через UI — в планах (P0). Пока вручную.

Установщик (Inno Setup) — в планах (P0). Критично для распространения.

Ссылки на код
запросить: client/autostart.py — set_autostart

запросить: client/updater.py — UpdateChecker, apply_update

запросить: client/config.py — CLIENT_VERSION, DOWNLOAD_DIR

запросить: client/settings_dialog.py — GeneralTab.autostart

запросить: client/main.py — install_signal_handlers, обработка обновления

запросить: server/main.py — GET /api/v1/version

запросить: server/models.py — модель ClientVersion

запросить: server/web_admin.py — (форма публикации — не реализована)

запросить: client/.env — TRACKER_VERSION

Открытые вопросы / чего не хватает
нет данных: точный путь к .exe в реестре для prod-сборки.

нет данных: реализован ли retry при скачивании обновления.

нет данных: есть ли прогресс-бар при скачивании.

нет данных: реализован ли авто-перезапуск после установки.

нет данных: проверяется ли подпись .exe — нет.

не решено: нужен ли авто-перезапуск после обновления.

не решено: как быть с mandatory-обновлениями (блокировать клиент или нет).

не решено: нужна ли канареечная раскатка (сначала на 1 ПК).

не решено: публикация версий через UI (P0).

не решено: установщик Inno Setup (P0).

не решено: обновление через SCP (обсуждалось).

не решено: откат обновления (rollback).

не решено: проверка целостности .exe (хеш или подпись).

не решено: работает ли автозапуск на macOS — не реализован.

не решено: как быть с антивирусами при скачивании .exe.

не решено: нужна ли поддержка delta-обновлений (только изменения).

Готово. Один файл выше. Следующий по индексу — 04_CLIENT\09_REGISTRATION.md.