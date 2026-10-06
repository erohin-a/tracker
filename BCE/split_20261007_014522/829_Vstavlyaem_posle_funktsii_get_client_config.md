<!-- Часть 829 из 1409 -->
# Вставляем после функции get_client_config
*Хлебные крошки:* Вставляем после функции get_client_config

[◀ Проверки](828_Proverki.md) | [Оглавление](00_BCE_INDEX.md) | [Приём изменений настроек от клиента ▶](830_Priem_izmeneniy_nastroek_ot_klienta.md)

---

# Вставляем после функции get_client_config
marker = "    return eff\n\n"
pos = content.find(marker)
if pos < 0:
    print("ERROR: маркер конца get_client_config не найден")
    raise SystemExit(1)
insert_at = pos + len(marker)

new_endpoint = '''# ============================================================
