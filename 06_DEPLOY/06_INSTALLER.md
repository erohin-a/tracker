# Установщик
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 05_SCP\03_BUILD.md, 04_CLIENT\09_REGISTRATION.md, 04_CLIENT\08_AUTOSTART_UPDATE.md

## Назначение
Описать процесс создания и работы установщика клиента Tracker: PyInstaller, Inno Setup, экран bootstrap-токена, копирование `ca.pem`, ярлыки, автозапуск. Это карта для разработчика, который собирает установщик, и для администратора, который раскатывает клиент на ПК сотрудников.

## Содержание

### Зачем нужен установщик
- Клиент на Python + PyQt6 не может работать без Python.
- Установщик упаковывает всё в один `.exe`.
- Сотрудник запускает один файл — и клиент готов к работе.
- Без установщика нельзя раздать клиент 50+ сотрудникам.

### Два этапа сборки

#### Этап 1. PyInstaller
- Собирает Python-приложение в папку `client/dist/Tracker/`.
- Внутри: `Tracker.exe`, `_internal/` (DLL, библиотеки), `ca.pem`.

#### Этап 2. Inno Setup
- Упаковывает папку `client/dist/Tracker/` в единый `TrackerSetup.exe`.
- Добавляет: экран bootstrap-токена, ярлыки, автозапуск.

### Параметры PyInstaller

```powershell
pyinstaller --onedir --noconsole --name Tracker ^
  --icon=client/icon.ico ^
  --add-data "client/ca.pem;." ^
  --upx-dir="" ^
  client/main.py
Почему так:

Параметр	Значение	Причина
--onedir	Папка, не один файл	Быстрее стартует, лучше для антивирусов
--noconsole	Без консоли	Клиент работает в трее
--name Tracker	Имя .exe	Tracker.exe
--icon	Иконка	client/icon.ico
--add-data	ca.pem в корень	Для HTTPS
--upx-dir=""	Отключить UPX	UPX ломает PyQt6 DLL
Что получается:

text
client/dist/Tracker/
├── Tracker.exe
├── ca.pem
└── _internal/
    ├── PyQt6/
    ├── cryptography/
    ├── httpx/
    ├── pynput/
    ├── keyring/
    └── ...
Возможные проблемы PyInstaller:

Проблема	Причина	Решение
ModuleNotFoundError	Модуль не подтянут	--hidden-import
PyQt6 не запускается	Нет Qt plugin	--add-data для platforms/
Антивирус блокирует	Эвристика	Подписать .exe
UPX ломает DLL	Сжатие	--upx-dir=""
ca.pem не найден	Не добавлен	--add-data "client/ca.pem;."
Inno Setup
Назначение: упаковать client/dist/Tracker/ в TrackerSetup.exe.

Файл: installer.iss в корне D:\tracker\ (не создан, планируется).

Параметры установки:

ini
[Setup]
AppName=Tracker
AppVersion=1.0.0
DefaultDirName={localappdata}\Tracker
PrivilegesRequired=lowest
OutputBaseFilename=TrackerSetup-1.0.0
Compression=lzma2
SolidCompression=yes
OutputDir=client\dist
Ключевые параметры:

Параметр	Значение	Причина
DefaultDirName	{localappdata}\Tracker	Установка без прав администратора
PrivilegesRequired	lowest	Не требует UAC
Compression	lzma2	Максимальное сжатие
OutputDir	client\dist	Где будет .exe
Что устанавливается:

Все файлы из client/dist/Tracker/ в {localappdata}\Tracker\.

Ярлык в Startup.

Ярлык в меню «Пуск».

Экран bootstrap-токена
Назначение: сотрудник вводит bootstrap-токен прямо при установке.

Реализация в Inno Setup:

CreateInputQueryPage или CreateInputOptionPage.

Одно поле: «Bootstrap-токен».

Если пусто — клиент покажет RegistrationDialog при первом запуске.

Планируемая логика:

Пользователь запускает TrackerSetup.exe.

Установщик показывает экран «Введите bootstrap-токен».

Сотрудник вводит токен (полученный от админа).

Установщик записывает токен в %APPDATA%\Tracker\bootstrap.txt.

Клиент при первом запуске читает токен и регистрируется автоматически.

Файл bootstrap.txt:

Путь: %APPDATA%\Tracker\bootstrap.txt.

Формат: обычный текст, одна строка — токен.

Удаляется после успешной регистрации.

Копирование ca.pem
Что: сертификат сервера для проверки HTTPS.

Откуда: client/ca.pem (вшит в установщик через PyInstaller).

Куда: %APPDATA%\Tracker\ca.pem.

Зачем: клиент использует его для httpx при проверке сертификата.

Реализация в Inno Setup:

Файл ca.pem уже внутри client/dist/Tracker/.

После установки копируется в {app}.

Клиент при старте ищет ca.pem в %APPDATA%\Tracker\ca.pem.

Важно: нужно скопировать из {app}\ca.pem в %APPDATA%\Tracker\ca.pem.

Возможные проблемы:

Проблема	Причина	Решение
ca.pem не найден	Не в --add-data	Добавить в PyInstaller
SSL: CERTIFICATE_VERIFY_FAILED	Не скопирован в %APPDATA%	Добавить в Inno Setup
ca.pem устарел	Сертификат перевыпущен	Пересобрать установщик
Ярлыки
Ярлык в Startup:

ini
[Icons]
Name: "{userstartup}\Tracker"; Filename: "{app}\Tracker.exe"
Ярлык в меню «Пуск»:

ini
Name: "{userprograms}\Tracker"; Filename: "{app}\Tracker.exe"
Ярлык на рабочем столе (опционально):

ini
Name: "{userdesktop}\Tracker"; Filename: "{app}\Tracker.exe"; Tasks: desktopicon
Что делают ярлыки:

Startup — автозапуск при входе в систему.

Меню «Пуск» — для ручного запуска.

Рабочий стол — опционально.

Автозапуск
Через ярлык в Startup:

Inno Setup создаёт ярлык в {userstartup}.

Windows автоматически запускает его при входе.

Не требует прав администратора.

Альтернатива — реестр:

HKCU\Software\Microsoft\Windows\CurrentVersion\Run.

Клиент может сам прописать себя через set_autostart(enabled=True).

Inno Setup может прописать сразу.

Что лучше: ярлык в Startup — проще, стандартнее, не требует прав.

Что НЕ реализовано
installer.iss — не создан.

Экран bootstrap-токена — не реализован.

Копирование ca.pem в %APPDATA% — не реализовано.

Ярлыки в Startup и меню «Пуск» — не реализованы.

Проверка, что сервер доступен — не реализована.

Проверка наличия прав — не реализована.

Проверка, что клиент не запущен — не реализована.

Авто-запуск клиента после установки — не реализован.

Удаление предыдущей версии перед установкой — не реализовано.

Сохранение config.json при обновлении — не реализовано.

Планируемый installer.iss
Структура:

[Setup] — общие параметры.

[Files] — что копировать.

[Icons] — ярлыки.

[Run] — что запустить после установки.

[Code] — экран bootstrap-токена.

[UninstallDelete] — что удалить при деинсталляции.

Секция [Files]:

ini
[Files]
Source: "client\dist\Tracker\*"; DestDir: "{app}"; Flags: recursesubdirs
Секция [Run]:

ini
[Run]
Filename: "{app}\Tracker.exe"; Description: "Запустить Tracker"; Flags: postinstall nowait skipifsilent
Секция [UninstallDelete]:

ini
[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: files; Name: "{userappdata}\Tracker\config.json"
Проверка установщика
Проверить .exe:

powershell
Get-Item D:\tracker\client\dist\TrackerSetup-1.0.0.exe
Установить на чистой машине:

Запустить TrackerSetup.exe.

Ввести bootstrap-токен (если есть).

Дождаться завершения.

Проверить %LOCALAPPDATA%\Tracker\ — должны быть Tracker.exe, _internal/.

Проверить %APPDATA%\Tracker\ — должны быть ca.pem, bootstrap.txt.

Проверить ярлык в Startup: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\.

Перезагрузить ПК — клиент должен запуститься автоматически.

Проверить регистрацию: клиент появляется в /admin/computers.

Связь с обновлениями
Обновление через установщик:

Разработчик собирает новую версию TrackerSetup-1.1.0.exe.

Публикует через /admin/versions/new (P0, не реализовано).

Клиент при проверке /api/v1/version видит новую версию.

Скачивает TrackerSetup-1.1.0.exe.

Запускает установщик.

Установщик закрывает старый клиент, устанавливает новый.

Данные (config.json, data.db) сохраняются.

Что нужно сохранить при обновлении:

%APPDATA%\Tracker\config.json.

%APPDATA%\Tracker\data.db.

%APPDATA%\Tracker\credentials.enc.

%APPDATA%\Tracker\ca.pem.

Что нужно обновить:

%LOCALAPPDATA%\Tracker\Tracker.exe.

%LOCALAPPDATA%\Tracker\_internal\.

Известные проблемы
Проблема	Причина	Решение
Антивирус блокирует	Эвристика	Подписать .exe
ModuleNotFoundError в .exe	Не подтянут модуль	--hidden-import
PyQt6 не запускается	Нет Qt plugin	--add-data
ca.pem не найден	Не скопирован в %APPDATA%	Добавить в Inno Setup
Ярлык в Startup не создаётся	Inno Setup ошибка	Проверить {userstartup}
Клиент не запускается	Нет прав	PrivilegesRequired=lowest
bootstrap.txt не читается	Путь неверный	%APPDATA%\Tracker\bootstrap.txt
В Setup долго распаковывается	--onefile	Использовать --onedir
config.json перезаписывается	Установщик не сохраняет	Добавить в installer.iss
Два клиента в трее	Не закрыт старый	Добавить проверку в установщик
Быстрая диагностика
powershell
# Проверить, что установщик собран
Get-Item D:\tracker\client\dist\TrackerSetup-*.exe

# Проверить, что PyInstaller собрал папку
Get-ChildItem D:\tracker\client\dist\Tracker\

# Проверить, что ca.pem внутри
Test-Path D:\tracker\client\dist\Tracker\ca.pem

# Проверить, что клиент запускается из папки
D:\tracker\client\dist\Tracker\Tracker.exe
Что НЕ реализовано
installer.iss — не создан.

Экран bootstrap-токена — не реализован.

Копирование ca.pem в %APPDATA% — не реализовано.

Ярлыки — не реализованы.

Проверка доступности сервера — не реализована.

Авто-запуск после установки — не реализован.

Удаление предыдущей версии — не реализовано.

Сохранение config.json при обновлении — не реализовано.

Подпись .exe — не реализована.

Проверка SHA-256 — не реализована.

Канареечная раскатка — не реализована.

Обновление без переустановки — не реализовано.

Деинсталляция — не реализована.

Ключевые решения
PyInstaller --onedir. Быстрее стартует, лучше для антивирусов.

UPX отключён. Стабильность важнее размера.

Inno Setup с PrivilegesRequired=lowest. Установка без прав администратора.

Установка в {localappdata}. Не требует прав, не конфликтует с другими пользователями.

Экран bootstrap-токена — опция. Можно вшить, можно ввести вручную.

ca.pem вшивается в установщик. Не нужно раздавать отдельно.

Ярлык в Startup. Автозапуск при входе в систему.

Сборка через SCP BuildTab — в планах. Пока вручную.

Публикация через UI — P0. Пока вручную через SQL.

Не подписываем .exe (пока). В планах — P1.

Ссылки на код
запросить: control/gui.py — BuildTab (заглушка)

запросить: client/main.py — точка входа для PyInstaller

запросить: client/requirements.txt — зависимости

запросить: client/icon.ico — иконка

запросить: client/ca.pem — для вшивания

запросить: installer.iss — скрипт Inno Setup (не создан)

запросить: server/models.py — ClientVersion

запросить: server/main.py — GET /api/v1/version

запросить: server/web_admin.py — форма публикации (не реализована)

Открытые вопросы / чего не хватает
нет данных: полный текст installer.iss — не создан.

нет данных: реализован ли BuildTab в SCP — нет, заглушка.

нет данных: где хранится bootstrap.txt — %APPDATA%\Tracker\bootstrap.txt (по контексту).

нет данных: есть ли client/icon.ico — нужно проверить.

нет данных: тестировался ли .exe на чистой машине — нет.

нет данных: работает ли установщик без прав администратора — заявлено, не проверено.

не решено: как передавать bootstrap-токен в Inno Setup (#define или файл).

не решено: делать ли проверку подписи .exe — P1.

не решено: нужен ли авто-перезапуск после обновления.

не решено: как быть с канареечной раскаткой.

не решено: нужна ли публикация через UI (P0) — да.

не решено: как избежать ложных срабатываний антивирусов.

не решено: подписывать ли .exe корпоративным сертификатом.

не решено: нужна ли поддержка macOS/Linux в установщике.

не решено: как обновлять ca.pem на уже установленных клиентах (без переустановки).

не решено: должен ли установщик создавать ярлык на рабочем столе.

не решено: логировать ли сборку в audit_log (сейчас только stdout).

Готово. Один файл выше. Следующий по индексу — 07_QUALITY\01_TESTING.md.