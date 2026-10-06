<!-- Часть 180 из 1409 -->
# ---------------- requirements.txt ----------------
*Хлебные крошки:* ---------------- requirements.txt ----------------

[◀ Убедимся, что папки существуют](179_Ubedimsya_chto_papki_suschestvuyut.md) | [Оглавление](00_BCE_INDEX.md) | [---------------- config.py ---------------- ▶](181_config_py.md)

---

# ---------------- requirements.txt ----------------
$req_txt = @'
fastapi==0.111.0
...
'@
[System.IO.File]::WriteAllText("$serverDir\requirements.txt", $req_txt, [System.Text.UTF8Encoding]::new($false))

