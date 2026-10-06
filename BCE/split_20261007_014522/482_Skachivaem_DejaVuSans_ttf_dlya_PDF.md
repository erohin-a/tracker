<!-- Часть 482 из 1409 -->
# --- Скачиваем DejaVuSans.ttf для PDF ---
*Хлебные крошки:* --- Скачиваем DejaVuSans.ttf для PDF ---

[◀ --- requirements.txt: добавить reportlab ---](481_requirements_txt_dobavit_reportlab.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](483_part.md)

---

# --- Скачиваем DejaVuSans.ttf для PDF ---
Write-Host "`n--- Шрифт для PDF ---" -ForegroundColor Cyan
$fontsDir = "$serverDir\fonts"
New-Item -ItemType Directory -Force -Path $fontsDir | Out-Null

$fontFile = "$fontsDir\DejaVuSans.ttf"
if (Test-Path $fontFile) {
    Write-Host "Шрифт уже есть: $fontFile" -ForegroundColor Yellow
} else {
    # Пробуем несколько источников
    $urls = @(
        "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
        "https://cdn.jsdelivr.net/gh/dejavu-fonts/dejavu-fonts@master/ttf/DejaVuSans.ttf"
    )
    $ok = $false
    foreach ($u in $urls) {
        try {
            Write-Host "  Пробуем: $u"
            Invoke-WebRequest -Uri $u -OutFile $fontFile -UseBasicParsing -ErrorAction Stop
            $ok = $true
            Write-Host "  OK  скачали из $u" -ForegroundColor Green
            break
        } catch {
            Write-Host "  не вышло: $_" -ForegroundColor Yellow
        }
    }

    if (-not $ok) {
        Write-Host "  Не удалось скачать DejaVuSans.ttf. Пробуем взять системный Arial…" -ForegroundColor Yellow
        $winFont = "$env:WINDIR\Fonts\arial.ttf"
        if (Test-Path $winFont) {
            Copy-Item $winFont $fontFile -Force
            Write-Host "  OK  скопирован $winFont ? $fontFile" -ForegroundColor Green
        } else {
            Write-Host "  ВНИМАНИЕ: шрифта нет. PDF будет с квадратиками." -ForegroundColor Red
        }
    }

    if (Test-Path $fontFile) {
        $size = (Get-Item $fontFile).Length
        Write-Host "  Размер: $size байт"
    }
}
________________________________________
Скрипт C3 — патч web_admin.py (календарь)
Добавляем функции и роуты календаря в существующий web_admin.py. Ничего не удаляем.
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("@router.get(\"/calendar\"")) {
    Write-Host "Календарь уже добавлен — пропускаем" -ForegroundColor Yellow
} else {
    # Импорт CalendarDay
    if ($content -notmatch "CalendarDay") {
        $content = $content.Replace(
            "    AppSetting, AuditLog, BootstrapToken, Computer, Department,",
            "    AppSetting, AuditLog, BootstrapToken, CalendarDay, Computer, Department,"
        )
    }

    # Добавляем блок календаря перед "Аудит"
    $calendarBlock = @'

