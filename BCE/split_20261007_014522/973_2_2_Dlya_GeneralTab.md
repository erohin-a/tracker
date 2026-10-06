<!-- Часть 973 из 1409 -->
# ---------- 2.2. Для GeneralTab ----------
*Хлебные крошки:* ---------- 2.2. Для GeneralTab ----------

[◀ ---------- 2.1. Для ReminderTab ----------](972_2_1_Dlya_ReminderTab.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 2.3. Для RegistrationTab ---------- ▶](974_2_3_Dlya_RegistrationTab.md)

---

# ---------- 2.2. Для GeneralTab ----------
old_g = '''        layout.addStretch()
        self.setLayout(layout)

    def _load(self):
        # Автозапуск
        enabled = bool(get_setting("autostart_enabled", False))'''

new_g = '''        layout.addStretch()
        self.setLayout(layout)
        self._collect_translatables()

    def _collect_translatables(self):
        """Собираем ссылки на виджеты и их i18n-ключи."""
        self._tr_groups = []
        gbs = self.findChildren(QGroupBox)
        keys = [
            "general.group.autostart",
            "general.group.appearance",
            "general.group.language",
            "general.group.notifications",
        ]
        for gb, key in zip(gbs, keys):
            self._tr_groups.append((gb, key))

        self._tr_labels = []
        for name, key in [
            ("lbl_general_theme", "general.theme"),
            ("lbl_general_lang", "general.lang"),
        ]:
            lbl = self.findChild(QLabel, name)
            if lbl:
                self._tr_labels.append((lbl, key))

        self._tr_checkboxes = [
            (self.cb_autostart, "general.autostart"),
            (self.cb_notif_offline, "general.notif.offline"),
            (self.cb_notif_eod, "general.notif.eod"),
        ]

    def _retranslate(self):
        for gb, key in getattr(self, "_tr_groups", []):
            gb.setTitle(t(key))
        for lbl, key in getattr(self, "_tr_labels", []):
            lbl.setText(t(key))
        for cb, key in getattr(self, "_tr_checkboxes", []):
            cb.setText(t(key))

        # ComboBox тема — перезаписываем тексты опций
        for i, code in enumerate(("light", "dark", "system")):
            self.cb_theme.setItemText(i, t(f"general.theme.{code}"))

        # ComboBox язык — только переводим заголовок, названия языков не трогаем
        # Тултипы
        self.cb_autostart.setToolTip(t("general.autostart.hint"))
        self.cb_theme.setToolTip(t("general.theme.hint"))
        self.cb_lang.setToolTip(t("general.lang.hint"))
        self.cb_notif_offline.setToolTip(t("general.notif.offline.hint"))
        self.cb_notif_eod.setToolTip(t("general.notif.eod.hint"))

    def _load(self):
        # Автозапуск
        enabled = bool(get_setting("autostart_enabled", False))'''

if old_g in content:
    content = content.replace(old_g, new_g, 1)
    print("OK: GeneralTab._retranslate добавлен")
else:
    print("ERROR: не найден _load в GeneralTab")
    raise SystemExit(1)


