<!-- Часть 631 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Функция перевода](630_Funktsiya_perevoda.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](632_Proverka_sintaksisa.md)

---

# ============================================================
def t(key: str, lang: Optional[str] = None) -> str:
    """
    Возвращает перевод по ключу.

    Аргументы:
      key  — ключ вида "menu.employees" (см. TRANSLATIONS выше).
      lang — код языка ("ru" или "en"). Если None или неизвестный —
             используется DEFAULT_LANG.

    Логика fallback (если перевод отсутствует):
      1. Пробуем взять перевод на нужном языке.
      2. Если нет — на DEFAULT_LANG.
      3. Если нет — возвращаем сам ключ (чтобы было видно, где дырка).
    """
    lang = lang or DEFAULT_LANG
    entry = TRANSLATIONS.get(key)
    if entry is None:
        # Такого ключа нет — возвращаем сам ключ, чтобы ошибка была видна
        return key
    if lang in entry:
        return entry[lang]
    return entry.get(DEFAULT_LANG) or key


def is_valid_lang(code: str) -> bool:
    """Проверяет, поддерживается ли такой код языка."""
    return code in {l["code"] for l in SUPPORTED_LANGS}
'@

[System.IO.File]::WriteAllText($i18nPath, $i18nPy, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $i18nPath" -ForegroundColor Green

