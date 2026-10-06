<!-- Часть 1173 из 1409 -->
# Ищем внутри функции close_stale_sessions строку с неполным импортом
*Хлебные крошки:* Ищем внутри функции close_stale_sessions строку с неполным импортом

[◀ Что	Оценка](1172_Chto_Otsenka.md) | [Оглавление](00_BCE_INDEX.md) | [Показываем функцию close_stale_sessions — первые 30 строк ▶](1174_Pokazyvaem_funktsiyu_close_stale_sessions_pervye_30_strok.md)

---

# Ищем внутри функции close_stale_sessions строку с неполным импортом
old = "from .models import AppSetting as _AppSetting, Record as _Record"

new = (
    "from .models import (\n"
    "        AppSetting as _AppSetting,\n"
    "        Record as _Record,\n"
    "        WorkSession,\n"
    "        AuditLog,\n"
    "    )"
)

if new in content:
    print("SKIP: импорт уже расширен")
elif old in content:
    content = content.replace(old, new, 1)
    PATH.write_text(content, encoding="utf-8")
    print("OK: импорт WorkSession и AuditLog добавлен")
else:
    print("WARN: строка с импортом не найдена — ищу альтернативу")
    # Альтернатива: возможно строка уже другая
    m = re.search(r"from \.models import [^\n]*AppSetting[^\n]*\n", content)
    if m:
        print("Найдено:", m.group(0).strip())
        print("Проверь вручную и пришли эту строку")
    else:
        print("Модели вообще не импортируются — надо смотреть файл целиком")

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

