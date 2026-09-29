import sqlite3


def open_index(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS pages
        USING fts5(path UNINDEXED, page UNINDEXED, body)
    """)
    return conn


def add_document(conn: sqlite3.Connection, path: str, pages: list[str]) -> None:
    rows = [(path, page_number, text) for page_number, text in enumerate(pages, start=1)]
    with conn:
        conn.executemany("INSERT INTO pages (path, page, body) VALUES (?, ?, ?)", rows)


def search(conn: sqlite3.Connection, query: str, limit: int = 10) -> list[tuple[str, int]]:
    return conn.execute(
        """
        SELECT path, page FROM pages
        WHERE pages MATCH ?
        ORDER BY bm25(pages)
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()
