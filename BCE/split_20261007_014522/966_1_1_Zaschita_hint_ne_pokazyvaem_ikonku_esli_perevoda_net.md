<!-- Часть 966 из 1409 -->
# ---------- 1.1. Защита _hint: не показываем иконку, если перевода нет ----------
*Хлебные крошки:* ---------- 1.1. Защита _hint: не показываем иконку, если перевода нет ----------

[◀ Очистим лог — будем смотреть только свежее](965_Ochistim_log_budem_smotret_tolko_svezhee.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 1.2. _label_with_hint: не добавляем иконку, если _hint вернул None ---------- ▶](967_1_2_label_with_hint_ne_dobavlyaem_ikonku_esli_hint_vernul_None.md)

---

# ---------- 1.1. Защита _hint: не показываем иконку, если перевода нет ----------
old_hint = '''def _hint(text_key: str) -> QLabel:
    """Возвращает маленькую метку ? с подсказкой из i18n."""
    lbl = QLabel("?")
    lbl.setToolTip(t(text_key))
    lbl.setStyleSheet("color: #8a94a6; margin-left: 3px;")
    lbl.setCursor(Qt.CursorShape.WhatsThisCursor)
    return lbl'''

new_hint = '''def _hint(text_key: str):
    """
    Возвращает маленькую метку ? с подсказкой из i18n.
    Если перевода нет — возвращает None (иконка не создаётся).
    """
    text = t(text_key)
    if not text or text == text_key:
        return None
    lbl = QLabel("?")
    lbl.setToolTip(text)
    lbl.setStyleSheet("color: #8a94a6; margin-left: 3px;")
    lbl.setCursor(Qt.CursorShape.WhatsThisCursor)
    return lbl'''

if old_hint in content:
    content = content.replace(old_hint, new_hint, 1)
    print("OK: _hint защищена от пустых переводов")
else:
    print("SKIP: _hint уже пропатчена")


