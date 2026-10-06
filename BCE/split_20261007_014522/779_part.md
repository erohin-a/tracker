<!-- Часть 779 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ УДАЛИТЬ все партиции при генерации любой миграции.](778_UDALIT_vse_partitsii_pri_generatsii_lyuboy_migratsii.md) | [Оглавление](00_BCE_INDEX.md) | [Add include_object to context.configure in both offline and online ▶](780_Add_include_object_to_context_configure_in_both_offline_and_online.md)

---

# ============================================================
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True'''

content = content.replace(old, new, 1)

