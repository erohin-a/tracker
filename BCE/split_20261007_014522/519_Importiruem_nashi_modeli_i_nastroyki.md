<!-- Часть 519 из 1409 -->
# Импортируем наши модели и настройки
*Хлебные крошки:* Импортируем наши модели и настройки

[◀ Добавляем путь до models](518_Dobavlyaem_put_do_models.md) | [Оглавление](00_BCE_INDEX.md) | [URL берём из наших настроек, а не из alembic.ini ▶](520_URL_berem_iz_nashih_nastroek_a_ne_iz_alembic_ini.md)

---

# Импортируем наши модели и настройки
from models import Base  # noqa
from config import settings  # noqa

config = context.config

