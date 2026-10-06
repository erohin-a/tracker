<!-- Часть 817 из 1409 -->
# Проверяем, что include_object применён в обоих configure()
*Хлебные крошки:* Проверяем, что include_object применён в обоих configure()

[◀ Используем regex, который найдёт строку "compare_type=True," и добавит после неё](816_Ispolzuem_regex_kotoryy_naydet_stroku_compare_type_True_i_dobavit_posle_nee.md) | [Оглавление](00_BCE_INDEX.md) | [revision identifiers, used by Alembic ▶](818_revision_identifiers_used_by_Alembic.md)

---

# Проверяем, что include_object применён в обоих configure()
count = content.count("include_object=include_object,")
print(f"include_object добавлен в {count} context.configure() (ожидаем 2)")

if count != 2:
    print("ПРЕДУПРЕЖДЕНИЕ: ожидалось 2, получено " + str(count))
    print("Проверьте env.py вручную")
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_env.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _fix_env.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_env.py
Что ожидаем:
text
OK: env.py пропатчен
SYNTAX OK
include_object добавлен в 2 context.configure() (ожидаем 2)
________________________________________
Скрипт 3 — фикс .mako шаблона (английский, без крокозябр)
В твоём файле 2602b71902d4 в docstring была каша: Opisanie migracii вЂ” chto menyaetsya.... Это потому что шаблон .mako содержит кириллицу, которая при генерации на Windows портится. Меняем на английский — не будет проблем с кодировкой.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$makoContent = @'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Description of this migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

