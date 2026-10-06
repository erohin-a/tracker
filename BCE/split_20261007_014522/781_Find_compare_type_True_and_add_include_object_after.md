<!-- Часть 781 из 1409 -->
# Find "compare_type=True," and add include_object after
*Хлебные крошки:* Find "compare_type=True," and add include_object after

[◀ Add include_object to context.configure in both offline and online](780_Add_include_object_to_context_configure_in_both_offline_and_online.md) | [Оглавление](00_BCE_INDEX.md) | [Online ▶](782_Online.md)

---

# Find "compare_type=True," and add include_object after
content = re.sub(
    r"(compare_type=True,)",  # match
    r"\1\n            include_object=include_object,",
    content
)
But wait, in the offline case, indentation is 12 spaces for compare_type=True,? Let me check:
text
    context.configure(
        url=url,
        target_metadata=target_metadata,
        ...
        compare_type=True,  # отслеживать изменения типов колонок
    )
That's 8 spaces. And online:
text
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=False,
        )
That's 12 spaces.
So different indentations. The re.sub approach needs to preserve indentation... Actually since I'm inserting after and the resulting code will have same indentation as the matched line, let me just add a newline and same indent:
python
import re

def add_include_object(match):
    line = match.group(0)  # "compare_type=True,"
    # Detect indent by looking at the match position in the original
    # ... complex
Too complicated. Let me just do a straightforward .replace() with the exact strings.
Actually — since this is a one-time fix, let me be pragmatic:
python
