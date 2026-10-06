<!-- Часть 424 из 1409 -->
# Чистим лог, чтобы видеть только свежее
*Хлебные крошки:* Чистим лог, чтобы видеть только свежее

[◀ Все записи от старой регистрации — в poisoned (не отправляем)](423_Vse_zapisi_ot_staroy_registratsii_v_poisoned_ne_otpravlyaem.md) | [Оглавление](00_BCE_INDEX.md) | [--- 1. Обновляем client/.env --- ▶](425_1_Obnovlyaem_client_env.md)

---

# Чистим лог, чтобы видеть только свежее
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

python -m client.main
Параллельно во втором окне PowerShell следите за логом:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки:
text
tracker.sync INFO SyncWorker started; server=https://localhost
tracker.sync INFO Server reachable (HTTP 200)
И далее при синхронизации — POST .../records/batch "HTTP/1.1 200 OK" без 500.
На панели клиента должно быть «? онлайн» зелёным.
________________________________________
Что мы починили
Проблема	Было	Стало
audit_log.entity_id переполнялось списком UUID	500	Кладём только первый UUID, всё в new_value
Клиент бесконечно шлёт записи с bad_signature	Ретрай вечно	Очистили через SQL; сервер теперь корректно ответит rejected
Старые записи, подписанные до перерегистрации	Копились	Помечены poisoned=1, больше не отправляются
________________________________________
После запуска
Проверить, что новый код в контейнере:
powershell
docker compose exec api grep -c "rejected\[:50\]" /app/server/main.py
Должно вернуть 1.
Проверить логи клиента после 1 минуты работы:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 20 -Encoding UTF8
Должны быть 200 OK без 500.
Если «онлайн» появилось — можно двигаться дальше. Скажите результат, и я выдам следующий блок по вашему списку:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров с зависимой фильтрацией и поиском
XLSX — убрать «Группа»/«Аварийный», добавить «Год / Месяц / Число»
Группировка «Месяц ? Сотрудник» в онлайн-отчёте
Календарь рабочих/нерабочих дней + подсветка Сб/Вс
Heartbeat + Онлайн/Оффлайн на дашборде
Массовая привязка ПК через CSV
PDF-отчёт
Запускайте скрипты 1–4 по порядку. Если снова 500 или 409 — присылайте логи, разрулим за один шаг.
Синхронизации с сервером нет он офлайн (.venv) PS D:\tracker> Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8 2026-09-17 21:18:24,747 INFO tracker.http Using CA bundle: C:\Users\erohin\AppData\Roaming\Tracker\ca.pem 2026-09-17 21:18:24,749 WARNING tracker.http Pinning DISABLED 2026-09-17 21:18:26,438 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed 2026-09-17 21:18:27,929 INFO tracker.main Work session started uid=3711c076-111b-4107-b901-f24fe7ee36c7 2026-09-17 21:18:32,444 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:19:06,958 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:19:27,369 INFO tracker.main Work session stopped uid=3711c076-111b-4107-b901-f24fe7ee36c7 2026-09-17 21:19:30,360 INFO tracker.main Work session started uid=86ed721b-16a3-47a1-a7fc-79eeb225974a 2026-09-17 21:19:31,881 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:19:36,392 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed (.venv) PS D:\tracker> Get-Content "$env:APPDATA\Tracker\client.log" -Tail 20 -Encoding UTF8 2026-09-17 21:18:24,747 INFO tracker.http Using CA bundle: C:\Users\erohin\AppData\Roaming\Tracker\ca.pem 2026-09-17 21:18:24,749 WARNING tracker.http Pinning DISABLED 2026-09-17 21:18:26,438 WARNING tracker.updater version check: [Errno 11001] getaddrinfo failed 2026-09-17 21:18:27,929 INFO tracker.main Work session started uid=3711c076-111b-4107-b901-f24fe7ee36c7 2026-09-17 21:18:32,444 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:19:06,958 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:19:27,369 INFO tracker.main Work session stopped uid=3711c076-111b-4107-b901-f24fe7ee36c7 2026-09-17 21:19:30,360 INFO tracker.main Work session started uid=86ed721b-16a3-47a1-a7fc-79eeb225974a 2026-09-17 21:19:31,881 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:19:36,392 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:20:10,906 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:20:45,431 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed 2026-09-17 21:21:19,972 WARNING tracker.sync sync failed: [Errno 11001] getaddrinfo failed (.venv) PS D:\tracker> docker compose exec api grep -c "rejected\[:50\]" /app/server/main.py 1
The user's log shows getaddrinfo failed — this is a DNS resolution error. The host localhost isn't resolving. This happens when:
Docker containers aren't running (no server on localhost:443)
Network/DNS problem
The client is trying to connect to a different URL
getaddrinfo failed on Windows usually means the hostname cannot be resolved at all. Let me check — https://localhost should resolve fine on Windows. But wait — maybe the issue is that they closed Docker Desktop or the containers aren't running.
Actually — the earlier log was from 17:xx, now it's 21:xx. Probably Docker Desktop was closed or rebooted. Let me guide them to check.
Also note earlier the client worked (200 OK responses). Now suddenly getaddrinfo failed — the most common cause is:
Docker Desktop not running
Machine was rebooted and Docker didn't start
VPN/DNS issue
Let me give a quick diagnosis + fix. Don't overcomplicate.
Also the grep returned 1 — so the server patch IS in the container image. Good. But server might not be running now.
Simple steps:
Check docker is running
Check curl works from Windows
If not — start docker desktop / docker compose up
Restart client
getaddrinfo failed — это DNS, а не наш код
Коротко: getaddrinfo failed означает, что Windows не может разрешить имя localhost в IP-адрес. К нашему серверному коду это отношения не имеет — запрос даже не уходит. Скорее всего, у вас:
не запущен Docker Desktop после перезагрузки/выхода,
либо контейнеры остановлены.
Проверим за 30 секунд.
________________________________________
Шаг 1. Проверить, работает ли сервер
В PowerShell:
powershell
docker compose ps
Если увидите пусто или контейнеры Exited/Restarting — сервер не работает. Запускайте:
powershell
cd D:\tracker
docker compose up -d
Start-Sleep -Seconds 20
docker compose ps
Должны быть все три контейнера Up (db, api, nginx).
________________________________________
Шаг 2. Проверить связь с сервером с Windows
powershell
curl.exe -k https://localhost/api/v1/version
{"latest_version": ...} — сервер отвечает, можно запускать клиент.
Failed to connect / could not resolve host — сервер не запущен или порт занят, см. Шаг 3.
curl: (7) Failed to connect — Docker Desktop выключен.
________________________________________
Шаг 3. Проверить, что вообще происходит с DNS на этой машине
powershell
Test-NetConnection localhost -Port 443
nslookup localhost
Ожидаемо:
TcpTestSucceeded : True
nslookup вернёт 127.0.0.1
Если TcpTestSucceeded : False — сервер не слушает порт 443. Смотрите:
powershell
docker compose logs nginx --tail=30
docker compose logs api --tail=30
________________________________________
Шаг 4. Если Docker Desktop не запущен
Бывает после перезагрузки. Проверьте в трее — иконка Docker Desktop должна быть активна (не серая). Если серый — кликните, запустите, подождите 30–60 секунд.
Либо из PowerShell:
powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 60
docker compose up -d
________________________________________
Шаг 5. Если ничего не помогает — принудительно 127.0.0.1
Иногда Windows балуется с резолвингом localhost. Попробуйте в client/.env заменить:
ini
TRACKER_SERVER_URL=https://127.0.0.1
Сохранить, перезапустить клиент. 127.0.0.1 — это IP, резолвинг не нужен.
Но проверьте, что сертификат подходит: у вас в certs/fullchain.pem SAN содержит DNS:localhost, IP:127.0.0.1 — значит 127.0.0.1 тоже валиден. Ок.
________________________________________
Шаг 6. Проверить связь с того же клиента
Пока клиент запущен, отдельно в PowerShell:
powershell
curl.exe -k https://localhost/api/v1/version
Если curl.exe работает, а клиент — нет, пришлите:
powershell
Get-Content D:\tracker\client\.env
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 5 -Encoding UTF8
________________________________________
Что мне прислать
Пришлите одним сообщением:
powershell
docker compose ps
curl.exe -k https://localhost/api/v1/version
Test-NetConnection localhost -Port 443
Три команды. По ним сразу скажу, что именно сломалось.
________________________________________
Мой прогноз: контейнеры просто не запущены — после того как мы в прошлый раз делали docker compose down, машина, вероятно, перезагружалась, Docker Desktop не поднялся автоматически. Запускается всё за 30 секунд. Причём grep в контейнере уже показал 1 — значит образ с патчем правильный, и как только сервер запустится, всё заработает.
Этот ответ сгенерирован AI, только для справки.
Клиент: getaddrinfo failed — DNS не резолвит localhost. Но curl с localhost работает, Test-NetConnection работает. Значит проблема специфична для Python/httpx.
getaddrinfo failed в Python-клиенте — это часто бывает, когда IPv6/IPv4 конфликт. localhost в Windows резолвится в ::1 (IPv6). nginx слушает [::]:443, значит должен работать через IPv6.
Но! httpx может вести себя иначе. Или проблема в том, что клиент читает не тот SERVER_URL.
Стоп — посмотрим внимательно. curl.exe -k https://localhost/... работает. Но nslookup localhost говорит "Non-existent domain" — DNS-сервер не знает localhost. Это значит, что localhost резолвится только через hosts-файл (там обычно 127.0.0.1 localhost и ::1 localhost).
Почему Python не может? Возможно:
nslookup игнорирует hosts, а Python — нет. То есть в hosts localhost есть, но...
Проблема с IPv6 — httpx может пытаться сначала ::1, а контейнер nginx слушает [::]:443 в Linux, но в Windows через Docker — IPv6 может не пробрасываться.
Actually, это классика: Docker Desktop на Windows не всегда пробрасывает IPv6 правильно. [::]:443->443/tcp показывает, что контейнер слушает на IPv6, но Windows-хост с ::1 может не достучаться.
curl.exe умеет fallback на IPv4, а httpx/httpx-с-httpcore — не всегда.
Проверим: curl.exe -4 -k https://localhost/... — работает ли IPv4.
Но давайте проще: заменим в client/.env localhost на 127.0.0.1 — явный IPv4. Сертификат с SAN IP:127.0.0.1 тоже подходит.
Это самое простое решение.
Также нужно проверить, что клиент точно читает актуальный .env. В логах Using CA bundle: ...ca.pem — значит .env читается.
Смотрю внимательнее на логи: клиент загрузил CA bundle, но getaddrinfo failed сразу после этого при version check. Значит SERVER_URL из .env — https://localhost. И localhost не резолвится.
Причина: возможно, у пользователя на машине домен ANTOR.msk (судя по DNS-серверу v-DC2.ANTOR.msk), и group policy переопределила DNS-суффикс. localhost резолвится только через hosts, но Python тоже должен смотреть в hosts.
Стоп — nslookup localhost говорит "Non-existent domain". Это ключ. nslookup использует только DNS, не hosts. Так что это ничего не доказывает. Но Test-NetConnection localhost вернул ::1 — значит hosts-файл резолвит.
Есть ещё вариант: в Python из venv сломан socket.getaddrinfo. Такое бывает, если в виртуалке есть библиотека, подменяющая DNS. Но маловероятно.
Самое надёжное решение: 127.0.0.1 в client/.env.
Кроме того, добавим диагностику в клиент: перед sync делаем DNS-проверку socket.getaddrinfo и пишем в лог, что получилось.
Хотя, стоп. Смотрю ещё раз. Клиент запущен до того как docker compose up был запущен? Не то. Смотрим в логи: 21:18:24 клиент запущен, все сообщения 21:18-21:21. А потом docker compose ps показал 7 minutes ago — то есть ~21:13. Значит контейнеры УЖЕ работали в 21:18. Значит проблема именно в DNS/socket.
Ладно, самое простое:
Сменить localhost на 127.0.0.1 в client/.env.
Перезапустить клиент.
Также в конфиг клиента можно добавить fallback: если getaddrinfo для localhost не удаётся, пробуем 127.0.0.1.
Давайте просто сделаем. Скину скрипт, который:
Меняет .env клиента: localhost ? 127.0.0.1.
Перезапускает клиент.
И проверяем.
Если сработает — на будущее можно добавить в клиент автоматический fallback. Но это уж потом.
Найдена причина — IPv6 vs IPv4 в Docker Desktop
Смотрите на вывод внимательно:
Test-NetConnection localhost -Port 443 ? RemoteAddress: ::1 (IPv6-адрес!)
nslookup localhost ? "Non-existent domain" (DNS-сервер v-DC2.ANTOR.msk не знает localhost)
curl.exe -k https://localhost/... ? работает (curl сам делает fallback IPv6 ? IPv4)
Python/httpx при localhost идёт в IPv6 (::1) и не имеет fallback
Docker Desktop в Windows пробрасывает порт 443 так: 0.0.0.0:443->443/tcp, [::]:443->443/tcp. Формально и IPv4, и IPv6. Но WSL2 часто ломает IPv6-проброс. И когда Windows резолвит localhost в ::1 — контейнер по этому адресу недоступен, а curl об этом не жалуется, потому что автоматически переключается на 127.0.0.1.
Python так не умеет — падает с getaddrinfo failed.
Решение: заменить в .env клиента localhost на 127.0.0.1. Всё остальное работает как есть — сертификат у вас с SAN IP:127.0.0.1, так что проверка пройдёт.
________________________________________
Скрипт — правим client/.env + перезапуск
powershell
$ErrorActionPreference = "Stop"

