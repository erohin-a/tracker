<!-- Часть 824 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Клиентские настройки напоминания (приём от клиента)](823_Klientskie_nastroyki_napominaniya_priem_ot_klienta.md) | [Оглавление](00_BCE_INDEX.md) | [Находим начало функции get_client_config ▶](825_Nahodim_nachalo_funktsii_get_client_config.md)

---

# ============================================================
from typing import Optional as _Opt

class ClientSettingsIn(BaseModel):
    """Настройки, которые клиент может поменять локально и запушить на сервер."""
    reminder_enabled: _Opt[bool] = None
    reminder_threshold_minutes: _Opt[int] = Field(None, ge=1, le=480)
    reminder_repeat_minutes: _Opt[int] = Field(None, ge=1, le=480)
    reminder_max_per_day: _Opt[int] = Field(None, ge=1, le=100)
    end_of_day_hour: _Opt[int] = Field(None, ge=0, le=23)
    end_of_day_minute: _Opt[int] = Field(None, ge=0, le=59)


class ClientSettingsOut(BaseModel):
    """Эффективные настройки — что клиент получит в ответе."""
    reminder_enabled: bool
    reminder_threshold_minutes: int
    reminder_repeat_minutes: int
    reminder_max_per_day: int
    end_of_day_hour: int
    end_of_day_minute: int
    # Источник: "personal" / "global" — для UI клиента (показать бейдж)
    source_reminder: str = "global"
    source_end_of_day: str = "global"
'@

$schemasPath = "D:\tracker\server\schemas.py"
$content = [System.IO.File]::ReadAllText($schemasPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("class ClientSettingsIn")) {
    Write-Host "SKIP: ClientSettingsIn уже есть" -ForegroundColor Yellow
} else {
    $content = $content.TrimEnd() + $addition + "`n"
    [System.IO.File]::WriteAllText($schemasPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: ClientSettingsIn добавлена" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$schemasPath', encoding='utf-8').read()); print('SYNTAX OK')"
Ожидаем: SYNTAX OK.
________________________________________
Скрипт 3 — главный: патч /api/v1/client-config (мерж персональных)
Здесь логика:
Читаем X-Computer-Uid из headers (опционально).
Если есть — находим Computer, потом employee_id.
Читаем employee_settings для этого employee_id.
Для каждого поля: personal.value if not None else global_default.
Возвращаем эффективные значения + source_reminder / source_end_of_day (какие поля персональные).
Используем Python-патчер — надёжнее, чем Replace со сложными строками.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import sys
import ast
import re

MAIN = r"D:\tracker\server\main.py"

with open(MAIN, "r", encoding="utf-8") as f:
    content = f.read()

if "def _merge_effective_settings" in content:
    print("SKIP: уже пропатчен")
    raise SystemExit(0)

