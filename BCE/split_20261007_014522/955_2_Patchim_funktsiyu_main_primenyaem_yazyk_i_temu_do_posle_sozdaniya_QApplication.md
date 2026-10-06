<!-- Часть 955 из 1409 -->
# 2. Патчим функцию main() — применяем язык и тему до/после создания QApplication
*Хлебные крошки:* 2. Патчим функцию main() — применяем язык и тему до/после создания QApplication

[◀ 1. Добавляем импорты в начало файла (после существующих)](954_1_Dobavlyaem_importy_v_nachalo_fayla_posle_suschestvuyuschih.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка импортов всего клиента ▶](956_Proverka_importov_vsego_klienta.md)

---

# 2. Патчим функцию main() — применяем язык и тему до/после создания QApplication
old_main = '''def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)'''

new_main = '''def main():
    # --- Применяем сохранённый язык до создания любых виджетов ---
    try:
        set_language(get_language_code())
        log.info("Client language = %s", get_language_code())
    except Exception:
        log.exception("Failed to set language")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # --- Применяем сохранённую тему ---
    try:
        _theme = get_theme_code()
        themes.apply_theme(app, _theme)
        log.info("Client theme = %s", _theme)
    except Exception:
        log.exception("Failed to apply theme")

    # --- Сбрасываем флаг restart_required после перезапуска ---
    try:
        if get_setting("restart_required"):
            set_setting("restart_required", False)
            log.info("Restart flag cleared")
    except Exception:
        log.exception("Failed to clear restart flag")'''

if old_main in content:
    content = content.replace(old_main, new_main, 1)
    print("OK: main() пропатчен — тема и язык применяются")
else:
    print("ERROR: не найден блок 'def main()'")
    print("Проверьте вручную: ищите 'def main():' в client/main.py")
    raise SystemExit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_main_client.py", $patcher, [System.Text.UTF8Encoding]::new($false))

Write-Host "=== Запуск патчера main.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_main_client.py
Что ожидаем:
text
OK: добавлены импорты themes/i18n/config
OK: main() пропатчен — тема и язык применяются
SYNTAX OK
________________________________________
Скрипт 6 — Финальный тест
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
client\.venv\Scripts\Activate.ps1

