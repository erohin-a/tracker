<!-- Часть 859 из 1409 -->
# Ищем строку language = ... внутри класса
*Хлебные крошки:* Ищем строку language = ... внутри класса

[◀ Находим класс AdminUser](858_Nahodim_klass_AdminUser.md) | [Оглавление](00_BCE_INDEX.md) | [Вставляем новую строку с правильным отступом после target ▶](860_Vstavlyaem_novuyu_stroku_s_pravilnym_otstupom_posle_target.md)

---

# Ищем строку language = ... внутри класса
target = 'language = Column(String(8), default="ru", nullable=False)'
if target not in class_body:
    print(f"ERROR: строка '{target}' не найдена в AdminUser")
    # выведем первые 30 строк класса для отладки
    for i, line in enumerate(class_body.splitlines()[:30]):
        print(f"  {i:2}: {line}")
    raise SystemExit(1)

