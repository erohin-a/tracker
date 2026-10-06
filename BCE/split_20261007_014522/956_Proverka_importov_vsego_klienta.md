<!-- Часть 956 из 1409 -->
# Проверка импортов всего клиента
*Хлебные крошки:* Проверка импортов всего клиента

[◀ 2. Патчим функцию main() — применяем язык и тему до/после создания QApplication](955_2_Patchim_funktsiyu_main_primenyaem_yazyk_i_temu_do_posle_sozdaniya_QApplication.md) | [Оглавление](00_BCE_INDEX.md) | [Проверим i18n во всех ключах, которые использует settings_dialog ▶](957_Proverim_i18n_vo_vseh_klyuchah_kotorye_ispolzuet_settings_dialog.md)

---

# Проверка импортов всего клиента
python -c @"
from client import i18n, themes, config
from client.settings_dialog import SettingsDialog, ReminderTab, GeneralTab, RegistrationTab
from client import main as client_main

print('=== Все импорты OK ===')
print()

