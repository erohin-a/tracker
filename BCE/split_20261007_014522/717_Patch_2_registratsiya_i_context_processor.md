<!-- Часть 717 из 1409 -->
# --- Патч 2: регистрация _() и context processor ---
*Хлебные крошки:* --- Патч 2: регистрация _() и context processor ---

[◀ --- Патч 1: импорты ---](716_Patch_1_importy.md) | [Оглавление](00_BCE_INDEX.md) | [------------------------------------------------------------ ▶](718_part.md)

---

# --- Патч 2: регистрация _() и context processor ---
if ($content -match "templates\.context_processors\.append") {
    Write-Host "Патч 2: _() и context processor уже зарегистрированы" -ForegroundColor Yellow
    "step2: already patched" | Out-File $log -Append -Encoding utf8
} else {
    # Используем простые однострочные маркеры (без переносов)
    $oldFilter = 'templates.env.filters["dt"] = _fmt_dt_global'
    if ($content.Contains($oldFilter)) {
        $addition = @'

