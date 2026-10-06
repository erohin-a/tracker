<!-- Часть 964 из 1409 -->
# t(f"key.{var}") — f-строки
*Хлебные крошки:* t(f"key.{var}") — f-строки

[◀ t("key") и t('key')](963_tkey_i_tkey.md) | [Оглавление](00_BCE_INDEX.md) | [Очистим лог — будем смотреть только свежее ▶](965_Ochistim_log_budem_smotret_tolko_svezhee.md)

---

# t(f"key.{var}") — f-строки
pattern2 = re.compile(r'''\bt\(\s*f["']([a-z_][a-z_.0-9]*\.)\{''')
for prefix in pattern2.findall(src):
    # prefix оканчивается точкой, ищем какому полю соответствует
    for suffix in ('light', 'dark', 'system'):
        keys.add(prefix + suffix)

print(f'Всего ключей найдено в settings_dialog.py: {len(keys)}')
missing = [k for k in sorted(keys) if k not in i18n.TRANSLATIONS]
if missing:
    print()
    print('ОТСУТСТВУЮТ в TRANSLATIONS:')
    for k in missing:
        print(f'  {k}')
    sys.exit(1)
else:
    print('Все ключи найдены в TRANSLATIONS')
    sys.exit(0)
'@

[System.IO.File]::WriteAllText("D:\tracker\_check_i18n_keys.py", $checker, [System.Text.UTF8Encoding]::new($false))

client\.venv\Scripts\Activate.ps1
& client\.venv\Scripts\python.exe _check_i18n_keys.py
Что ожидаем:
text
Всего ключей найдено в settings_dialog.py: 60 (примерно)
Все ключи найдены в TRANSLATIONS
Если увидишь ОТСУТСТВУЮТ — пришли мне список, добавлю их в i18n.py.
________________________________________
Скрипт 7 — запуск клиента и проверка
Закрой старый клиент (трей ? Выход). Затем:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
client\.venv\Scripts\Activate.ps1

