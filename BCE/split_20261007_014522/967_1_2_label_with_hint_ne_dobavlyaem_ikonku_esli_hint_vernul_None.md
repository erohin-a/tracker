<!-- Часть 967 из 1409 -->
# ---------- 1.2. _label_with_hint: не добавляем иконку, если _hint вернул None ----------
*Хлебные крошки:* ---------- 1.2. _label_with_hint: не добавляем иконку, если _hint вернул None ----------

[◀ ---------- 1.1. Защита _hint: не показываем иконку, если перевода нет ----------](966_1_1_Zaschita_hint_ne_pokazyvaem_ikonku_esli_perevoda_net.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 1.3. Убираем секцию "Подключение к серверу" из вкладки Общие ---------- ▶](968_1_3_Ubiraem_sektsiyu_Podklyuchenie_k_serveru_iz_vkladki_Obschie.md)

---

# ---------- 1.2. _label_with_hint: не добавляем иконку, если _hint вернул None ----------
old_lwh = '''def _label_with_hint(text_key: str, hint_key: str) -> QWidget:
    """Строка: текст + ? с тултипом. Для вставки в QFormLayout."""
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(2)
    h.addWidget(QLabel(t(text_key)))
    h.addWidget(_hint(hint_key))
    h.addStretch()
    return w'''

new_lwh = '''def _label_with_hint(text_key: str, hint_key: str) -> QWidget:
    """Строка: текст + ? (если есть перевод). Для вставки в QFormLayout."""
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(2)
    lbl = QLabel(t(text_key))
    lbl.setObjectName(f"lbl_{text_key.replace('.', '_')}")
    h.addWidget(lbl)
    hint = _hint(hint_key)
    if hint is not None:
        h.addWidget(hint)
    h.addStretch()
    return w'''

if old_lwh in content:
    content = content.replace(old_lwh, new_lwh, 1)
    print("OK: _label_with_hint не добавляет пустые иконки")
else:
    print("SKIP: _label_with_hint уже пропатчена")


