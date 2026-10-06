<!-- Часть 969 из 1409 -->
# ---------- 1.4. Убираем методы _on_save_server и _on_check_connection из GeneralTab ----------
*Хлебные крошки:* ---------- 1.4. Убираем методы _on_save_server и _on_check_connection из GeneralTab ----------

[◀ ---------- 1.3. Убираем секцию "Подключение к серверу" из вкладки Общие ----------](968_1_3_Ubiraem_sektsiyu_Podklyuchenie_k_serveru_iz_vkladki_Obschie.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 1.5. Убираем из _load() загрузку server/fingerprint ---------- ▶](970_1_5_Ubiraem_iz_load_zagruzku_server_fingerprint.md)

---

# ---------- 1.4. Убираем методы _on_save_server и _on_check_connection из GeneralTab ----------
old_methods = '''    def _on_save_server(self):
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
            self.conn_status.setStyleSheet("font-size: 12px; color: #dc3545;")'''

if old_methods in content:
    content = content.replace(old_methods, "", 1)
    print("OK: методы _on_save_server / _on_check_connection убраны из GeneralTab")
else:
    print("WARN: методы не найдены (возможно уже убраны)")


