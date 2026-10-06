<!-- Часть 475 из 1409 -->
# Дефолт — 127.0.0.1, чтобы не упираться в IPv6-резолвинг localhost
*Хлебные крошки:* Дефолт — 127.0.0.1, чтобы не упираться в IPv6-резолвинг localhost

[◀ Чистим лог](474_Chistim_log.md) | [Оглавление](00_BCE_INDEX.md) | [Сколько минут без активности — порог авто-закрытия висящей сессии ▶](476_Skolko_minut_bez_aktivnosti_porog_avto_zakrytiya_visyaschey_sessii.md)

---

# Дефолт — 127.0.0.1, чтобы не упираться в IPv6-резолвинг localhost
SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://127.0.0.1")
SSL_CA_BUNDLE = os.environ.get("TRACKER_CA_BUNDLE", str(BASE_DIR / "ca.pem"))
PINNED_CERT_SHA256 = os.environ.get("TRACKER_PIN", "").strip().lower()

SYNC_INTERVAL = 30
ACTIVE_WINDOW_INTERVAL = 5
IDLE_THRESHOLD = 60
MAX_DB_SIZE_MB = 500
BATCH_SIZE = 200
COLLECT_KEYSTROKE_CHARS = False

