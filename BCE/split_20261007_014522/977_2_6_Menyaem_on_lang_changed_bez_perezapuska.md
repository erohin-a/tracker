<!-- Часть 977 из 1409 -->
# ---------- 2.6. Меняем _on_lang_changed — без перезапуска ----------
*Хлебные крошки:* ---------- 2.6. Меняем _on_lang_changed — без перезапуска ----------

[◀ ---------- 2.5. В GeneralTab — добавляем сигнал language_changed и меняем _on_lang_changed ----------](976_2_5_V_GeneralTab_dobavlyaem_signal_language_changed_i_menyaem_on_lang_changed.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 3.1. Убираем inline-стили с панели (QFrame) ---------- ▶](978_3_1_Ubiraem_inline_stili_s_paneli_QFrame.md)

---

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

