# HANDOFF_INSTALLER.md — передача: серверный инсталлятор

Статус: бриф для следующего чата
Дата: 2026-10-12
Связанные: 06_DEPLOY/03_WINDOWS_SETUP.md, 06_DEPLOY/06_INSTALLER.md,
           06_DEPLOY/01_DOCKER.md, 06_DEPLOY/02_NGINX_TLS.md, HANDOFF.md

## Задача

Построить `TrackerServerSetup.exe` — единый установщик сервера
«Трекера» для Windows-машины (LAN). По аналогии с клиентским
`TrackerSetup.exe`, но для развёртывания серверной части.

### Что делает инсталлятор на чистой Windows

1. Проверяет, установлен ли Docker Desktop. Если нет — ставит
   (winget install Docker.DockerDesktop), ждёт готовности демона.
2. Разворачивает файлы проекта Tracker (архив).
3. Создаёт `.env`:
   - генерирует SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY
     (через secrets.token_urlsafe);
   - DATABASE_URL — стандартное значение;
   - не перезатирает существующий .env, если пользователь не
     попросит (для повторной установки / апгрейда).
4. Проверяет сертификаты certs/fullchain.pem + certs/privkey.pem:
   - если нет — выпускает self-signed (openssl в контейнере или
     через логику SCP на LAN-IP);
   - CN = 127.0.0.1, SAN = localhost, 127.0.0.1, LAN-IP,
     hostname, tracker, tracker.local.
5. Запускает `docker compose up -d --build` и ждёт healthy.
6. Настраивает firewall: правило `Tracker HTTPS`, TCP:443.
7. Создаёт ярлыки: «Tracker — админка» (браузер), «Tracker SCP»
   (запуск control.gui_main через python venv).
8. При повторном запуске — режим «Обновить сервер» (без сброса БД,
   только пересборка контейнеров).

### Что НЕ входит

- Windows Server (только Windows 10/11 x64).
- Linux/macOS.
- Установка PostgreSQL отдельно (используется контейнер).

## Что уже готово (переиспользуем)

| Компонент | Путь | Роль |
|---|---|---|
| deploy.json | D:\tracker\deploy.json | server_url, cert_cn, cert_san, hostname_alias |
| control/deploy.py | control/deploy.py | load/save/get/set_values |
| control/build.py | control/build.py | шаблон Inno + PyInstaller + prepare_client_env |
| control/build_tab.py | control/build_tab.py | UI: чекбоксы, QThread, лог |
| control/network_tab.py | control/network_tab.py | LAN-IP, firewall, перевыпуск cert, hosts |
| client/installer.iss | client/installer.iss | шаблон Inno для копирования |
| docker-compose.yml | docker-compose.yml | db + api + nginx, volume pgdata |
| server/entrypoint.sh | server/entrypoint.sh | миграции Alembic + gunicorn |
| server/Dockerfile | server/Dockerfile | python:3.11-slim |
| .env | D:\tracker\.env | SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY |

## Что нужно решить

1. Где разворачивать: C:\Program Files\Tracker\ (UAC) или
   D:\tracker\ (без UAC). Скорее — второе.
2. Docker Desktop: winget / оффлайн-инсталлятор / вручную.
3. Сертификат: генерить внутри инсталлятора или через SCP-логику.
4. Firewall: UAC-запрос (netsh advfirewall).
5. Обновление сервера: второй режим, без сброса pgdata.
6. Дистрибутив: Inno с [Files] из D:\tracker\* или архив .zip,
   который инсталлятор распаковывает.

## Файлы, которые нужно прислать в следующем чате

Обязательно:
1. docs/HANDOFF.md
2. docs/00_INDEX.md
3. docs/06_DEPLOY/03_WINDOWS_SETUP.md
4. docs/06_DEPLOY/01_DOCKER.md
5. docs/06_DEPLOY/02_NGINX_TLS.md
6. docs/06_DEPLOY/06_INSTALLER.md
7. docs/06_DEPLOY/05_UPDATES.md
8. docker-compose.yml
9. server/Dockerfile
10. server/entrypoint.sh
11. .env (структура, без значений)
12. deploy.json
13. client/installer.iss
14. control/config.py
15. control/deploy.py
16. control/build.py
17. control/build_tab.py
18. control/network_tab.py
19. control/gui.py (как подключаются вкладки)
20. список файлов control/ (нужно увидеть, где выпуск сертификата)

Желательно:
21. control/services_tab.py
22. control/admin.py
23. control/publish.py

## Команды (шпаргалка)

Сервер:
  cd D:\tracker
  docker compose ps
  docker compose logs api --tail=30
  docker compose down && docker compose up -d --build

Админка:
  https://192.168.0.35/admin/login
  логин admin, пароль = ADMIN_API_KEY из .env

Сборка клиента:
  SCP - вкладка «Сборка» - «Собрать полностью» + «Опубликовать версию»

Сборка сервера (предстоит):
  D:\tracker\installer\TrackerServerSetup.exe

## Состояние проекта на 2026-10-12

- Готовность: ~97%. P0 «Публикация версий через UI» закрыт.
- Сервер: FastAPI + PostgreSQL 16 + nginx + Docker, миграции до
  a1b2c3d4e5f6, 7 задач планировщика.
- Админка: 75+ роутов, страница /admin/versions.
- Клиент: PyQt6, обновление с проверкой sha256, диалог согласия.
- SCP: вкладки Статус, Сертификат, Сервисы, Сеть, Сборка, Админ,
  публикация версий.
- KB опубликован: https://erohin-a.github.io/tracker/
