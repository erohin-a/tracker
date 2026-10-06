<!-- Часть 181 из 1409 -->
# ---------------- config.py ----------------
*Хлебные крошки:* ---------------- config.py ----------------

[◀ ---------------- requirements.txt ----------------](180_requirements_txt.md) | [Оглавление](00_BCE_INDEX.md) | [---------------- web_admin.py ---------------- ▶](182_web_admin_py.md)

---

# ---------------- config.py ----------------
$config_py = @'
...
'@
[System.IO.File]::WriteAllText("$serverDir\config.py", $config_py, [System.Text.UTF8Encoding]::new($false))

