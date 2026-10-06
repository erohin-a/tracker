<!-- Часть 587 из 1409 -->
# 2) Заменяем функцию on_startup
*Хлебные крошки:* 2) Заменяем функцию on_startup

[◀ ------------------------------------------------------------](586_part.md) | [Оглавление](00_BCE_INDEX.md) | [3) Убираем импорт init_db (он больше не нужен) — но оставляем саму функцию в database.py, ▶](588_3_Ubiraem_import_init_db_on_bolshe_ne_nuzhen_no_ostavlyaem_samu_funktsiyu_v_data.md)

---

# 2) Заменяем функцию on_startup
$oldStartup = @'
@app.on_event("startup")
def on_startup():
    init_db()
'@

$newStartup = @'
@app.on_event("startup")
def on_startup():
    """
    При старте приложения:
      1. Запускаем все миграции Alembic (создают/обновляют схему БД).
      2. Миграции идемпотентны — если схема уже актуальна, ничего не делают.

    Почему Alembic, а не Base.metadata.create_all():
      - create_all только создаёт новые таблицы, но не меняет существующие.
      - Alembic умеет изменять колонки, индексы, добавлять/удалять поля.
      - Alembic хранит историю версий схемы, можно откатиться.
    """
    # Путь до alembic.ini — он лежит рядом с этим файлом
    _here = os.path.dirname(os.path.abspath(__file__))
    alembic_ini = os.path.join(_here, "alembic.ini")
    alembic_script = os.path.join(_here, "alembic")

    alembic_cfg = AlembicConfig(alembic_ini)
    alembic_cfg.set_main_option("script_location", alembic_script)

    log.info("Применение миграций Alembic...")
    try:
        alembic_command.upgrade(alembic_cfg, "head")
        log.info("Миграции Alembic успешно применены")
    except Exception as e:
        log.exception("Ошибка применения миграций Alembic")
        # Не поднимаем сервер, если схема не готова — иначе будут 500-е
        raise RuntimeError(f"Не удалось применить миграции: {e}") from e
'@

if ($content.Contains($oldStartup)) {
    $content = $content.Replace($oldStartup, $newStartup)
    Write-Host "OK: on_startup обновлён на запуск Alembic" -ForegroundColor Green
} elseif ($content.Contains($newStartup)) {
    Write-Host "on_startup уже пропатчен" -ForegroundColor Yellow
} else {
    Write-Host "НЕ НАЙДЕН блок on_startup — правьте вручную" -ForegroundColor Red
    Write-Host "Ищите: '@app.on_event(`"startup`")'" -ForegroundColor Yellow
    exit 1
}

