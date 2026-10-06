<!-- Часть 762 из 1409 -->
# 2. Remove all single-line op.drop_index('records_...') calls
*Хлебные крошки:* 2. Remove all single-line op.drop_index('records_...') calls

[◀ Pattern: op.create_table('records_...' followed by any number of indented lines ending with `    )\n`](761_Pattern_op_create_tablerecords_followed_by_any_number_of_indented_lines_ending_w.md) | [Оглавление](00_BCE_INDEX.md) | [3. Remove all single-line op.drop_table('records_...') calls ▶](763_3_Remove_all_single_line_op_drop_tablerecords_calls.md)

---

# 2. Remove all single-line op.drop_index('records_...') calls
pattern_dropidx = re.compile(r"\n    op\.drop_index\('records_[^']*'.*?\)\n")
content = pattern_dropidx.sub("\n", content)

