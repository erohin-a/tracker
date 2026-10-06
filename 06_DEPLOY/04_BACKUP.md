# Бэкапы
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 06_DEPLOY\01_DOCKER.md, 03_SERVER\03_MODELS.md, 05_SCP\01_OVERVIEW.md, 09_OPS\01_RUNBOOK.md

## Назначение
Описать резервное копирование и восстановление БД «Трекер»: что бэкапить, как, куда, как часто, что делать при потере данных. Это карта для администратора, который отвечает за сохранность, и для разработчика, который дорабатывает автоматизацию.

## Содержание

### Зачем нужны бэкапы
- **Потеря данных:** случайное `docker compose down -v` удаляет volume `pgdata`.
- **Сбой диска:** физическая поломка носителя.
- **Ошибка администратора:** удаление ПК через hard delete, сброс БД.
- **Миграция:** переезд на другой сервер.
- **Аудит:** восстановление истории за период.
- **152-ФЗ:** требование сохранности персональных данных.

### Что бэкапить

| Что | Как | Обязательно |
|---|---|---|
| БД `tracker` (все таблицы) | `pg_dump` | ✅ |
| Файл `.env` (секреты) | Копирование файла | ✅ |
| Сертификаты `certs/` | Копирование папки | ✅ |
| `client/ca.pem` | Копирование файла | ⚠ желательно |
| `docker-compose.yml` | Копирование файла | ⚠ желательно |
| `server/nginx.conf` | Копирование файла | ⚠ желательно |
| Volume `pgdata` | Docker snapshot | ❌ не рекомендуется |

**Ключевой момент:** без `SECRET_ENCRYPTION_KEY` из `.env` бэкап БД **бесполезен** — `client_secret` в `computers.client_secret_enc` не расшифруются. Храните `.env` отдельно от дампа.

### Ручной бэкап (`pg_dump`)

**Команда:**
```powershell
cd D:\tracker
docker compose exec -T db pg_dump -U tracker tracker > backup_$(Get-Date -Format yyyyMMdd_HHmm).sql
Что делает:

docker compose exec -T db — запуск внутри контейнера db без TTY.

pg_dump -U tracker tracker — дамп БД tracker.

> backup_YYYYMMDD_HHMM.sql — сохранение в файл.

Формат: plain SQL (текстовый). Можно смотреть, редактировать, восстанавливать через psql.

Альтернативные форматы:

powershell
# Custom format (сжатый, для pg_restore)
docker compose exec -T db pg_dump -U tracker -Fc tracker > backup.dump

# Directory format (параллельный дамп)
docker compose exec -T db pg_dump -U tracker -Fd -j 4 -f /tmp/backup_dir tracker
Размер: для 50 сотрудников и года данных — 100–500 МБ.

Время: 1–3 минуты.

Куда сохранять:

Не в D:\tracker\ — при переустановке потеряется.

Сетевая папка.

Облако (Яндекс.Диск, Google Drive).

Внешний диск.

Восстановление
Из plain SQL:

powershell
cd D:\tracker
Get-Content backup_20260926_0300.sql | docker compose exec -T db psql -U tracker -d tracker
Важно:

БД должна существовать.

Если таблицы уже есть — будет ошибка. Сначала сбросить:

powershell
docker compose down -v
docker compose up -d --build
# Дождаться миграций, потом восстановить
Из custom format:

powershell
docker compose exec -T db pg_restore -U tracker -d tracker --clean --if-exists < backup.dump
Проверка после восстановления:

sql
SELECT COUNT(*) FROM computers;
SELECT COUNT(*) FROM employees;
SELECT COUNT(*) FROM work_sessions;
SELECT COUNT(*) FROM records;
SELECT version_num FROM alembic_version;
Автоматический бэкап
Вариант 1: Windows Task Scheduler (рекомендуется)
Создать D:\tracker\backup.bat:

bat
@echo off
cd /d D:\tracker
docker compose exec -T db pg_dump -U tracker tracker > backup_%date:~-4%%date:~3,2%%date:~0,2%.sql
Настроить в Планировщике задач Windows:

Открыть «Планировщик заданий».

Создать задачу: «Tracker Backup».

Триггер: ежедневно в 03:00.

Действие: запуск D:\tracker\backup.bat.

Условия: «Выполнять только при подключении к сети» — снять.

Ротация (хранить 30 дней):
Добавить в backup.bat:

bat
forfiles /P D:\tracker\backups /M backup_*.sql /D -30 /C "cmd /c del @path"
Вариант 2: Планировщик в контейнере db
Не реализован.

Требует установки cron или pg_cron в контейнер.

Сложнее, чем Task Scheduler.

Вариант 3: SCP вкладка «Бэкапы»
Не реализована.

Планируется: кнопка «Сделать бэкап», настройка расписания, просмотр списка.

См. 05_SCP\01_OVERVIEW.md.

Модель backup_config (не реализована)
В server/models.py есть модель BackupConfig:

Поле	Тип	Описание
id	Integer PK	
enabled	Boolean	Включено ли
path	String(512)	Куда сохранять
schedule_cron	String(64)	По умолчанию 0 3 * * *
retention_days	Integer	По умолчанию 30
last_backup_at	DateTime	
Статус: модель есть, но планировщик её не использует. Бэкапы — только вручную или через Task Scheduler.

Что НЕ восстанавливается из бэкапа БД
Что	Почему	Как восстановить
.env (секреты)	Файл, не в БД	Хранить отдельно
certs/	Файлы, не в БД	Хранить отдельно
Volume pgdata	Не бэкапится через pg_dump	Только через pg_dump
Настройки Docker	В docker-compose.yml	Копировать файл
nginx.conf	Файл	Копировать файл
client/ca.pem	Файл	Пересобрать или копировать
Правило: бэкап = pg_dump + .env + certs/ + docker-compose.yml + nginx.conf.

Проверка бэкапа
Размер файла:

powershell
Get-Item D:\tracker\backups\backup_*.sql | Select-Object Name, Length
Если файл 0 байт — что-то пошло не так.

Начало файла:

powershell
Get-Content backup_20260926.sql -TotalCount 20
Должны быть строки -- PostgreSQL database dump, SET statement_timeout, CREATE TABLE.

Восстановление на тестовой БД:

Развернуть отдельный контейнер db_test.

Восстановить туда бэкап.

Проверить COUNT(*) по таблицам.

Retention (хранение)
Рекомендации:

Период	Хранить
Последние 7 дней	Ежедневные
Последние 4 недели	Еженедельные (воскресенье)
Последние 12 месяцев	Ежемесячные (1-е число)
Всё остальное	Удалять
Реализация: не автоматизирована. Вручную через Task Scheduler + forfiles или скрипт на Python.

Известные проблемы
Проблема	Причина	Решение
Бэкап 0 байт	docker compose exec без -T	Добавить -T
permission denied	Нет прав на запись в папку	Использовать D:\tracker\backups
database "tracker" does not exist	БД не создана	docker compose up -d --build
Восстановление падает на CREATE TABLE	Таблицы уже есть	Сбросить БД (down -v)
role "tracker" does not exist	Нет пользователя	Проверить docker-compose.yml
Бэкап идёт часами	Большая БД	Использовать -Fd -j 4
unexpected EOF при restore	Битый файл	Пересоздать бэкап
Файл в UTF-16	PowerShell > пишет в UTF-16	Использовать | Out-File -Encoding utf8
SECRET_ENCRYPTION_KEY утерян	Не хранится с бэкапом	Хранить .env отдельно
Восстановление после docker compose down -v
Сценарий: случайно удалили volume pgdata.

Что делать:

Не паниковать. Проверить, есть ли бэкап.

Не запускать docker compose up -d --build — Alembic создаст пустые таблицы.

Развернуть сервер с пустым volume.

Восстановить бэкап:

powershell
Get-Content backup_YYYYMMDD.sql | docker compose exec -T db psql -U tracker -d tracker
Проверить COUNT(*).

Перезапустить api:

powershell
docker compose restart api
Если бэкапа нет:

Данные потеряны безвозвратно.

Клиенты накопят новые данные и отправят.

Старые сессии/records восстановить нельзя.

Хранение .env
Правило: .env никогда не коммитить в git.

Хранение:

Отдельный файл в защищённой папке.

В менеджере паролей (KeePass, 1Password, Bitwarden).

На бумаге в сейфе (для критичных систем).

Почему это критично:

Без SECRET_ENCRYPTION_KEY — client_secret в БД не расшифруются.

Без ADMIN_API_KEY — нет доступа в админку.

Без JWT_SECRET — сессии админки не работают.

Проверка целостности бэкапа
Вариант 1 (простой):

powershell
# Размер > 0
Get-Item backup.sql | Select-Object Length

# Начало и конец
Get-Content backup.sql -TotalCount 5
Get-Content backup.sql -Tail 5
Конец должен содержать -- PostgreSQL database dump complete.

Вариант 2 (полный):

Создать тестовую БД:

powershell
docker run --rm -d --name pg_test -e POSTGRES_USER=tracker -e POSTGRES_PASSWORD=tracker -e POSTGRES_DB=tracker -p 5433:5432 postgres:16-alpine
Восстановить:

powershell
Get-Content backup.sql | docker exec -i pg_test psql -U tracker -d tracker
Проверить:

powershell
docker exec -i pg_test psql -U tracker -d tracker -c "SELECT COUNT(*) FROM computers;"
Удалить тестовую БД:

powershell
docker stop pg_test
Что НЕ реализовано
Автоматический бэкап через планировщик приложения.

Вкладка «Бэкапы» в SCP.

Просмотр списка бэкапов в админке.

Восстановление из UI.

Инкрементальные бэкапы.

Бэкап в облако (S3, Яндекс.Диск).

Шифрование бэкапа.

Уведомление при сбое бэкапа.

Мониторинг размера бэкапов.

Ротация с автоматическим удалением старых.

Ключевые решения
pg_dump как основной инструмент. Стандарт PostgreSQL, надёжно.

Plain SQL для читаемости. Custom format — для больших БД.

.env и certs/ хранить отдельно от БД. Без них бэкап бесполезен.

Не бэкапить volume pgdata. pg_dump надёжнее и переносимее.

Windows Task Scheduler для автоматизации. Проще, чем cron в контейнере.

Ежедневно в 03:00. Минимальная нагрузка.

Хранить 30 дней. Компромисс между объёмом и историей.

Сетевые папки или облако. Не на том же диске.

Проверка бэкапа раз в месяц. Восстановление на тестовой БД.

SECRET_ENCRYPTION_KEY критичен. Без него — всё пропало.

Ссылки на код
запросить: docker-compose.yml — контейнер db

запросить: server/models.py — модель BackupConfig (не используется)

запросить: server/tasks.py — TASKS_REGISTRY (нет задачи бэкапа)

запросить: control/gui.py — AdminTab (вкладка «Бэкапы» — не реализована)

запросить: D:\tracker\.env — секреты

запросить: D:\tracker\certs\ — сертификаты

Открытые вопросы / чего не хватает
нет данных: реализована ли автоматизация бэкапа — нет.

нет данных: где хранятся бэкапы в проекте — не описано.

нет данных: есть ли скрипт backup.bat — обсуждался, возможно, не создан.

нет данных: тестировалось ли восстановление из бэкапа — не подтверждено.

нет данных: есть ли retention-политика — рекомендации есть, автоматики нет.

не решено: делать ли бэкап через BackupConfig + планировщик.

не решено: где хранить бэкапы (сетевая папка, облако, внешний диск).

не решено: шифровать ли бэкап (152-ФЗ).

не решено: как уведомлять о сбое бэкапа (Telegram, Email).

не решено: нужны ли инкрементальные бэкапы.

не решено: делать ли бэкап на уровне Docker volume (snapshot).

не решено: как восстанавливать .env и certs/ — вручную или через SCP.

не решено: нужна ли кнопка «Сделать бэкап» в админке.

не решено: как быть с большими БД (100+ ГБ) — -Fd -j 4.

не решено: должен ли бэкап включать audit_log — да, по умолчанию.

не решено: нужен ли экспорт records в CSV для долгосрочного хранения.

Готово. Один файл выше. Следующий по индексу — 06_DEPLOY\05_UPDATES.md.