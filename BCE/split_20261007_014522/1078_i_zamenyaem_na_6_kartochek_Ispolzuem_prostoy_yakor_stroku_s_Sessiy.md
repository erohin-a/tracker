<!-- Часть 1078 из 1409 -->
# и заменяем на 6 карточек. Используем простой якорь — строку с "Сессий"
*Хлебные крошки:* и заменяем на 6 карточек. Используем простой якорь — строку с "Сессий"

[◀ Ищем существующий блок с 4 карточками (Сессий/Отработано/Эффективно/Аварийных)](1077_Ischem_suschestvuyuschiy_blok_s_4_kartochkami_Sessiy_Otrabotano_Effektivno_Avari.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ▶](1079_Proverka.md)

---

# и заменяем на 6 карточек. Используем простой якорь — строку с "Сессий"
$oldCards = @'
<div class="row g-3 mb-4">
 <div class="col-md-3"><div class="card"><div class="card-body">
 <div class="text-muted small">Сессий</div>
 <div class="fs-4">{{ report.totals.sessions }}</div>
 </div></div></div>
 <div class="col-md-3"><div class="card"><div class="card-body">
 <div class="text-muted small">Отработано</div>
 <div class="fs-4">{{ report.totals.worked_duration | dur }}</div>
 </div></div></div>
 <div class="col-md-3"><div class="card"><div class="card-body">
 <div class="text-muted small">Эффективно</div>
 <div class="fs-4 text-success">{{ report.totals.effective_duration | dur }}</div>
 </div></div></div>
 <div class="col-md-3"><div class="card"><div class="card-body">
 <div class="text-muted small">Аварийных</div>
 <div class="fs-4">{{ report.totals.abnormal }}</div>
 </div></div></div>
</div>
'@

$newCards = @'
<div class="row g-3 mb-4">
 <div class="col-md-2"><div class="card"><div class="card-body">
 <div class="text-muted small">Сессий</div>
 <div class="fs-4">{{ report.totals.sessions }}</div>
 </div></div></div>
 <div class="col-md-2"><div class="card"><div class="card-body">
 <div class="text-muted small">
 Отработано
 <span class="hint" data-bs-toggle="tooltip" title="От старта первой до конца последней сессии за день — табель.">?</span>
 </div>
 <div class="fs-4">{{ report.totals.worked_span_duration | dur }}</div>
 </div></div></div>
 <div class="col-md-2"><div class="card"><div class="card-body">
 <div class="text-muted small">
 С трекером
 <span class="hint" data-bs-toggle="tooltip" title="Union интервалов сессий — сумма без пересечений (2 ПК не удваивают).">?</span>
 </div>
 <div class="fs-4 text-primary">{{ report.totals.worked_duration | dur }}</div>
 </div></div></div>
 <div class="col-md-2"><div class="card"><div class="card-body">
 <div class="text-muted small">
 Эффективно
 <span class="hint" data-bs-toggle="tooltip" title="Активные интервалы без простоев больше порога паузы.">?</span>
 </div>
 <div class="fs-4 text-success">{{ report.totals.effective_duration | dur }}</div>
 </div></div></div>
 <div class="col-md-2"><div class="card"><div class="card-body">
 <div class="text-muted small">
 Перерыв
 <span class="hint" data-bs-toggle="tooltip" title="Отработано минус С трекером — время между сессиями (обед, отходы).">?</span>
 </div>
 <div class="fs-4 text-warning">{{ report.totals.break_duration | dur }}</div>
 </div></div></div>
 <div class="col-md-2"><div class="card"><div class="card-body">
 <div class="text-muted small">
 Простой
 <span class="hint" data-bs-toggle="tooltip" title="С трекером минус Эффективно — паузы внутри сессий.">?</span>
 </div>
 <div class="fs-4 text-muted">{{ report.totals.idle_duration | dur }}</div>
 </div></div></div>
</div>
'@

if ($content.Contains($oldCards)) {
    $content = $content.Replace($oldCards, $newCards, 1)
    Write-Host "OK: report_result.html — карточки расширены до 6" -ForegroundColor Green
} else {
    Write-Host "WARN: не найден блок 4 карточек — попробуем запасной паттерн" -ForegroundColor Yellow
    # Запасной вариант — искать по одному заголовку
    if ($content.Contains('<div class="text-muted small">Эффективно</div>')) {
        Write-Host "Нашли блок Эффективно. Патч по частям..." -ForegroundColor Cyan
        # Разширяем class col-md-3 до col-md-2 для всех карточек
        $content = $content.Replace('class="col-md-3"><div class="card"><div class="card-body">
 <div class="text-muted small">Сессий', 'class="col-md-2"><div class="card"><div class="card-body">
 <div class="text-muted small">Сессий')
        Write-Host "Это ручная правка — лучше открой файл и посмотри" -ForegroundColor Yellow
    } else {
        Write-Host "ERROR: не нашли маркеров. Открой файл вручную" -ForegroundColor Red
    }
}

[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))

