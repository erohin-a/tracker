<!-- Часть 1001 из 1409 -->
# ---------- 1. Добавляем datetime в импорты ----------
*Хлебные крошки:* ---------- 1. Добавляем datetime в импорты ----------

[◀ Проверка ключевых маркеров](1000_Proverka_klyuchevyh_markerov.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 2. Чистим крокозябры в комментарии к connected ---------- ▶](1002_2_Chistim_krokozyabry_v_kommentarii_k_connected.md)

---

# ---------- 1. Добавляем datetime в импорты ----------
if "from datetime import datetime" in content:
    print("SKIP: datetime уже импортирован")
else:
    old = "import json\nimport logging\nimport threading\n"
    new = ("import json\nimport logging\nimport threading\n"
           "from datetime import datetime, timezone\n")
    if old in content:
        content = content.replace(old, new, 1)
        print("OK: datetime/timezone добавлены в импорты")
    else:
        print("ERROR: не найдены импорты в начале sync.py")
        raise SystemExit(1)

