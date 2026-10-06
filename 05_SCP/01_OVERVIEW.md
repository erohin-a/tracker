# SCP — обзор
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 05_SCP\02_CERTIFICATES.md, 05_SCP\03_BUILD.md, 05_SCP\04_ADMIN.md, 01_PRODUCT\05_SCP_UI.md

## Назначение
Описать SCP (Server Control Panel) на уровне архитектуры: зачем существует, как запускается, какие зависимости, что входит в его ответственность, а что — нет. Детали по вкладкам — в отдельных KB-файлах.

## Содержание

### Что такое SCP
- **Server Control Panel** — отдельное десктопное приложение на PyQt6.
- Работает **на том же ПК, где развёрнут сервер** (или имеет доступ к файлам `D:\tracker` и Docker).
- **Не веб-приложение.** Не путать с веб-админкой (`/admin/*`).
- **Не часть клиента.** Отдельный процесс, отдельная папка `control/`.
- **Не работает удалённо.** Только локально на сервере.

### Зачем нужен SCP
SCP закрывает операции уровня сервера, которые неудобно или опасно делать через веб-админку:

1. **Работа с TLS-сертификатами** — просмотр, обновление, экспорт `ca.pem`.
2. **Сборка клиента** — PyInstaller + Inno Setup (в разработке).
3. **Администрирование секретов** — сброс пароля веб-админа, `ADMIN_API_KEY` (в разработке).
4. **Просмотр состояния** — контейнеры, версия API, размер БД (в работе).

**Чего SCP НЕ делает:**
- Не управляет сотрудниками, отделами, ПК — это в веб-админке.
- Не строит отчёты — это в веб-админке.
- Не редактирует настройки приложения — это в `/admin/settings`.
- Не работает по сети — только локально.

### Архитектура
D:\tracker
├── control/
│ ├── init.py # пустой, делает папку пакетом
│ ├── gui.py # основной файл: SCPWindow, вкладки
│ └── main.py # точка входа: from control.gui import main
├── certs/ # сертификаты (fullchain.pem, privkey.pem)
├── client/ # клиент (для сборки и ca.pem)
├── server/ # сервер (nginx.conf)
└── docker-compose.yml # для docker compose restart nginx

text

**Взаимодействие:**
- С сервером — **напрямую**, не через API: файлы, Docker CLI, SQL.
- С OpenSSL — через `subprocess`.
- С Docker — через `docker compose` CLI.
- С БД — не взаимодействует напрямую (только через файлы и Docker).

### Запуск

```powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m control.main
Особенности:

Использует тот же venv, что и клиент (client\.venv).

Требует Windows (пути зашиты как D:\tracker).

Требует OpenSSL в стандартном месте (C:\Program Files\OpenSSL-Win64\bin\openssl.exe).

Требует Docker Desktop запущенным (для перезапуска nginx).

Зависимости
Пакет	Зачем
PyQt6	GUI
cryptography	Чтение сертификатов (x509, hashes)
logging	Логи
subprocess	OpenSSL, Docker CLI
pathlib, shutil	Файловые операции
datetime	Даты сертификатов
Никаких собственных зависимостей. Всё уже есть в client/requirements.txt.

Главное окно (SCPWindow)
Класс QMainWindow, заголовок «Tracker SCP — Server Control Panel».

Размер: 900×700 по умолчанию.

QTabWidget с вкладками.

Статус-бар: путь BASE_DIR.

Текущие вкладки:

#	Вкладка	Статус
1	🔐 Сертификат (CertificateTab)	Реализована
2	📦 Сборка клиента (BuildTab)	Заглушка («В разработке»)
3	⚙ Администрирование (AdminTab)	Заглушка («В разработке»)
Планируемые (обсуждались):

Бэкапы (pg_dump).

Планировщик (просмотр scheduled_tasks).

Логи (docker compose logs).

Информация о контейнерах.

Константы и пути (control/gui.py)
python
BASE_DIR = Path(r"D:\tracker")
CERTS_DIR = BASE_DIR / "certs"
CLIENT_DIR = BASE_DIR / "client"
NGINX_CONF = BASE_DIR / "server" / "nginx.conf"
DOCKER_COMPOSE = BASE_DIR / "docker-compose.yml"
FULLCHAIN = CERTS_DIR / "fullchain.pem"
PRIVKEY = CERTS_DIR / "privkey.pem"
CLIENT_CA = CLIENT_DIR / "ca.pem"
OpenSSL:

python
OPENSSL_FALLBACKS = [
    r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
    r"C:\Program Files\OpenSSL\bin\openssl.exe",
    r"C:\OpenSSL-Win64\bin\openssl.exe",
    "openssl",  # если в PATH
]
Функция find_openssl() ищет первый существующий.

Docker-взаимодействие
docker_compose_restart(service) — subprocess.run(["docker", "compose", "restart", service], cwd=BASE_DIR, timeout=60).

docker_compose_ps() — docker compose ps (для вкладки «Информация»).

Ключевое: cwd=str(BASE_DIR) — иначе docker compose не найдёт docker-compose.yml.

Работа с сертификатами
Чтение: cryptography.x509.load_pem_x509_certificate.

Генерация: openssl req -x509 -newkey rsa:4096 ... через subprocess.

Бэкап: certs/backup_YYYYMMDD_HHMMSS/.

Откат: при ошибке openssl — восстановление из бэкапа.

Подробности — в 05_SCP\02_CERTIFICATES.md.

Логирование
logging.basicConfig(level=logging.INFO).

Logger tracker.scp.

Формат: %(asctime)s %(levelname)s %(name)s %(message)s.

Логи — в stdout (консоль) + UI-панель (QPlainTextEdit) на вкладках.

Обработка ошибок
Ошибка	Причина	Что видит админ
FileNotFoundError: openssl.exe	OpenSSL не установлен	Понятное сообщение с winget install
TimeoutExpired	openssl/docker не отвечает	«Timeout > N сек»
docker: command not found	Docker не в PATH	«docker не найден в PATH»
PermissionError	Нет прав на файл	Сообщение об ошибке
x509.ExtensionNotFound	Нет SAN в сертификате	Пустой список SAN
ssl.SSLCertVerificationError	Неверный сертификат	Показать отпечаток
Что НЕ реализовано
BuildTab — сборка .exe и установщика (P1).

AdminTab — сброс пароля, смена ADMIN_API_KEY (P1).

Вкладка «Информация» — состояние контейнеров (в работе).

Вкладка «Бэкапы» — pg_dump, ротация (P2).

Вкладка «Логи» — просмотр docker compose logs (P2).

Вкладка «Планировщик» — просмотр scheduled_tasks (P2).

Кнопка «Сохранить ca.pem в файл» — обсуждалась, не реализована.

Авто-детект «сертификат истекает» — обсуждалось, не реализовано.

Авто-перезапуск nginx при смене сертификата — есть checkbox, но реализация не проверена.

Проверка подписи .exe — не реализована.

Планируемые улучшения
Единая тёмная тема QSS для всех вкладок.

Прогресс-бар при сборке клиента.

Кнопка «Перезапустить API без rebuild».

Автопроверка свободного места на диске.

Просмотр audit_log за последние 24 часа.

Ключевые решения
SCP — отдельное приложение, не часть админки. Операции уровня сервера — отдельно от контента.

PyQt6 + тот же venv, что у клиента. Не плодим окружения.

Прямое взаимодействие с файлами/Docker/OpenSSL. Не через API — SCP локальный.

Три вкладки: Сертификат, Сборка, Админ. MVP.

OpenSSL через subprocess. Не используем Python-библиотеки для генерации (openssl надёжнее).

Бэкап сертификатов перед перевыпуском. Обязательно, с откатом.

cwd=BASE_DIR для docker compose. Иначе не находит docker-compose.yml.

BuildTab и AdminTab — заглушки. Не блокируют релиз.

Не работает удалённо. Только на сервере.

Ссылки на код
запросить: control/gui.py — SCPWindow, CertificateTab, BuildTab, AdminTab, RenewCertDialog, find_openssl, generate_certificate, backup_certs, docker_compose_restart

запросить: control/main.py — точка входа

запросить: control/__init__.py — пустой

запросить: certs/fullchain.pem, certs/privkey.pem — сертификаты

запросить: client/ca.pem — копия для клиента

запросить: server/nginx.conf — для перезапуска nginx

запросить: docker-compose.yml — для docker compose

запросить: client/requirements.txt — зависимости (PyQt6, cryptography)

Открытые вопросы / чего не хватает
нет данных: полный текст control/gui.py — реконструирован, но не показан целиком.

нет данных: реализована ли вкладка «Информация» (состояние контейнеров) — в работе.

нет данных: есть ли кнопка «Сохранить ca.pem в файл» — обсуждалась, возможно, не реализована.

нет данных: работает ли авто-откат при ошибке openssl — заявлен, не проверен.

нет данных: показывается ли понятная ошибка при отсутствии Docker — да, есть обработка FileNotFoundError.

не решено: использовать ли #define или отдельный файл для bootstrap-токена в Inno Setup.

не решено: делать ли SCP полностью на QSS тёмной темы.

не решено: нужен ли авто-детект «сертификат скоро истекает» (за 30 дней).

не решено: нужна ли в SCP кнопка «Перезапустить API без rebuild».

не решено: должен ли SCP уметь работать с удалённым сервером (SSH).

не решено: как быть с Linux-сервером (пути D:\tracker зашиты под Windows).

не решено: нужна ли в SCP вкладка «Бэкапы» (или через Windows Task Scheduler).

не решено: интегрировать ли SCP с updater (публикация версий).

не решено: логировать ли действия SCP в audit_log (сейчас только stdout).

Готово. Один файл выше. Следующий по индексу — 05_SCP\02_CERTIFICATES.md.