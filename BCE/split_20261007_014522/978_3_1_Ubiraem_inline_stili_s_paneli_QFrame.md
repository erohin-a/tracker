<!-- Часть 978 из 1409 -->
# ---------- 3.1. Убираем inline-стили с панели (QFrame) ----------
*Хлебные крошки:* ---------- 3.1. Убираем inline-стили с панели (QFrame) ----------

[◀ ---------- 2.6. Меняем _on_lang_changed — без перезапуска ----------](977_2_6_Menyaem_on_lang_changed_bez_perezapuska.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 3.2. Убираем inline-стили с кнопок старт/стоп (заменим на objectName) ---------- ▶](979_3_2_Ubiraem_inline_stili_s_knopok_start_stop_zamenim_na_objectName.md)

---

# ---------- 3.1. Убираем inline-стили с панели (QFrame) ----------
old_panel = '''        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background: #f8f9fa; border: 1px solid #dee2e6;"
            " border-radius: 6px; padding: 8px; }"
        )'''

new_panel = '''        panel = QFrame()
        panel.setObjectName("infoPanel")'''

if old_panel in content:
    content = content.replace(old_panel, new_panel, 1)
    print("OK: inline-стиль панели убран")
else:
    print("WARN: inline-стиль панели не найден")

