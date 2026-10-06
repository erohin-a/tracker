<!-- Часть 763 из 1409 -->
# 3. Remove all single-line op.drop_table('records_...') calls
*Хлебные крошки:* 3. Remove all single-line op.drop_table('records_...') calls

[◀ 2. Remove all single-line op.drop_index('records_...') calls](762_2_Remove_all_single_line_op_drop_indexrecords_calls.md) | [Оглавление](00_BCE_INDEX.md) | [4. Remove all single-line op.create_index('records_...', ...) calls ▶](764_4_Remove_all_single_line_op_create_indexrecords_calls.md)

---

# 3. Remove all single-line op.drop_table('records_...') calls
pattern_droptbl = re.compile(r"\n    op\.drop_table\('records_[^']*'\)\n")
content = pattern_droptbl.sub("\n", content)

