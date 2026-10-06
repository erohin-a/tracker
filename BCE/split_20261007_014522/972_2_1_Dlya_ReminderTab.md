<!-- Часть 972 из 1409 -->
# ---------- 2.1. Для ReminderTab ----------
*Хлебные крошки:* ---------- 2.1. Для ReminderTab ----------

[◀ ---------- 1.6. Убираем _wrap_row, он больше не нужен ----------](971_1_6_Ubiraem_wrap_row_on_bolshe_ne_nuzhen.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 2.2. Для GeneralTab ---------- ▶](973_2_2_Dlya_GeneralTab.md)

---

# ---------- 2.1. Для ReminderTab ----------
old = '''        layout.addStretch()
        self.setLayout(layout)

    def _load(self):
        cfg = reminder_settings.get_all()'''

new = '''        layout.addStretch()
        self.setLayout(layout)
        self._collect_translatables()

    def _collect_translatables(self):
        """Собираем ссылки на виджеты и их i18n-ключи для retranslate."""
        self._tr_items = []
        # GroupBox — заголовки
        for gb, key in [
            (self.findChild(QGroupBox, ""), None),  # placeholder
        ]:
            pass
        # Проще: явно перечислим
        self._tr_groups = []
        self._tr_labels = []

        # GroupBox-и: их два
        gbs = self.findChildren(QGroupBox)
        if len(gbs) >= 2:
            self._tr_groups = [
                (gbs[0], "reminder.group.start"),
                (gbs[1], "reminder.group.eod"),
            ]

        # Найдём метки через findChildren — уже с objectName
        for name, key in [
            ("lbl_reminder_threshold", "reminder.threshold"),
            ("lbl_reminder_repeat", "reminder.repeat"),
            ("lbl_reminder_max_per_day", "reminder.max_per_day"),
            ("lbl_reminder_eod_hour", "reminder.eod_hour"),
        ]:
            lbl = self.findChild(QLabel, name)
            if lbl:
                self._tr_labels.append((lbl, key))

        # Кнопки
        self._tr_buttons = [
            (self.btn_save, "btn.save"),
            (self.btn_reset_local, "reminder.btn.reset_to_global"),
        ]
        # Чекбокс
        self._tr_checkboxes = [
            (self.cb_enabled, "reminder.enabled"),
        ]

    def _retranslate(self):
        """Обновляет все тексты вкладки на текущий язык i18n."""
        for gb, key in getattr(self, "_tr_groups", []):
            gb.setTitle(t(key))
        for lbl, key in getattr(self, "_tr_labels", []):
            lbl.setText(t(key))
        for btn, key in getattr(self, "_tr_buttons", []):
            btn.setText(t(key))
        for cb, key in getattr(self, "_tr_checkboxes", []):
            cb.setText(t(key))
        # Тултипы — перечитываем по objectName
        for name, key in [
            ("reminder.threshold.hint", "reminder.threshold.hint"),
        ]:
            pass
        # Обновляем подсказки у ключевых полей
        self.sp_threshold.setToolTip(t("reminder.threshold.hint"))
        self.sp_repeat.setToolTip(t("reminder.repeat.hint"))
        self.sp_max.setToolTip(t("reminder.max_per_day.hint"))
        self.sp_eod_hour.setToolTip(t("reminder.eod.hint"))
        self.sp_eod_minute.setToolTip(t("reminder.eod.hint"))
        # Источник
        src = db.get_meta("reminder.source_reminder") or "global"
        if src == "personal":
            self.source_label.setText(t("reminder.source.personal"))
        else:
            self.source_label.setText(t("reminder.source.global"))

    def _load(self):
        cfg = reminder_settings.get_all()'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: ReminderTab._retranslate добавлен")
else:
    print("ERROR: не найден _load в ReminderTab")
    raise SystemExit(1)


