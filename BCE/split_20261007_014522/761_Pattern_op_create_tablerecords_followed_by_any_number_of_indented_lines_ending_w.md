<!-- Часть 761 из 1409 -->
# Pattern: op.create_table('records_...' followed by any number of indented lines ending with `    )\n`
*Хлебные крошки:* Pattern: op.create_table('records_...' followed by any number of indented lines ending with `    )\n`

[◀ 1. Remove multi-line op.create_table('records_...' blocks](760_1_Remove_multi_line_op_create_tablerecords_blocks.md) | [Оглавление](00_BCE_INDEX.md) | [2. Remove all single-line op.drop_index('records_...') calls ▶](762_2_Remove_all_single_line_op_drop_indexrecords_calls.md)

---

# Pattern: op.create_table('records_...' followed by any number of indented lines ending with `    )\n`
pattern_create = re.compile(
    r"\n    op\.create_table\('records_[^']*',.*?\n    \)\n",
    re.DOTALL
)
content = pattern_create.sub("\n", content)

