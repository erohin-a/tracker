<!-- Часть 940 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Вкладка 1. Напоминание](939_Vkladka_1_Napominanie.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](941_part.md)

---

# ============================================================
class ReminderTab(QWidget):
    """Поля напоминания. Сохранение: сначала локально, потом PUT на сервер."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout()

        self.source_label = QLabel("")
        self.source_label.setStyleSheet("font-size: 12px; color: #555;")
        layout.addWidget(self.source_label)

        # --- Группа 1: Напоминание о старте ---
        grp1 = QGroupBox(t("reminder.group.start"))
        form1 = QFormLayout()

        self.cb_enabled = QCheckBox(t("reminder.enabled"))
        self.cb_enabled.setToolTip(t("reminder.threshold.hint"))
        form1.addRow(self.cb_enabled)

        self.sp_threshold = QSpinBox()
        self.sp_threshold.setRange(1, 480)
        self.sp_threshold.setSuffix(" мин")
        self.sp_threshold.setToolTip(t("reminder.threshold.hint"))
        form1.addRow(
            _label_with_hint("reminder.threshold", "reminder.threshold.hint"),
            self.sp_threshold,
        )

        self.sp_repeat = QSpinBox()
        self.sp_repeat.setRange(1, 480)
        self.sp_repeat.setSuffix(" мин")
        self.sp_repeat.setToolTip(t("reminder.repeat.hint"))
        form1.addRow(
            _label_with_hint("reminder.repeat", "reminder.repeat.hint"),
            self.sp_repeat,
        )

        self.sp_max = QSpinBox()
        self.sp_max.setRange(1, 100)
        self.sp_max.setToolTip(t("reminder.max_per_day.hint"))
        form1.addRow(
            _label_with_hint("reminder.max_per_day", "reminder.max_per_day.hint"),
            self.sp_max,
        )

        grp1.setLayout(form1)
        layout.addWidget(grp1)

        # --- Группа 2: Конец дня ---
        grp2 = QGroupBox(t("reminder.group.eod"))
        form2 = QFormLayout()

        self.sp_eod_hour = QSpinBox()
        self.sp_eod_hour.setRange(0, 23)
        self.sp_eod_hour.setSuffix(" ч")
        self.sp_eod_hour.setToolTip(t("reminder.eod.hint"))
        form2.addRow(
            _label_with_hint("reminder.eod_hour", "reminder.eod.hint"),
            self.sp_eod_hour,
        )

        self.sp_eod_minute = QSpinBox()
        self.sp_eod_minute.setRange(0, 59)
        self.sp_eod_minute.setSuffix(" мин")
        self.sp_eod_minute.setToolTip(t("reminder.eod.hint"))
        form2.addRow(t("reminder.eod_minute"), self.sp_eod_minute)

        hint_zero = QLabel(t("reminder.eod_hour.zero"))
        hint_zero.setStyleSheet("color: #8a94a6; font-size: 11px;")
        form2.addRow("", hint_zero)

        grp2.setLayout(form2)
        layout.addWidget(grp2)

        # --- Кнопки ---
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton(t("btn.save"))
        self.btn_save.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; "
            "border: none; border-radius: 6px; padding: 8px 18px;"
        )
        self.btn_save.clicked.connect(self._on_save)

        self.btn_reset_local = QPushButton(t("reminder.btn.reset_to_global"))
        self.btn_reset_local.setToolTip(t("reminder.btn.reset_to_global.tooltip"))
        self.btn_reset_local.clicked.connect(self._on_reset_to_global)

        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_reset_local)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.status_label)

        layout.addStretch()
        self.setLayout(layout)

    def _load(self):
        cfg = reminder_settings.get_all()
        self.cb_enabled.setChecked(bool(cfg.get("reminder_enabled")))
        self.sp_threshold.setValue(int(cfg.get("reminder_threshold_minutes", 15)))
        self.sp_repeat.setValue(int(cfg.get("reminder_repeat_minutes", 10)))
        self.sp_max.setValue(int(cfg.get("reminder_max_per_day", 5)))
        self.sp_eod_hour.setValue(int(cfg.get("end_of_day_hour", 19)))
        self.sp_eod_minute.setValue(int(cfg.get("end_of_day_minute", 0)))

        src = db.get_meta("reminder.source_reminder") or "global"
        if src == "personal":
            self.source_label.setText(t("reminder.source.personal"))
        else:
            self.source_label.setText(t("reminder.source.global"))

    def _on_save(self):
        payload = {
            "reminder_enabled": self.cb_enabled.isChecked(),
            "reminder_threshold_minutes": self.sp_threshold.value(),
            "reminder_repeat_minutes": self.sp_repeat.value(),
            "reminder_max_per_day": self.sp_max.value(),
            "end_of_day_hour": self.sp_eod_hour.value(),
            "end_of_day_minute": self.sp_eod_minute.value(),
        }

        try:
            reminder_settings.set_many(payload)
        except Exception as e:
            log.exception("local save failed")
            QMessageBox.critical(self, t("btn.cancel"),
                                 f"Local save failed: {e}")
            return

        uid = get_computer_uid() or ""
        if not uid:
            self._set_status(t("reminder.status.local_only"), "#e0a800")
            return

        try:
            resp = http_client.put(
                f"{get_server_url()}/api/v1/client-settings",
                json=payload,
                headers={"X-Computer-Uid": uid},
                timeout=10.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                accepted = {
                    "reminder_enabled": bool(data.get("reminder_enabled", payload["reminder_enabled"])),
                    "reminder_threshold_minutes": int(data.get("reminder_threshold_minutes", payload["reminder_threshold_minutes"])),
                    "reminder_repeat_minutes": int(data.get("reminder_repeat_minutes", payload["reminder_repeat_minutes"])),
                    "reminder_max_per_day": int(data.get("reminder_max_per_day", payload["reminder_max_per_day"])),
                    "end_of_day_hour": int(data.get("end_of_day_hour", payload["end_of_day_hour"])),
                    "end_of_day_minute": int(data.get("end_of_day_minute", payload["end_of_day_minute"])),
                }
                reminder_settings.set_many(accepted)
                self._load()

                src = data.get("source_reminder", "global")
                db.set_meta("reminder.source_reminder", src)
                db.set_meta("reminder.source_end_of_day", data.get("source_end_of_day", "global"))

                self._set_status(t("reminder.status.synced"), "#28a745")
                log.info("settings pushed to server, source=%s", src)
            elif resp.status_code == 400:
                detail = resp.json().get("detail", "PC not linked")
                self._set_status(
                    t("reminder.status.server_refused", detail=detail), "#e0a800")
            elif resp.status_code in (401, 403):
                self._set_status(t("reminder.status.not_authorized"), "#dc3545")
            else:
                self._set_status(
                    t("reminder.status.server_error", code=resp.status_code), "#e0a800")
        except Exception as e:
            log.warning("push to server failed: %s", e)
            self._set_status(
                t("reminder.status.net_error", err=str(e)), "#e0a800")

    def _on_reset_to_global(self):
        reply = QMessageBox.question(
            self,
            t("reminder.reset.confirm_title"),
            t("reminder.reset.confirm_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        uid = get_computer_uid() or ""
        if not uid:
            QMessageBox.warning(self, t("btn.cancel"),
                                t("reminder.reset.not_registered"))
            return

        try:
            resp = http_client.delete(
                f"{get_server_url()}/api/v1/client-settings",
                headers={"X-Computer-Uid": uid},
                timeout=10.0,
            )
            if resp.status_code == 400:
                self._set_status(t("reminder.reset.not_linked"), "#dc3545")
                return
            if resp.status_code in (401, 403):
                self._set_status(t("reminder.reset.unauth"), "#dc3545")
                return
            if resp.status_code != 200:
                self._set_status(
                    t("reminder.reset.server_error", code=resp.status_code), "#dc3545")
                return
        except Exception as e:
            log.warning("delete client-settings failed: %s", e)
            self._set_status(
                t("reminder.status.net_error", err=str(e)), "#dc3545")
            return

        try:
            resp = http_client.get(
                f"{get_server_url()}/api/v1/client-config",
                headers={"X-Computer-Uid": uid},
                timeout=10.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                payload = {
                    "reminder_enabled": bool(data.get("reminder_enabled", True)),
                    "reminder_threshold_minutes": int(data.get("reminder_threshold_minutes", 15)),
                    "reminder_repeat_minutes": int(data.get("reminder_repeat_minutes", 10)),
                    "reminder_max_per_day": int(data.get("reminder_max_per_day", 5)),
                    "end_of_day_hour": int(data.get("end_of_day_hour", 19)),
                    "end_of_day_minute": int(data.get("end_of_day_minute", 0)),
                }
                reminder_settings.set_many(payload)
                db.set_meta("reminder.source_reminder",
                            data.get("source_reminder", "global"))
                db.set_meta("reminder.source_end_of_day",
                            data.get("source_end_of_day", "global"))
                self._load()
                self._set_status(t("reminder.reset.success"), "#28a745")
                log.info("reset to global done")
            else:
                self._set_status(
                    t("reminder.reset.partial", code=resp.status_code), "#e0a800")
        except Exception as e:
            log.warning("reload after reset failed: %s", e)
            self._set_status(
                t("reminder.status.net_error", err=str(e)), "#e0a800")

    def _set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {color};")
'@

[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part1.tmp", $part1, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: часть 1 записана ($($part1.Length) символов)" -ForegroundColor Green
________________________________________
Скрипт 2 — Часть 2: GeneralTab
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$part2 = @'


