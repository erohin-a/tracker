# ...docstring...

*Часть 61 из 100. Источник: `BCE.md`.*

[◀ ============================================================](060_part.md) | [Оглавление](00_BCE_INDEX.md) | [1. Добавляем импорты в начало файла (после существующих) ▶](062_1_Dobavlyaem_importy_v_nachalo_fayla_posle_suschestvuyuschih.md)

---

# ...docstring...
import json
import logging
import socket

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (...)

from . import db, http_client, reminder_settings
from .autostart import set_autostart
from .config import (
    BASE_DIR, SERVER_URL,
    get_setting, set_setting,
    get_server_url, get_cert_fingerprint,
    get_language_code, get_theme_code,
)
from .i18n import t, SUPPORTED_LANGS, set_language, get_language
from .registration import get_computer_uid

log = logging.getLogger("tracker.settings_dialog")


class ReminderTab(QWidget):
    # ... логика с i18n и тултипами
Честно говоря, придётся много написать. Постараюсь быть эффективным.
Один момент: пользователь сказал "программа для других неизвестная и необходимо где это возможно и в клиентской части и в админской делать всплывающие окошки что это и для чего". Значит, добавляю tooltip через .setToolTip(t("...hint")) или, что лучше, добавляю helper-функцию hint_label(t_key) которая возвращает QLabel с ? и tooltip.
Хорошо. Пишу.
Также добавлю кнопку «Проверить соединение» — она делает GET на /api/v1/version и показывает результат. Нужно учесть, что URL может быть ещё не сохранён — тогда проверяем по введённому.
Пишу все три части.
Дам все три части в одном сообщении + патч main.py. Постараюсь быть компактным, но не в ущерб функциональности.
Также надо подумать — при смене языка в диалоге ставим в config.json новое значение и предлагаем перезапуск. А при смене темы — применяем сразу через themes.apply_theme (передаём QApplication.instance()).
Для этого settings_dialog получит доступ к app. Проще всего через QApplication.instance().
Пишу.
Насчёт длинны. Пусть будет так:
Скрипт 1: part1 (ReminderTab) — ~130 строк
Скрипт 2: part2 (GeneralTab) — ~200 строк
Скрипт 3: part3 (RegistrationTab + SettingsDialog) — ~250 строк
Скрипт 4: склейка + проверка
Скрипт 5: патч main.py
Начнём.
Также мне надо перепроверить сигнатуру reminder_settings.get_all() и .set_many() — они у нас есть в проекте, использовались в текущем settings_dialog.py. Значит, ок.
Двигаюсь.
Отлично, база для Спринта A готова. Теперь большой блок — переписываем settings_dialog.py целиком.
Почему частями: файл получится ~600 строк. По твоему опыту — большие here-string'и в PowerShell ломаются. Поэтому пишу в 3 .tmp файла, потом склеиваю. Если что-то пойдёт не так — увидим, какая часть поломалась.
________________________________________
Скрипт 1 — Часть 1: заголовок + ReminderTab
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$part1 = @'
# ============================================================
# Окно настроек клиента Tracker
# ============================================================
# Три вкладки:
#   1. Напоминание  — 6 полей + кнопка «Сбросить к общим»
#   2. Общие        — тема, язык, автозапуск, уведомления, адрес сервера
#   3. Регистрация  — UID, hostname, сервер, отпечаток, bootstrap-токен
# ============================================================

import json
import logging
import socket

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget,
)

from . import db, http_client, reminder_settings, themes
from .autostart import set_autostart
from .config import (
    BASE_DIR,
    get_cert_fingerprint,
    get_language_code,
    get_server_url,
    get_setting,
    get_theme_code,
    set_setting,
)
from .i18n import SUPPORTED_LANGS, get_language, set_language, t
from .registration import get_computer_uid

log = logging.getLogger("tracker.settings_dialog")


def _hint(text_key: str) -> QLabel:
    """Возвращает маленькую метку ? с подсказкой из i18n."""
    lbl = QLabel("?")
    lbl.setToolTip(t(text_key))
    lbl.setStyleSheet("color: #8a94a6; margin-left: 3px;")
    lbl.setCursor(Qt.CursorShape.WhatsThisCursor)
    return lbl


def _label_with_hint(text_key: str, hint_key: str) -> QWidget:
    """Строка: текст + ? с тултипом. Для вставки в QFormLayout."""
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(2)
    h.addWidget(QLabel(t(text_key)))
    h.addWidget(_hint(hint_key))
    h.addStretch()
    return w


# ============================================================
# Вкладка 1. Напоминание
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


# ============================================================
# Вкладка 2. Общие
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


# ============================================================
# Вкладка 3. Регистрация
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


# ============================================================
# Сам диалог
# ============================================================
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("settings.title"))
        self.setMinimumSize(660, 640)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        tabs = QTabWidget()
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
        self.setLayout(layout)
'@

[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part3.tmp", $part3, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: часть 3 записана ($($part3.Length) символов)" -ForegroundColor Green
________________________________________
Скрипт 4 — Склейка частей + проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$p1 = [System.IO.File]::ReadAllText("D:\tracker\client\_sd_part1.tmp", [System.Text.UTF8Encoding]::new($false))
$p2 = [System.IO.File]::ReadAllText("D:\tracker\client\_sd_part2.tmp", [System.Text.UTF8Encoding]::new($false))
$p3 = [System.IO.File]::ReadAllText("D:\tracker\client\_sd_part3.tmp", [System.Text.UTF8Encoding]::new($false))

$full = $p1 + $p2 + $p3

# Записываем финальный файл
[System.IO.File]::WriteAllText("D:\tracker\client\settings_dialog.py", $full, [System.Text.UTF8Encoding]::new($false))

# Чистим временные
Remove-Item "D:\tracker\client\_sd_part1.tmp" -ErrorAction SilentlyContinue
Remove-Item "D:\tracker\client\_sd_part2.tmp" -ErrorAction SilentlyContinue
Remove-Item "D:\tracker\client\_sd_part3.tmp" -ErrorAction SilentlyContinue

Write-Host "OK: settings_dialog.py собран ($($full.Length) символов)" -ForegroundColor Green

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'D:\tracker\client\settings_dialog.py', encoding='utf-8').read()); print('SYNTAX OK')"

# Проверяем ключевые классы
$content = [System.IO.File]::ReadAllText("D:\tracker\client\settings_dialog.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("class ReminderTab", "class GeneralTab", "class RegistrationTab", "class SettingsDialog",
                 "get_server_url", "get_cert_fingerprint", "themes.apply_theme", "SUPPORTED_LANGS")) {
    if ($content.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}
Что ожидаем:
text
OK: settings_dialog.py собран (~25000 символов)
SYNTAX OK
 OK: class ReminderTab
 OK: class GeneralTab
 OK: class RegistrationTab
 OK: class SettingsDialog
 OK: get_server_url
 OK: get_cert_fingerprint
 OK: themes.apply_theme
 OK: SUPPORTED_LANGS
________________________________________
Скрипт 5 — Патч main.py (применение темы + языка при старте)
Смотрим на текущий main() в client/main.py. Сейчас там создаётся QApplication и MainWindow. Нужно:
Перед созданием окна — применить сохранённый язык к i18n
После создания QApplication — применить тему через themes.apply_theme
Если в config.json есть флаг restart_required=True — сбросить и логировать
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\client\main.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "themes.apply_theme" in content and "set_language(get_language_code())" in content:
    print("SKIP: main.py уже пропатчен")
    raise SystemExit(0)

