<!-- Часть 794 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ УДАЛИТЬ все партиции при генерации любой миграции.](793_UDALIT_vse_partitsii_pri_generatsii_lyuboy_migratsii.md) | [Оглавление](00_BCE_INDEX.md) | [2. Добавляем include_object=include_object в оба context.configure(...) ▶](795_2_Dobavlyaem_include_object_include_object_v_oba_context_configure.md)

---

# ============================================================
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith("records_") and name != "records":
        return False
    return True'''

content = content.replace(old_marker, new_block, 1)

