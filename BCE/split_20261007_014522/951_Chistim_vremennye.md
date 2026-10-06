<!-- Часть 951 из 1409 -->
# Чистим временные
*Хлебные крошки:* Чистим временные

[◀ Записываем финальный файл](950_Zapisyvaem_finalnyy_fayl.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](952_Proverka_sintaksisa.md)

---

# Чистим временные
Remove-Item "D:\tracker\client\_sd_part1.tmp" -ErrorAction SilentlyContinue
Remove-Item "D:\tracker\client\_sd_part2.tmp" -ErrorAction SilentlyContinue
Remove-Item "D:\tracker\client\_sd_part3.tmp" -ErrorAction SilentlyContinue

Write-Host "OK: settings_dialog.py собран ($($full.Length) символов)" -ForegroundColor Green

