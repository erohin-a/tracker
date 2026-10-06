<!-- Часть 783 из 1409 -->
# Offline
*Хлебные крошки:* Offline

[◀ Online](782_Online.md) | [Оглавление](00_BCE_INDEX.md) | [Match "compare_type=True," with any leading whitespace, capture the whitespace ▶](784_Match_compare_type_True_with_any_leading_whitespace_capture_the_whitespace.md)

---

# Offline  
content = content.replace(
    "            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True,",
    "            target_metadata=target_metadata,\n            literal_binds=True,\n            dialect_opts={\"paramstyle\": \"named\"},\n            compare_type=True,\n            include_object=include_object,"
)
Hmm, but I'm not 100% sure of the exact whitespace in the file. Let me use a regex that handles both:
python
import re

