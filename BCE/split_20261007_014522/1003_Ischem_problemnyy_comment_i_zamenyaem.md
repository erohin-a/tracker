<!-- Часть 1003 из 1409 -->
# Ищем проблемный comment и заменяем
*Хлебные крошки:* Ищем проблемный comment и заменяем

[◀ ---------- 2. Чистим крокозябры в комментарии к connected ----------](1002_2_Chistim_krokozyabry_v_kommentarii_k_connected.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 3. Проверим синтаксис ---------- ▶](1004_3_Proverim_sintaksis.md)

---

# Ищем проблемный comment и заменяем
import re
old_comment_pat = re.compile(
    r'(connected = pyqtSignal\(\)\s*#[^\n]*)\n'
)
def fix_comment(m):
    line = m.group(1)
    return 'connected = pyqtSignal()   # сервер доступен (для UI: "? онлайн")\n'

new_content, n = old_comment_pat.subn(fix_comment, content, count=1)
if n > 0:
    content = new_content
    print("OK: комментарий к connected почищен")
else:
    print("SKIP: comment к connected не найден (возможно уже чистый)")

