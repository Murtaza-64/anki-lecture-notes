from pathlib import Path

import pymupdf


def extract_pages(path: str | Path) -> list[str]:
    with pymupdf.open(path) as doc:
        return [page.get_text() for page in doc]
