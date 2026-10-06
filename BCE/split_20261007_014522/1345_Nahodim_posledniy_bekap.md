<!-- Часть 1345 из 1409 -->
# Находим последний бэкап
*Хлебные крошки:* Находим последний бэкап

[◀ Восстанавливает файлы из последнего бэкапа remove_pivot_pdf.](1344_Vosstanavlivaet_fayly_iz_poslednego_bekapa_remove_pivot_pdf.md) | [Оглавление](00_BCE_INDEX.md) | [Восстанавливаем ВСЕ файлы из бэкапа ▶](1346_Vosstanavlivaem_VSE_fayly_iz_bekapa.md)

---

# Находим последний бэкап
backups = sorted([p for p in BACKUP_ROOT.iterdir() if p.is_dir()])
if not backups:
    print("Бэкапов нет!")
    raise SystemExit(1)
src = backups[-1]
print(f"Бэкап: {src}")

