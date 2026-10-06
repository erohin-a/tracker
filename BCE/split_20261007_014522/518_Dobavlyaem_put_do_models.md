<!-- Часть 518 из 1409 -->
# Добавляем путь до models
*Хлебные крошки:* Добавляем путь до models

[◀ server/main.py](517_server_main_py.md) | [Оглавление](00_BCE_INDEX.md) | [Импортируем наши модели и настройки ▶](519_Importiruem_nashi_modeli_i_nastroyki.md)

---

# Добавляем путь до models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

