# Runbook
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 07_QUALITY\03_DIAGNOSTICS.md, 07_QUALITY\02_KNOWN_ISSUES.md, 03_SERVER\05_TASKS.md

## Назначение
Ежедневный и еженедельный чек-лист администратора «Трекера»: что проверять, какие команды выполнять, что делать при типовых сбоях. Это карта для администратора, который эксплуатирует систему, и для дежурного, который разбирается с инцидентом.

## Содержание

### Ежедневные проверки (5 минут)

#### Утро — проверить, что всё живо
```powershell
cd D:\tracker

# 1. Docker Desktop запущен?
docker info | Select-String "Server Version"

# 2. Контейнеры живы?
docker compose ps

# 3. API отвечает?
curl.exe -k https://localhost/api/v1/version

# 4. БД видит таблицы?
docker compose exec -T db psql -U tracker -d tracker -c "\dt"

# 5. Планировщик работал ночью?
docker compose exec -T db psql -U tracker -d tracker -c "SELECT task_name, status, started_at FROM task_runs ORDER BY id DESC LIMIT 5;"
Что должно быть:

Все три контейнера Up.

API отвечает JSON.

БД видит таблицы.

В task_runs нет error за последние 24 часа.

Дашборд (30 секунд)
Открыть https://localhost/admin.

Компьютеры онлайн — норма 80–100% в рабочее время.

Сессии сегодня — растут в течение дня.

Последние действия — нет подозрительных.

Аварийные за 24 часа — не больше 2–3 (норма).

Проверка ПК (1 минута)
Открыть /admin/computers.

Отсортировать по last_seen_at.

Если ПК не выходил на связь > 30 минут в рабочее время — связаться с сотрудником.

Логи (1 минута)
powershell
docker compose logs api --tail=50 | Select-String "Error|Traceback|Exception"
Если есть ошибки — смотреть 07_QUALITY\02_KNOWN_ISSUES.md.

Еженедельные проверки (30 минут)
Понедельник — итоги прошлой недели
/admin/reports → период «Прошлая неделя».

Группировка «По сотрудникам».

Проверить:

Нет аномальных значений (17+ часов за день).

Нет сотрудников с 0 часов.

Аварийные сессии — в разумных пределах.

Проверка партиций
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT tablename FROM pg_tables WHERE tablename LIKE 'records_%' AND tablename != 'records' ORDER BY tablename;"
Должно быть: партиции на 12 месяцев вперёд. Если нет — запустить create_future_partitions вручную.

Проверка records_default
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM records_default;"
Должно быть: 0. Если больше — есть проблема с партициями.

Размер БД
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT pg_size_pretty(pg_database_size('tracker'));"
docker system df
Норма: рост предсказуемый, нет скачков.

Бэкап
Проверить, что бэкап за неделю есть.

Проверить размер (не 0 байт).

Раз в месяц — восстановить на тестовой БД.

Сертификат
powershell
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -dates
Норма: осталось > 30 дней. Если меньше — планировать перевыпуск.

Свободное место
powershell
Get-PSDrive D | Select-Object Used, Free
Норма: > 10% свободно. Если меньше — чистить.

Логи за неделю
powershell
docker compose logs api --since 168h 2>&1 | Select-String "Error|Traceback" | Measure-Object
Считаем количество ошибок. Если растёт — разбираться.

Ежемесячные проверки (1–2 часа)
Отчёт за месяц
/admin/reports → период «Прошлый месяц».

Группировка «Рабочие дни × Сотрудник».

Проверить:

Все сотрудники работали.

Нет аномалий.

Отработано ≈ С трекером.

Аудит
/admin/audit — последние 200 записей.

Проверить, нет ли подозрительных действий.

/admin/logins — история входов.

Проверить, нет ли неудачных попыток входа.

Проверка планировщика
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron, last_run_at, last_run_status FROM scheduled_tasks ORDER BY id;"
Норма: критичные задачи (create_future_partitions, aggregate_daily_stats, close_stale_sessions) включены и успешны.

Восстановление из бэкапа (тест)
Создать тестовую БД:

powershell
docker run --rm -d --name pg_test -e POSTGRES_USER=tracker -e POSTGRES_PASSWORD=tracker -e POSTGRES_DB=tracker -p 5433:5432 postgres:16-alpine
Восстановить последний бэкап.

Проверить COUNT(*) по ключевым таблицам.

Удалить тестовую БД.

Обновление документации
Обновить 07_QUALITY\02_KNOWN_ISSUES.md при новых проблемах.

Обновить этот RUNBOOK при изменении процедур.

Типовые сбои и что делать
1. Клиент не отправляет данные
Симптом: в /admin/computers ПК офлайн, last_seen_at старый.

Что делать:

Проверить, что ПК включён и клиент запущен.

Проверить client.log на ПК:

powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 30 -Encoding UTF8
Проверить связь: curl.exe -k https://<server>/api/v1/version.

Если getaddrinfo failed — исправить TRACKER_SERVER_URL на https://127.0.0.1.

Если SSL: CERTIFICATE_VERIFY_FAILED — обновить ca.pem.

Если 401 — перерегистрировать ПК.

2. Сессия висит 17 часов
Симптом: в отчёте аномально длинная сессия.

Что делать:

Проверить, что close_stale_sessions включена:

powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT enabled FROM scheduled_tasks WHERE name='close_stale_sessions';"
Проверить stale_session_hours в /admin/settings.

Если сессия старая — закрыть вручную:

sql
UPDATE work_sessions SET session_end = (SELECT MAX(client_ts) FROM records WHERE session_uid = work_sessions.session_uid), abnormal_termination = true WHERE session_end IS NULL AND session_start < NOW() - INTERVAL '2 hours';
3. Задача планировщика падает
Симптом: в task_runs статус error.

Что делать:

Посмотреть сообщение:

powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT task_name, status, message FROM task_runs WHERE status='error' ORDER BY id DESC LIMIT 5;"
Посмотреть логи API:

powershell
docker compose logs api --tail=100 | Select-String "Error|Traceback"
Типовые причины:

NameError: WorkSession — нет импорта → исправлено.

PermissionError — файл занят → обход через copy /y.

После исправления — пересобрать:

powershell
docker compose down && docker compose up -d --build
4. 500 на отчётах
Симптом: ошибка при генерации отчёта.

Что делать:

Логи:

powershell
docker compose logs api --tail=100
Типовые причины:

Paragraph не импортирован → исправлено.

Шаблон использует dt, но фильтр убран → вернуть фильтр.

cutoff_online не передан → исправить.

Перезапустить API:

powershell
docker compose restart api
5. Клиент «офлайн», сервер работает
Симптом: дашборд показывает ПК офлайн, но сервер отвечает.

Что делать:

Проверить связь с ПК:

powershell
Test-NetConnection <server-ip> -Port 443
Проверить ca.pem на ПК.

Проверить, что сертификат не истёк:

powershell
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -dates
Проверить, что TRACKER_SERVER_URL корректен.

6. Docker Desktop не запускается
Симптом: Cannot connect to the Docker daemon.

Что делать:

Проверить, что WSL 2 включён:

powershell
wsl --status
Проверить, что виртуализация включена в BIOS.

Перезапустить Docker Desktop.

Если не помогает — перезагрузить ПК.

7. Порт 443 занят
Симптом: nginx не поднимается.

Что делать:

Найти, кто держит порт:

powershell
netstat -ano | findstr :443
Найти процесс по PID:

powershell
Get-Process -Id <pid>
Остановить или сменить порт.

8. База данных не отвечает
Симптом: db в состоянии unhealthy.

Что делать:

Логи:

powershell
docker compose logs db --tail=50
Проверить, что volume не удалён:

powershell
docker volume ls | Select-String pgdata
Если volume на месте — перезапустить:

powershell
docker compose restart db
9. Не хватает места на диске
Симптом: disk full.

Что делать:

Проверить размер БД:

powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT pg_size_pretty(pg_database_size('tracker'));"
Очистить старые партиции (DROP TABLE records_YYYY_MM для месяцев старше retention).

Очистить логи Docker:

powershell
docker system prune -a --volumes
Очистить старые бэкапы.

10. Забыл пароль админа
Симптом: не могу войти в админку.

Что делать:

Если есть другой админ — он может сбросить пароль через /admin/users/{id}/reset-password.

Если нет — через SQL:

sql
-- Сгенерировать bcrypt-хеш нового пароля
-- Обновить в БД
UPDATE admin_users SET password_hash = '<new_hash>' WHERE username = 'admin';
Или через ADMIN_API_KEY из .env.

Команды «первой помощи»
Перезапустить API после правки HTML
powershell
docker compose restart api
Пересобрать API после правки Python
powershell
docker compose down && docker compose up -d --build
Посмотреть логи в реальном времени
powershell
docker compose logs -f api
Проверить, что всё живо
powershell
docker compose ps && curl.exe -k https://localhost/api/v1/version
Открыть psql
powershell
docker compose exec db psql -U tracker -d tracker
Сделать бэкап БД
powershell
docker compose exec -T db pg_dump -U tracker tracker > backup_$(Get-Date -Format yyyyMMdd_HHmm).sql
Перезапустить сертификат
powershell
docker compose restart nginx
Что делать при инциденте
Порядок действий
Зафиксировать проблему. Что, когда, где.

Собрать диагностику:

powershell
docker compose logs api --tail=200 > _diag_api.log
docker compose logs nginx --tail=100 > _diag_nginx.log
docker compose logs db --tail=100 > _diag_db.log
docker compose ps > _diag_ps.log
Проверить по 07_QUALITY\02_KNOWN_ISSUES.md — возможно, уже известна.

Применить решение из файла.

Если не помогает — восстановить из бэкапа.

Записать инцидент в 09_OPS\04_INCIDENTS.md (если создан).

Уведомить ответственного.

Если всё сломалось
Не паниковать. Сначала бэкап:

powershell
docker compose exec -T db pg_dump -U tracker tracker > emergency_backup.sql
Проверить volume pgdata — не удалён ли.

Полностью пересобрать:

powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 30
docker compose ps
docker compose logs api --tail=50
Восстановить бэкап, если нужно.

Ссылки на другие KB-файлы
Тема	Файл
Известные проблемы	07_QUALITY\02_KNOWN_ISSUES.md
Диагностика	07_QUALITY\03_DIAGNOSTICS.md
Docker	06_DEPLOY\01_DOCKER.md
Nginx/TLS	06_DEPLOY\02_NGINX_TLS.md
Бэкапы	06_DEPLOY\04_BACKUP.md
Планировщик	03_SERVER\05_TASKS.md
Партиции	03_SERVER\06_PARTITIONS.md
Безопасность	07_QUALITY\04_SECURITY.md
152-ФЗ	08_LEGAL\01_152FZ.md
Ключевые решения
Ежедневные проверки — 5 минут. Утро, дашборд, логи.

Еженедельные — 30 минут. Партиции, бэкап, сертификат, место.

Ежемесячные — 1–2 часа. Отчёт, аудит, тест восстановления.

Типовые сбои — с готовыми решениями. 10 сценариев.

Команды «первой помощи» — в одном месте. Быстрый доступ.

Сбор диагностики — в файлы. Удобно прислать разработчику.

Порядок при инциденте — от фиксации к решению. Не паниковать.

Ссылки на код
запросить: docker-compose.yml — контейнеры

запросить: server/main.py — API, middleware

запросить: server/tasks.py — задачи планировщика

запросить: server/web_admin.py — админка

запросить: client/db.py — локальная БД

запросить: client/main.py — логика клиента

Открытые вопросы / чего не хватает
нет данных: есть ли регламент эскалации — не описан.

нет данных: есть ли дежурный администратор — не назначен.

нет данных: есть ли SLA на восстановление — не определён.

нет данных: есть ли процедура инцидентов (пост-мортем) — планируется.

не решено: нужен ли формальный журнал инцидентов (отдельный файл).

не решено: как эскалировать проблему к разработчику.

не решено: нужны ли автоматические алерты (P2).

не решено: как быть с инцидентами в нерабочее время.

не решено: нужен ли мониторинг (Prometheus/Grafana, P3).

не решено: как тестировать процедуры восстановления.

не решено: нужна ли страница /admin/health для быстрой диагностики.

не решено: как обучать новых администраторов.

не решено: нужна ли автоматизация бэкапов через Task Scheduler (P2).

не решено: как быть с инцидентами на удалённых ПК (без физического доступа).

не решено: нужна ли интеграция с тикет-системой.

Готово. Один файл выше. Следующий по индексу — 09_OPS\02_MONITORING.md.