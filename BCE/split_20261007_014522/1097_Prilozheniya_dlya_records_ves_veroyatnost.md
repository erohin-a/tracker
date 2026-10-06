<!-- Часть 1097 из 1409 -->
# Приложения для records (вес = вероятность)
*Хлебные крошки:* Приложения для records (вес = вероятность)

[◀ (last, first, middle, dept_idx)](1096_last_first_middle_dept_idx.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Очистка (только наши тестовые данные) ---------- ▶](1098_Ochistka_tolko_nashi_testovye_dannye.md)

---

# Приложения для records (вес = вероятность)
APPS = [
    ("1cv8.exe",       25),
    ("browser.exe",    20),
    ("OUTLOOK.EXE",    15),
    ("EXCEL.EXE",      15),
    ("WINWORD.EXE",    10),
    ("Code.exe",        5),
    ("max.exe",         5),
    ("explorer.exe",    3),
    ("notepad.exe",     2),
]

def weighted_choice(items):
    total = sum(w for _, w in items)
    r = random.uniform(0, total)
    upto = 0
    for name, w in items:
        if upto + w >= r:
            return name
        upto += w
    return items[-1][0]

