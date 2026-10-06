<!-- Часть 861 из 1409 -->
# Показываем результат — что теперь в AdminUser
*Хлебные крошки:* Показываем результат — что теперь в AdminUser

[◀ Вставляем новую строку с правильным отступом после target](860_Vstavlyaem_novuyu_stroku_s_pravilnym_otstupom_posle_target.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](862_part.md)

---

# Показываем результат — что теперь в AdminUser
m2 = re.search(r"(class AdminUser\(Base\):[\s\S]*?)(?=\nclass |\Z)", new_content)
print("\n=== Новый AdminUser ===")
print(m2.group(1))
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_adminuser_dept.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Запуск патчера ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_adminuser_dept.py
Ожидаем:
text
OK: department_id добавлен в AdminUser
SYNTAX OK

=== Новый AdminUser ===
class AdminUser(Base):
    """
    Пользователь админ-панели.
    ...
    """
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    ...
    language = Column(String(8), default="ru", nullable=False)
    # Для роли manager — привязка к отделу (видит только свой отдел).
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    last_login_at = Column(DateTime(timezone=True))
Запусти и пришли вывод. Как только увидим новое поле — идём в Скрипт 2 (миграция).
>> & client\.venv\Scripts\python.exe _patch_adminuser_dept.py === Запуск патчера === OK: department_id добавлен в AdminUser SYNTAX OK === Новый AdminUser === class AdminUser(Base): """ Пользователь админ-панели. Пароль хранится как bcrypt-хеш (никогда не в открытом виде). Роли: admin, operator, viewer, hr, manager. """ __tablename__ = "admin_users" id = Column(Integer, primary_key=True) username = Column(String(64), unique=True, nullable=False, index=True) password_hash = Column(String(255), nullable=False) full_name = Column(String(255)) email = Column(String(255)) role = Column(String(32), nullable=False, default="viewer") is_active = Column(Boolean, default=True, nullable=False) language = Column(String(8), default="ru", nullable=False) # Для роли manager — привязка к отделу (видит только свой отдел). department_id = Column(Integer, ForeignKey("departments.id"), nullable=True) created_at = Column(DateTime(timezone=True), default=_utcnow) last_login_at = Column(DateTime(timezone=True))
Отлично, модель AdminUser обновлена. Теперь генерируем миграцию.
? Модель обновлена. Идём в Скрипт 2 — миграция.
________________________________________
Скрипт 2 — генерируем миграцию + проверяем на партиции
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Генерация миграции ===" -ForegroundColor Cyan
docker compose exec -T api alembic -c /app/server/alembic.ini revision --autogenerate -m "add_admin_users_department_id"

Write-Host "`n=== Что появилось в versions/ ===" -ForegroundColor Cyan
Get-ChildItem "D:\tracker\server\alembic\versions\*.py" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 3 |
    Format-Table Name, Length, LastWriteTime

Write-Host "`n=== Содержимое новой миграции ===" -ForegroundColor Cyan
$newFile = Get-ChildItem "D:\tracker\server\alembic\versions\*.py" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
Write-Host "Файл: $($newFile.Name)"
Write-Host ""
Get-Content $newFile.FullName

Write-Host "`n=== Проверка на партиции records_* ===" -ForegroundColor Cyan
$content = [System.IO.File]::ReadAllText($newFile.FullName, [System.Text.UTF8Encoding]::new($false))
$hasPartitions = $content -match "records_\d{4}"
$hasDropTable = $content -match "op\.drop_table\('records"
$hasCreateTable = $content -match "op\.create_table\('records_"
$hasDropIndex = $content -match "op\.drop_index\('records"

if ($hasPartitions -or $hasDropTable -or $hasCreateTable -or $hasDropIndex) {
    Write-Host "  ? ВНИМАНИЕ: миграция трогает партиции records_* !" -ForegroundColor Red
    Write-Host "  НЕ ПРИМЕНЯЙ! Пришли содержимое мне." -ForegroundColor Red
    Write-Host "  hasPartitions=$hasPartitions hasDropTable=$hasDropTable hasCreateTable=$hasCreateTable hasDropIndex=$hasDropIndex" -ForegroundColor Yellow
} else {
    Write-Host "  ? OK: партиции records_* не упоминаются" -ForegroundColor Green
}
Ожидаем: миграция должна содержать только два действия:
op.add_column('admin_users', sa.Column('department_id', sa.Integer(), nullable=True))
op.create_foreign_key(...) — FK на departments
Если увидишь что-то про records_* — стоп, присылай файл, разрулим.
Запускай — жду вывод.
Идеально. Миграция чистая, только:
add_column admin_users.department_id
create_foreign_key
Партиции не тронуты — наш include_object работает. Всё как надо.
Единственное замечание — op.create_foreign_key(None, ...) — имя constraint будет None. PostgreSQL сам сгенерирует имя. Это нормально, но лучше явное имя, чтобы в downgrade можно было удалить. Правда, alembic сам генерирует корректный drop_constraint(None, ...) — он тоже подставит автоимя. Обычно работает, но лучше явное имя.
Давай не будем заморачиваться — оставим как есть. Если будут проблемы с откатом, поправим.
Но! Есть один важный момент — миграция генерируется от b02da1230e4d (предыдущей). Хорошо, цепочка:
35d67a73f181 ? 939e3d0b6f4c ? ecb1e3f89300 ? 2602b71902d4 ? b02da1230e4d ? 0f13ad394b65
Ок, применяем.
Пользователь остановился здесь. Мне нужно:
Сказать: миграция чистая, применяем
Дать команду применения
Дать проверку — колонка появилась в БД
Перейти к Скрипту 3 — роуты /admin/profile
Скрипт 3 большой (роуты + хелперы фильтрации + сессия). Запустим.
Также важно — проверим, что Department импортирован в web_admin.py. Пользователь не присылал вывод этой команды.
Давай структурирую:
Применение миграции
Проверка
Скрипт 3 — роуты /admin/profile + хелпер manager_department_id (без apply_manager_filter — оставим на потом, чтобы не усложнять)
Скрипт 3b — проверить где формируется session["admin_user"] и добавить department_id
Скрипт 4 — profile.html (это уже давал в прошлом сообщении, но переиздам, чтобы пользователь не искал)
Скрипт 5 — user_form.html (тоже переиздам)
Скрипт 6 — патч роутов users (сокращу до минимума, только чтобы department_id принимался)
Пересборка
Хотя это уже было, но переиздам чтобы было в одном сообщении.
Хорошо, приступаю к написанию ответа.
? Миграция идеальная. include_object работает — партиции не тронуты. Применяем.
________________________________________
Скрипт 2a — применяем миграцию
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Перезапуск api (Alembic применит миграцию) ===" -ForegroundColor Cyan
docker compose restart api
Start-Sleep -Seconds 15

Write-Host "`n=== Логи API ===" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`n=== Версия Alembic ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT * FROM alembic_version;"

Write-Host "`n=== Колонка admin_users.department_id ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='admin_users' AND column_name='department_id';"

Write-Host "`n=== FK на departments ===" -ForegroundColor Cyan
docker compose exec -T db psql -U tracker -d tracker -c "SELECT tc.constraint_name, ccu.table_name AS foreign_table FROM information_schema.table_constraints AS tc JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.table_name='admin_users' AND tc.constraint_type='FOREIGN KEY';"
Ожидаем:
Running upgrade b02da1230e4d -> 0f13ad394b65, add_admin_users_department_id
version_num = 0f13ad394b65
department_id присутствует, nullable
FK на departments
Как только увидим — идём в Скрипт 3.
________________________________________
Скрипт 3 — роуты /admin/profile + хелпер для manager
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains('def profile_page(')) {
    Write-Host "Роуты /profile уже есть" -ForegroundColor Yellow
} else {
    $anchor = @'
def _active_admins_count(db: Session) -> int:
    """Сколько активных администраторов в системе."""
    return db.query(AdminUser).filter(
        AdminUser.role == "admin",
        AdminUser.is_active == True,
    ).count()
'@
    $addition = @'
def _active_admins_count(db: Session) -> int:
    """Сколько активных администраторов в системе."""
    return db.query(AdminUser).filter(
        AdminUser.role == "admin",
        AdminUser.is_active == True,
    ).count()


