import sqlite3

# Bump whenever what gets stored changes: these tables, the tokenizer, or the text cleaning
SCHEMA_VERSION = 1


def open_index(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    # The index can always be rebuilt from the PDFs, so an older one is dropped, not converted
    if conn.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
        conn.execute("DROP TABLE IF EXISTS pages")
        conn.execute("DROP TABLE IF EXISTS files")

    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS pages
        USING fts5(path UNINDEXED, page UNINDEXED, body, tokenize = 'porter unicode61')
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            mtime REAL NOT NULL
        )
    """)
    # Set last, so a rebuild that fails partway is simply redone on the next open.
    # PRAGMA takes no ? placeholders; this is safe only because it's our own integer constant.
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
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


def search_with_snippets(conn: sqlite3.Connection, query: str, limit: int = 10) -> list[tuple[str, int, str]]:
    rows = conn.execute(
        """
        SELECT path, page, snippet(pages, 2, '[', ']', '…', 12) FROM pages
        WHERE pages MATCH ?
        ORDER BY bm25(pages)
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()
    return [(path, page, " ".join(snippet.split())) for path, page, snippet in rows]
