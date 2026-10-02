import html
import re


def clean_card_text(field_html: str) -> str:
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", field_html)

    # Turn HTML entities back into characters
    text = html.unescape(text)

    # Remove maths notation
    text = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", " ", text, flags=re.DOTALL)

    return " ".join(text.split())
