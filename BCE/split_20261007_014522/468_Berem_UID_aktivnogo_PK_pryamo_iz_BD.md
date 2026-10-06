<!-- Часть 468 из 1409 -->
# Берём UID активного ПК прямо из БД
*Хлебные крошки:* Берём UID активного ПК прямо из БД

[◀ ============================================================"](467_part.md) | [Оглавление](00_BCE_INDEX.md) | [--- 1. Гарантированно правильный client/.env --- ▶](469_1_Garantirovanno_pravilnyy_client_env.md)

---

# Берём UID активного ПК прямо из БД
$realUid = docker compose exec -T db psql -U tracker -d tracker -t -A -c "SELECT computer_uid FROM computers WHERE is_active = true ORDER BY last_seen_at DESC LIMIT 1;"
$realUid = $realUid.Trim()
Write-Host "Используем UID: $realUid"
$r = curl.exe -k -s -X POST https://localhost/api/v1/heartbeat -H "X-Computer-Uid: $realUid"
Write-Host "Ответ: $r"
Ожидаемый вывод:
text
--- POST /api/v1/heartbeat без заголовка (ожидаем 422) ---
HTTP-код: 422

--- POST /api/v1/heartbeat с фейковым UID (ожидаем 401) ---
HTTP-код: 401

--- POST /api/v1/heartbeat с настоящим UID ---
Используем UID: ed1ef589-33eb-479b-b3f5-48ec4b7a4283
Ответ: {"status":"ok","server_time":"2026-09-17T..."}
Пояснение:
Без заголовка X-Computer-Uid ? 422 (FastAPI: обязательный заголовок не передан)
С фейковым UID ? 401 (такого ПК нет)
С настоящим UID ? 200 OK + JSON
________________________________________
Проверка heartbeat в реальной работе
Клиент должен быть запущен. Если он был закрыт — запустите заново:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Проверьте last_seen_at в БД — должно обновляться даже без активной сессии:
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at, NOW() - last_seen_at AS age FROM computers ORDER BY last_seen_at DESC LIMIT 5;"
Ожидаемо: age у активного ПК меньше 5 минут, даже если вы не нажимали «Начать работу».
Подождите 3 минуты — heartbeat уходит раз в 6-й цикл синхронизации (30 сек ? 6 = 3 мин). Если age > 5 минут у вашего ПК при работающем клиенте — что-то не так, будем разбираться.
________________________________________
Проверка массовой привязки
Откройте https://localhost/admin/computers
Сверху должна быть карточка «Массовая привязка ПК к сотрудникам из CSV» с полем загрузки файла
Создайте тестовый файл bulk.csv:
text
hostname;1C_ID
PC-TEST-01;ИВАНОВ
PC-TEST-02;12345
Загрузите — вверху появится плашка с результатом.
Если реальных ПК с такими hostname нет — увидите «Не найдены ПК: 2», это нормально для теста.
________________________________________
Что у нас сейчас работает
? Дашборд с онлайн/оффлайн
? Heartbeat-эндпоинт + клиент шлёт его в фоне
? Массовая привязка ПК через CSV
? Фильтры в отчётах (мультивыбор + поиск + зависимая фильтрация)
? Группировка «Месяц ? Сотрудник»
? XLSX с колонками Год/Месяц/Число и правильным форматом времени
________________________________________
Что дальше — Подблок C
Скажите «поехали», и пришлю Подблок C:
Календарь рабочих/нерабочих дней — таблица calendar_days, автозаполнение Сб/Вс как нерабочих на год вперёд, ручная правка, страница /admin/calendar.
Подсветка в отчётах — рабочие дни зелёным/неработные серым/выходные жёлтым.
Чекбокс «Учитывать нерабочие дни» — уже частично сделан в настройках.
PDF-отчёт — reportlab + шрифт с кириллицей, кнопка «Скачать PDF».
Запускайте проверку выше. Если 422/401/200 — как ожидается, то heartbeat работает, и можно переходить к C. Если что-то не так — пришлите вывод блока и docker compose logs api --tail=30.
В клиентской части сервер опять офлайн
Клиент показывает офлайн. Из предыдущей истории — было несколько причин:
getaddrinfo failed — резолвинг localhost (IPv6)
500 ошибки на сервере
Сейчас после пересборки — что могло сломаться? Скорее всего клиент использует старый URL (localhost) или мы снова сделали docker compose down/up, и что-то поменялось.
Также надо проверить — может клиент упал из-за того что контейнер был пересобран, но клиент не перезапущен.
Дам пошаговую диагностику + правку config.py клиента, чтобы он брал URL из .env, а не дефолтный localhost.
Смотрю на прошлое — мы уже правили client/.env на 127.0.0.1. Но лог показывает https://localhost. Значит .env либо перезаписан, либо не читается.
Мне нужно:
Проверить что в client/.env
Проверить что в client/config.py DEFAULT для SERVER_URL — если клиент упал на дефолт, значит .env не читается
Возможно проблема в getaddrinfo failed ? опять localhost
Дам скрипт, который:
показывает .env
показывает config.py
меняет дефолт в config.py на 127.0.0.1 (на случай если .env не подхватится)
перезапускает клиент
Проще всего — поправить DEFAULT_SERVER_URL в config.py на 127.0.0.1 и добавить в клиент логирование загруженного .env.
Посмотрю на config.py клиента — там SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://tracker.example.com"). Заменить дефолт на 127.0.0.1.
И заодно добавлю в sync.py лог с URL при старте — уже есть log.info("SyncWorker started; server=%s", SERVER_URL). В логе клиента я этого не вижу. Значит либо старый sync.py (без этой строки), либо лог не с того места смотрим.
Дам скрипт, который чистит и правит всё сразу.
Диагностика «офлайн» в клиенте
Из прошлого раза мы уже выяснили: getaddrinfo failed — проблема с резолвингом localhost (IPv6 ::1). Мы поменяли .env, но, видимо, .env не подхватывается или вы снова запустили клиент со старым config.py.
Сделаем два уровня защиты сразу: пропишем правильный URL и в .env, и в дефолте config.py. Тогда даже если .env не прочитается — клиент возьмёт правильный адрес.
________________________________________
Скрипт 1 — диагностика (без изменений)
powershell
$ErrorActionPreference = "Continue"

Write-Host "=== 1. Что в client\.env ===" -ForegroundColor Cyan
if (Test-Path D:\tracker\client\.env) {
    Get-Content D:\tracker\client\.env
} else {
    Write-Host "  ФАЙЛ НЕ НАЙДЕН!" -ForegroundColor Red
}

Write-Host "`n=== 2. Что в config.py (дефолт SERVER_URL) ===" -ForegroundColor Cyan
Select-String -Path D:\tracker\client\config.py -Pattern "SERVER_URL|TRACKER_SERVER"

Write-Host "`n=== 3. Логи клиента (последние 15 строк) ===" -ForegroundColor Cyan
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 15 -Encoding UTF8

Write-Host "`n=== 4. Достижимость сервера ===" -ForegroundColor Cyan
Write-Host "Через localhost:"
curl.exe -k -s -o $null -w "  HTTP %{http_code}`n" https://localhost/api/v1/version

Write-Host "Через 127.0.0.1:"
curl.exe -k -s -o $null -w "  HTTP %{http_code}`n" https://127.0.0.1/api/v1/version

Write-Host "`n=== 5. Что видит Python ===" -ForegroundColor Cyan
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -c @"
import socket
for host in ('localhost', '127.0.0.1'):
    try:
        res = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        print(f'  {host} -> {res[0][4]}')
    except Exception as e:
        print(f'  {host} -> ОШИБКА: {e}')
"@
Пришлите вывод этих 5 блоков. По ним сразу будет видно причину.
________________________________________
Скрипт 2 — «укрепляем» конфиг клиента (правь на всякий случай)
Скрипт делает так, чтобы клиент всегда шёл на 127.0.0.1 — даже если .env не прочитается.
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

