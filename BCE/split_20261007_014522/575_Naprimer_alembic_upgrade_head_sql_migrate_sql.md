<!-- Часть 575 из 1409 -->
# Например: alembic upgrade head --sql > migrate.sql
*Хлебные крошки:* Например: alembic upgrade head --sql > migrate.sql

[◀ Используется для генерации SQL-скриптов без применения.](574_Ispolzuetsya_dlya_generatsii_SQL_skriptov_bez_primeneniya.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](576_part.md)

---

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


