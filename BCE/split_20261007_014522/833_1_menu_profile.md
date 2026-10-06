<!-- Часть 833 из 1409 -->
# 1. menu.profile
*Хлебные крошки:* 1. menu.profile

[◀ Проверки](832_Proverki.md) | [Оглавление](00_BCE_INDEX.md) | [2. profile.* ключи ▶](834_2_profile_klyuchi.md)

---

# 1. menu.profile
if '"menu.profile"' not in content:
    old = '"menu.logout":'
    new = '"menu.profile": {"ru": "Мой профиль", "en": "My profile"},\n    "menu.logout":'
    if old in content:
        content = content.replace(old, new, 1)
        changed.append("menu.profile")

