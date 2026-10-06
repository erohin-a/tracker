<!-- Часть 418 из 1409 -->
# Потом заново:
*Хлебные крошки:* Потом заново:

[◀ В окне клиента — правый клик на трее ? Выход](417_V_okne_klienta_pravyy_klik_na_tree_Vyhod.md) | [Оглавление](00_BCE_INDEX.md) | [Смотрим что там ▶](419_Smotrim_chto_tam.md)

---

# Потом заново:
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Проверьте статус на панели — должно быть «? онлайн» зелёным.
И параллельно логи:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки после перезапуска:
text
tracker.sync INFO Server reachable (HTTP 200)
tracker.sync INFO Session ... synced
tracker.sync INFO Batch: accepted=N rejected=0
________________________________________
Что мы сделали (в двух словах)
Проблема	Было	Стало
/api/v1/sessions ? 409 при чужой сессии	Ретрай бесконечно	200 OK, «принято»
/api/v1/records/batch ? 500 при дубле record_uid	IntegrityError	Ищем дубликаты по всей таблице + защита от race
Сессия принадлежит другому computer_id после перерегистрации	Клиент зависал	Игнорируется, всё принимается
________________________________________
После того как «онлайн» появится
Проверьте, что батчи больше не 500:
powershell
docker compose logs api --tail=20
Не должно быть Traceback.
На клиенте:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 30 -Encoding UTF8
Должны быть только accepted=N rejected=0 без ошибок.
________________________________________
Как только убедимся, что связь ровная — переходим к следующему блоку:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация, поиск.
XLSX — убрать «Группа»/«Аварийный», добавить «Год / Месяц / Число».
Группировка «Месяц ? Сотрудник» для онлайн-отчёта.
Календарь рабочих/нерабочих дней.
Heartbeat + Онлайн/Оффлайн на дашборде.
Массовая привязка ПК через CSV.
PDF-отчёт.
Запускайте скрипты 1 ? 2 ? 3 по порядку и пришлите логи (клиент + api), если что-то снова начнёт ругаться.
Сервер продолжает быть офлайн
The user's log shows continuous 500 errors on /api/v1/records/batch. The server was updated with new code that should handle this, but the client still shows the errors. Let me analyze:
Client is sending records
Server returns 500 on /api/v1/records/batch
Even after my previous fix, still 500
I need to look at the API logs to see the actual traceback. The client log only shows HTTP 500, not the server-side error.
Let me ask the user for the API logs. Also, likely cause: the server code I provided still has issues. Let me think about what could be wrong:
Looking at my updated ingest_records:
We look up existing_uids across all records
We use db.flush() inside a loop with try/except IntegrityError
But if there's an error mid-loop, the whole transaction may be in a bad state
Wait - there's a problem! When IntegrityError happens and we db.rollback(), that rolls back the entire transaction, losing all previously accepted records. And then subsequent adds may not have a proper session.
Also the previous approach:
python
db.add(Record(...))
db.flush()
accepted.append(rec.record_uid)
except IntegrityError:
    db.rollback()
This is problematic because rollback undoes everything from the start of the transaction.
But more importantly - if the session is in a bad state after a 500 error, subsequent retries fail too.
The real question: what's causing the initial 500? We need server logs.
Let me ask for docker compose logs api --tail=100 to see the traceback.
Actually, most likely scenario given the log:
The client has old records (from previous registration with different secret)
The client_secret is different now (after re-registration), so HMAC verification fails
Or: the old records have an old computer_id in local SQLite and... no wait, the computer_id is server-side.
Hmm. Let me think again. The client registered with uid ed1ef589-33eb-479b-b3f5-48ec4b7a4283. The old session 08f34fe3 is being rejected as 409 (belongs to another computer). But the server now returns 200 for that.
Wait - the log shows that after re-registration:
POST /sessions ? 409 (for old session)
POST /records/batch ? 500 (still!)
The server code I provided should handle sessions belonging to another computer. But looking at the log, it seems the server code was NOT updated — still returning 409. So either:
Server was not rebuilt
Or rebuild failed
Let me ask for API logs.
Also - I should note in the client log at 17:19:12 there's "getaddrinfo failed" — that's DNS resolution failure. And the client shows that it needs to bypass this by retrying.
But right now the client is running, so DNS works. The main issue is 500 on /api/v1/records/batch.
I need to:
Ask for API logs
Provide a diagnostic SQL to see what's happening
Let me be direct and ask for API logs to see the traceback. Meanwhile, I'll also give a "clean up stuck records" SQL that removes records from old computer_uid.
Actually, thinking more carefully — the likely issue is:
The client has old records in local SQLite. Some of those records were already sent AND stored under the previous computer_id (when the same PC registered under old UID af354a84...). When the new registration happened (ed1ef589...), the client's synced=0 records include:
Old records NOT yet synced (before registration switch)
New records
Old records have their record_uid in server DB from BEFORE. Now when client sends them under new computer_id, server's existing_uids check now catches them...
Wait, my new code checks existing_uids across entire table. So it should find them. Unless the server code wasn't actually deployed.
Yes — most likely: server wasn't rebuilt. Let me ask to check.
Let me write a concise diagnostic + fix script.
Что происходит
Из логов клиента видно, что сервер всё ещё возвращает 500 и 409 на старых эндпоинтах. Значит, либо образ не пересобрался, либо в контейнере остался старый код.
Проверим за 30 секунд.
________________________________________
Шаг 1. Проверить, что новый код в контейнере
Выполните в PowerShell:
powershell
cd D:\tracker

Write-Host "--- Что видит контейнер ---" -ForegroundColor Cyan
docker compose exec -T api grep -c "belongs_to_another_computer" /app/server/main.py
docker compose exec -T api grep -c "existing_uids" /app/server/main.py
Ожидаемо: обе команды вернут 1 или больше.
Если 0 — значит контейнер работает со старым кодом. Нужно пересобрать:
powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose ps
________________________________________
Шаг 2. Посмотреть traceback сервера
Это самое важное. Выполните:
powershell
docker compose logs api --tail=100
Ищите блок Traceback. Скорее всего увидите что-то вроде:
text
sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "records_record_uid_key"
DETAIL: Key (record_uid)=(...) already exists.
Пришлите мне последние 40 строк с Traceback — по ним точно пойму, что чинить.
________________________________________
Шаг 3. Пока ждём — быстрый обходной путь
Пока разбираемся, можно развязать ситуацию на клиенте — очистить очередь от «застрявших» записей, которые не проходят, чтобы клиент перестал долбить сервер. Запустите в отдельном окне PowerShell (не в том, где клиент):
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
import os
import sqlite3
p = os.path.join(os.environ['APPDATA'], 'Tracker', 'data.db')
c = sqlite3.connect(p)
cur = c.cursor()

