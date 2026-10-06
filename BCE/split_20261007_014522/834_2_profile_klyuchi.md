<!-- Часть 834 из 1409 -->
# 2. profile.* ключи
*Хлебные крошки:* 2. profile.* ключи

[◀ 1. menu.profile](833_1_menu_profile.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](835_part.md)

---

# 2. profile.* ключи
if '"profile.title"' not in content:
    block = '''
    # ---------- Профиль пользователя ----------
    "profile.title":       {"ru": "Мой профиль", "en": "My profile"},
    "profile.hint":        {"ru": "Измените свои данные или смените пароль.", "en": "Change your info or password."},
    "profile.username":    {"ru": "Логин", "en": "Username"},
    "profile.full_name":   {"ru": "ФИО", "en": "Full name"},
    "profile.email":       {"ru": "Email", "en": "Email"},
    "profile.role":        {"ru": "Роль", "en": "Role"},
    "profile.language":    {"ru": "Язык интерфейса", "en": "UI language"},
    "profile.save":        {"ru": "Сохранить", "en": "Save"},
    "profile.saved":       {"ru": "Данные сохранены", "en": "Data saved"},
    "profile.change_pw":   {"ru": "Сменить пароль", "en": "Change password"},
    "profile.old_pw":      {"ru": "Текущий пароль", "en": "Current password"},
    "profile.new_pw":      {"ru": "Новый пароль", "en": "New password"},
    "profile.new_pw2":     {"ru": "Повторите новый пароль", "en": "Repeat new password"},
    "profile.pw_changed":  {"ru": "Пароль изменён", "en": "Password changed"},
    "profile.pw_wrong":    {"ru": "Неверный текущий пароль", "en": "Wrong current password"},
    "profile.pw_mismatch": {"ru": "Новые пароли не совпадают", "en": "New passwords don't match"},
    "profile.pw_too_short": {"ru": "Пароль должен быть минимум 8 символов", "en": "Password must be at least 8 characters"},
    "profile.my_logins":   {"ru": "Мои входы", "en": "My logins"},
'''

    # Вставляем перед def t(
    t_idx = content.find("def t(")
    close_idx = content.rfind("}", 0, t_idx)

    before = content[:close_idx]
    after = content[close_idx:]

    # Убеждаемся, что последняя строка словаря с запятой
    lines = before.split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            if not lines[i].rstrip().endswith(","):
                lines[i] = lines[i].rstrip() + ","
            break
    before = "\n".join(lines)

    content = before + block.rstrip() + "\n" + after
    changed.append("profile.* ключи")

with open(I18N, "w", encoding="utf-8") as f:
    f.write(content)

print("Изменения:")
for c in changed:
    print(f"  OK: {c}")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

print()
for c in ['"menu.profile"', '"profile.title"', '"profile.change_pw"', '"profile.pw_changed"']:
    print(f"  {'OK' if c in content else 'MISS'}: {c}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_i18n_profile.py", $patcher, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _patch_i18n_profile.py
Что ожидаем:
text
Изменения:
  OK: menu.profile
  OK: profile.* ключи

SYNTAX OK
  OK: "menu.profile"
  OK: "profile.title"
  OK: "profile.change_pw"
  OK: "profile.pw_changed"
________________________________________
Скрипт 2 — покажи полный base.html
Мне нужны строки 130-260, чтобы точно обернуть в условия.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$lines = [System.IO.File]::ReadAllLines("D:\tracker\server\templates\base.html", [System.Text.UTF8Encoding]::new($false))

Write-Host "=== base.html: строки 130-260 ===" -ForegroundColor Cyan
for ($i = 129; $i -lt [Math]::Min(260, $lines.Length); $i++) {
    Write-Host ("{0,4}: {1}" -f ($i + 1), $lines[$i])
}
Пришли мне вывод. По нему сразу сделаю патч — оберну секции в условия по ролям и добавлю ссылку на /admin/profile.
________________________________________
Скрипт 3 — параллельно починим крокозябры в users.html и logins.html
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

