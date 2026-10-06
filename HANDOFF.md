# HANDOFF.md — сводка проекта «Трекер»
Статус: черновик
Дата: 2026-10-05
Связанные файлы KB: 00_INDEX.md, 01_PRODUCT\01_OVERVIEW.md, 03_SERVER\01_ARCHITECTURE.md, 04_CLIENT\01_ARCHITECTURE.md, 09_OPS\01_RUNBOOK.md

## Назначение
Краткая сводка проекта «Трекер» для быстрого входа в контекст. Дополняет 00_INDEX.md: индекс — карта всех KB-файлов, HANDOFF — выжимка самого важного. Прикладывать вместе с 00_INDEX.md при переходе в новый чат.

---

## 1. Паспорт проекта
- **Название:** «Трекер» — система учёта рабочего времени сотрудников.
- **Рабочая папка:** `D:\tracker`.
- **KB:** `D:\tracker\docs\` (58 файлов).
- **Стек сервера:** FastAPI + PostgreSQL 16 + SQLAlchemy 2.0 + Alembic + nginx + Docker.
- **Стек клиента:** PyQt6 + httpx + pynput + keyring + cryptography + SQLite (WAL).
- **SCP:** PyQt6 (отдельное приложение `control/`).
- **Готовность:** ~90%. Осталось: PDF-экспорт, установщик, публикация версий, ca.pem через UI, i18n/темы до конца, SCP BuildTab/AdminTab, бэкапы, алерты.

---

## 2. Архитектура (кратко)
ПК сотрудника: Tracker.exe (PyQt6) + SQLite
│ HTTPS + HMAC-SHA256
▼
Сервер (Docker Compose):
nginx (443) → FastAPI (8000) → PostgreSQL 16

APScheduler (партиции, агрегаты, закрытие сессий)

Alembic (6 миграций)

партиционирование records по месяцам

text

---

## 3. Команды (шпаргалка)

### Сервер
```powershell
cd D:\tracker
docker compose up -d --build          # собрать и запустить
docker compose down                    # остановить
docker compose down -v                 # СБРОС БД (удаляет volume)
docker compose ps
docker compose logs api --tail=30
docker compose logs nginx --tail=30
docker compose restart api             # после правки HTML
docker compose down && docker compose up -d --build   # после правки Python
Клиент
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 30 -Encoding UTF8
Alembic
powershell
docker compose exec -T api alembic -c /app/server/alembic.ini revision --autogenerate -m "описание"
docker compose exec -T api alembic -c /app/server/alembic.ini upgrade head
Админка
text
https://localhost/admin/login
Логин: admin
Пароль: ADMIN_API_KEY из D:\tracker\.env
4. Ключевые решения (почему так)
Решение	Почему
HMAC-SHA256 на каждой записи	Целостность + офлайн-режим
Fernet для client_secret	Обратимое шифрование симметричного ключа
bcrypt (без passlib)	Меньше зависимостей, нет warnings
SQLite WAL на клиенте	Офлайн-first, транзакции
Партиционирование records по месяцам	До 100+ млн записей
5 метрик отчётов	Отработано, С трекером, Интенсивная, Эффективно, Пауза
close_session_at(last_activity)	Защита от «17 часов за день»
include_object в Alembic	Защита партиций от autogenerate
activity_gap_minutes = 5	Компромисс, настраивается
workday_start_hour = 6	Ночные смены, стандарт кадров
Union интервалов для 2 ПК	Не блокируем, не удваиваем
PivotTable.js, не WebDataRocks	Свободная лицензия, Excel-подобный UI
Скриншоты не собираются	Приватность + 152-ФЗ
Содержимое нажатий не пишется	COLLECT_KEYSTROKE_CHARS = False
5. Карта KB
Все детали — в D:\tracker\docs\. Основные разделы:

Раздел	Что внутри
01_PRODUCT	Обзор, роли, UI админки/клиента/SCP, глоссарий
02_METRICS	Метрики, отчёты, pivot, экспорт, календарь, графики
03_SERVER	Архитектура, API, модели, аутентификация, планировщик, партиции, Alembic, i18n, шаблоны, настройки
04_CLIENT	Архитектура, сбор, синхронизация, локальная БД, напоминания, UI, темы/i18n, автозапуск/обновление, регистрация
05_SCP	Обзор, сертификаты, сборка, администрирование
06_DEPLOY	Docker, nginx/TLS, установка на Windows, бэкапы, обновления, установщик
07_QUALITY	Тестирование, известные проблемы, диагностика, безопасность
08_LEGAL	152-ФЗ, согласия
09_OPS	Runbook, мониторинг, алерты, инциденты
99_RAW	История чатов, скриншоты, логи
6. Состояние (что сделано)
Сервер
✅ Регистрация ПК по bootstrap-токену.

✅ HMAC-подпись записей и батчей.

✅ Идемпотентность.

✅ Партиционирование records.

✅ Планировщик: 3 активные задачи + 4 отключённые.

✅ Alembic: 6 миграций, include_object.

✅ Роли, аутентификация, аудит.

✅ Настройки, календарь, графики.

Админка
✅ 75+ роутов.

✅ Все страницы CRUD.

✅ Отчёты: 6 группировок, 5 метрик, блок «Без привязки».

✅ Экспорт CSV/XLSX (PDF — старые колонки).

✅ Pivot (PivotTable.js).

✅ i18n RU/EN (частично).

✅ Планировщик, аудит, корзина.

Клиент
✅ Регистрация, трей, кнопки Старт/Пауза/Стоп.

✅ Сбор активности + window + idle.

✅ Офлайн-буфер (SQLite + WAL).

✅ Синхронизация + heartbeat.

✅ Напоминания.

⚠️ Темы, i18n, settings_dialog (частично).

SCP
✅ Вкладка «Сертификат».

⚠️ BuildTab, AdminTab — заглушки.

7. Что осталось (roadmap)
🔴 P0 — блокеры
PDF-экспорт отчётов (новые колонки).

Cookie 401 → редирект на /admin/login.

Установщик клиента (Inno Setup).

Публикация версий через UI.

🟡 P1 — эксплуатация
Замена ca.pem через UI.

Полный i18n клиента (retranslate главного окна).

Тёмная тема до конца.

SCP BuildTab/AdminTab.

Бэкапы по расписанию.

Просмотр логов клиента в админке.

Алерты (Telegram/Email).

🟢 P2 — развитие
Импорт/экспорт сотрудников через Excel.

Индивидуальные графики работы.

Отчёт «Опоздания/переработки».

Графики активности по часам.

Live-страница «Кто сейчас работает».

Страница «Сегодня».

Отчёт «Отделы × Программы».

Матрица «сотрудник × программа».

⚫ P3 — инфраструктура
Тесты pytest.

152-ФЗ (юридическое оформление).

Партиционирование hot-таблиц.

Мониторинг Prometheus/Grafana.

8. Стиль работы
Команды: PowerShell here-string ломается на блоках > 30 строк. Для крупных правок — Python-патчеры.

Проверка синтаксиса: всегда ast.parse() после правки Python.

Правки Python: docker compose down && docker compose up -d --build. Не restart.

Правки HTML: docker compose restart api — достаточно.

Проверка: docker compose logs api --tail=30, psql -c "...".

Стиль ответов: русский, «ты», комментарии в коде на русском.

Пользователь — не программист. Объяснять подробно, давать готовые скрипты.

9. Секреты (где что)
Секрет	Где
SECRET_ENCRYPTION_KEY	D:\tracker\.env
JWT_SECRET	D:\tracker\.env
ADMIN_API_KEY	D:\tracker\.env (пароль admin + admin API)
client_secret	keyring Windows + computers.client_secret_enc (Fernet)
TLS-ключ	D:\tracker\certs\privkey.pem
Bootstrap-токен	bootstrap_tokens (хеш)
Правило: реальные значения секретов не хранить в документации. Только форматы и процедуры ротации.

10. Приоритеты на ближайшее время
Закрыть P0: PDF, cookie 401, установщик, публикация версий.

Потом P1: ca.pem через UI, i18n, темы, SCP, бэкапы, алерты.

Затем P2: импорт/экспорт, графики, опоздания, Live, «Сегодня».

В конце P3: тесты, 152-ФЗ, мониторинг.

Главное: не переделывать уже сделанное. Сначала блокеры, потом удобство, потом развитие.

Готово. Один файл выше. Следующий — обновить 00_INDEX.md.

text

---

## Шаг 2. Обновить `00_INDEX.md`

Выполни в PowerShell:

```powershell
cd D:\tracker\docs

# 1. Заменить все "не создан" на "черновик"
(Get-Content 00_INDEX.md -Raw -Encoding UTF8).Replace('| не создан |', '| черновик |') |
  Set-Content 00_INDEX.md -Encoding UTF8 -NoNewline

# 2. Проверить результат
Select-String -Path 00_INDEX.md -Pattern "черновик" | Measure-Object
Select-String -Path 00_INDEX.md -Pattern "не создан" | Measure-Object
Должно быть: 58 черновиков, 0 «не создан».

Затем добавь строку про HANDOFF в конец таблицы индекса (перед 99_RAW или после). Вставь вручную или командой:

powershell
cd D:\tracker\docs
$handoffRow = '| `HANDOFF.md` | Сводка проекта | Краткая выжимка: паспорт, архитектура, команды, состояние, roadmap, секреты | черновик | все KB-файлы |'
$content = Get-Content 00_INDEX.md -Raw -Encoding UTF8
# Вставить перед строкой с 99_RAW
$content = $content -replace '(\| `99_RAW\\01_CHAT_HISTORY\.md`)', "$handoffRow`n`$1"
Set-Content 00_INDEX.md -Value $content -Encoding UTF8 -NoNewline