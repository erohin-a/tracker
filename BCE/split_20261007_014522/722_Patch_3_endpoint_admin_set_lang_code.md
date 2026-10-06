<!-- Часть 722 из 1409 -->
# --- Патч 3: endpoint /admin/set-lang/{code} ---
*Хлебные крошки:* --- Патч 3: endpoint /admin/set-lang/{code} ---

[◀ ------------------------------------------------------------](721_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](723_part.md)

---

# --- Патч 3: endpoint /admin/set-lang/{code} ---
if ($content -match "/set-lang/") {
    Write-Host "Патч 3: endpoint /set-lang/ уже есть" -ForegroundColor Yellow
    "step3: already patched" | Out-File $log -Append -Encoding utf8
} else {
    # Простой однострочный маркер
    $oldMarker = '# Логин / логаут'
    if ($content.Contains($oldMarker)) {
        # Вставляем НАД маркером — заменяем его на [блок нового кода] + [маркер]
        $setLangBlock = @'
