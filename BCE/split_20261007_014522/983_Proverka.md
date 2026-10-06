<!-- Часть 983 из 1409 -->
# Проверка
*Хлебные крошки:* Проверка

[◀ Переписываем apply_theme — теперь есть оба QSS](982_Perepisyvaem_apply_theme_teper_est_oba_QSS.md) | [Оглавление](00_BCE_INDEX.md) | [Сначала посмотрим текущее содержимое (в каком месте падает) ▶](984_Snachala_posmotrim_tekuschee_soderzhimoe_v_kakom_meste_padaet.md)

---

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

