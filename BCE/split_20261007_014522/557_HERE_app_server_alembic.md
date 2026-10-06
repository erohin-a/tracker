<!-- Часть 557 из 1409 -->
# _HERE = /app/server/alembic
*Хлебные крошки:* _HERE = /app/server/alembic

[◀ ------------------------------------------------------------](556_part.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](558_part.md)

---

# _HERE = /app/server/alembic
_SERVER_DIR = os.path.dirname(_HERE)       # /app/server
_APP_DIR = os.path.dirname(_SERVER_DIR)    # /app
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

