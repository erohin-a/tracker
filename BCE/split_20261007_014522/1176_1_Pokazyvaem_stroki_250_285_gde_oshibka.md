<!-- Часть 1176 из 1409 -->
# 1. Показываем строки 250-285 (где ошибка)
*Хлебные крошки:* 1. Показываем строки 250-285 (где ошибка)

[◀ plus something for Record](1175_plus_something_for_Record.md) | [Оглавление](00_BCE_INDEX.md) | [2. Пробуем распарсить ▶](1177_2_Probuem_rasparsit.md)

---

# 1. Показываем строки 250-285 (где ошибка)
print("=== Строки 250-285 ===")
for i in range(249, min(285, len(lines))):
    print(f"{i+1:4} | {lines[i]}")

print()
print("=== Все строки с 'from .models import' ===")
for i, line in enumerate(lines, 1):
    if "from .models import" in line:
        # Печатаем строку и 5 следующих
        for j in range(i - 1, min(i + 6, len(lines))):
            print(f"{j+1:4} | {lines[j]}")
        print("---")

