<!-- Часть 825 из 1409 -->
# Находим начало функции get_client_config
*Хлебные крошки:* Находим начало функции get_client_config

[◀ ============================================================](824_part.md) | [Оглавление](00_BCE_INDEX.md) | [Находим конец функции (следующий @app. или # ===) ▶](826_Nahodim_konets_funktsii_sleduyuschiy_app_ili.md)

---

# Находим начало функции get_client_config
start_marker = '@app.get("/api/v1/client-config")'
start = content.find(start_marker)
if start < 0:
    print("ERROR: декоратор /api/v1/client-config не найден")
    raise SystemExit(1)

