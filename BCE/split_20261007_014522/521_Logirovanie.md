<!-- Часть 521 из 1409 -->
# Логирование
*Хлебные крошки:* Логирование

[◀ URL берём из наших настроек, а не из alembic.ini](520_URL_berem_iz_nashih_nastroek_a_ne_iz_alembic_ini.md) | [Оглавление](00_BCE_INDEX.md) | [/app должен быть в sys.path ▶](522_app_dolzhen_byt_v_sys_path.md)

---

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
