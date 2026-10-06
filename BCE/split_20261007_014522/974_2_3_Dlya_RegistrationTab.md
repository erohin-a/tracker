<!-- Часть 974 из 1409 -->
# ---------- 2.3. Для RegistrationTab ----------
*Хлебные крошки:* ---------- 2.3. Для RegistrationTab ----------

[◀ ---------- 2.2. Для GeneralTab ----------](973_2_2_Dlya_GeneralTab.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 2.4. В SettingsDialog — применить retranslate ко всем вкладкам ---------- ▶](975_2_4_V_SettingsDialog_primenit_retranslate_ko_vsem_vkladkam.md)

---

# ---------- 2.3. Для RegistrationTab ----------
old_r = '''        layout.addStretch()
        self.setLayout(layout)

    def _load(self):
        self.lbl_uid.setText(get_computer_uid() or "(не зарегистрирован)")'''

new_r = '''        layout.addStretch()
        self.setLayout(layout)
        self._collect_translatables()

    def _collect_translatables(self):
        self._tr_groups = []
        gbs = self.findChildren(QGroupBox)
        keys = ["reg.group.info", "reg.group.server"]
        for gb, key in zip(gbs, keys):
            self._tr_groups.append((gb, key))

        self._tr_labels = []
        for name, key in [
            ("lbl_reg_server_url", "reg.server_url"),
            ("lbl_reg_cert_fingerprint", "reg.cert_fingerprint"),
            ("lbl_reg_bootstrap_token", "reg.bootstrap_token"),
        ]:
            lbl = self.findChild(QLabel, name)
            if lbl:
                self._tr_labels.append((lbl, key))

        self._tr_buttons = [
            (self.btn_save_server, "reg.btn.save_server"),
            (self.btn_check, "reg.btn.check_connection"),
            (self.btn_reregister, "reg.reregister"),
        ]

    def _retranslate(self):
        for gb, key in getattr(self, "_tr_groups", []):
            gb.setTitle(t(key))
        for lbl, key in getattr(self, "_tr_labels", []):
            lbl.setText(t(key))
        for btn, key in getattr(self, "_tr_buttons", []):
            btn.setText(t(key))

        # Тултипы
        self.ed_server.setToolTip(t("reg.server_url.hint"))
        self.ed_fingerprint.setToolTip(t("reg.cert_fingerprint.hint"))
        self.ed_token.setToolTip(t("reg.bootstrap_token.hint"))

    def _load(self):
        self.lbl_uid.setText(get_computer_uid() or "(не зарегистрирован)")'''

if old_r in content:
    content = content.replace(old_r, new_r, 1)
    print("OK: RegistrationTab._retranslate добавлен")
else:
    print("ERROR: не найден _load в RegistrationTab")
    raise SystemExit(1)


