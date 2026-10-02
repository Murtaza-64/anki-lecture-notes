import sqlite3
from pathlib import Path

from .index import indexed_files, remove_document, replace_document
from .pdf_text import extract_pages


def sync_folder(conn: sqlite3.Connection, folder: str | Path) -> dict[str, str]:
    on_disk = {str(path): path.stat().st_mtime for path in Path(folder).rglob("*.pdf")}
    indexed = indexed_files(conn)
    result = {}

    for path, mtime in on_disk.items():
        if indexed.get(path) != mtime:
            try:
                pages = extract_pages(path)
                replace_document(conn, path, pages, mtime)
                result[path] = "indexed"
            except Exception:
                result[path] = "failed"

    for path in indexed.keys() - on_disk.keys():
        remove_document(conn, path)
        result[path] = "removed"

    return result
