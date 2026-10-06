<!-- Часть 479 из 1409 -->
# Добавляем CalendarDay в models.py
*Хлебные крошки:* Добавляем CalendarDay в models.py

[◀ Чистим лог, чтобы видеть только свежее](478_Chistim_log_chtoby_videt_tolko_svezhee.md) | [Оглавление](00_BCE_INDEX.md) | [Миграция БД ▶](480_Migratsiya_BD.md)

---

# Добавляем CalendarDay в models.py
$content = [System.IO.File]::ReadAllText($modelsPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("class CalendarDay")) {
    Write-Host "Модель CalendarDay уже есть" -ForegroundColor Yellow
} else {
    $addition = @'


class CalendarDay(Base):
    """Календарь рабочих/нерабочих дней.

    По умолчанию (если записи нет): Пн-Пт — рабочие, Сб-Вс — нерабочие.
    Если запись есть — используется её значение is_working.
    """
    __tablename__ = "calendar_days"

    day = Column(String(10), primary_key=True)   # ISO YYYY-MM-DD
    is_working = Column(Boolean, nullable=False, default=True)
    note = Column(String(255))
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
'@
    $content = $content + $addition
    [System.IO.File]::WriteAllText($modelsPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  CalendarDay добавлен в models.py" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$modelsPath', encoding='utf-8').read()); print('  SYNTAX OK')"

