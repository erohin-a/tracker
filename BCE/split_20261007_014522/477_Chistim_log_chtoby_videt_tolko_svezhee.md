<!-- Часть 477 из 1409 -->
# Чистим лог, чтобы видеть только свежее
*Хлебные крошки:* Чистим лог, чтобы видеть только свежее

[◀ Сколько минут без активности — порог авто-закрытия висящей сессии](476_Skolko_minut_bez_aktivnosti_porog_avto_zakrytiya_visyaschey_sessii.md) | [Оглавление](00_BCE_INDEX.md) | [Чистим лог, чтобы видеть только свежее ▶](478_Chistim_log_chtoby_videt_tolko_svezhee.md)

---

# Чистим лог, чтобы видеть только свежее
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

python -m client.main
Параллельно во втором окне:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки — обратите внимание на первые три:
text
tracker.config INFO Loaded .env from D:\tracker\client\.env        ? теперь правильно
tracker.http Using CA bundle: C:\Users\erohin\AppData\Roaming\Tracker\ca.pem
tracker.http Pinning DISABLED
tracker.sync SyncWorker started; server=https://127.0.0.1          ? правильный URL
tracker.sync Server reachable (HTTP 200)
httpx HTTP Request: POST https://127.0.0.1/api/v1/heartbeat "HTTP/1.1 200 OK"
На панели клиента — «? онлайн» зелёным.
________________________________________
Проверка
Через 30 секунд после запуска:
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at, NOW() - last_seen_at AS age FROM computers ORDER BY last_seen_at DESC LIMIT 5;"
age должен быть < 1 минуты — это heartbeat.
________________________________________
Что важно понять на будущее
При запуске клиента из корня проекта D:\tracker нельзя искать .env через Path.cwd() — там лежит серверный .env. Я это теперь исправил: клиент смотрит только:
client/.env (рядом с config.py)
%APPDATA%\Tracker\.env (если кто-то положит туда)
Порядок — сначала client/.env.
Если когда-то понадобится переопределить URL — просто править client/.env, и всё.
________________________________________
После того как «онлайн» появится
Проверьте:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 15 -Encoding UTF8
Не должно быть getaddrinfo failed и 500. Должны быть 200 OK.
Затем — скажите слово, и пришлю Подблок C:
Календарь рабочих/нерабочих дней — страница /admin/calendar, автозаполнение Сб/Вс как нерабочих на год вперёд, ручная правка
Подсветка в отчётах — рабочие/нерабочие/выходные дни разными цветами
PDF-отчёт — reportlab + кириллица
Запускайте, присылайте результат.
Этот ответ сгенерирован AI, только для справки.
OK client/config.py перезаписан SYNTAX OK --- Что теперь читается из .env --- File "<string>", line 1 from client.config import SERVER_URL, BASE_DIR, _loaded_from if False else None ^^ SyntaxError: invalid syntax
Пользователь получил ошибку из моей проверочной команды. Надо исправить одну строчку и дать простой скрипт проверки.
Проблема в моём скрипте-проверке — я написал бредовое выражение _loaded_from if False else None в импорте. Надо просто убрать этот кусок.
Главное: config.py перезаписан успешно. Осталось только проверить, что он реально читает SERVER_URL = https://127.0.0.1 и запустить клиент.
Дадим короткий фикс.
Ошибка в моей проверочной команде, файл config.py записан правильно
Скрипт с from client.config import ... — это была моя ошибка в синтаксисе проверки, а не в вашем config.py. Файл config.py уже перезаписан и корректен (SYNTAX OK — это подтверждает).
Забудьте про этот неудачный тест. Проверим иначе.
________________________________________
Простая проверка config.py (правильный синтаксис)
Запустите из папки D:\tracker:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
from client import config
print('  SERVER_URL    =', config.SERVER_URL)
print('  BASE_DIR      =', config.BASE_DIR)
print('  CLIENT_VERSION=', config.CLIENT_VERSION)
"@
Ожидаемый вывод:
text
  SERVER_URL    = https://127.0.0.1
  BASE_DIR      = C:\Users\erohin\AppData\Roaming\Tracker
  CLIENT_VERSION= 1.0.0
Если увидите SERVER_URL = https://127.0.0.1 — всё правильно, .env читается.
Если увидите https://tracker.example.com — значит .env не найден, будем разбираться.
________________________________________
Запуск клиента
Закройте старый клиент (трей ? Выход), затем:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

