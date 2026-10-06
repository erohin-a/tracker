<!-- Часть 957 из 1409 -->
# Проверим i18n во всех ключах, которые использует settings_dialog
*Хлебные крошки:* Проверим i18n во всех ключах, которые использует settings_dialog

[◀ Проверка импортов всего клиента](956_Proverka_importov_vsego_klienta.md) | [Оглавление](00_BCE_INDEX.md) | [Плюс ключи из f-строк ▶](958_Plyus_klyuchi_iz_f_strok.md)

---

# Проверим i18n во всех ключах, которые использует settings_dialog
import re
with open(r'D:\tracker\client\settings_dialog.py', encoding='utf-8') as f:
    src = f.read()

keys = set(re.findall(r't\(["\']([a-z_]+\.[a-z_.0-9]+)["\']', src))
