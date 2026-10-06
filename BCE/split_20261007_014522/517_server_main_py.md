<!-- Часть 517 из 1409 -->
# server/main.py
*Хлебные крошки:* server/main.py

[◀ Что	Решение](516_Chto_Reshenie.md) | [Оглавление](00_BCE_INDEX.md) | [Добавляем путь до models ▶](518_Dobavlyaem_put_do_models.md)

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

