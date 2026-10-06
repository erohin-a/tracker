<!-- Часть 826 из 1409 -->
# Находим конец функции (следующий @app. или # ===)
*Хлебные крошки:* Находим конец функции (следующий @app. или # ===)

[◀ Находим начало функции get_client_config](825_Nahodim_nachalo_funktsii_get_client_config.md) | [Оглавление](00_BCE_INDEX.md) | [Новая версия функции ▶](827_Novaya_versiya_funktsii.md)

---

# Находим конец функции (следующий @app. или # ===)
end1 = content.find("\n@app.", start + 10)
end2 = content.find("\n# ===", start + 10)
ends = [e for e in (end1, end2) if e > 0]
if not ends:
    print("ERROR: не нашли конец функции")
    raise SystemExit(1)
end = min(ends)

