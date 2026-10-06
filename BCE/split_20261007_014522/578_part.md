<!-- Часть 578 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Режим online (обычный — подключается к БД и накатывает)](577_Rezhim_online_obychnyy_podklyuchaetsya_k_BD_i_nakatyvaet.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](579_part.md)

---

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


