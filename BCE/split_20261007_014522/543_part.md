<!-- Часть 543 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Настройки логирования Alembic (вывод в консоль)](542_Nastroyki_logirovaniya_Alembic_vyvod_v_konsol.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](544_part.md)

---

# ============================================================
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'@

[System.IO.File]::WriteAllText($alembicIni, $iniContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $alembicIni" -ForegroundColor Green
________________________________________
Скрипт D3 — создаём server/alembic/env.py
Это ключевой файл. Он говорит Alembic: «вот твои модели, вот твоя БД».
powershell
powershell
$ErrorActionPreference = "Stop"
$alembicDir = "D:\tracker\server\alembic"
New-Item -ItemType Directory -Force -Path $alembicDir | Out-Null
New-Item -ItemType Directory -Force -Path "$alembicDir\versions" | Out-Null

$envPy = @'
