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


def build_query(text: str) -> str:
    # Lowercase words, punctuation dropped
    words = [word.lower() for word in re.findall(r"\w+", text)]

    # word-word pairs glued together, as the PDF cleaning may have joined them
    joined = [(first + second).lower() for first, second in re.findall(r"(\w+)-(\w+)", text)]

    # Wrap each unique word in quotes and OR them together
    return " OR ".join(f'"{word}"' for word in dict.fromkeys(words + joined))