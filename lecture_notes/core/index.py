import sqlite3


def open_index(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS pages
        USING fts5(path UNINDEXED, page UNINDEXED, body)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            mtime REAL NOT NULL
        )
    """)
    return conn


def replace_document(conn: sqlite3.Connection, path: str, pages: list[str], mtime: float) -> None:
    rows = [(path, page_number, text) for page_number, text in enumerate(pages, start=1)]
    with conn:
        conn.execute("DELETE FROM pages WHERE path = ?", (path,))
        conn.executemany("INSERT INTO pages (path, page, body) VALUES (?, ?, ?)", rows)
        conn.execute("INSERT OR REPLACE INTO files (path, mtime) VALUES (?, ?)", (path, mtime))


def remove_document(conn: sqlite3.Connection, path: str) -> None:
    with conn:
        conn.execute("DELETE FROM pages WHERE path = ?", (path,))
        conn.execute("DELETE FROM files WHERE path = ?", (path,))


def indexed_files(conn: sqlite3.Connection) -> dict[str, float]:
    return dict(conn.execute("SELECT path, mtime FROM files").fetchall())


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
