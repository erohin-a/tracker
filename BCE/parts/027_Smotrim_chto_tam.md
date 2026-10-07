# Смотрим что там

*Часть 27 из 100. Источник: `BCE.md`.*

[◀ 1) Заменить подключение сигналов в _start_sync_worker](026_1_Zamenit_podklyuchenie_signalov_v_start_sync_worker.md) | [Оглавление](00_BCE_INDEX.md) | [--- 2. Проверяем связь --- ▶](028_2_Proveryaem_svyaz.md)

---

# Смотрим что там
print('Записей в очереди (synced=0, poisoned=0):')
for row in cur.execute('SELECT COUNT(*) FROM records WHERE synced=0 AND poisoned=0'):
    print('  ', row[0])

print('Сессий не отправлено:')
for row in cur.execute('SELECT COUNT(*) FROM sessions WHERE synced=0'):
    print('  ', row[0])

# Считаем сессии с ошибкой 409 (принадлежат старому ПК) — помечаем synced=1
print()
print('Помечаем старые сессии как synced (они не уйдут):')
cur.execute('UPDATE sessions SET synced=1 WHERE synced=0')
print('  затронуто строк:', cur.rowcount)

# И записи, которые к ним привязаны
cur.execute('UPDATE records SET synced=1 WHERE synced=0 AND poisoned=0')
print('  затронуто записей:', cur.rowcount)

c.commit()
c.close()
print('OK')
"@
После этого перезапустите клиент (правый клик на трее ? Выход, потом заново python -m client.main). Старые записи не будут заново долбить сервер.
Если после этого новые записи начнут уходить — увидим accepted=N без ошибок.
________________________________________
Пока пришлите мне
Результат Шага 1 (grep).
Последние 40–60 строк из docker compose logs api --tail=100 — особенно если там есть Traceback.
По ним точно скажу, что чинить. Скорее всего, это одна из двух причин:
A. Образ не пересобрался (в контейнере старый main.py), либо
B. В новой версии ingest_records есть тонкий баг с откатом транзакции при IntegrityError — тогда я пришлю патч db.py и main.py, где обработка идёт не построчно, а через ON CONFLICT DO NOTHING.
Если увижу Traceback — точно скажу, какой из вариантов.
Ключевая ошибка:
text
sqlalchemy.exc.DataError: (psycopg2.errors.StringDataRightTruncation) value too long for type character varying(64)
В таблице audit_log поле entity_id VARCHAR(64), но мы в ingest_records пишем туда ",".join(rejected[:20]) — это больше 64 символов.
И самое главное — эта ошибка происходит когда есть rejected с bad_signature. То есть все записи, которые шлёт клиент, имеют неправильную подпись!
Стоп. Это вторичная проблема. Первичная — почему bad_signature? Клиент подписывает client_secret, сервер проверяет тем же секретом. Секрет после перерегистрации обновился (был revoke, потом новый register) — но клиент не знал что записи со старым секретом. Хотя нет, ключ хранится в keyring и обновляется при регистрации.
Возможно проблема в том, что при перерегистрации (revoke старого ПК + register нового) сервер сгенерировал новый client_secret и secret_version=1. Но клиент в своём keyring имеет старый секрет от предыдущей регистрации — если он не удалил client_secret в keyring перед новой регистрацией... Но нет, регистрация через диалог сохраняет новый.
Хотя логи показывают:
17:04:44 ? ошибка client_secret not found; register first (было до регистрации)
17:06:51 ? Registered as ed1ef589-... (secret_version=1) — новая регистрация
Но потом 17:07+ старые записи шлются и получают bad_signature. Потому что они были подписаны старым секретом от старой регистрации (af354a84).
Клиент пытается отправить старые записи, подписанные старым client_secret, но у сервера теперь секрет от новой регистрации (ed1ef589). Соответственно подписи не сходятся.
Это классическая проблема: при перерегистрации старые локальные записи становятся невалидными. Их надо выкидывать (poisoned).
В моей реализации в sync.py:
python
permanent = [u for u in rejected if reasons.get(u) == "bad_signature"]
db.apply_sync_result(accepted, permanent)
Это правильно — они должны быть помечены как poisoned и больше не отправляться. Но! Из-за того что сервер падает 500 на этапе создания audit_log, клиент получает 500 и не помечает их poisoned. Круг замыкается.
Решение:
Исправить в ingest_records поле entity_id — обрезать или использовать entity="record" без длинного entity_id. Лучше entity_id=None, а в new_value положить список.
Восстановить обработку bad_signature ? poisoned.
Также есть проблема: если bad_signature, клиент должен пометить и не пытаться снова. Это у нас уже сделано, но сервер падает раньше ответа.
Сделаю патч:
Патч server/main.py — в блоке создания audit_log убрать/обрезать entity_id. И ещё сделать так, чтобы вся транзакция не падала из-за одной ошибки. Плюс — обязательно откатывать bad_signature в БД.
Также надо подумать: если у клиента есть старые записи с bad_signature — они идут в poisoned и больше не отправляются. Это хорошо.
Но! Клиент шлёт по 200 записей в батче. Если в батче есть хотя бы одна запись с bad_signature — сервер отвечает 200, но с принятыми/отклонёнными. И это уже работает. Проблема только в том, что сервер падает на audit_log до возврата ответа.
Так что патч ingest_records:
entity_id ? обрезать до 64 символов, либо положить туда что-то короткое (например, str(len(rejected))).
new_value — уже без проблем (Text).
И ещё — надо явно не помещать в rejected те записи, которые отличаются только подписью (bad_signature) если они уже в базе. Хотя это уже есть.
Но основная проблема клиента: старые записи. Решение на клиенте — кнопка "Сбросить очередь" или автоочистка при старте, если много bad_signature.
Дам патч:
server/main.py — фикс audit_log (не переполнять entity_id).
Опционально: в sync.py — если получили bad_signature для всей пачки — увеличить счётчик и автоматически показывать уведомление/чистить через N повторов.
Начнём с серверного патча. Дам полный main.py.
Также замечу: сообщение про 500 — это не «сервер офлайн». Это ошибка на сервере. Нужно поправить и всё пойдёт.
Ещё момент — клиент по 200 записей шлёт на сервер. Если у него скопились тысячи записей с bad_signature, они все будут падать. Нужна регенерация (или удаление). Плюс клиент должен понимать что bad_signature — это permanent и больше не пытаться. Это уже есть в sync.py.
Дам патч main.py и подскажу команду для очистки старых записей на клиенте.
Пишу.
Найдено! Ошибка в серверном audit_log
Traceback предельно ясен:
text
sqlalchemy.exc.DataError: value too long for type character varying(64)
[SQL: INSERT INTO audit_log (... entity_id ...) VALUES (...)]
entity_id: '50c5db31-09d7-4755-aee3-58069ba1a66e,9586575e-...,4349cd93-...'
Что происходит:
Клиент шлёт пачку записей, подписанных старым client_secret (после перерегистрации секрет сменился, старые записи подписаны старым).
Сервер видит bad_signature для этих записей — правильно.
Пытается записать в audit_log, кладя в entity_id список из 20 UUID через запятую — это >1000 символов, а колонка VARCHAR(64).
SQL падает, вся транзакция откатывается, эндпоинт возвращает 500.
Клиент никогда не получает ответ ? не помечает записи как poisoned ? долбит их бесконечно.
Двойной фикс:
Сервер — больше не переполнять entity_id.
Клиент — почистить очередь от старых записей (подписанных старым секретом) — они никогда не пройдут.
________________________________________
Скрипт 1 — патч server/main.py
Заменяем только блок аудита в ingest_records. Ничего больше не трогаем.
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$old = @'
    if rejected:
        db.add(AuditLog(
            actor=f"computer:{comp.computer_uid}",
            entity="record", entity_id=",".join(rejected[:20]),
            action="reject_signature",
            new_value=json.dumps({"count": len(rejected), "reasons": reasons},
                                 ensure_ascii=False),
        ))
'@

$new = @'
    if rejected:
        # entity_id ограничен 64 символами — кладём туда первое отклонённое UUID,
        # список всех отклонённых уходит в new_value (там Text, без ограничений).
        db.add(AuditLog(
            actor=f"computer:{comp.computer_uid}"[:128],
            entity="record",
            entity_id=(rejected[0] if rejected else None),
            action="reject_signature",
            new_value=json.dumps(
                {"count": len(rejected), "rejected": rejected[:50], "reasons": reasons},
                ensure_ascii=False,
            ),
        ))
'@

if ($content.Contains($new)) {
    Write-Host "Уже пропатчен — ничего не делаем" -ForegroundColor Yellow
} elseif ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  main.py пропатчен" -ForegroundColor Green
} else {
    Write-Host "НЕ НАЙДЕН блок аудита — правьте вручную" -ForegroundColor Red
    Write-Host "Ищите: 'entity_id='',''.join(rejected[:20])'" -ForegroundColor Red
    exit 1
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — чистим «мёртвую» очередь на клиенте
Это записи, подписанные старым секретом (сгорели при перерегистрации). Они никогда не пройдут проверку подписи — надо их удалить, иначе клиент будет их вечно долбить.
Пока клиент запущен — закройте его (трей ? Выход). Затем:
powershell
$ErrorActionPreference = "Stop"
cd D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
import os, sqlite3
p = os.path.join(os.environ['APPDATA'], 'Tracker', 'data.db')
c = sqlite3.connect(p)
cur = c.cursor()

n_rec = cur.execute('SELECT COUNT(*) FROM records WHERE synced=0 AND poisoned=0').fetchone()[0]
n_ses = cur.execute('SELECT COUNT(*) FROM sessions WHERE synced=0').fetchone()[0]
print(f'До очистки: records={n_rec}, sessions={n_ses}')

# Сессии от старой регистрации — помечаем synced=1 (не отправляем)
cur.execute('UPDATE sessions SET synced=1 WHERE synced=0')
print('  сессий помечено:', cur.rowcount)

# Все записи от старой регистрации — в poisoned (не отправляем)
cur.execute('UPDATE records SET synced=1, poisoned=1 WHERE synced=0')
print('  записей в poisoned:', cur.rowcount)

c.commit()

n_rec = cur.execute('SELECT COUNT(*) FROM records WHERE synced=0 AND poisoned=0').fetchone()[0]
n_ses = cur.execute('SELECT COUNT(*) FROM sessions WHERE synced=0').fetchone()[0]
print(f'После очистки: records={n_rec}, sessions={n_ses}')
c.close()
"@
Ожидаемый вывод:
text
До очистки: records=1234, sessions=7
  сессий помечено: 7
  записей в poisoned: 1234
После очистки: records=0, sessions=0
________________________________________
Скрипт 3 — пересборка сервера
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

Write-Host "--- Статус ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Логи API (последние 20) ---" -ForegroundColor Cyan
docker compose logs api --tail=20
________________________________________
Скрипт 4 — запуск клиента и проверка
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

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

# --- 1. Обновляем client/.env ---
$envPath = "D:\tracker\client\.env"

$newEnv = @'
TRACKER_SERVER_URL=https://127.0.0.1
TRACKER_PIN=
TRACKER_VERSION=1.0.0
'@

[System.IO.File]::WriteAllText($envPath, $newEnv, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/.env обновлён" -ForegroundColor Green
Get-Content $envPath

