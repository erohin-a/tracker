<!-- Часть 569 из 1409 -->
# Настраиваем логирование из alembic.ini
*Хлебные крошки:* Настраиваем логирование из alembic.ini

[◀ у нас строка подключения формируется из .env.](568_u_nas_stroka_podklyucheniya_formiruetsya_iz_env.md) | [Оглавление](00_BCE_INDEX.md) | [Эталон метаданных — с ним Alembic сравнивает реальную БД ▶](570_Etalon_metadannyh_s_nim_Alembic_sravnivaet_realnuyu_BD.md)

---

# Настраиваем логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

