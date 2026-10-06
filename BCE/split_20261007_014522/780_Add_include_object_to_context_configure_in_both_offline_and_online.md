<!-- Часть 780 из 1409 -->
# Add include_object to context.configure in both offline and online
*Хлебные крошки:* Add include_object to context.configure in both offline and online

[◀ ============================================================](779_part.md) | [Оглавление](00_BCE_INDEX.md) | [Find "compare_type=True," and add include_object after ▶](781_Find_compare_type_True_and_add_include_object_after.md)

---

# Add include_object to context.configure in both offline and online
content = content.replace(
    "    context.configure(\n            url=url,\n            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True, # отслеживать изменения типов колонок\n        )",
    "    context.configure(\n            url=url,\n            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True,\n            include_object=include_object,\n        )"
)
Hmm, hardcoding the exact text to replace is fragile. Let me use a more robust approach — find compare_type=True in env.py and add include_object=include_object after it (only once per occurrence).
Actually, looking at my previous env.py:
python
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # отслеживать изменения типов колонок
    )
    ...

def run_migrations_online() -> None:
    connectable = engine_from_config(...)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=False,
        )
Both have compare_type=True,. So I can find all occurrences and add include_object=include_object, after each.
python
import re

