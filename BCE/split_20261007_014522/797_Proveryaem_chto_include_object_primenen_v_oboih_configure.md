<!-- Часть 797 из 1409 -->
# Проверяем, что include_object применён в обоих configure()
*Хлебные крошки:* Проверяем, что include_object применён в обоих configure()

[◀ Используем regex, который сохраняет отступ](796_Ispolzuem_regex_kotoryy_sohranyaet_otstup.md) | [Оглавление](00_BCE_INDEX.md) | [revision identifiers, used by Alembic ▶](798_revision_identifiers_used_by_Alembic.md)

---

# Проверяем, что include_object применён в обоих configure()
count = content.count("include_object=include_object,")
print(f"include_object добавлен в {count} context.configure() (ожидаем 2)")
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
Скрипт 3 — фикс .mako шаблона (чтобы docstring не был в крокозябрах)
Заодно переведём шаблон миграций на английский — не будет проблем с кодировкой на Windows.
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

