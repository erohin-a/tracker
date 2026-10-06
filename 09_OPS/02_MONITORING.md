# Мониторинг
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 09_OPS\01_RUNBOOK.md, 07_QUALITY\03_DIAGNOSTICS.md, 03_SERVER\05_TASKS.md

## Назначение
Описать, что и как мониторить в «Трекере»: здоровье сервера, БД, планировщика, клиентов, свободное место, сертификат. Это карта для администратора, который следит за системой, и для разработчика, который планирует автоматизацию.

## Содержание

### Принципы
- **Мониторинг ручной.** Автоматизации нет.
- **Проверки регулярные.** Ежедневно, еженедельно, ежемесячно.
- **Метрики простые.** Без Prometheus/Grafana (P3).
- **Источник — логи и SQL.** Никаких внешних систем.
- **Алерты — в планах (P2).** Сейчас только ручная проверка.

### Что мониторить

| Область | Что проверять | Периодичность | Приоритет |
|---|---|---|---|
| Сервер | Docker, контейнеры, API | Ежедневно | Высокий |
| БД | Размер, таблицы, партиции | Еженедельно | Высокий |
| Планировщик | `task_runs`, ошибки | Ежедневно | Высокий |
| Клиенты | Онлайн/офлайн ПК | Ежедневно | Высокий |
| Свободное место | Диск, volume | Еженедельно | Средний |
| Сертификат | Срок действия | Еженедельно | Средний |
| Бэкапы | Наличие, размер | Еженедельно | Высокий |
| Ошибки API | 500, трейсбеки | Ежедневно | Высокий |
| Аудит | Подозрительные действия | Ежемесячно | Средний |

---

### 1. Сервер и контейнеры

#### Проверки
```powershell
cd D:\tracker

# Docker запущен
docker info | Select-String "Server Version"

# Контейнеры живы
docker compose ps

# API отвечает
curl.exe -k https://localhost/api/v1/version

# Nginx отвечает
curl.exe -k -I https://localhost/admin/login
Норма
Три контейнера: db, api, nginx — все Up.

API возвращает JSON.

Nginx возвращает 200 или 302.

Отклонения
Симптом	Что значит	Действие
Контейнер Restarting	Ошибка в коде/миграции	docker compose logs <name> --tail=100
Контейнер Exit	Упал	То же
db unhealthy	БД не отвечает	docker compose logs db --tail=50
API не отвечает	Ошибка приложения	Логи API
Nginx не отвечает	Ошибка конфига/порта	Логи nginx
2. База данных
Метрики
Метрика	SQL	Норма
Размер БД	SELECT pg_size_pretty(pg_database_size('tracker'));	Растёт предсказуемо
Количество записей	SELECT COUNT(*) FROM records;	Растёт в рабочее время
Количество сессий	SELECT COUNT(*) FROM work_sessions;	Растёт в рабочее время
Незакрытые сессии	SELECT COUNT(*) FROM work_sessions WHERE session_end IS NULL;	Не больше 1–2
Записи в records_default	SELECT COUNT(*) FROM records_default;	0
Партиции	SELECT tablename FROM pg_tables WHERE tablename LIKE 'records_%';	12+ месяцев вперёд
Размер audit_log	SELECT pg_size_pretty(pg_total_relation_size('audit_log'));	Не растёт бесконтрольно
Проверки
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT pg_size_pretty(pg_database_size('tracker'));"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM records;"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM records_default;"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT tablename FROM pg_tables WHERE tablename LIKE 'records_%' AND tablename != 'records' ORDER BY tablename;"
Отклонения
Симптом	Что значит	Действие
records_default > 0	Нет партиции на месяц	Запустить create_future_partitions
Партиции < 6 месяцев вперёд	Не создаются	Проверить планировщик
Размер БД растёт скачками	Утечка данных	Проверить records, audit_log
Незакрытых сессий > 5	Проблема с close_stale_sessions	Проверить задачу
audit_log растёт бесконтрольно	Нет retention	Включить cleanup_old_* (P2)
3. Планировщик
Метрики
Метрика	SQL	Норма
Задачи включены	SELECT name, enabled FROM scheduled_tasks;	Критичные — true
Последний запуск	SELECT task_name, status, started_at FROM task_runs ORDER BY id DESC LIMIT 5;	Без error
Ошибки за 24 часа	SELECT COUNT(*) FROM task_runs WHERE status='error' AND started_at >= NOW() - INTERVAL '24 hours';	0
Проверки
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT name, enabled, schedule_cron, last_run_status FROM scheduled_tasks ORDER BY id;"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT task_name, status, started_at, message FROM task_runs ORDER BY id DESC LIMIT 10;"
Критичные задачи
create_future_partitions — должна быть включена.

aggregate_daily_stats — должна быть включена.

close_stale_sessions — должна быть включена.

Отклонения
Симптом	Что значит	Действие
Задача disabled	Кто-то выключил	Включить в /admin/scheduler
error в task_runs	Ошибка в задаче	Смотреть логи, 07_QUALITY\02_KNOWN_ISSUES.md
Нет запусков за сутки	Scheduler не работает	Проверить advisory lock, логи API
Задача не создаёт партиции	Ошибка SQL	Смотреть логи, запустить вручную
4. Клиенты (ПК сотрудников)
Метрики
Метрика	SQL	Норма
ПК онлайн	SELECT COUNT(*) FROM computers WHERE last_seen_at >= NOW() - INTERVAL '10 minutes';	80–100% в рабочее время
ПК офлайн	SELECT hostname, last_seen_at FROM computers WHERE last_seen_at < NOW() - INTERVAL '30 minutes' AND is_active = true;	Не больше 5–10%
ПК отозванные	SELECT COUNT(*) FROM computers WHERE is_active = false;	По ситуации
Версии клиентов	SELECT client_version, COUNT(*) FROM computers GROUP BY client_version;	Большинство на последней
Проверки
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM computers WHERE last_seen_at >= NOW() - INTERVAL '10 minutes';"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT hostname, last_seen_at FROM computers WHERE is_active = true AND last_seen_at < NOW() - INTERVAL '30 minutes' ORDER BY last_seen_at;"
Отклонения
Симптом	Что значит	Действие
Много ПК офлайн	Проблема с сетью/сервером	Проверить API, nginx
Один ПК офлайн > часа	Проблема на ПК	Связаться с сотрудником
ПК на старой версии	Не обновились	Проверить /api/v1/version
ПК отозван	revoke	Перерегистрация
5. Свободное место
Метрики
powershell
Get-PSDrive D | Select-Object Used, Free
docker system df
Норма
Диск D: > 10% свободно.

Docker: volume pgdata не больше 70% от диска.

Отклонения
Симптом	Что значит	Действие
Диск < 10%	Мало места	Чистить логи, партиции, бэкапы
Volume растёт быстро	Утечка данных	Проверить records, audit_log
Docker занимает много	Старые образы	docker system prune -a
6. Сертификат
Метрики
powershell
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -dates
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -fingerprint -sha256
Норма
Осталось > 30 дней.

SAN содержит localhost и 127.0.0.1.

Отклонения
Симптом	Что значит	Действие
Осталось < 30 дней	Скоро истечёт	Перевыпустить через SCP
Осталось < 7 дней	Критично	Перевыпустить срочно
Истёк	Клиенты не подключаются	Перевыпустить + раздать ca.pem
Отпечаток изменился	Кто-то перевыпустил	Проверить audit_log
7. Бэкапы
Метрики
powershell
Get-Item D:\tracker\backups\backup_*.sql | Select-Object Name, Length, LastWriteTime
Норма
Ежедневный бэкап есть.

Размер > 0 байт.

Возраст < 24 часов.

Отклонения
Симптом	Что значит	Действие
Нет бэкапа за сутки	Скрипт не сработал	Проверить Task Scheduler
Размер 0 байт	Ошибка pg_dump	Проверить команду
Бэкап старый (> 7 дней)	Не делается	Настроить автоматизацию
Файл не читается	Битый	Пересоздать
8. Ошибки API
Метрики
powershell
docker compose logs api --tail=100 | Select-String "Error|Traceback|Exception" | Measure-Object
Норма
0 ошибок за последний час.

Отклонения
Симптом	Что значит	Действие
Traceback в логах	Ошибка Python	Смотреть 07_QUALITY\02_KNOWN_ISSUES.md
500 регулярно	Системная проблема	Собрать диагностику
401 массово	Сгорели токены	Проверить /admin/tokens
409 на sessions	Старая версия клиента	Обновить клиент
9. Аудит и безопасность
Метрики
powershell
docker compose exec -T db psql -U tracker -d tracker -c "SELECT created_at, actor, entity, action FROM audit_log ORDER BY id DESC LIMIT 20;"
docker compose exec -T db psql -U tracker -d tracker -c "SELECT COUNT(*) FROM admin_logins WHERE success = false AND created_at >= NOW() - INTERVAL '24 hours';"
Норма
Нет подозрительных действий.

Неудачных входов < 5 за 24 часа.

Отклонения
Симптом	Что значит	Действие
Много неудачных входов	Brute-force	Проверить IP, добавить rate limiting (P2)
Странные действия в аудите	Компрометация	Сменить пароли, ротировать ключи
Входы с новых IP	Возможная угроза	Проверить с админом
Сводная таблица метрик
Метрика	Норма	Как проверить
Контейнеры Up	3/3	docker compose ps
API отвечает	JSON	curl.exe -k https://localhost/api/v1/version
ПК онлайн	80–100%	SQL по last_seen_at
Незакрытых сессий	≤ 2	SQL по session_end IS NULL
records_default	0	SQL
Партиции вперёд	≥ 12 мес	SQL
Ошибки в task_runs	0 за 24ч	SQL
Свободно на диске	> 10%	Get-PSDrive D
Сертификат	> 30 дней	openssl x509 -dates
Бэкап	< 24 часов	Get-Item backup*.sql
500 в логах	0 за час	Select-String
Что НЕ реализовано
Prometheus + Grafana (P3).

Автоматические алерты (P2).

Health-страница /admin/health.

Метрики в реальном времени.

Интеграция с Telegram/Email.

Автоматическая проверка сертификата.

Автоматическая проверка бэкапов.

Мониторинг клиентов из админки.

Дашборд «Требуют внимания».

Что делать при отклонении
Зафиксировать отклонение (какая метрика, какое значение).

Проверить по 07_QUALITY\02_KNOWN_ISSUES.md.

Собрать диагностику (см. 07_QUALITY\03_DIAGNOSTICS.md).

Применить решение из RUNBOOK (09_OPS\01_RUNBOOK.md).

Записать в журнал инцидентов (P3).

Ключевые решения
Ручной мониторинг. Без внешних систем.

Простые метрики. SQL + логи + команды.

Регулярность. Ежедневно / еженедельно / ежемесячно.

Сводная таблица метрик. Быстрая оценка.

Критичные метрики — высокий приоритет. ПК онлайн, партиции, бэкапы, ошибки.

Автоматизация — в планах (P3). Prometheus/Grafana.

Алерты — в планах (P2). Telegram/Email.

Health-страница — в планах (P2). /admin/health.

Ссылки на код
запросить: docker-compose.yml — контейнеры

запросить: server/main.py — middleware, API

запросить: server/tasks.py — задачи, TASKS_REGISTRY

запросить: server/models.py — модели для SQL

запросить: client/db.py — локальная БД клиента

запросить: server/web_admin.py — админка, дашборд

запросить: certs/fullchain.pem — сертификат

Открытые вопросы / чего не хватает
нет данных: реализован ли Prometheus/Grafana — нет (P3).

нет данных: есть ли health-страница — нет.

нет данных: есть ли алерты — нет (P2).

нет данных: тестировались ли метрики на больших объёмах — нет.

нет данных: есть ли дашборд «Требуют внимания» — нет.

не решено: нужны ли алерты (P2).

не решено: нужен ли Prometheus/Grafana (P3).

не решено: нужна ли health-страница в админке.

не решено: нужен ли мониторинг клиентов из админки.

не решено: нужна ли автоматическая проверка сертификата (за 30 дней).

не решено: нужна ли автоматическая проверка бэкапов.

не решено: как быть с мониторингом на удалённых ПК.

не решено: нужен ли rate limiting на API (P2).

не решено: нужен ли журнал инцидентов (P3).

не решено: как тестировать метрики перед внедрением автоматизации.

не решено: нужен ли экспорт метрик в CSV для отчётов.

не решено: как быть с мониторингом в нерабочее время.

не решено: нужна ли интеграция с тикет-системой (Jira, Redmine).

не решено: нужен ли SCP-раздел «Мониторинг».

Готово. Один файл выше. Следующий по индексу — 09_OPS\03_ALERTS.md.