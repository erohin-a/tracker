# HANDOFF.md — сводка проекта «Трекер»
Статус: черновик
Дата: 2026-10-07
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
- **Готовность:** ~95%. Осталось: ca.pem через UI, i18n/темы до конца, бэкапы, алерты, публикация версий.

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
Сводные — в Excel, не в вебе	PivotTable.js убрали: сложно настраивать, обычный XLSX удобнее
Скриншоты не собираются	Приватность + 152-ФЗ
Редирект 401 на /admin/login через middleware	UX браузера: вместо JSON — форма логина; API-ветка /admin/api/* не тронута
next после логина (со скрытым полем)	Возврат на исходную страницу; проверяем, что путь начинается с /admin (защита от open redirect)
SCP AdminTab как «аварийный люк»	Критичные операции (пароль админа, ADMIN_API_KEY) — напрямую в БД/.env; удобные (токены, диагностика) — через API. Работает, даже если api лежит
Содержимое нажатий не пишется	COLLECT_KEYSTROKE_CHARS = False
5. Карта KB
Все детали — в D:\tracker\docs\. Основные разделы:

Раздел	Что внутри
01_PRODUCT	Обзор, роли, UI админки/клиента/SCP, глоссарий
02_METRICS	Метрики, отчёты, экспорт (CSV/XLSX), календарь, графики
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

✅ Экспорт CSV/XLSX. PDF/печать — через браузер (Ctrl+P).

❌ Pivot (PivotTable.js) — удалён. Сводные строим в Excel из XLSX.

✅ i18n RU/EN (частично).

✅ Планировщик, аудит, корзина.
✅ Cookie 401 → редирект на /admin/login?next=... (middleware в main.py).
✅ После логина возврат на исходную страницу (next, безопасно проверяется).

Клиент
✅ Регистрация, трей, кнопки Старт/Пауза/Стоп.

✅ Сбор активности + window + idle.

✅ Офлайн-буфер (SQLite + WAL).

✅ Синхронизация + heartbeat.

✅ Напоминания.

⚠️ Темы, i18n, settings_dialog (частично).

SCP
✅ Вкладка «Сертификат».

✅ BuildTab (2026-10-11): 3 кнопки (полная сборка / только PyInstaller / только Inno),
   чекбоксы clean и skip PyInstaller, tooltips, лог сборки. control/build_tab.py.
✅ AdminTab (2026-10-11), «гибрид». control/admin_tab.py + control/admin.py.
   Напрямую (docker compose exec api): reset_admin_password, recreate_admin,
   rotate_admin_api_key (бэкап .env), db_diagnostics.
   Через API: Проверить API, Статус сервисов (docker compose ps).

7. Что осталось (roadmap)
🔴 P0 — блокеры



Публикация версий через UI.

🟡 P1 — эксплуатация
Замена ca.pem через UI.

Полный i18n клиента (retranslate главного окна).

Тёмная тема до конца.


Бэкапы по расписанию.

Просмотр логов клиента в админке.

Алерты (Telegram/Email).
UX-аудит админки и клиента: интуитивность, всплывающие подсказки (тултипы)
у ключевых кнопок, что упущено, единый стиль диалогов, тексты сообщений.

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
Закрыть P0: публикация версий через UI.

Параллельно P1: ca.pem через UI, UX-аудит админки и клиента (тултипы, интуитивность),
i18n, темы, бэкапы, алерты.

Затем P2: импорт/экспорт, графики, опоздания, Live, «Сегодня».

В конце P3: тесты, 152-ФЗ, мониторинг.

Главное: не переделывать уже сделанное. Сначала блокеры, потом удобство, потом развитие.

---

## 11. Что делать в следующем чате (после handoff)

1. Реализовать ca.pem через UI (SCP).
2. Публикация версий через UI.
3. UX-аудит админки и клиента (тултипы, интуитивность, единый стиль ошибок).

---

## 12. Обновление 2026-10-12 (после handoff)

### Реализовано в SCP
- Вкладка «Сервисы» (control/services_tab.py): перезапуск
  контейнеров (nginx/api/db/всё/полная пересборка), логи, alembic
  current/history/heads. Все кнопки с tooltips.
- Вкладка «Сеть» (control/network_tab.py): LAN-IP, правило
  брандмауэра Tracker HTTPS, редактирование deploy.json,
  hosts-строка, кнопка «Открыть админку».
- Кнопка «Быстрое продление (только срок)» в CertificateTab.
- Кнопка «Перевыпуск сертификата с LAN-IP» на вкладке «Сеть».
- Tooltips на всех новых и ключевых старых элементах.
- Вшивание server_url из deploy.json в client/.env при сборке
  (control/build.py, prepare_client_env).
- installer.iss: client/.env -> %APPDATA%\Tracker\.env.

### Новые файлы
- control/deploy.py — модуль чтения/записи deploy.json.
- control/services_tab.py — вкладка «Сервисы».
- control/network_tab.py — вкладка «Сеть».
- D:\tracker\deploy.json — единый конфиг деплоя.

### Изменены
- control/gui.py — подключены ServicesTab и NetworkTab.
- control/build.py — prepare_client_env().
- client/installer.iss — .env в %APPDATA%\Tracker\.

### Проверено
- Сертификат перевыпущен: SAN = localhost, 127.0.0.1, 192.168.0.35,
  ws147, tracker, tracker.local.
- С андроид-телефона через VPN: https://192.168.0.35/admin/login
  открывается.
- Установщик собран (34 МБ), ca.pem + .env вшиты.

### Обновлено в KB
- Созданы: 05_SCP\05_NETWORK.md, 05_SCP\06_SERVICES.md.
- Дополнены: 05_SCP\02_CERTIFICATES.md, 06_DEPLOY\06_INSTALLER.md.
- Обновлён: 00_INDEX.md (+2 строки).
