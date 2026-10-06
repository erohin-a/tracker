<!-- Часть 658 из 1409 -->
# Текущий язык запроса. По умолчанию — русский.
*Хлебные крошки:* Текущий язык запроса. По умолчанию — русский.

[◀ ============================================================](657_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](659_part.md)

---

# Текущий язык запроса. По умолчанию — русский.
_current_lang: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_lang", default=DEFAULT_LANG
)


def set_current_lang(lang: Optional[str]) -> str:
    """
    Устанавливает язык для текущего запроса.
    Если язык не поддерживается — ставит DEFAULT_LANG.
    Возвращает фактически установленный код.
    """
    if not lang or not is_valid_lang(lang):
        lang = DEFAULT_LANG
    _current_lang.set(lang)
    return lang


def get_current_lang() -> str:
    """Возвращает язык текущего запроса."""
    return _current_lang.get()


def _(key: str) -> str:
    """
    Короткая обёртка для использования в шаблонах и коде.
    Пример: _("menu.employees") -> "Сотрудники" или "Employees".
    """
    return t(key, _current_lang.get())
'@

[System.IO.File]::WriteAllText("$serverDir\web_i18n.py", $webI18n, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: создан $serverDir\web_i18n.py" -ForegroundColor Green


