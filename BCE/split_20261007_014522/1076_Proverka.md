<!-- Часть 1076 из 1409 -->
# Проверка
*Хлебные крошки:* Проверка

[◀ Удаляем всё старое между <script> и </script> в конце и вставляем новое](1075_Udalyaem_vse_staroe_mezhdu_script_i_script_v_kontse_i_vstavlyaem_novoe.md) | [Оглавление](00_BCE_INDEX.md) | [Ищем существующий блок с 4 карточками (Сессий/Отработано/Эффективно/Аварийных) ▶](1077_Ischem_suschestvuyuschiy_blok_s_4_kartochkami_Sessiy_Otrabotano_Effektivno_Avari.md)

---

# Проверка
$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
foreach ($m in @('setYesterday', 'setToday', 'setLastNDays')) {
    Write-Host (" {0}: {1}" -f $m, $(if ($check.Contains($m)) { "OK" } else { "MISS" })) -ForegroundColor $(if ($check.Contains($m)) { "Green" } else { "Red" })
}
Скрипт 2 — Патч report_result.html: добавить карточки Перерыв и Простой
Точечно правим секцию с карточками — расширяем «Отработано» до 6 карточек в ряд.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\report_result.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains('Перерыв = span')) {
    Write-Host "SKIP: карточки уже расширены" -ForegroundColor Yellow
    exit 0
}

