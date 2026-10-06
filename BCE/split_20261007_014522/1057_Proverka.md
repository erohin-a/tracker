<!-- Часть 1057 из 1409 -->
# Проверка
*Хлебные крошки:* Проверка

[◀ 3. В new_vals добавляем обработку](1056_3_V_new_vals_dobavlyaem_obrabotku.md) | [Оглавление](00_BCE_INDEX.md) | [Пробуем монопольно открыть файл — если не получится, кто-то держит ▶](1058_Probuem_monopolno_otkryt_fayl_esli_ne_poluchitsya_kto_to_derzhit.md)

---

# Проверка
$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
if ($check.Contains("stale_session_hours")) {
    Write-Host " Поле в шаблоне: OK" -ForegroundColor Green
} else {
    Write-Host " Поле в шаблоне: MISS" -ForegroundColor Red
}
Что ожидаем:
text
OK: поле stale_session_hours добавлено
 Поле в шаблоне: OK
________________________________________
Пересборка сервера
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Проверка синтаксиса ===" -ForegroundColor Cyan
client\.venv\Scripts\python.exe -c "import ast; ast.parse(open(r'D:\tracker\server\web_admin.py', encoding='utf-8').read()); ast.parse(open(r'D:\tracker\server\main.py', encoding='utf-8').read()); ast.parse(open(r'D:\tracker\server\tasks.py', encoding='utf-8').read()); print('ALL SYNTAX OK')"

Write-Host "`n=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25

Write-Host "`n=== Статус ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Логи API (последние 30 строк) ===" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`n=== Проверка что задача зарегистрирована ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron FROM scheduled_tasks WHERE name='close_stale_sessions';"

Write-Host "`n=== Проверка что настройка есть ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT key, value FROM app_settings WHERE key='stale_session_hours';"
Что ожидаем:
ALL SYNTAX OK
все 3 контейнера Up
в логах — Scheduler запущен в этом воркере
в scheduled_tasks — строка close_stale_sessions | t | */30 * * * *
в app_settings — пусто или stale_session_hours | 2 (если сохранял)
________________________________________
Что делаем дальше
Запускай по порядку:
Шаг 3+6 — патч отчётов. Ожидаем 3 OK + SYNTAX OK.
Шаг 4 — предохранитель. Ожидаем 1 OK + SYNTAX OK.
Шаг 5a — новая задача. Ожидаем OK + SYNTAX OK.
Шаг 5b — настройка. Ожидаем 3 OK + SYNTAX OK.
Шаг 5c — шаблон. Ожидаем OK + проверка.
Пересборка. Ожидаем статус Up и всё чисто.
Присылай вывод. Если где-то ERROR — стоп, пришли только этот шаг, поправим.
После этого:
Откроем /admin/settings и убедимся, что поле «Автозакрытие зависших сессий» появилось.
Сформируем отчёт за 23.09 и увидим, что 24 часа превратились в ~5-6.
Обнулим БД (docker compose down -v) для чистой работы.
>> & client\.venv\Scripts\python.exe _patch_tasks_stale.py === Патч tasks.py === OK: задача зарегистрирована в TASKS_REGISTRY Traceback (most recent call last): File "D:\tracker\_patch_tasks_stale.py", line 133, in <module> with open(PATH, "w", encoding="utf-8") as f: ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ PermissionError: [Errno 13] Permission denied: 'D:\\tracker\\server\\tasks.py'
Пользователь запустил патчи. Шаг 3+6 — OK. Шаг 5a (tasks.py) упал с PermissionError — файл занят. Скорее всего контейнер api его держит, или что-то ещё.
PermissionError на tasks.py — наиболее вероятная причина: файл открыт в редакторе (VS Code, Notepad++) или занят процессом. Также может быть — контейнер Docker смонтирован и файл read-only (но у нас не mount, у нас копируется при сборке).
Проверим и перезапустим. Также нужно проверить, что предыдущие шаги (4, 5b, 5c) выполнены — но пользователь показывает только вывод для 3+6 и 5a. Скорее всего он не успел/не показал остальные.
Дам диагностику + обходной путь: закрыть VS Code / редакторы, сохранить через временный файл, или использовать os.replace.
Также важно: после шага 3+6 надо пересобрать api, но перед этим надо доделать 4, 5a, 5b, 5c.
План ответа:
Причина — файл занят (VS Code / проводник / другое).
Диагностика — какие процессы держат файл (можно через PowerShell).
Обходной путь: если VS Code открыт — закрыть; или копировать через временный файл + os.replace.
Продолжить с шага 4, 5b, 5c.
Пересборка.
Дам скрипт-обходной путь, который пишет во временный файл и заменяет через os.replace — это работает даже если файл залочен на чтение/запись в другом процессе (но не всегда на Windows).
На Windows os.replace может не сработать, если файл открыт в другом процессе с эксклюзивной блокировкой. Проверим.
Также лучше сначала сохранить то, что уже сделано (шаг 3+6 прошёл), и не терять. Второй запуск 5a должен пойти.
Стратегия: сначала повторим 5a — возможно, был временный лок от антивируса. Если упадёт снова — попросим закрыть VS Code.
Ошибка PermissionError: [Errno 13] Permission denied на server/tasks.py — файл кем-то занят. Скорее всего, он открыт в редакторе (VS Code, Notepad++, PyCharm) или в проводнике залочен проводником/антивирусом.
Шаги 3+6 прошли — это отлично. Не теряем их результат.
Сначала — закрыть всё, что может держать файл:
Закрой VS Code / PyCharm / Notepad++, если открыт tasks.py или папка server/.
Закрой окно проводника Windows, если открыта папка D:\tracker\server.
Подожди 3 секунды (антивирус может проверять файл).
Теперь диагностика и повтор.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Кто держит tasks.py ===" -ForegroundColor Cyan
