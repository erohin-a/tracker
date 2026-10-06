<!-- Часть 975 из 1409 -->
# ---------- 2.4. В SettingsDialog — применить retranslate ко всем вкладкам ----------
*Хлебные крошки:* ---------- 2.4. В SettingsDialog — применить retranslate ко всем вкладкам ----------

[◀ ---------- 2.3. Для RegistrationTab ----------](974_2_3_Dlya_RegistrationTab.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 2.5. В GeneralTab — добавляем сигнал language_changed и меняем _on_lang_changed ---------- ▶](976_2_5_V_GeneralTab_dobavlyaem_signal_language_changed_i_menyaem_on_lang_changed.md)

---

# ---------- 2.4. В SettingsDialog — применить retranslate ко всем вкладкам ----------
old_sd = '''        tabs = QTabWidget()
        tabs.addTab(ReminderTab(), t("settings.tab.reminder"))
        tabs.addTab(GeneralTab(), t("settings.tab.general"))
        tabs.addTab(RegistrationTab(), t("settings.tab.registration"))

        btn_close = QPushButton(t("btn.close"))
        btn_close.setMinimumHeight(36)
        btn_close.clicked.connect(self.accept)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_close)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addLayout(bottom)
        self.setLayout(layout)'''

new_sd = '''        self._tabs = QTabWidget()
        self._tab_reminder = ReminderTab()
        self._tab_general = GeneralTab()
        self._tab_registration = RegistrationTab()
        self._tabs.addTab(self._tab_reminder, t("settings.tab.reminder"))
        self._tabs.addTab(self._tab_general, t("settings.tab.general"))
        self._tabs.addTab(self._tab_registration, t("settings.tab.registration"))

        self._btn_close = QPushButton(t("btn.close"))
        self._btn_close.setMinimumHeight(36)
        self._btn_close.clicked.connect(self.accept)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(self._btn_close)

        layout = QVBoxLayout()
        layout.addWidget(self._tabs)
        layout.addLayout(bottom)
        self.setLayout(layout)

        # Сигнал от GeneralTab — «язык изменился, обнови всех»
        self._tab_general.language_changed.connect(self._on_language_changed)

    def _on_language_changed(self):
        """Вызывается GeneralTab при смене языка — обновляем все вкладки."""
        log.info("SettingsDialog: retranslating all tabs")
        self.setWindowTitle(t("settings.title"))
        self._tabs.setTabText(0, t("settings.tab.reminder"))
        self._tabs.setTabText(1, t("settings.tab.general"))
        self._tabs.setTabText(2, t("settings.tab.registration"))
        self._btn_close.setText(t("btn.close"))
        try:
            self._tab_reminder._retranslate()
        except Exception:
            log.exception("retranslate ReminderTab failed")
        try:
            self._tab_general._retranslate()
        except Exception:
            log.exception("retranslate GeneralTab failed")
        try:
            self._tab_registration._retranslate()
        except Exception:
            log.exception("retranslate RegistrationTab failed")'''

if old_sd in content:
    content = content.replace(old_sd, new_sd, 1)
    print("OK: SettingsDialog._on_language_changed добавлен")
else:
    print("ERROR: не найден конструктор SettingsDialog")
    raise SystemExit(1)


