<!-- Часть 758 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Заполнено = override для этого сотрудника.](757_Zapolneno_override_dlya_etogo_sotrudnika.md) | [Оглавление](00_BCE_INDEX.md) | [Identifikatory revizii (ispolzuyutsya Alembic dlya otslezhivaniya) ▶](759_Identifikatory_revizii_ispolzuyutsya_Alembic_dlya_otslezhivaniya.md)

---

# ============================================================
class EmployeeSettings(Base):
    __tablename__ = "employee_settings"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True,
                         nullable=False, index=True)

    # --- Напоминание о старте работы ---
    reminder_enabled = Column(Boolean, nullable=True)
    reminder_threshold_minutes = Column(Integer, nullable=True)
    reminder_repeat_minutes = Column(Integer, nullable=True)
    reminder_max_per_day = Column(Integer, nullable=True)

    # --- Конец дня ---
    end_of_day_hour = Column(Integer, nullable=True)
    end_of_day_minute = Column(Integer, nullable=True)

    # Кто и когда последний раз менял настройки
    updated_at = Column(DateTime(timezone=True), default=_utcnow,
                        onupdate=_utcnow)
    updated_by = Column(String(128))
'@
    $content = $content.TrimEnd() + $addition + "`n"
    [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: EmployeeSettings добавлена" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$path', encoding='utf-8').read()); print('SYNTAX OK')"

Write-Host "`n=== Проверка ===" -ForegroundColor Cyan
$check = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
foreach ($m in @('class EmployeeSettings', 'reminder_enabled = Column(Boolean, nullable=True)',
                 'end_of_day_hour = Column(Integer, nullable=True)', 'updated_by = Column')) {
    if ($check.Contains($m)) {
        Write-Host "  OK: $m" -ForegroundColor Green
    } else {
        Write-Host "  ПОТЕРЯНО: $m" -ForegroundColor Red
    }
}
Скрипт P2 — Alembic-миграция
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Генерация миграции ===" -ForegroundColor Cyan
docker compose exec -T api alembic -c /app/server/alembic.ini revision --autogenerate -m "add_employee_settings"

Write-Host "`n=== Что появилось в versions/ ===" -ForegroundColor Cyan
Get-ChildItem D:\tracker\server\alembic\versions\*.py |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 3 |
    Format-Table Name, Length, LastWriteTime
Что ожидаем:
text
INFO  [alembic.autogenerate.compare] Detected added table 'employee_settings'
Generating ... add_employee_settings.py ... done
Важно: в сгенерированной миграции не должно быть операций с records_YYYY_MM (мы это уже проходили в Спринте 1.2). Если увидишь — пришли, я скажу как вырезать.
Проверим содержимое:
powershell
$newFile = Get-ChildItem D:\tracker\server\alembic\versions\*.py |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
Write-Host "Новый файл: $($newFile.Name)"
Write-Host ""
Get-Content $newFile.FullName
Пришли содержимое — я посмотрю, нет ли там чего лишнего.
Скрипт P3 — применить миграцию
После проверки миграции:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

docker compose restart api
Start-Sleep -Seconds 12

Write-Host "`n=== Версия Alembic ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT * FROM alembic_version;"

Write-Host "`n=== Таблица employee_settings ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "\d employee_settings"
Ожидаем:
text
 version_num
--------------
 <новый_rev>           (не 35d67a73f181)

                                     Table "public.employee_settings"
     Column       |           Type           | Collation | Nullable | Default
------------------+--------------------------+-----------+----------+---------
 id               | integer                  |           | not null |
 employee_id      | integer                  |           | not null |
 reminder_enabled | boolean                  |           |          |
 ...
________________________________________
Порядок
P1 — добавить модель
P2 — сгенерировать миграцию, прислать содержимое файла
P3 — применить (только после проверки)
Запускай P1, потом P2. Не применяй миграцию, пока я не посмотрю её содержимое — в прошлый раз автогенерация чуть не удалила партиции.
После того как миграция пройдёт — следующим сообщением:
Патч /api/v1/client-config — эффективные настройки для ПК.
UI: страница /admin/employees/{id}/settings.
Endpoint PUT /api/v1/client-settings.
А потом уже клиентская часть.
Последний в веденный код 21.09.2026 в 17-20
PS D:\tracker> $newFile = Get-ChildItem D:\tracker\server\alembic\versions\*.py |
>>     Sort-Object LastWriteTime -Descending |
>>     Select-Object -First 1
>> Write-Host "Новый файл: $($newFile.Name)"
>> Write-Host ""
>> Get-Content $newFile.FullName
Новый файл: 2602b71902d4_add_employee_settings.py

"""add_employee_settings

Revision ID: 2602b71902d4
Revises: ecb1e3f89300
Create Date: 2026-09-21 16:54:24.696715+03:00

Opisanie migracii вЂ” chto menyaetsya i zachem.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

