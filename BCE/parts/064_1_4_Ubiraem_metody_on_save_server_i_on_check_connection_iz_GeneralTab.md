# ---------- 1.4. Убираем методы _on_save_server и _on_check_connection из GeneralTab ----------

*Часть 64 из 100. Источник: `BCE.md`.*

[◀ Очистим лог — будем смотреть только свежее](063_Ochistim_log_budem_smotret_tolko_svezhee.md) | [Оглавление](00_BCE_INDEX.md) | [Сначала посмотрим текущее содержимое (в каком месте падает) ▶](065_Snachala_posmotrim_tekuschee_soderzhimoe_v_kakom_meste_padaet.md)

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


# ---------- 1.5. Убираем из _load() загрузку server/fingerprint ----------
old_load = '''        # Сервер
        self.ed_server.setText(get_server_url() or "")
        self.ed_fingerprint.setText(get_cert_fingerprint() or "")

        # Уведомления'''

new_load = '''        # Уведомления'''

if old_load in content:
    content = content.replace(old_load, new_load, 1)
    print("OK: _load() больше не читает сервер/отпечаток")
else:
    print("WARN: блок загрузки сервера не найден")


# ---------- 1.6. Убираем _wrap_row, он больше не нужен ----------
old_wrap = '''    def _wrap_row(self, inner_layout):
        w = QWidget()
        w.setLayout(inner_layout)
        return w

'''
if old_wrap in content:
    content = content.replace(old_wrap, "", 1)
    print("OK: _wrap_row убран")
else:
    print("SKIP: _wrap_row уже убран")


with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_sd_cleanup.py", $patcher, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _patch_sd_cleanup.py
Что ожидаем:
text
OK: _hint защищена от пустых переводов
OK: _label_with_hint не добавляет пустые иконки
OK: секция Подключение убрана из Общих
OK: методы _on_save_server / _on_check_connection убраны из GeneralTab
OK: _load() больше не читает сервер/отпечаток
OK: _wrap_row убран
SYNTAX OK
________________________________________
Скрипт 2 — Retranslate: переключение языка без перезапуска
Добавляем метод _retranslate() в каждый класс и вызываем его при смене языка.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\settings_dialog.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "def _retranslate" in content:
    print("SKIP: retranslate уже есть")
    raise SystemExit(0)

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


# ---------- 2.5. В GeneralTab — добавляем сигнал language_changed и меняем _on_lang_changed ----------
old_imports = "from PyQt6.QtCore import Qt"
new_imports = "from PyQt6.QtCore import Qt, pyqtSignal"
if old_imports in content:
    content = content.replace(old_imports, new_imports, 1)
    print("OK: pyqtSignal импортирован")

old_class_g = '''class GeneralTab(QWidget):
    """Автозапуск, тема, язык, уведомления, адрес сервера."""

    def __init__(self, parent=None):'''

new_class_g = '''class GeneralTab(QWidget):
    """Автозапуск, тема, язык, уведомления."""

    language_changed = pyqtSignal()

    def __init__(self, parent=None):'''

if old_class_g in content:
    content = content.replace(old_class_g, new_class_g, 1)
    print("OK: GeneralTab.language_changed сигнал добавлен")
else:
    print("ERROR: не найден class GeneralTab")
    raise SystemExit(1)


# ---------- 2.6. Меняем _on_lang_changed — без перезапуска ----------
old_lang = '''    def _on_lang_changed(self):
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
                app.quit()'''

new_lang = '''    def _on_lang_changed(self):
        code = self.cb_lang.currentData()
        if code == self._initial_lang:
            return
        set_setting("language", code)
        # Меняем глобальный язык i18n — все новые вызовы t() будут на новом языке
        set_language(code)
        # Сообщаем SettingsDialog, что нужно обновить все вкладки
        self.language_changed.emit()
        log.info("Language changed to %s (hot swap)", code)'''

if old_lang in content:
    content = content.replace(old_lang, new_lang, 1)
    print("OK: _on_lang_changed работает без перезапуска")
else:
    print("ERROR: не найден _on_lang_changed")
    raise SystemExit(1)


with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_sd_retranslate.py", $patcher, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _patch_sd_retranslate.py
Что ожидаем:
text
OK: ReminderTab._retranslate добавлен
OK: GeneralTab._retranslate добавлен
OK: RegistrationTab._retranslate добавлен
OK: SettingsDialog._on_language_changed добавлен
OK: pyqtSignal импортирован
OK: GeneralTab.language_changed сигнал добавлен
OK: _on_lang_changed работает без перезапуска
SYNTAX OK
________________________________________
Скрипт 3 — Патч client/main.py (тема + retranslate + inline-стили)
Убираем inline-стили панели, добавляем retranslate для главного окна.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\main.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

# ---------- 3.1. Убираем inline-стили с панели (QFrame) ----------
old_panel = '''        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background: #f8f9fa; border: 1px solid #dee2e6;"
            " border-radius: 6px; padding: 8px; }"
        )'''

new_panel = '''        panel = QFrame()
        panel.setObjectName("infoPanel")'''

if old_panel in content:
    content = content.replace(old_panel, new_panel, 1)
    print("OK: inline-стиль панели убран")
else:
    print("WARN: inline-стиль панели не найден")

# ---------- 3.2. Убираем inline-стили с кнопок старт/стоп (заменим на objectName) ----------
old_start_btn = '''        self.btn_start = QPushButton("? Начать работу")
        self.btn_start.setStyleSheet(
            "background-color:#28a745; color:white; font-weight:bold;"
            "padding:14px; font-size:15px; border:none; border-radius:6px;"
        )'''

new_start_btn = '''        self.btn_start = QPushButton("? Начать работу")
        self.btn_start.setObjectName("btnStart")'''

if old_start_btn in content:
    content = content.replace(old_start_btn, new_start_btn, 1)
    print("OK: inline-стиль кнопки Старт убран")

old_stop_btn = '''        self.btn_stop = QPushButton("? Конец работы")
        self.btn_stop.setStyleSheet(
            "background-color:#dc3545; color:white; font-weight:bold;"
            "padding:14px; font-size:15px; border:none; border-radius:6px;"
        )'''

new_stop_btn = '''        self.btn_stop = QPushButton("? Конец работы")
        self.btn_stop.setObjectName("btnStop")'''

if old_stop_btn in content:
    content = content.replace(old_stop_btn, new_stop_btn, 1)
    print("OK: inline-стиль кнопки Стоп убран")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_main_cleanup.py", $patcher, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _patch_main_cleanup.py
Что ожидаем:
text
OK: inline-стиль панели убран
OK: inline-стиль кнопки Старт убран
OK: inline-стиль кнопки Стоп убран
SYNTAX OK
________________________________________
Скрипт 4 — Дополняем QSS в themes.py
Добавляем стили для #infoPanel, #btnStart, #btnStop, QMainWindow и других.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\themes.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "#infoPanel" in content:
    print("SKIP: QSS уже дополнен")
    raise SystemExit(0)

# Дополняем DARK_QSS перед закрывающими тройными кавычками
addition = '''
/* ---------- Главное окно ---------- */
QMainWindow { background-color: #2b2b2b; }
QMainWindow > QWidget { background-color: #2b2b2b; }

/* ---------- Панель информации в главном окне ---------- */
QFrame#infoPanel {
    background-color: #3a3a3a;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { color: #e0e0e0; background: transparent; }
QFrame#infoPanel QLabel[role="title"] { color: #a0a0a0; }

/* ---------- Кнопки старт/стоп ---------- */
QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:pressed { background-color: #218838; }
QPushButton#btnStart:disabled { background-color: #404040; color: #888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:pressed { background-color: #c82333; }
QPushButton#btnStop:disabled { background-color: #404040; color: #888; }

/* ---------- Светлый QSS-вариант тоже нужен ---------- */
'''

LIGHT_QSS = """
QFrame#infoPanel {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { background: transparent; }

QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:disabled { background-color: #c0c0c0; color: #888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:disabled { background-color: #c0c0c0; color: #888; }
"""

"""

# Найдём конец DARK_QSS
marker = '"""\n\n\ndef apply_theme'
pos = content.find(marker)
if pos < 0:
    print("ERROR: не найден конец DARK_QSS")
    raise SystemExit(1)

new_content = content[:pos] + addition + content[pos:]

# Переписываем apply_theme — теперь есть оба QSS
old_apply = '''def apply_theme(app, code: str) -> bool:
    """
    Применяет тему к приложению.
    code: "light" | "dark" | "system"
    """
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(DARK_QSS)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet("")
        log.info("Applied %s theme", code or "light")
        return True
    else:
        log.warning("Unknown theme: %s, using light", code)
        app.setStyleSheet("")
        return False'''

new_apply = '''def apply_theme(app, code: str) -> bool:
    """
    Применяет тему к приложению.
    code: "light" | "dark" | "system"
    """
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(DARK_QSS)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet(LIGHT_QSS)
        log.info("Applied %s theme", code or "light")
        return True
    else:
        log.warning("Unknown theme: %s, using light", code)
        app.setStyleSheet(LIGHT_QSS)
        return False'''

if old_apply in new_content:
    new_content = new_content.replace(old_apply, new_apply, 1)
    print("OK: apply_theme теперь использует LIGHT_QSS")
else:
    print("WARN: apply_theme не найден — LIGHT_QSS не будет использоваться")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

# Проверка
for m in ["#infoPanel", "#btnStart", "#btnStop", "LIGHT_QSS", "DARK_QSS"]:
    print(f" {'OK' if m in new_content else 'MISS'}: {m}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_themes.py", $patcher, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _patch_themes.py
Что ожидаем:
text
OK: apply_theme теперь использует LIGHT_QSS
SYNTAX OK
 OK: #infoPanel
 OK: #btnStart
 OK: #btnStop
 OK: LIGHT_QSS
 OK: DARK_QSS
________________________________________
Скрипт 5 — Фикс sync.py: cap pause_sec failed: name 'datetime' is not defined
Патчим через Python — найдём место с cap pause_sec и убедимся, что datetime импортирован.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

