<!-- Часть 474 из 1409 -->
# Чистим лог
*Хлебные крошки:* Чистим лог

[◀ эмулируем импорт config через dotenv](473_emuliruem_import_config_cherez_dotenv.md) | [Оглавление](00_BCE_INDEX.md) | [Дефолт — 127.0.0.1, чтобы не упираться в IPv6-резолвинг localhost ▶](475_Defolt_127_0_0_1_chtoby_ne_upiratsya_v_IPv6_rezolving_localhost.md)

---

# Чистим лог
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

python -m client.main
Во втором окне PowerShell:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Что хотим увидеть:
text
tracker.http Using CA bundle: ...
tracker.http Pinning DISABLED
tracker.sync SyncWorker started; server=https://127.0.0.1    ? важно, что 127.0.0.1
tracker.sync Server reachable (HTTP 200)
httpx HTTP Request: POST https://127.0.0.1/api/v1/heartbeat "HTTP/1.1 200 OK"
На панели клиента — «? онлайн» зелёным.
________________________________________
Если снова офлайн — пришлите мне
Одним сообщением:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 20 -Encoding UTF8
docker compose logs api --tail=15
docker compose ps
По этим трём блокам точно пойму, что сломано.
________________________________________
Возможные причины и что делать
Симптом в логе	Причина	Решение
getaddrinfo failed	Резолвится localhost в ::1	Скрипт 2 выше (127.0.0.1)
SSL: CERTIFICATE_VERIFY_FAILED	Сертификат не покрывает 127.0.0.1	Проверить ca.pem, в нём должен быть SAN с IP:127.0.0.1
Connection refused	nginx не слушает 443	docker compose ps, docker compose logs nginx
Server reachable (HTTP 500)	Падает сервер	docker compose logs api --tail=40
Логи пустые после запуска	Клиент упал до логирования	Запустить в консоли без pythonw, увидеть traceback
Запускайте Скрипт 1 (диагностика), пришлите вывод — и сразу поймём, что именно у вас. Затем Скрипт 2 и 3.
Смотрим внимательно. В логах:
text
2026-09-17 22:47:01,479 INFO tracker.http Using CA bundle: C:\Users\erohin\AppData\Roaming\Tracker\ca.pem
2026-09-17 22:47:01,479 WARNING tracker.http Pinning DISABLED
2026-09-17 22:47:03,174 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed
Клиент .env говорит TRACKER_SERVER_URL=https://127.0.0.1 — уже правильно!
Но getaddrinfo failed — значит клиент всё ещё стучится на localhost, а не на 127.0.0.1.
Проверим причину. В config.py дефолт всё ещё https://tracker.example.com, но это дефолт, если .env не читается.
Проверим — возможно ли, что .env не читается при запуске клиента? Или наоборот.
Наиболее вероятные причины:
Клиент закешировал модуль config при первом импорте, а потом .env изменился — но нет, при рестарте процесса всё перечитывается.
.env читается из D:\tracker\client\.env, но клиент запускается из D:\tracker, где Path.cwd() = D:\tracker, а не D:\tracker\client.
Смотрим config.py клиента:
python
_candidates = [
    Path.cwd() / ".env",
    Path(__file__).resolve().parent / ".env",
    Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
]
Второй кандидат — Path(__file__).resolve().parent / ".env" = D:\tracker\client\.env. Должен читаться.
Проверим, но на самом деле — логи показывают, что .env читается. Строка Loaded .env from ... должна быть в логе. Но её нет в выводе!
Смотрим внимательно на логи:
text
2026-09-17 22:47:01,479 INFO tracker.http Using CA bundle: ...
2026-09-17 22:47:01,479 WARNING tracker.http Pinning DISABLED
2026-09-17 22:47:03,174 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed
Нет строки Loaded .env from .... Значит .env не читается!
Почему? Потому что в конфиге клиента try: с python-dotenv. Если dotenv не установлен — будет _log.error("python-dotenv not installed"). Но у нас он есть.
Может, дело в том, что клиент запускается как python -m client.main из D:\tracker, и Path.cwd() = D:\tracker. Первый кандидат — D:\tracker\.env (это корневой .env сервера! там SECRET_ENCRYPTION_KEY=...). Этот файл ЕСТЬ. Значит load_dotenv загружает его первым и останавливается.
Смотрим код:
python
for p in _candidates:
    if p.exists():
        load_dotenv(p, override=True)
        _loaded_from = p
        break
Да! Первый существующий кандидат — D:\tracker\.env (корневой .env сервера с SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY). Там нет TRACKER_SERVER_URL. Поэтому используется дефолт https://tracker.example.com ? getaddrinfo failed для tracker.example.com.
Вот она причина!
Решение: поменять порядок кандидатов, чтобы сначала читался .env рядом с config.py (client/.env), а корневой серверный .env не трогался.
Или — использовать другой префикс при чтении: явно client/.env приоритетнее.
Лучшее решение — поменять порядок в config.py:
python
_candidates = [
    Path(__file__).resolve().parent / ".env",   # client/.env — приоритет!
    Path.cwd() / ".env",
    Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
]
Или ещё жёстче — читать только client/.env и %APPDATA%/Tracker/.env, игнорируя cwd/.env.
Также добавить проверку: если в файле нет TRACKER_SERVER_URL — не считать его «загруженным», идти дальше.
Даю полный config.py с исправлением.
Плюс — дефолт изменить на https://127.0.0.1.
Кстати, нужно ещё учесть, что клиент уже запускается с client/.env, но фактически загружается D:\tracker\.env. После фикса — пойдёт на 127.0.0.1.
Отлично. Пишу полный config.py клиента.
Найдена настоящая причина — клиент читает не тот .env
Смотрите на лог:
text
2026-09-17 22:47:01,479 INFO tracker.http Using CA bundle: ...
2026-09-17 22:47:01,479 WARNING tracker.http Pinning DISABLED
2026-09-17 22:47:03,174 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed
Нет строки Loaded .env from .... Значит .env клиента не читается вообще, а используется дефолт https://tracker.example.com ? getaddrinfo failed.
Почему так? Смотрим client/config.py:
python
_candidates = [
    Path.cwd() / ".env",                        # ? D:\tracker\.env (СЕРВЕРНЫЙ!)
    Path(__file__).resolve().parent / ".env",   # ? D:\tracker\client\.env (правильный)
    ...
]
for p in _candidates:
    if p.exists():
        load_dotenv(p, override=True)
        break
Вы запускаете python -m client.main из D:\tracker ? Path.cwd() = D:\tracker. Там есть серверный .env (с SECRET_ENCRYPTION_KEY, ADMIN_API_KEY и т.д.). Он находится первым, читается, а TRACKER_SERVER_URL в нём нет ? берётся дефолт.
Решение: поменять порядок — сначала искать .env рядом с самим config.py (т.е. в client/), а корневой игнорировать.
________________________________________
Скрипт — полная замена client/config.py
powershell
$ErrorActionPreference = "Stop"
$cfgPath = "D:\tracker\client\config.py"

$config_py = @'
import logging as _logging
import os
from pathlib import Path

_log = _logging.getLogger("tracker.config")

try:
    from dotenv import load_dotenv

    # Ищем .env в порядке приоритета.
    # ВАЖНО: первым идёт .env рядом с этим файлом (client/.env),
    # а НЕ .env в текущей директории — иначе при запуске из корня
    # проекта подхватится серверный .env, где TRACKER_* переменных нет.
    _candidates = [
        Path(__file__).resolve().parent / ".env",                       # client/.env
        Path(os.environ.get("APPDATA", Path.home())) / "Tracker" / ".env",
    ]
    _loaded_from = None
    for p in _candidates:
        if p.exists():
            load_dotenv(p, override=True)
            _loaded_from = p
            break
    if _loaded_from:
        _log.info("Loaded .env from %s", _loaded_from)
    else:
        _log.warning(".env not found in %s", [str(p) for p in _candidates])
except ImportError:
    _log.error("python-dotenv not installed; .env will NOT be read")


APP_NAME = "Tracker"
CLIENT_VERSION = os.environ.get("TRACKER_VERSION", "1.0.0")

if os.name == "nt":
    BASE_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    BASE_DIR = Path.home() / f".{APP_NAME.lower()}"

BASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "data.db"
LOG_PATH = BASE_DIR / "client.log"
DOWNLOAD_DIR = BASE_DIR / "updates"
DOWNLOAD_DIR.mkdir(exist_ok=True)

