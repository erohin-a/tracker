# server/main.py

*Часть 40 из 100. Источник: `BCE.md`.*

[◀ Что	Решение](039_Chto_Reshenie.md) | [Оглавление](00_BCE_INDEX.md) | [чтобы не ломать ничего. ▶](041_chtoby_ne_lomat_nichego.md)

---

# server/main.py
from alembic.config import Config
from alembic import command

@app.on_event("startup")
def on_startup():
    # Запускаем миграции Alembic
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
Alembic должен найти alembic.ini в рабочей директории. У нас рабочая директория контейнера — /app, там же лежит server/. Значит alembic.ini должен быть в /app/ или в /app/server/. Путь укажем в Config("server/alembic.ini") или использовать script_location = server/alembic.
Или — перенести всё в корень: alembic.ini в /app/alembic.ini, папка alembic/ в /app/alembic/. Но это не по структуре server/.
Лучше: server/alembic.ini, server/alembic/. В контейнере это /app/server/alembic.ini и /app/server/alembic/. Пути в alembic.ini для script_location — относительные. Настраиваем на server/alembic.
Хм, надо внимательно с путями.
Проще так:
В alembic.ini указать script_location = server/alembic (относительно /app).
Config("server/alembic.ini") — тоже относительно /app.
В server/main.py при импорте вызывать command.upgrade с этими путями.
Или еще проще — использовать абсолютные пути:
python
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
alembic_cfg = Config(os.path.join(BASE_DIR, "server", "alembic.ini"))
alembic_cfg.set_main_option("script_location", os.path.join(BASE_DIR, "server", "alembic"))
Но в контейнере BASE_DIR будет /app, а файлы — в /app/server/. Это работает.
Хорошо, давайте писать.
Ключевые технические моменты, которые надо продумать:
env.py — должен знать про наши модели и про URL БД.
URL берём из settings.database_url (наши pydantic-настройки).
Модели — из models.Base.metadata.
Импорт from server.models import Base — но в контейнере пакет server, а при локальном запуске (для разработки) — тоже.
Baseline миграция — как её создать?
Можно через alembic revision --autogenerate -m "baseline" — Alembic сам сгенерирует по текущим моделям.
Или написать вручную — если autogenerate не сработает.
Проблема: у нас есть существующие таблицы в БД. Alembic autogenerate сравнит модели с БД. Если БД уже есть (docker volume) и модели совпадают — он скажет «нет изменений» и создаст пустую миграцию. Что тогда?
Решение: снести volume (docker compose down -v), запустить с пустой БД, при первом старте Alembic создаст всё с нуля.
Но у нас пользователь уже тестировал, у него есть данные? Скорее всего нет — мы ему говорили, что это тестовое. Спросим его.
Партиционирование в Alembic. Native partitioning — через op.execute(raw_sql). Autogenerate это не создаёт — пишем вручную.
Миграции и существующие данные. Если у пользователя всё-таки есть данные — нужно:
Сделать pg_dump.
Снести volume.
Alembic накатит схему.
pg_restore --data-only — но с partitioned-таблицей это надо аккуратно.
Проще: если данных нет — снести volume, начать чисто.
Итог:
Пишу ответ со:
Итоговой сводкой решений пользователя.
Планом Спринта 1 (два подэтапа).
Кодом Спринта 1.1 (Alembic + baseline).
Инструкцией по запуску.
Вопросами, которые нужно решить перед стартом (например, есть ли данные, которые жалко).
Пусть это будет аккуратный, готовый к применению код. Комментарии — на русском.
Оценю объём. Alembic-настройка — примерно:
alembic.ini — 20 строк.
alembic/env.py — 60 строк.
alembic/script.py.mako — 40 строк (стандартный шаблон).
Изменения в requirements.txt — 1 строка.
Изменения в main.py — 10 строк.
Изменения в Dockerfile — 3 строки.
Baseline миграция — сгенерируем через autogenerate, но покажу как.
Ок, пишу.
Насчёт "удалить init_db" — надо решить, оставить её как fallback или убрать. Оставить как fallback — плохо, потому что Alembic и create_all могут конфликтовать. Уберём.
Но! Если Alembic не сработает, приложение не поднимется. Это может привести к ситуации, когда «всё сломалось и не запускается». Поэтому — сделаем Alembic с обработкой ошибок: если миграции падают, приложение всё равно стартует, но в логах будет ошибка.
Хм, нет, лучше — не стартует. Пользователь увидит явную ошибку, а не будет работать с полусломанной схемой.
Ок, финальное решение: убрать init_db, Alembic запускается при старте, при ошибке — приложение не стартует, в логах понятная ошибка.
А на случай «я хочу откатиться» — инструкция в конце: как отключить Alembic и вернуться к create_all.
Начинаю писать.
Ещё момент — нужно ли на Спринт 1 добавлять поля в models? Да, потому что baseline должен содержать правильные модели. Но! Мы собирались добавлять новые таблицы (роли, расписания, планировщик...) в Спринте 1.2.
Решение: baseline = текущее состояние моделей. Все новые модели — в Спринте 1.2. Так чище.
То есть: в Спринте 1.1 модели не меняются вообще. Alembic просто фиксирует текущую схему.
Отлично. Пишу.
Финальная проверка по контексту:
Пользователь использует D:\tracker
У него сервер на Docker Compose
Модели в server/models.py
Настройки в server/config.py (класс Settings)
main.py — FastAPI
init_db() вызывается в @app.on_event("startup")
Значит, изменения:
server/requirements.txt — добавить alembic==1.13.2
server/alembic.ini — новый файл
server/alembic/env.py — новый файл
server/alembic/script.py.mako — новый файл
server/alembic/versions/ — пустая папка, куда ляжет baseline
server/main.py — заменить init_db() на запуск Alembic
Через PowerShell-скрипты, как раньше.
Одна тонкость: env.py должен импортировать Base из models. Но models.py в свою очередь импортирует из config.py, который требует переменные из .env. В Docker это работает, потому что .env монтируется через docker-compose. Но Alembic должен это тоже видеть.
Значит, при запуске Alembic через FastAPI — всё в контейнере, всё в порядке.
Ок, пишу ответ.
Формат ответа:
Краткое резюме решений (то, что подтвердил пользователь).
План Спринта 1 с разбивкой.
Скрипт 1.1.a — requirements.txt
Скрипт 1.1.b — alembic.ini
Скрипт 1.1.c — alembic/env.py
Скрипт 1.1.d — alembic/script.py.mako
Скрипт 1.1.e — патч main.py
Скрипт 1.1.f — создание baseline-миграции (через docker)
Инструкция по запуску
Что дальше
Начну.
Насчёт длины ответа — будет длинно. Постараюсь компактно, но с полным описанием.
Комментарии в коде — на русском.
Пишу.
Хм, важный момент — я должен уточнить у пользователя: есть ли у него данные, которые жалко? Потому что если есть — надо сохранить. Если нет — можно снести volume.
И второй момент — проверить, что Docker Compose собирает контейнер из свежего кода (мы это уже делали, всё норм).
И третий — Alembic в контейнере должен иметь доступ к alembic.ini и папке alembic/. Dockerfile у нас копирует server/ целиком:
text
COPY server/ ./server/
Значит, если alembic.ini в server/, и папка alembic/ в server/, они скопируются.
Пути в alembic.ini:
script_location = server/alembic — относительно /app/.
sqlalchemy.url — не нужен в ini, будем брать из settings в env.py.
Но env.py при запуске через command.upgrade(cfg, "head") — работает в контексте текущей рабочей директории. В контейнере рабочая директория — /app (см. WORKDIR /app в Dockerfile).
Тогда Config("server/alembic.ini") — откроется /app/server/alembic.ini. Хорошо.
Но! Config ищет ini относительно cwd, если путь относительный. Или лучше сразу абсолютный:
python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
alembic_cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
alembic_cfg.set_main_option("script_location", os.path.join(BASE_DIR, "alembic"))
Здесь __file__ — /app/server/main.py, BASE_DIR = /app/server. Тогда ini — /app/server/alembic.ini, script — /app/server/alembic/. Правильно.
Ок.
Ещё одно: alembic.ini должен иметь секцию [alembic] с параметрами. Минимальный набор:
ini
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
Правильно.
env.py:
python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Добавляем путь до models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Импортируем наши модели и настройки
from models import Base  # noqa
from config import settings  # noqa

config = context.config

# URL берём из наших настроек, а не из alembic.ini
config.set_main_option("sqlalchemy.url", settings.database_url)

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
Проблема: from models import Base — работает, когда BASE_DIR = /app/server в sys.path. Тогда models импортируется как модуль. Но в main.py мы импортируем .models — как относительный. Может быть конфликт.
Лучше:
python
from server.models import Base
from server.config import settings
Тогда нужно, чтобы /app был в sys.path. Что обычно так и есть, если запускать python -m server.main или через gunicorn server.main:app.
Хм. У нас в Dockerfile:
text
WORKDIR /app
COPY server/ ./server/
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "server.main:app"]
Тогда /app/server/main.py виден как server.main. Значит server — это пакет. И from server.models import Base — правильно.
В env.py (который в /app/server/alembic/env.py):
python
# /app должен быть в sys.path
sys.path.insert(0, "/app")  # или динамически
from server.models import Base
from server.config import settings
Но /app может быть не всегда. Лучше вычислить:
python
import sys, os
SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /app/server
APP_DIR = os.path.dirname(SERVER_DIR)  # /app
sys.path.insert(0, APP_DIR)
from server.models import Base
from server.config import settings
Ок.
script.py.mako — дефолтный.
Baseline миграция — лучше через autogenerate. Но команда должна выполняться внутри контейнера:
bash
docker compose exec api alembic revision --autogenerate -m "baseline"
Но тогда нужна команда alembic в PATH контейнера. Она будет, если package установлен через pip.
Проверим — alembic==1.13.2 в requirements.txt ? pip install ? команда alembic доступна.
Но! При autogenerate Alembic подключается к БД. Если БД пустая — сгенерирует все таблицы. Если уже есть (как у нас от create_all) — скажет «нет изменений».
Хм. Что делать?
Решено: идём по пути чистого старта:
Сбросить volume (docker compose down -v).
Первый старт — Alembic видит пустую БД, при запуске создаёт всё с нуля.
Но baseline надо сгенерировать до сброса — из текущих моделей.
Альтернатива — руками написать baseline. Но это долго.
Ещё вариант — сбросить volume, при старте приложение падает, потому что таблиц нет. Затем прогнать alembic revision --autogenerate — он подтянет модели, а БД пустая ? сгенерирует все CREATE. Затем alembic upgrade head — создаст всё.
Но это не получится автоматически, если Alembic запускается при старте FastAPI. Потому что приложение упадёт при первом старте.
Хм. Порядок:
Вариант 1 — ручной baseline:
Установить Alembic.
Сбросить volume.
Создать приложение с пустыми миграциями (без вызова upgrade).
Запустить контейнер ? FastAPI стартует (init_db убран, но и upgrade не зовётся) ? БД пустая, приложение работает, но не может ничего.
Выполнить docker compose exec api alembic revision --autogenerate -m "baseline" ? создаст миграцию.
Проверить миграцию, поправить если нужно.
В main.py включить command.upgrade(cfg, "head").
docker compose restart api ? Alembic накатит миграцию ? БД создана.
Вариант 2 — предустановленная миграция:
Установить Alembic локально (на хосте) — Python есть, pip install alembic.
Настроить env.py.
alembic revision --autogenerate -m "baseline" — локально, подключившись к БД. Но БД в контейнере — как?
Или локальный Postgres, или проброс порта из контейнера (5432 не проброшен, только 443 для nginx).
Сгенерированную миграцию кладём в проект.
docker compose up -d --build.
Хм. Вариант 1 проще — Alembic работает в контейнере, где БД доступна по имени db.
Ок, идём Вариантом 1.
Но нужно решить ещё один момент: у пользователя в БД тестовые данные. Если сбросить volume — потеряются. Пользователь это знает? Он сказал «мы тестировали», значит понимает.
Спрошу в конце: «Если у тебя там что-то важное — сделай бэкап до сброса».
Или, ещё лучше — сделать оба пути:
Путь А (быстрый, для тестовых данных): сброс volume + Alembic с нуля.
Путь Б (аккуратный, для реальных данных): pg_dump ? сброс ? Alembic ? pg_restore.
Начну с А.
Ок, всё. Пишу ответ.
Хм, ещё момент — при сбросе volume теряется BootstrapToken. То есть если у пользователя есть активные клиенты — им придётся перерегистрироваться.
Предупрежу об этом.
Ещё лучше — не сбрасывать volume, а сделать baseline, который умеет работать с существующей БД:
Alembic с baseline-миграцией на текущую схему.
Первое применение — с флагом «уже существует»: alembic stamp head — это говорит Alembic «схема соответствует этой версии, ничего не делай».
Дальнейшие миграции — обычным upgrade head.
Но чтобы это работало — нужно, чтобы baseline-миграция точно совпадала с текущей схемой БД. То есть нужно сгенерировать её по модели, а потом применить через stamp, а не через upgrade.
Это профессиональный подход, но сложнее.
Учитывая, что у пользователя тестовые данные — проще сбросить.
Финальное решение:
Baseline-миграция на текущую схему (генерируем autogenerate при пустой БД).
Сброс volume (пользователь подтвердит — у него тестовые данные).
Запуск с Alembic — схема создаётся с нуля.
Ок, теперь точно пишу.
Формат ответа будет такой:
________________________________________
ЧАСТЬ A. Резюме решений (кратко)
ЧАСТЬ B. Что делает Спринт 1 и почему важен
ЧАСТЬ C. План Спринта 1 (два подэтапа)
ЧАСТЬ D. Спринт 1.1 — код
Скрипт D1: requirements.txt
Скрипт D2: alembic.ini
Скрипт D3: alembic/env.py
Скрипт D4: alembic/script.py.mako
Скрипт D5: патч main.py
Скрипт D6: сброс volume + первый запуск
Скрипт D7: генерация baseline
Скрипт D8: включение Alembic + перезапуск
ЧАСТЬ E. Проверка
ЧАСТЬ F. Что дальше
________________________________________
Приступаю.
Насчёт длины — давайте не буду пихать все детали. Дам конкретику и понятные скрипты.
Хм. Про script.py.mako — это стандартный файл, я могу его дать коротким.
Пишу.
Разбор ответов и старт Спринта 1
Отлично, теперь картина полная. Все спорные места закрыты. Ниже — фиксация решений и первый шаг кода.
________________________________________
ЧАСТЬ A. Итоговая фиксация решений
Пункт	Решение
Графики работы	Вариант В: отдел ? шаблон ? сотрудник. Плюс галка «включить/выключить», по умолчанию — выключено
Импорт/экспорт сотрудников	+ колонка «График» в шаблоне
Live-страница	Делаем
Роли	Сразу 5: admin, operator, viewer, hr, manager
Планировщик	Делаем, гибкий
Агрегация	Делаем, гибрид (сырые 30–90 дней + агрегаты вечно)
Бэкапы	Делаем, по умолчанию выключено
API-страница	Делаем, как рекомендовал
Rate-limiting	Делаем
Партиционирование	Делаем
Русский везде	Делаем
________________________________________
ЧАСТЬ B. Что делает Спринт 1 и почему важен
Главная проблема сейчас: нет миграций. Каждое изменение модели — ручной ALTER TABLE. Пока мы работаем с тестовыми данными, это терпимо. Но как только начнём добавлять роли, расписания, планировщик, API-ключи, daily_stats — таблиц станет 15+. Ручные ALTER превратятся в хаос.
Alembic решает три задачи:
Версионирование схемы. Каждое изменение БД — файл-миграция. Можно откатить.
Автоматическая накатка. При старте сервера — все миграции применяются сами.
Совместная работа. Если к проекту подключатся другие — им не нужно вручную восстанавливать схему.
Партиционирование records решает задачу роста:
Сегодня: 6400 записей/день на человека.
За год на 50 человек: 120 миллионов записей.
Обычная таблица начнёт тормозить.
Партиционированная — нет.
Важно сделать партиционирование сейчас, пока данных мало. Позже миграция займёт часы.
Структура Спринта 1:
1.1. Alembic: настройка + baseline-миграция. Ничего в моделях не меняем.
1.2. Новые таблицы (роли, расписания, планировщик, API-ключи, daily_stats, soft delete, бэкапы) + партиционирование records.
Начинаем с 1.1.
________________________________________
ЧАСТЬ C. Спринт 1.1 — Alembic
Ключевые решения
Alembic запускается при старте FastAPI через @app.on_event("startup"). Проще, чем отдельный контейнер.
Убираем init_db() (create_all) — иначе Alembic и create_all будут конфликтовать.
Пути: server/alembic.ini, server/alembic/ (env.py + versions). В контейнере /app/server/alembic.ini.
Первая миграция — baseline. Сгенерируем её на пустой БД (сбросим volume), чтобы Alembic сам создал все CREATE TABLE из моделей.
?? Важно перед стартом
Сброс volume (docker compose down -v) удалит:
Все зарегистрированные ПК ? клиентам придётся перерегистрироваться.
Все сессии, записи, bootstrap-токены.
Сотрудников, отделы, настройки.
Если там что-то жалко — сделай дамп БД перед этим:
powershell
cd D:\tracker
docker compose exec -T db pg_dump -U tracker tracker > backup_before_alembic.sql
Данные восстановим, если что. Но пока — будем считать, что у тебя тестовые данные.
________________________________________
Скрипт D1 — обновляем requirements.txt
powershell
powershell
$ErrorActionPreference = "Stop"
$reqPath = "D:\tracker\server\requirements.txt"
$req = [System.IO.File]::ReadAllText($reqPath, [System.Text.UTF8Encoding]::new($false))

# Добавляем alembic, если ещё нет
if ($req -notmatch "alembic") {
    $req = $req.TrimEnd() + "`nalembic==1.13.2`n"
    [System.IO.File]::WriteAllText($reqPath, $req, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: alembic добавлен в requirements.txt" -ForegroundColor Green
} else {
    Write-Host "alembic уже есть" -ForegroundColor Yellow
}
Get-Content $reqPath
________________________________________
Скрипт D2 — создаём server/alembic.ini
powershell
powershell
$ErrorActionPreference = "Stop"
$alembicIni = "D:\tracker\server\alembic.ini"

$iniContent = @'
# ============================================================
# Конфигурация Alembic для проекта «Трекер»
# ============================================================
# Этот файл читается Alembic при запуске миграций.
# Параметр sqlalchemy.url здесь НЕ задаём — он берётся из
# server/config.py (переменная DATABASE_URL), чтобы не дублировать
# строку подключения в двух местах.
# ============================================================

[alembic]
# Папка, где лежат сами миграции и env.py
# Путь относительный от этого файла
script_location = alembic

# Префикс для автогенерируемых имён файлов миграций.
# Например: 001_a1b2c3_baseline.py
file_template = %%(rev)s_%%(slug)s

# Часовой пояс для дат в миграциях
timezone = Europe/Moscow

# Куда складывать миграции
# (относительно script_location)
version_locations = %(here)s/alembic/versions

# sqlalchemy.url намеренно не задан здесь. Он будет установлен
# программно в env.py из server/config.py.

# ============================================================
# Настройки логирования Alembic (вывод в консоль)
# ============================================================
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'@

[System.IO.File]::WriteAllText($alembicIni, $iniContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $alembicIni" -ForegroundColor Green
________________________________________
Скрипт D3 — создаём server/alembic/env.py
Это ключевой файл. Он говорит Alembic: «вот твои модели, вот твоя БД».
powershell
powershell
$ErrorActionPreference = "Stop"
$alembicDir = "D:\tracker\server\alembic"
New-Item -ItemType Directory -Force -Path $alembicDir | Out-Null
New-Item -ItemType Directory -Force -Path "$alembicDir\versions" | Out-Null

$envPy = @'
# ============================================================
# Окружение Alembic для проекта «Трекер»
# ============================================================
# Этот скрипт Alembic выполняет при каждом запуске миграции.
# Его задача — сообщить Alembic:
#   1. Где взять URL базы данных (у нас — из server/config.py)
#   2. Какие модели являются «эталоном» схемы (server/models.py, Base.metadata)
#   3. Как подключаться к БД (online или offline режим)
# ============================================================

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ------------------------------------------------------------
# 1. Добавляем корень проекта в sys.path, чтобы импортировать
#    пакет server (в контейнере это /app, локально — D:\tracker)
# ------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
# _HERE = /app/server/alembic
_SERVER_DIR = os.path.dirname(_HERE)       # /app/server
_APP_DIR = os.path.dirname(_SERVER_DIR)    # /app
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

# ------------------------------------------------------------
# 2. Импортируем наши модели и настройки.
#    Base.metadata содержит описания всех таблиц — Alembic
#    сравнит их с реальной БД и сгенерирует миграцию.
# ------------------------------------------------------------
from server.models import Base  # noqa: E402
from server.config import settings  # noqa: E402

# ------------------------------------------------------------
# 3. Читаем alembic.ini (он лежит рядом — в server/)
# ------------------------------------------------------------
config = context.config

# Устанавливаем URL БД из наших настроек.
# Это важнее, чем sqlalchemy.url в alembic.ini, потому что
# у нас строка подключения формируется из .env.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Настраиваем логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Эталон метаданных — с ним Alembic сравнивает реальную БД
target_metadata = Base.metadata


# ============================================================
# Режим offline (без реального подключения)
# ============================================================
# Используется для генерации SQL-скриптов без применения.
# Например: alembic upgrade head --sql > migrate.sql
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,   # отслеживать изменения типов колонок
    )
    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# Режим online (обычный — подключается к БД и накатывает)
# ============================================================
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # не держим соединения
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            # Для партиционированных таблиц:
            include_schemas=False,
        )

        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------------
# Точка входа: Alembic сам решает, какой режим использовать
# ------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'@

[System.IO.File]::WriteAllText("$alembicDir\env.py", $envPy, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $alembicDir\env.py" -ForegroundColor Green
________________________________________
Скрипт D4 — создаём server/alembic/script.py.mako
Это шаблон, по которому Alembic создаёт новые файлы миграций.
powershell
powershell
$ErrorActionPreference = "Stop"
$mako = "D:\tracker\server\alembic\script.py.mako"

$makoContent = @'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Описание миграции — что меняется и зачем.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Идентификаторы ревизии (используются Alembic для отслеживания)
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Применение миграции — что делаем при обновлении схемы."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Откат миграции — что делаем при возврате к предыдущей версии."""
    ${downgrades if downgrades else "pass"}
'@

[System.IO.File]::WriteAllText($mako, $makoContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $mako" -ForegroundColor Green
________________________________________
Скрипт D5 — патчим server/main.py
Заменяем init_db() на запуск Alembic.
powershell
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

# 1) Добавляем импорты Alembic после существующих импортов
if ($content -notmatch "alembic.config") {
    # Находим строку с "from .web_admin import router"
    $anchor = "from .web_admin import router as admin_web_router"
    $imports = @'
from .web_admin import router as admin_web_router

# ------------------------------------------------------------
# Alembic: запуск миграций при старте приложения
# ------------------------------------------------------------
import os
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
'@
    $content = $content.Replace($anchor, $imports)
    Write-Host "OK: добавлены импорты Alembic" -ForegroundColor Green
}

# 2) Заменяем функцию on_startup
$oldStartup = @'
@app.on_event("startup")
def on_startup():
    init_db()
'@

$newStartup = @'
@app.on_event("startup")
def on_startup():
    """
    При старте приложения:
      1. Запускаем все миграции Alembic (создают/обновляют схему БД).
      2. Миграции идемпотентны — если схема уже актуальна, ничего не делают.

    Почему Alembic, а не Base.metadata.create_all():
      - create_all только создаёт новые таблицы, но не меняет существующие.
      - Alembic умеет изменять колонки, индексы, добавлять/удалять поля.
      - Alembic хранит историю версий схемы, можно откатиться.
    """
    # Путь до alembic.ini — он лежит рядом с этим файлом
    _here = os.path.dirname(os.path.abspath(__file__))
    alembic_ini = os.path.join(_here, "alembic.ini")
    alembic_script = os.path.join(_here, "alembic")

    alembic_cfg = AlembicConfig(alembic_ini)
    alembic_cfg.set_main_option("script_location", alembic_script)

    log.info("Применение миграций Alembic...")
    try:
        alembic_command.upgrade(alembic_cfg, "head")
        log.info("Миграции Alembic успешно применены")
    except Exception as e:
        log.exception("Ошибка применения миграций Alembic")
        # Не поднимаем сервер, если схема не готова — иначе будут 500-е
        raise RuntimeError(f"Не удалось применить миграции: {e}") from e
'@

if ($content.Contains($oldStartup)) {
    $content = $content.Replace($oldStartup, $newStartup)
    Write-Host "OK: on_startup обновлён на запуск Alembic" -ForegroundColor Green
} elseif ($content.Contains($newStartup)) {
    Write-Host "on_startup уже пропатчен" -ForegroundColor Yellow
} else {
    Write-Host "НЕ НАЙДЕН блок on_startup — правьте вручную" -ForegroundColor Red
    Write-Host "Ищите: '@app.on_event(`"startup`")'" -ForegroundColor Yellow
    exit 1
}

# 3) Убираем импорт init_db (он больше не нужен) — но оставляем саму функцию в database.py,
