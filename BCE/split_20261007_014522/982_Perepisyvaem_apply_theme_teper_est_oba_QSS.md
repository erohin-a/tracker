<!-- Часть 982 из 1409 -->
# Переписываем apply_theme — теперь есть оба QSS
*Хлебные крошки:* Переписываем apply_theme — теперь есть оба QSS

[◀ Найдём конец DARK_QSS](981_Naydem_konets_DARK_QSS.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ▶](983_Proverka.md)

---

# Переписываем apply_theme — теперь есть оба QSS
old_apply = '''def apply_theme(app, code: str) -> bool:
    """
    Применяет тему к приложению.
    code: "light" | "dark" | "system"
    """
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(DARK_QSS)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet("")
        log.info("Applied %s theme", code or "light")
        return True
    else:
        log.warning("Unknown theme: %s, using light", code)
        app.setStyleSheet("")
        return False'''

new_apply = '''def apply_theme(app, code: str) -> bool:
    """
    Применяет тему к приложению.
    code: "light" | "dark" | "system"
    """
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(DARK_QSS)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet(LIGHT_QSS)
        log.info("Applied %s theme", code or "light")
        return True
    else:
        log.warning("Unknown theme: %s, using light", code)
        app.setStyleSheet(LIGHT_QSS)
        return False'''

if old_apply in new_content:
    new_content = new_content.replace(old_apply, new_apply, 1)
    print("OK: apply_theme теперь использует LIGHT_QSS")
else:
    print("WARN: apply_theme не найден — LIGHT_QSS не будет использоваться")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

