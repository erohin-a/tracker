<!-- Часть 979 из 1409 -->
# ---------- 3.2. Убираем inline-стили с кнопок старт/стоп (заменим на objectName) ----------
*Хлебные крошки:* ---------- 3.2. Убираем inline-стили с кнопок старт/стоп (заменим на objectName) ----------

[◀ ---------- 3.1. Убираем inline-стили с панели (QFrame) ----------](978_3_1_Ubiraem_inline_stili_s_paneli_QFrame.md) | [Оглавление](00_BCE_INDEX.md) | [Дополняем DARK_QSS перед закрывающими тройными кавычками ▶](980_Dopolnyaem_DARK_QSS_pered_zakryvayuschimi_troynymi_kavychkami.md)

---

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

