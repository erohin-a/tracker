<!-- Часть 764 из 1409 -->
# 4. Remove all single-line op.create_index('records_...', ...) calls
*Хлебные крошки:* 4. Remove all single-line op.create_index('records_...', ...) calls

[◀ 3. Remove all single-line op.drop_table('records_...') calls](763_3_Remove_all_single_line_op_drop_tablerecords_calls.md) | [Оглавление](00_BCE_INDEX.md) | [Clean up multiple blank lines ▶](765_Clean_up_multiple_blank_lines.md)

---

# 4. Remove all single-line op.create_index('records_...', ...) calls
pattern_createidx = re.compile(r"\n    op\.create_index\('records_[^']*'.*?\)\n")
content = pattern_createidx.sub("\n", content)

