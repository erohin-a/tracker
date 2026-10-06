<!-- Часть 946 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Вкладка 3. Регистрация](945_Vkladka_3_Registratsiya.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](947_part.md)

---

# ============================================================
class RegistrationTab(QWidget):
    """Информация о ПК + кнопки сохранения адреса/проверки/перерегистрации."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout()

        # --- Информация о ПК ---
        grp_info = QGroupBox(t("reg.group.info"))
        form_info = QFormLayout()

        self.lbl_uid = QLabel("—")
        self.lbl_uid.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        form_info.addRow(t("reg.uid"), self.lbl_uid)

        self.lbl_host = QLabel("—")
        form_info.addRow(t("reg.hostname"), self.lbl_host)

        grp_info.setLayout(form_info)
        layout.addWidget(grp_info)

        # --- Адрес сервера ---
        grp_srv = QGroupBox(t("reg.group.server"))
        f_srv = QFormLayout()

        self.ed_server = QLineEdit()
        self.ed_server.setPlaceholderText("https://tracker.company.ru")
        self.ed_server.setToolTip(t("reg.server_url.hint"))
        f_srv.addRow(
            _label_with_hint("reg.server_url", "reg.server_url.hint"),
            self.ed_server,
        )

        self.ed_fingerprint = QLineEdit()
        self.ed_fingerprint.setPlaceholderText("64 hex-символа")
        self.ed_fingerprint.setToolTip(t("reg.cert_fingerprint.hint"))
        f_srv.addRow(
            _label_with_hint("reg.cert_fingerprint",
                             "reg.cert_fingerprint.hint"),
            self.ed_fingerprint,
        )

        self.ed_token = QLineEdit()
        self.ed_token.setPlaceholderText("одноразовый токен от администратора")
        self.ed_token.setToolTip(t("reg.bootstrap_token.hint"))
        f_srv.addRow(
            _label_with_hint("reg.bootstrap_token",
                             "reg.bootstrap_token.hint"),
            self.ed_token,
        )

        srv_btns = QHBoxLayout()
        self.btn_save_server = QPushButton(t("reg.btn.save_server"))
        self.btn_save_server.clicked.connect(self._on_save_server)
        self.btn_check = QPushButton(t("reg.btn.check_connection"))
        self.btn_check.clicked.connect(self._on_check_connection)
        srv_btns.addWidget(self.btn_save_server)
        srv_btns.addWidget(self.btn_check)
        srv_btns.addStretch()
        w_btns = QWidget()
        w_btns.setLayout(srv_btns)
        f_srv.addRow("", w_btns)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 12px;")
        f_srv.addRow("", self.status_label)

        grp_srv.setLayout(f_srv)
        layout.addWidget(grp_srv)

        # --- Предупреждение о перерегистрации ---
        warn = QLabel(t("reg.reregister.warn"))
        warn.setWordWrap(True)
        warn.setStyleSheet(
            "color: #856404; background: #fff3cd; "
            "padding: 8px; border-radius: 4px;"
        )
        layout.addWidget(warn)

        self.btn_reregister = QPushButton(t("reg.reregister"))
        self.btn_reregister.setStyleSheet(
            "background-color: #dc3545; color: white; font-weight: bold; "
            "border: none; border-radius: 6px; padding: 10px 18px;"
        )
        self.btn_reregister.clicked.connect(self._on_reregister)
        layout.addWidget(self.btn_reregister)

        layout.addStretch()
        self.setLayout(layout)

    def _load(self):
        self.lbl_uid.setText(get_computer_uid() or "(не зарегистрирован)")
        self.lbl_host.setText(socket.gethostname())
        self.ed_server.setText(get_server_url() or "")
        self.ed_fingerprint.setText(get_cert_fingerprint() or "")

    def _on_save_server(self):
        url = self.ed_server.text().strip()
        fp = self.ed_fingerprint.text().strip().lower()
        token = self.ed_token.text().strip()

        if url and not url.startswith(("http://", "https://")):
            QMessageBox.warning(
                self, t("reg.server_url"),
                "URL должен начинаться с http:// или https://",
            )
            return
        if fp and (len(fp) != 64 or not all(c in "0123456789abcdef" for c in fp)):
            QMessageBox.warning(
                self, t("reg.cert_fingerprint"),
                "Отпечаток должен быть 64 hex-символа (0-9, a-f)",
            )
            return

        set_setting("server_url", url)
        set_setting("cert_fingerprint", fp)
        if token:
            # Сохраняем токен в bootstrap.txt — регистрация подхватит
            try:
                (BASE_DIR / "bootstrap.txt").write_text(
                    token, encoding="utf-8")
                log.info("Bootstrap token saved")
            except Exception as e:
                log.warning("Failed to save bootstrap token: %s", e)

        self._set_status(t("reg.server.saved"), "#28a745")
        log.info("Server URL saved: %s, fingerprint: %s", url, fp or "(none)")

    def _on_check_connection(self):
        url = self.ed_server.text().strip() or get_server_url()
        if not url:
            self._set_status(t("general.conn.no_server"), "#dc3545")
            return

        self._set_status(t("reg.server.checking"), "#6c757d")
        QApplication.processEvents()

        try:
            resp = http_client.get(f"{url}/api/v1/version",
                                   timeout=8.0, headers={})
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    version = data.get("latest_version", "?")
                except Exception:
                    version = "?"
                self._set_status(
                    t("reg.server.ok", version=version), "#28a745")
            else:
                self._set_status(
                    t("reg.server.fail", err=f"HTTP {resp.status_code}"),
                    "#dc3545")
        except Exception as e:
            self._set_status(t("reg.server.fail", err=str(e)), "#dc3545")

    def _on_reregister(self):
        old_uid = get_computer_uid()
        if not old_uid:
            QMessageBox.warning(self, t("btn.cancel"),
                                t("reg.reregister.no_uid"))
            return

        reply = QMessageBox.question(
            self,
            t("reg.reregister.confirm_title"),
            t("reg.reregister.confirm_text", uid=old_uid[:16]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            import keyring
            try:
                keyring.delete_password("tracker", "client_secret")
                log.info("Removed keyring[client_secret]")
            except Exception as e:
                log.warning("keyring.delete client_secret: %s", e)
        except Exception as e:
            log.exception("reregister failed")
            QMessageBox.critical(self, t("btn.cancel"),
                                 t("reg.reregister.error", err=str(e)))
            return

        QMessageBox.information(
            self,
            t("reg.reregister.done_title"),
            t("reg.reregister.done_text"),
        )
        self._load()

    def _set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {color};")


