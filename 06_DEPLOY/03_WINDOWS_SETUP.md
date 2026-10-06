# Установка на Windows
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 06_DEPLOY\01_DOCKER.md, 06_DEPLOY\02_NGINX_TLS.md, 09_OPS\01_RUNBOOK.md

## Назначение
Пошаговая инструкция первичной установки сервера «Трекер» на Windows: от требований до первого входа в админку. Это карта для администратора, который разворачивает систему, и для разработчика, который готовит дистрибутив.

## Содержание

### Требования

#### Аппаратные
| Параметр | Минимум | Рекомендуется |
|---|---|---|
| RAM | 4 ГБ | 8 ГБ |
| Диск | 20 ГБ | 50 ГБ SSD |
| CPU | 2 ядра | 4 ядра |

#### Программные
| Компонент | Версия | Назначение |
|---|---|---|
| Windows | 10/11 (64-bit) | ОС |
| Docker Desktop | 4.x+ | Контейнеры |
| OpenSSL | 3.x (Light) | Генерация сертификатов |
| Python | 3.11 или 3.12 | Для клиента и патчеров |
| PowerShell | 5.1 или 7.x | Команды |
| Git (опционально) | — | Если проект в репозитории |

#### Сетевые
- Статический IP или домен (для прода).
- Порт **443** свободен.
- Порт **80** — не используется (занят HTTP.sys).
- Интернет для скачивания образов Docker (первый запуск).

### Шаг 1. Установка Docker Desktop

1. Скачать с официального сайта: `https://www.docker.com/products/docker-desktop`.
2. Установить с настройками по умолчанию.
3. Перезагрузить ПК.
4. Запустить Docker Desktop, дождаться зелёной иконки в трее.
5. Проверить:
```powershell
docker info
docker compose version
Настройки Docker Desktop (рекомендуется):

General → Use WSL 2 based engine.

Resources → RAM: 4+ ГБ, CPU: 2+.

General → Start Docker Desktop when you sign in.

Возможные проблемы:

Проблема	Решение
WSL 2 installation is incomplete	wsl --install в PowerShell (от админа), перезагрузка
Virtualization is not enabled	Включить VT-x/AMD-V в BIOS
Docker Desktop не запускается	Проверить Hyper-V, обновить Windows
Шаг 2. Установка OpenSSL
Способ 1 (рекомендуется):

powershell
winget install ShiningLight.OpenSSL.Light
Способ 2 (вручную):

Скачать Win64 OpenSSL Light с https://slproweb.com/products/Win32OpenSSL.html.

Установить в C:\Program Files\OpenSSL-Win64\.

Проверка:

powershell
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" version
Ожидаемый вывод: OpenSSL 3.x.x ....

Шаг 3. Получение проекта
Если проект в Git:

powershell
cd D:\
git clone <repo-url> tracker
cd tracker
Если проект в архиве:

Распаковать в D:\tracker.

Убедиться, что структура: D:\tracker\server\, D:\tracker\client\, D:\tracker\control\.

Проверка структуры:

powershell
Get-ChildItem D:\tracker
Должны быть: docker-compose.yml, server/, client/, control/, certs/.

Шаг 4. Создание .env
Файл: D:\tracker\.env.

Содержимое:

ini
SECRET_ENCRYPTION_KEY=<44-символьный Fernet-ключ>
JWT_SECRET=<случайный токен>
ADMIN_API_KEY=<случайный токен>
Генерация ключей:

powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "import secrets; print(secrets.token_urlsafe(48))"
Создание файла:

powershell
$env_content = @"
SECRET_ENCRYPTION_KEY=<вставить>
JWT_SECRET=<вставить>
ADMIN_API_KEY=<вставить>
"@
[System.IO.File]::WriteAllText("D:\tracker\.env", $env_content, [System.Text.UTF8Encoding]::new($false))
Важно:

Файл в UTF-8 без BOM.

Без пробелов вокруг =.

Файл в .gitignore (не коммитить).

Не пересылать по открытым каналам.

Шаг 5. Создание TLS-сертификатов
powershell
cd D:\tracker\certs
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -x509 -newkey rsa:4096 `
  -keyout privkey.pem -out fullchain.pem -days 365 -nodes `
  -subj "/CN=localhost" `
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" `
  -addext "basicConstraints=critical,CA:TRUE"
Проверка:

powershell
Get-ChildItem D:\tracker\certs
Должны быть: fullchain.pem, privkey.pem.

Для прода: заменить на Let's Encrypt или корпоративный.

Шаг 6. Первый запуск сервера
powershell
cd D:\tracker
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
Ожидаемый вывод: три контейнера db, api, nginx — все Up.

Первый запуск может занять 3–5 минут:

Скачивание образов postgres:16-alpine, nginx:1.27-alpine, python:3.11-slim.

Сборка api.

Инициализация БД.

Применение Alembic-миграций.

Шаг 7. Проверка API
powershell
curl.exe -k https://localhost/api/v1/version
Ожидаемый ответ: JSON (может быть пустой, если версий нет).

Если ошибка — проверить логи:

powershell
docker compose logs api --tail=50
docker compose logs nginx --tail=50
docker compose logs db --tail=30
Шаг 8. Первый вход в админку
Открыть браузер: https://localhost/admin/login.

Предупреждение о самоподписанном сертификате — «Дополнительно» → «Перейти на localhost».

Логин: admin.

Пароль: значение ADMIN_API_KEY из .env.

Если таблица admin_users пуста — система перенаправит на /admin/setup.

Создать первого администратора.

Логин ≥ 3 символов, пароль ≥ 8 символов.

Шаг 9. Первичная настройка
Порядок:

Отделы (/admin/departments) — создать отделы.

Сотрудники (/admin/employees) — ФИО, 1C ID, отдел.

Календарь (/admin/calendar) — отметить праздники, рабочие субботы.

Настройки (/admin/settings) — проверить:

report_timezone — часовой пояс.

workday_start_hour — начало рабочего дня.

activity_gap_minutes — порог паузы.

stale_session_hours — автозакрытие.

Bootstrap-токены (/admin/tokens) — выпустить токены для ПК.

Шаг 10. Подготовка клиента
Собрать установщик клиента (см. 05_SCP\03_BUILD.md, 06_DEPLOY\06_INSTALLER.md) — в разработке.

Временный обходной путь — запуск клиента в dev-режиме:

powershell
cd D:\tracker
python -m venv client\.venv
client\.venv\Scripts\Activate.ps1
pip install -r client\requirements.txt
python -m client.main
Ввести bootstrap-токен в RegistrationDialog.

Проверить, что ПК появился в /admin/computers.

Шаг 11. Финальная проверка
powershell
# 1. Docker запущен
docker info | Select-String "Server Version"

# 2. Контейнеры живы
docker compose ps

# 3. API отвечает
curl.exe -k https://localhost/api/v1/version

# 4. БД видит таблицы
docker compose exec -T db psql -U tracker -d tracker -c "\dt"

# 5. Админка открывается
Start-Process "https://localhost/admin/login"
Все пять шагов успешны — сервер работает.

Настройка автозапуска Docker Desktop
Вариант 1 (встроенный):

Docker Desktop → Settings → General → «Start Docker Desktop when you sign in».

Вариант 2 (через реестр):

powershell
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $regPath -Name "Docker Desktop" -Value $dockerPath
Почему важно: после перезагрузки Windows Docker Desktop не запускается сам. Если сервер должен работать постоянно — автозапуск обязателен.

Настройка автозапуска контейнеров
В docker-compose.yml:

yaml
services:
  db:
    restart: unless-stopped
  api:
    restart: unless-stopped
  nginx:
    restart: unless-stopped
unless-stopped — контейнер поднимается при старте Docker, если не был остановлен вручную.

Не нужно вручную запускать docker compose up после каждой перезагрузки.

Открытие порта 443 в брандмауэре
Если сервер доступен из локальной сети:

powershell
New-NetFirewallRule -DisplayName "Tracker HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
Проверка:

powershell
Get-NetFirewallRule -DisplayName "Tracker HTTPS"
Известные проблемы
Проблема	Причина	Решение
Cannot connect to Docker daemon	Docker Desktop не запущен	Запустить Docker Desktop, подождать 60 сек
WSL 2 installation is incomplete	WSL не установлен	wsl --install, перезагрузка
Port 443 is already in use	Другая служба	netstat -ano | findstr :443, остановить службу
Port 80 is already in use	Windows HTTP.sys	Использовать только 443
openssl.exe not found	OpenSSL не установлен	winget install ShiningLight.OpenSSL.Light
.env не читается	Неверная кодировка	UTF-8 без BOM, WriteAllText с UTF8Encoding($false)
ModuleNotFoundError: server	Неверный build context	context: . в docker-compose.yml
unknown directive "CN=localhost"	Мусор в nginx.conf	Перезаписать файл
Клиент «офлайн»	Сервер недоступен	curl.exe -k https://localhost/api/v1/version
getaddrinfo failed	IPv6 vs IPv4	https://127.0.0.1 в client/.env
SSL: CERTIFICATE_VERIFY_FAILED	Нет ca.pem	Скопировать fullchain.pem в %APPDATA%\Tracker\ca.pem
Hostname mismatch	Сертификат без SAN	Перевыпустить с subjectAltName
Что делать, если ничего не помогает
Сохранить бэкап БД:

powershell
docker compose exec -T db pg_dump -U tracker tracker > backup_$(Get-Date -Format yyyyMMdd_HHmm).sql
Полностью пересобрать:

powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 30
docker compose ps
docker compose logs api --tail=50
Не удалять volume pgdata. Сначала бэкап.

Собрать диагностику:

powershell
docker compose logs api --tail=200 > D:\tracker\_diag_api.log
docker compose logs nginx --tail=100 > D:\tracker\_diag_nginx.log
docker compose logs db --tail=100 > D:\tracker\_diag_db.log
docker compose ps > D:\tracker\_diag_ps.log
Прислать логи разработчику.

Проверка после перезагрузки
powershell
# 1. Docker Desktop запустился
docker info | Select-String "Server Version"

# 2. Контейнеры поднялись
docker compose ps

# 3. API отвечает
curl.exe -k https://localhost/api/v1/version

# 4. Клиенты синхронизируются
docker compose logs api --tail=20 | Select-String "heartbeat"
Что НЕ реализовано
Автоматический установщик сервера (все шаги — вручную).

Скрипт первичной установки (setup.ps1).

Проверка требований перед установкой.

Автонастройка брандмауэра.

Автозапуск Docker Desktop через установщик.

Проверка свободного места на диске.

Резервное копирование по расписанию (см. 06_DEPLOY\04_BACKUP.md).

Ключевые решения
Docker Desktop + WSL 2. Основной способ развёртывания на Windows.

OpenSSL через winget. Простая установка.

Все секреты — в .env. UTF-8 без BOM.

Сертификаты — self-signed для локальной разработки. Let's Encrypt — для прода.

Только 443. Порт 80 занят Windows HTTP.sys.

Автозапуск Docker Desktop. Иначе после перезагрузки сервер не работает.

restart: unless-stopped. Контейнеры поднимаются автоматически.

Первый вход — admin / ADMIN_API_KEY. Если admin_users пуста — /admin/setup.

Диагностика через docker compose logs. Стандартные команды.

Ссылки на код
запросить: docker-compose.yml — три контейнера

запросить: server/Dockerfile — образ api

запросить: server/nginx.conf — конфиг nginx

запросить: D:\tracker\.env — секреты

запросить: certs/fullchain.pem, certs/privkey.pem — сертификаты

запросить: client/.env — конфиг клиента

запросить: client/requirements.txt — зависимости клиента

Открытые вопросы / чего не хватает
нет данных: есть ли скрипт автоматической установки — нет.

нет данных: тестировалась ли установка на чистой Windows — не подтверждено.

нет данных: сколько занимает первый запуск (скачивание образов + сборка).

нет данных: минимальные требования к CPU/RAM — заявлены, но не измерены.

не решено: нужен ли PowerShell-скрипт setup.ps1 для автоматизации.

не решено: как быть с портом 80 — использовать только 443 или сделать редирект.

не решено: нужна ли интеграция с Windows Task Scheduler для бэкапов.

не решено: как настраивать брандмауэр автоматически.

не решено: нужен ли docker-compose.override.yml для dev-режима.

не решено: как быть с антивирусами при сборке образа.

не решено: нужна ли поддержка Windows Server (не Desktop).

не решено: как быть с прокси в корпоративной сети.

не решено: нужна ли настройка NAT/bridge для нестандартных сетей.

не решено: как быть с установкой на нескольких ПК (несколько серверов).

не решено: должен ли сервер работать без интернета после первой установки.

не решено: нужен ли офлайн-набор образов Docker для установки без сети.

Готово. Один файл выше. Следующий по индексу — 06_DEPLOY\04_BACKUP.md.