<!-- Часть 943 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Вкладка 2. Общие](942_Vkladka_2_Obschie.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](944_part.md)

---

# ============================================================
class GeneralTab(QWidget):
    """Автозапуск, тема, язык, уведомления, адрес сервера."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initial_lang = get_language_code()
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout()

        # --- Автозапуск ---
        grp_auto = QGroupBox(t("general.group.autostart"))
        g1 = QVBoxLayout()
        self.cb_autostart = QCheckBox(t("general.autostart"))
        self.cb_autostart.setToolTip(t("general.autostart.hint"))
        self.cb_autostart.stateChanged.connect(self._on_autostart_changed)
        g1.addWidget(self.cb_autostart)
        hint = QLabel(t("general.autostart.hint"))
        hint.setStyleSheet("color: #8a94a6; font-size: 11px;")
        hint.setWordWrap(True)
        g1.addWidget(hint)
        grp_auto.setLayout(g1)
        layout.addWidget(grp_auto)

        # --- Внешний вид: тема ---
        grp_view = QGroupBox(t("general.group.appearance"))
        f_view = QFormLayout()

        self.cb_theme = QComboBox()
        for code in ("light", "dark", "system"):
            self.cb_theme.addItem(t(f"general.theme.{code}"), code)
        self.cb_theme.setToolTip(t("general.theme.hint"))
        self.cb_theme.currentIndexChanged.connect(self._on_theme_changed)
        f_view.addRow(
            _label_with_hint("general.theme", "general.theme.hint"),
            self.cb_theme,
        )
        grp_view.setLayout(f_view)
        layout.addWidget(grp_view)

        # --- Язык ---
        grp_lang = QGroupBox(t("general.group.language"))
        f_lang = QFormLayout()
        self.cb_lang = QComboBox()
        for lang in SUPPORTED_LANGS:
            self.cb_lang.addItem(lang["label"], lang["code"])
        self.cb_lang.setToolTip(t("general.lang.hint"))
        self.cb_lang.currentIndexChanged.connect(self._on_lang_changed)
        f_lang.addRow(
            _label_with_hint("general.lang", "general.lang.hint"),
            self.cb_lang,
        )
        grp_lang.setLayout(f_lang)
        layout.addWidget(grp_lang)

        # --- Подключение к серверу ---
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

        # --- Уведомления ---
        grp_notif = QGroupBox(t("general.group.notifications"))
        g3 = QVBoxLayout()

        self.cb_notif_offline = QCheckBox(t("general.notif.offline"))
        self.cb_notif_offline.setToolTip(t("general.notif.offline.hint"))
        self.cb_notif_offline.stateChanged.connect(self._on_notif_changed)
        g3.addWidget(self.cb_notif_offline)

        self.cb_notif_eod = QCheckBox(t("general.notif.eod"))
        self.cb_notif_eod.setToolTip(t("general.notif.eod.hint"))
        self.cb_notif_eod.stateChanged.connect(self._on_notif_changed)
        g3.addWidget(self.cb_notif_eod)

        grp_notif.setLayout(g3)
        layout.addWidget(grp_notif)

        layout.addStretch()
        self.setLayout(layout)

    def _wrap_row(self, inner_layout):
        w = QWidget()
        w.setLayout(inner_layout)
        return w

    def _load(self):
        # Автозапуск
        enabled = bool(get_setting("autostart_enabled", False))
        self.cb_autostart.blockSignals(True)
        self.cb_autostart.setChecked(enabled)
        self.cb_autostart.blockSignals(False)

        # Тема
        theme = get_theme_code()
        idx = self.cb_theme.findData(theme)
        if idx >= 0:
            self.cb_theme.blockSignals(True)
            self.cb_theme.setCurrentIndex(idx)
            self.cb_theme.blockSignals(False)

        # Язык
        lang = get_language_code()
        idx = self.cb_lang.findData(lang)
        if idx >= 0:
            self.cb_lang.blockSignals(True)
            self.cb_lang.setCurrentIndex(idx)
            self.cb_lang.blockSignals(False)

        # Сервер
        self.ed_server.setText(get_server_url() or "")
        self.ed_fingerprint.setText(get_cert_fingerprint() or "")

        # Уведомления
        notif = get_setting("notifications", {}) or {}
        self.cb_notif_offline.blockSignals(True)
        self.cb_notif_offline.setChecked(bool(notif.get("offline", True)))
        self.cb_notif_offline.blockSignals(False)
        self.cb_notif_eod.blockSignals(True)
        self.cb_notif_eod.setChecked(bool(notif.get("eod", True)))
        self.cb_notif_eod.blockSignals(False)

    def _on_autostart_changed(self, state):
        enabled = (state == 2)
        ok = set_autostart(enabled)
        if not ok:
            QMessageBox.warning(self, t("general.group.autostart"),
                                t("general.autostart.error"))
            self.cb_autostart.blockSignals(True)
            self.cb_autostart.setChecked(not enabled)
            self.cb_autostart.blockSignals(False)
            return
        set_setting("autostart_enabled", enabled)

    def _on_theme_changed(self):
        code = self.cb_theme.currentData()
        set_setting("theme", code)
        app = QApplication.instance()
        if app is not None:
            themes.apply_theme(app, code)
        log.info("Theme changed to %s", code)

    def _on_lang_changed(self):
        code = self.cb_lang.currentData()
        if code == self._initial_lang:
            return
        set_setting("language", code)
        # Меняем глобальный язык i18n на будущее (для новых окон), но UI диалога
        # сам не перерисуется — потребуется перезапуск.
        set_language(code)
        lang_label = self.cb_lang.currentText()
        reply = QMessageBox.question(
            self,
            t("general.lang.restart_title"),
            t("general.lang.restart_text", lang=lang_label),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            app = QApplication.instance()
            if app is not None:
                # Помечаем, что нужно перезапустить
                set_setting("restart_required", True)
                app.quit()

    def _on_notif_changed(self):
        notif = get_setting("notifications", {}) or {}
        notif["offline"] = self.cb_notif_offline.isChecked()
        notif["eod"] = self.cb_notif_eod.isChecked()
        set_setting("notifications", notif)

    def _on_save_server(self):
        url = self.ed_server.text().strip()
        fp = self.ed_fingerprint.text().strip().lower()

        if url and not url.startswith(("http://", "https://")):
            QMessageBox.warning(
                self, t("general.server_url"),
                "URL должен начинаться с http:// или https://",
            )
            return
        if fp and (len(fp) != 64 or not all(c in "0123456789abcdef" for c in fp)):
            QMessageBox.warning(
                self, t("general.cert_fingerprint"),
                "Отпечаток должен быть 64 hex-символа (0-9, a-f)",
            )
            return

        set_setting("server_url", url)
        set_setting("cert_fingerprint", fp)
        self.conn_status.setText(t("general.conn.saved"))
        self.conn_status.setStyleSheet("font-size: 12px; color: #28a745;")
        log.info("Server URL saved: %s, fingerprint: %s", url, fp or "(none)")

    def _on_check_connection(self):
        url = self.ed_server.text().strip() or get_server_url()
        if not url:
            self.conn_status.setText(t("general.conn.no_server"))
            self.conn_status.setStyleSheet("font-size: 12px; color: #dc3545;")
            return

        self.conn_status.setText(t("general.conn.checking"))
        self.conn_status.setStyleSheet("font-size: 12px; color: #6c757d;")
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
                self.conn_status.setText(
                    t("general.conn.ok", version=version))
                self.conn_status.setStyleSheet(
                    "font-size: 12px; color: #28a745;")
            else:
                self.conn_status.setText(
                    t("general.conn.fail", err=f"HTTP {resp.status_code}"))
                self.conn_status.setStyleSheet(
                    "font-size: 12px; color: #dc3545;")
        except Exception as e:
            self.conn_status.setText(t("general.conn.fail", err=str(e)))
            self.conn_status.setStyleSheet("font-size: 12px; color: #dc3545;")
'@

[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part2.tmp", $part2, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: часть 2 записана ($($part2.Length) символов)" -ForegroundColor Green
________________________________________
Скрипт 3 — Часть 3: RegistrationTab + SettingsDialog
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$part3 = @'


