<!-- Часть 971 из 1409 -->
# ---------- 1.6. Убираем _wrap_row, он больше не нужен ----------
*Хлебные крошки:* ---------- 1.6. Убираем _wrap_row, он больше не нужен ----------

[◀ ---------- 1.5. Убираем из _load() загрузку server/fingerprint ----------](970_1_5_Ubiraem_iz_load_zagruzku_server_fingerprint.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 2.1. Для ReminderTab ---------- ▶](972_2_1_Dlya_ReminderTab.md)

---

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

