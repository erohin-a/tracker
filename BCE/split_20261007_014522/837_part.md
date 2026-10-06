<!-- Часть 837 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ users.html — заменить [СЂРµРґ], [pw], [||], [>], [x]](836_users_html_zamenit_S_R_R_pw_x.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](838_part.md)

---

# ============================================================
$path = "D:\tracker\server\templates\users.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

$fixed = $content
$fixed = $fixed.Replace("[СЂРµРґ]", "??")
$fixed = $fixed.Replace("[pw]", "??")
$fixed = $fixed.Replace("[||]", "?")
$fixed = $fixed.Replace("[>]", "?")
$fixed = $fixed.Replace("[x]", "??")
$fixed = $fixed.Replace("[Р»РѕРіРё]", "??")

if ($fixed -ne $content) {
    [System.IO.File]::WriteAllText($path, $fixed, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: users.html — крокозябры заменены на emoji" -ForegroundColor Green
} else {
    Write-Host "users.html — нечего менять" -ForegroundColor Yellow
}

