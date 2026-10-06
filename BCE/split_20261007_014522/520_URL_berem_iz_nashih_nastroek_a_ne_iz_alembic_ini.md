<!-- Часть 520 из 1409 -->
# URL берём из наших настроек, а не из alembic.ini
*Хлебные крошки:* URL берём из наших настроек, а не из alembic.ini

[◀ Импортируем наши модели и настройки](519_Importiruem_nashi_modeli_i_nastroyki.md) | [Оглавление](00_BCE_INDEX.md) | [Логирование ▶](521_Logirovanie.md)

---

# URL берём из наших настроек, а не из alembic.ini
config.set_main_option("sqlalchemy.url", settings.database_url)

