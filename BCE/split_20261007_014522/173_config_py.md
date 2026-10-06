<!-- Часть 173 из 1409 -->
# --- config.py ---
*Хлебные крошки:* --- config.py ---

[◀ --- записи ---](172_zapisi.md) | [Оглавление](00_BCE_INDEX.md) | [... and so on ▶](174_and_so_on.md)

---

# --- config.py ---
$config_py = @'
...content...
'@

[System.IO.File]::WriteAllText("D:\tracker\server\config.py", $config_py, [System.Text.UTF8Encoding]::new($false))

