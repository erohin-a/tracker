<!-- Часть 959 из 1409 -->
# check_i18n_keys.py
*Хлебные крошки:* check_i18n_keys.py

[◀ Плюс ключи из f-строк](958_Plyus_klyuchi_iz_f_strok.md) | [Оглавление](00_BCE_INDEX.md) | [t("...") — обычные ▶](960_t_obychnye.md)

---

# check_i18n_keys.py
import sys
sys.path.insert(0, r'D:\tracker')

from client import i18n
import re

with open(r'D:\tracker\client\settings_dialog.py', encoding='utf-8') as f:
    src = f.read()

