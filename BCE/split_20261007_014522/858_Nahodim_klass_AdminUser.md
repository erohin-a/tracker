<!-- Часть 858 из 1409 -->
# Находим класс AdminUser
*Хлебные крошки:* Находим класс AdminUser

[◀ Смотрим, где формируется сессия](857_Smotrim_gde_formiruetsya_sessiya.md) | [Оглавление](00_BCE_INDEX.md) | [Ищем строку language = ... внутри класса ▶](859_Ischem_stroku_language_vnutri_klassa.md)

---

# Находим класс AdminUser
m = re.search(r"(class AdminUser\(Base\):[\s\S]*?)(?=\nclass |\Z)", content)
if not m:
    print("ERROR: class AdminUser не найден")
    raise SystemExit(1)

class_body = m.group(1)

