<!-- Часть 1075 из 1409 -->
# Удаляем всё старое между <script> и </script> в конце и вставляем новое
*Хлебные крошки:* Удаляем всё старое между <script> и </script> в конце и вставляем новое

[◀ 4. Итого внизу](1074_4_Itogo_vnizu.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ▶](1076_Proverka.md)

---

# Удаляем всё старое между <script> и </script> в конце и вставляем новое
$oldStart = $content.IndexOf('<script>')
$oldEnd = $content.IndexOf('</script>', $oldStart)
if ($oldStart -lt 0 -or $oldEnd -lt 0) {
    Write-Host "ERROR: не найден блок <script>" -ForegroundColor Red
    exit 1
}

$newScript = @'
<script>
function fmt(d) {
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart(2, '0');
    var dd = String(d.getDate()).padStart(2, '0');
    return y + '-' + m + '-' + dd;
}

// Установить оба поля
function setRange(fromDate, toDate) {
    document.getElementById('date_from').value = fmt(fromDate);
    document.getElementById('date_to').value = fmt(toDate);
}

// Сегодня: только сегодня
function setToday() {
    var now = new Date();
    setRange(now, now);
}

// Вчера: только вчера
function setYesterday() {
    var d = new Date();
    d.setDate(d.getDate() - 1);
    setRange(d, d);
}

// Последние N дней, включая сегодня
function setLastNDays(n) {
    var to = new Date();
    var from = new Date();
    from.setDate(from.getDate() - (n - 1));
    setRange(from, to);
}

function setThisMonth() {
    var now = new Date();
    var from = new Date(now.getFullYear(), now.getMonth(), 1);
    var to = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    setRange(from, to);
}

function setLastMonth() {
    var now = new Date();
    var from = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    var to = new Date(now.getFullYear(), now.getMonth(), 0);
    setRange(from, to);
}

function setThisYear() {
    var now = new Date();
    setRange(new Date(now.getFullYear(), 0, 1),
             new Date(now.getFullYear(), 11, 31));
}

// ---- Привязка кнопок к новым функциям ----
document.addEventListener('DOMContentLoaded', function () {
    // Ищем по тексту кнопки — надёжно, если порядок изменится
    document.querySelectorAll('button.btn-sm').forEach(function (btn) {
        var txt = (btn.textContent || '').trim();
        if (txt === 'Сегодня') btn.onclick = setToday;
        else if (txt === 'Вчера') btn.onclick = setYesterday;
        else if (txt === '7 дней') btn.onclick = function () { setLastNDays(7); };
        else if (txt === '30 дней') btn.onclick = function () { setLastNDays(30); };
        else if (txt === 'Этот месяц') btn.onclick = setThisMonth;
        else if (txt === 'Прошлый месяц') btn.onclick = setLastMonth;
        else if (txt === 'Этот год') btn.onclick = setThisYear;
    });
});
</script>
'@

$content = $content.Substring(0, $oldStart) + $newScript + $content.Substring($oldEnd + '</script>'.Length)

[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: reports.html — кнопки периодов переписаны" -ForegroundColor Green

