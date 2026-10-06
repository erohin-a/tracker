<!-- Часть 635 из 1409 -->
# server/web_i18n.py
*Хлебные крошки:* server/web_i18n.py

[◀ middleware или dependency:](634_middleware_ili_dependency.md) | [Оглавление](00_BCE_INDEX.md) | [Регистрируем `_` в Jinja ▶](636_Registriruem_v_Jinja.md)

---

# server/web_i18n.py
import contextvars
from typing import Optional
from .i18n import t, DEFAULT_LANG, is_valid_lang

_current_lang: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_lang", default=DEFAULT_LANG
)

def set_current_lang(lang: str) -> None:
    """Устанавливает язык для текущего запроса."""
    if not is_valid_lang(lang):
        lang = DEFAULT_LANG
    _current_lang.set(lang)

def get_current_lang() -> str:
    """Возвращает язык текущего запроса."""
    return _current_lang.get()

def _(key: str) -> str:
    """Короткая обёртка для шаблонов и кода."""
    return t(key, _current_lang.get())
В web_admin.py:
python
from .web_i18n import _, set_current_lang, get_current_lang
from .i18n import SUPPORTED_LANGS

