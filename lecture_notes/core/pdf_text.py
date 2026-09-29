import re
import unicodedata
from pathlib import Path

import pymupdf


def clean_text(text: str) -> str:
    # Replace characters that are only display variants with plain form
    text = unicodedata.normalize("NFKC", text)

    # Join words split across lines by a hyphen
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    return text


def extract_pages(path: str | Path) -> list[str]:
    with pymupdf.open(path) as doc:
        return [clean_text(page.get_text()) for page in doc]
