<!-- Часть 1177 из 1409 -->
# 2. Пробуем распарсить
*Хлебные крошки:* 2. Пробуем распарсить

[◀ 1. Показываем строки 250-285 (где ошибка)](1176_1_Pokazyvaem_stroki_250_285_gde_oshibka.md) | [Оглавление](00_BCE_INDEX.md) | [Ищем строку с хвостом ), WorkSession ▶](1178_Ischem_stroku_s_hvostom_WorkSession.md)

---

# 2. Пробуем распарсить
content = "\n".join(lines)
try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: line={e.lineno}, msg={e.msg}")
    print(f"Текст: {e.text}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_diag_tasks.py", $diag, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _diag_tasks.py
Что ожидаем увидеть
Скрипт покажет:
Строки 250–285 — там, где сейчас ошибка.
Все места, где есть from .models import — их может быть несколько.
Точное сообщение об ошибке с указанием строки.
Пришли мне вывод целиком. По нему я:
Пойму, где именно кривой отступ.
Дам точный патч, который заменит проблемный блок на корректный.
Проверю, что все нужные модели (WorkSession, AuditLog) импортированы.
Если у тебя теперь есть VS Code — можешь просто открыть D:\tracker\server\tasks.py, перейти на строку 265 (Ctrl+G ? 265) и прислать мне скриншот 10 строк до и 10 строк после. Это тоже сработает.
Now I can see the exact problem. Line 265 has ), WorkSession — the trailing , WorkSession is the leftover from my bad patch. The import block is already correct (lines 260-264 have all 4 models). The problem is just the extra , WorkSession at line 265.
Let me give a precise fix: replace ), WorkSession with ).
Let me write a Python patcher that fixes this.
Actually the cleanest way: read the file, replace the exact string ), WorkSession\n with )\n. Then check syntax.
Let me also verify the rest of the file looks fine — no other issues visible. The task itself references WorkSession, AuditLog, _Record, _AppSetting — all now imported.
Let me write a simple PowerShell script.
Всё видно: на строке 265 остался «хвост» от моего неудачного патча — ), WorkSession. Импорт на строках 260–264 уже правильный, надо просто убрать этот хвост.
Скрипт — точный фикс строки 265
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
from pathlib import Path

PATH = Path(r"D:\tracker\server\tasks.py")
lines = PATH.read_text(encoding="utf-8").splitlines()

