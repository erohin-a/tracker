<!-- Часть 981 из 1409 -->
# Найдём конец DARK_QSS
*Хлебные крошки:* Найдём конец DARK_QSS

[◀ Дополняем DARK_QSS перед закрывающими тройными кавычками](980_Dopolnyaem_DARK_QSS_pered_zakryvayuschimi_troynymi_kavychkami.md) | [Оглавление](00_BCE_INDEX.md) | [Переписываем apply_theme — теперь есть оба QSS ▶](982_Perepisyvaem_apply_theme_teper_est_oba_QSS.md)

---

# Найдём конец DARK_QSS
marker = '"""\n\n\ndef apply_theme'
pos = content.find(marker)
if pos < 0:
    print("ERROR: не найден конец DARK_QSS")
    raise SystemExit(1)

new_content = content[:pos] + addition + content[pos:]

