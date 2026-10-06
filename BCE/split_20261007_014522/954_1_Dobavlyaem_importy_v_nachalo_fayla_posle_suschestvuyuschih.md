<!-- Часть 954 из 1409 -->
# 1. Добавляем импорты в начало файла (после существующих)
*Хлебные крошки:* 1. Добавляем импорты в начало файла (после существующих)

[◀ Проверяем ключевые классы](953_Proveryaem_klyuchevye_klassy.md) | [Оглавление](00_BCE_INDEX.md) | [2. Патчим функцию main() — применяем язык и тему до/после создания QApplication ▶](955_2_Patchim_funktsiyu_main_primenyaem_yazyk_i_temu_do_posle_sozdaniya_QApplication.md)

---

# 1. Добавляем импорты в начало файла (после существующих)
old_imports_marker = "from .updater import UpdateChecker, apply_update"
new_imports = (
    "from .updater import UpdateChecker, apply_update\n"
    "from . import themes\n"
    "from .i18n import set_language\n"
    "from .config import get_language_code, get_theme_code, get_setting, set_setting"
)

if "from . import themes" not in content:
    if old_imports_marker in content:
        content = content.replace(old_imports_marker, new_imports, 1)
        print("OK: добавлены импорты themes/i18n/config")
    else:
        print("ERROR: не найден маркер импортов updater")
        raise SystemExit(1)

