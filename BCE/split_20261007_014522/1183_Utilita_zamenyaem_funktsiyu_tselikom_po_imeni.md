<!-- Часть 1183 из 1409 -->
# --- Утилита: заменяем функцию целиком по имени ---
*Хлебные крошки:* --- Утилита: заменяем функцию целиком по имени ---

[◀ Что	Приоритет](1182_Chto_Prioritet.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1184_part.md)

---

# --- Утилита: заменяем функцию целиком по имени ---
def replace_func(content: str, name: str, new_body: str) -> tuple[str, bool]:
    pattern = re.compile(
        rf"^def {re.escape(name)}\(.*?(?=\ndef |\n# ============|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(content)
    if not m:
        return content, False
    return content[:m.start()] + new_body.rstrip() + "\n" + content[m.end():], True

