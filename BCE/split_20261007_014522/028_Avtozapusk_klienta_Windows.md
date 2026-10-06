<!-- Часть 28 из 1409 -->
# Автозапуск клиента (Windows)
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 6. Ежедневная работа / Автозапуск клиента (Windows)

[◀ Запуск клиента вручную](027_Zapusk_klienta_vruchnuyu.md) | [Оглавление](00_BCE_INDEX.md) | [Просмотр данных (SQL) ▶](029_Prosmotr_dannyh_SQL.md)

---

### Автозапуск клиента (Windows)

```powershell
$startup = [Environment]::GetFolderPath("Startup")
$bat = "@echo off`r`ncd /d D:\tracker`r`nclient\.venv\Scripts\pythonw.exe -m client.main"
[System.IO.File]::WriteAllText("$startup\Tracker.bat", $bat, [System.Text.UTF8Encoding]::new($false))
```

