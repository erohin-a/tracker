# Сборка клиента
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 05_SCP\01_OVERVIEW.md, 06_DEPLOY\06_INSTALLER.md, 04_CLIENT\08_AUTOSTART_UPDATE.md

## Назначение
Описать процесс сборки клиентского установщика Tracker: PyInstaller, Inno Setup, вшивание `ca.pem` и bootstrap-токена. Это карта для разработчика, который настраивает сборку, и для администратора, который раскатывает клиент на ПК сотрудников.

## Содержание

### Зачем нужна сборка
- Клиент написан на Python + PyQt6. Без сборки сотрудник должен вручную ставить Python, venv, зависимости.
- Установщик `TrackerSetup.exe` — единый файл для распространения.
- Внутри: `.exe`, `ca.pem`, опционально bootstrap-токен.
- После установки: ярлык в Startup, автозапуск, регистрация.

### Что входит в установщик
| Компонент | Назначение |
|---|---|
| `Tracker.exe` (или `Tracker/` папка) | Скомпилированный клиент (PyInstaller) |
| `ca.pem` | Сертификат сервера для HTTPS |
| `bootstrap.txt` (опционально) | Bootstrap-токен (для первого запуска без ввода) |
| `client/.env` (опционально) | `TRACKER_SERVER_URL`, `TRACKER_PIN` |
| Ярлык в Startup | Автозапуск при входе в систему |
| Ярлык в меню «Пуск» | Для ручного запуска |

### PyInstaller

**Параметры:**
```powershell
pyinstaller --onedir --noconsole --name Tracker ^
  --icon=client/icon.ico ^
  --add-data "client/ca.pem;." ^
  --upx-dir="" ^
  client/main.py
Почему --onedir, а не --onefile:

--onefile распаковывает архив во временную папку при каждом запуске — медленно.

--onedir — быстрее стартует, легче отлаживать.

--onedir лучше для антивирусов (нет самозапуска из temp).

Почему upx=False:

UPX иногда ломает PyQt6 DLL.

Антивирусы чаще ругаются на UPX-сжатые бинарники.

Размер не критичен для локального сервера.

Почему --noconsole:

Клиент работает в трее, консольное окно не нужно.

Иконка:

client/icon.ico — иконка для .exe и трея.

Должна содержать несколько разрешений (16, 32, 48, 256).

Что попадает в дистрибутив:

text
client/dist/Tracker/
├── Tracker.exe
├── ca.pem
├── _internal/           # DLL, библиотеки Python
│   ├── PyQt6/
│   ├── cryptography/
│   └── ...
└── ...
Inno Setup
Назначение: упаковать client/dist/Tracker/ в единый TrackerSetup.exe.

Файл скрипта: installer.iss.

Планируемые шаги:

Проверка, что client/dist/Tracker/Tracker.exe существует.

Установка в {localappdata}\Tracker (без прав администратора).

Экран ввода bootstrap-токена (опционально).

Запись bootstrap.txt в %APPDATA%\Tracker\ (если введён).

Копирование ca.pem в %APPDATA%\Tracker\.

Ярлык в Startup ({userstartup}\Tracker.lnk).

Ярлык в меню «Пуск».

Запуск клиента после установки.

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
Экран с bootstrap-токеном:

CreateInputQueryPage или CreateInputOptionPage.

Одно поле: «Bootstrap-токен».

Если пусто — клиент покажет RegistrationDialog при первом запуске.

Ярлык в Startup:

ini
[Icons]
Name: "{userstartup}\Tracker"; Filename: "{app}\Tracker.exe"
Name: "{userprograms}\Tracker"; Filename: "{app}\Tracker.exe"
BuildTab в SCP (заглушка)
Текущее состояние: вкладка «📦 Сборка клиента» — заглушка с текстом «⏳ Вкладка в разработке».

Планируемое содержимое:

Элемент	Назначение
Чекбокс «Собрать EXE (PyInstaller)»	Запуск PyInstaller
Чекбокс «Собрать установщик (Inno Setup)»	Запуск ISCC
Поле «Bootstrap-токен по умолчанию»	Вшивается в установщик
Поле «URL сервера по умолчанию»	TRACKER_SERVER_URL
Поле «Версия»	1.0.0
Кнопка «Собрать»	Запуск сборки
Прогресс-бар	Ход сборки
Лог сборки	QPlainTextEdit
Ссылка на папку с дистрибутивом	client/dist/
Планируемая логика:

Проверить venv (client/.venv).

Проверить наличие PyInstaller.

Запустить PyInstaller через subprocess.

Дождаться завершения.

Запустить Inno Setup (ISCC.exe installer.iss).

Собрать TrackerSetup.exe.

Показать путь и открыть папку.

Публикация версий
Проблема: после сборки установщик нужно сделать доступным для клиентов.

Текущее состояние: публикация версий через UI не реализована (P0).

Обходной путь:

Собрать TrackerSetup.exe вручную.

Положить в server/static/downloads/.

Вручную добавить запись в client_versions:

sql
INSERT INTO client_versions (version, release_date, download_url, mandatory, release_notes)
VALUES ('1.1.0', NOW(), 'https://server/downloads/TrackerSetup-1.1.0.exe', false, '...');
Планируемая форма /admin/versions/new:

Загрузка .exe.

Версия.

Mandatory (checkbox).

Release notes (textarea).

Сохранение файла + запись в client_versions.

Процесс сборки (планируемый)
Разработчик: обновляет CLIENT_VERSION в client/.env.

Разработчик: запускает BuildTab в SCP.

SCP: активирует venv, запускает PyInstaller.

SCP: получает client/dist/Tracker/.

SCP: запускает ISCC с installer.iss.

SCP: получает client/dist/TrackerSetup-1.1.0.exe.

Разработчик: загружает установщик через /admin/versions/new.

Сервер: сохраняет файл, добавляет запись в client_versions.

Клиенты: при следующей проверке /api/v1/version видят новую версию.

Проверка сборки
Проверить, что .exe запускается:

powershell
cd D:\tracker\client\dist\Tracker
.\Tracker.exe
Проверить, что ca.pem внутри:

Открыть client/dist/Tracker/ — должен быть ca.pem.

Проверить установщик:

Запустить TrackerSetup.exe на чистой машине.

Проверить %APPDATA%\Tracker\ — должны появиться config.json, ca.pem.

Проверить Startup — должен быть ярлык.

Запустить клиент — должен показать RegistrationDialog.

Известные проблемы
Проблема	Причина	Решение
ModuleNotFoundError в .exe	PyInstaller не подтянул модуль	Добавить --hidden-import
PyQt6 не запускается	Отсутствует Qt plugin	Добавить --add-data для platforms/
Антивирус блокирует .exe	Эвристика	Подписать .exe, добавить в исключения
UPX ломает DLL	Сжатие	--upx-dir="" (отключить UPX)
ca.pem не найден	Не добавлен в --add-data	Добавить --add-data "client/ca.pem;."
Ярлык в Startup не создаётся	Inno Setup ошибка	Проверить {userstartup}
Клиент не запускается после установки	Нет прав	PrivilegesRequired=lowest
bootstrap.txt не читается	Путь неверный	%APPDATA%\Tracker\bootstrap.txt
В Setup долго распаковывается	--onefile	Использовать --onedir
Логи
text
2026-10-02 11:00:00 INFO tracker.build PyInstaller started
2026-10-02 11:00:30 INFO tracker.build PyInstaller finished: client/dist/Tracker/
2026-10-02 11:00:31 INFO tracker.build ISCC started
2026-10-02 11:00:45 INFO tracker.build ISCC finished: client/dist/TrackerSetup-1.1.0.exe
2026-10-02 11:00:45 INFO tracker.build Build complete
Связь с другими компонентами
С 06_DEPLOY\06_INSTALLER.md: детали Inno Setup, ярлыки, автозапуск.

С 04_CLIENT\08_AUTOSTART_UPDATE.md: публикация версий, client_versions, /api/v1/version.

С 05_SCP\02_CERTIFICATES.md: после перевыпуска сертификата — пересборка установщика с новым ca.pem.

С 04_CLIENT\09_REGISTRATION.md: bootstrap-токен в установщике.

Что НЕ реализовано
BuildTab в SCP — заглушка.

Публикация версий через UI — P0.

Проверка подписи .exe — не реализована.

Автоматическая сборка по тегу в git — нет.

Канареечная раскатка — нет.

Авто-пересборка при смене сертификата — нет.

Прогресс-бар сборки — нет.

Лог сборки в UI — нет.

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

Готово. Один файл выше. Следующий по индексу — 05_SCP\04_ADMIN.md.