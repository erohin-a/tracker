<!-- Часть 568 из 1409 -->
# у нас строка подключения формируется из .env.
*Хлебные крошки:* у нас строка подключения формируется из .env.

[◀ Это важнее, чем sqlalchemy.url в alembic.ini, потому что](567_Eto_vazhnee_chem_sqlalchemy_url_v_alembic_ini_potomu_chto.md) | [Оглавление](00_BCE_INDEX.md) | [Настраиваем логирование из alembic.ini ▶](569_Nastraivaem_logirovanie_iz_alembic_ini.md)

---

# у нас строка подключения формируется из .env.
config.set_main_option("sqlalchemy.url", settings.database_url)

