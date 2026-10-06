<!-- Часть 976 из 1409 -->
# ---------- 2.5. В GeneralTab — добавляем сигнал language_changed и меняем _on_lang_changed ----------
*Хлебные крошки:* ---------- 2.5. В GeneralTab — добавляем сигнал language_changed и меняем _on_lang_changed ----------

[◀ ---------- 2.4. В SettingsDialog — применить retranslate ко всем вкладкам ----------](975_2_4_V_SettingsDialog_primenit_retranslate_ko_vsem_vkladkam.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 2.6. Меняем _on_lang_changed — без перезапуска ---------- ▶](977_2_6_Menyaem_on_lang_changed_bez_perezapuska.md)

---

# ---------- 2.5. В GeneralTab — добавляем сигнал language_changed и меняем _on_lang_changed ----------
old_imports = "from PyQt6.QtCore import Qt"
new_imports = "from PyQt6.QtCore import Qt, pyqtSignal"
if old_imports in content:
    content = content.replace(old_imports, new_imports, 1)
    print("OK: pyqtSignal импортирован")

old_class_g = '''class GeneralTab(QWidget):
    """Автозапуск, тема, язык, уведомления, адрес сервера."""

    def __init__(self, parent=None):'''

new_class_g = '''class GeneralTab(QWidget):
    """Автозапуск, тема, язык, уведомления."""

    language_changed = pyqtSignal()

    def __init__(self, parent=None):'''

if old_class_g in content:
    content = content.replace(old_class_g, new_class_g, 1)
    print("OK: GeneralTab.language_changed сигнал добавлен")
else:
    print("ERROR: не найден class GeneralTab")
    raise SystemExit(1)


