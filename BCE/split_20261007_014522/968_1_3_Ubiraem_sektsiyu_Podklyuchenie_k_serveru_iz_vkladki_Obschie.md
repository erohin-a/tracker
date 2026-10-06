<!-- Часть 968 из 1409 -->
# ---------- 1.3. Убираем секцию "Подключение к серверу" из вкладки Общие ----------
*Хлебные крошки:* ---------- 1.3. Убираем секцию "Подключение к серверу" из вкладки Общие ----------

[◀ ---------- 1.2. _label_with_hint: не добавляем иконку, если _hint вернул None ----------](967_1_2_label_with_hint_ne_dobavlyaem_ikonku_esli_hint_vernul_None.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 1.4. Убираем методы _on_save_server и _on_check_connection из GeneralTab ---------- ▶](969_1_4_Ubiraem_metody_on_save_server_i_on_check_connection_iz_GeneralTab.md)

---

# ---------- 1.3. Убираем секцию "Подключение к серверу" из вкладки Общие ----------
old_conn_block = '''        # --- Подключение к серверу ---
        grp_conn = QGroupBox(t("general.group.connectivity"))
        f_conn = QFormLayout()

        self.ed_server = QLineEdit()
        self.ed_server.setPlaceholderText("https://tracker.example.com")
        self.ed_server.setToolTip(t("general.server_url.hint"))
        f_conn.addRow(
            _label_with_hint("general.server_url", "general.server_url.hint"),
            self.ed_server,
        )

        self.ed_fingerprint = QLineEdit()
        self.ed_fingerprint.setPlaceholderText("64 hex-символа (опционально)")
        self.ed_fingerprint.setToolTip(t("general.cert_fingerprint.hint"))
        f_conn.addRow(
            _label_with_hint("general.cert_fingerprint",
                             "general.cert_fingerprint.hint"),
            self.ed_fingerprint,
        )

        conn_btns = QHBoxLayout()
        self.btn_save_server = QPushButton(t("general.btn.save_server"))
        self.btn_save_server.clicked.connect(self._on_save_server)
        self.btn_check = QPushButton(t("general.btn.check_connection"))
        self.btn_check.clicked.connect(self._on_check_connection)
        conn_btns.addWidget(self.btn_save_server)
        conn_btns.addWidget(self.btn_check)
        conn_btns.addStretch()
        f_conn.addRow("", self._wrap_row(conn_btns))

        self.conn_status = QLabel("")
        self.conn_status.setWordWrap(True)
        self.conn_status.setStyleSheet("font-size: 12px;")
        f_conn.addRow("", self.conn_status)

        grp_conn.setLayout(f_conn)
        layout.addWidget(grp_conn)

'''

if old_conn_block in content:
    content = content.replace(old_conn_block, "", 1)
    print("OK: секция Подключение убрана из Общих")
else:
    print("WARN: блок Подключение не найден (возможно уже убран)")


