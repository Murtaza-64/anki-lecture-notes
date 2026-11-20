import sqlite3

from core.index import (
    SCHEMA_VERSION,
    indexed_files,
    open_index,
    remove_document,
    replace_document,
    search,
    search_with_snippets,
)


def test_search_finds_the_file_and_page_number():
    conn = open_index(":memory:")
    replace_document(conn, "arch.pdf", ["intro slide", "cache memory is fast"], 0.0)

    assert search(conn, "cache") == [("arch.pdf", 2)]


def test_search_with_several_words_needs_all_of_them():
    conn = open_index(":memory:")
    replace_document(conn, "arch.pdf", ["cache memory", "main memory"], 0.0)

    assert search(conn, "cache memory") == [("arch.pdf", 1)]


def test_search_for_a_missing_word_returns_nothing():
    conn = open_index(":memory:")
    replace_document(conn, "arch.pdf", ["cache memory"], 0.0)

    assert search(conn, "normalisation") == []


def test_search_ranks_a_rarer_word_first():
    conn = open_index(":memory:")
    replace_document(conn, "arch.pdf", ["memory layout", "memory bus", "memory cells", "cache lines"], 0.0)

    assert search(conn, "memory OR cache")[0] == ("arch.pdf", 4)


def test_search_ranks_more_mentions_first():
    conn = open_index(":memory:")
    replace_document(
        conn,
        "arch.pdf",
        ["cache lines here", "cache cache lines", "virtual memory", "main memory", "memory bus"],
        0.0,
    )

    assert search(conn, "cache") == [("arch.pdf", 2), ("arch.pdf", 1)]


def test_search_returns_at_most_limit_results():
    conn = open_index(":memory:")
    replace_document(conn, "arch.pdf", ["cache"] * 5, 0.0)

    assert len(search(conn, "cache", limit=3)) == 3


def test_replacing_a_document_removes_its_old_pages():
    conn = open_index(":memory:")
    replace_document(conn, "a.pdf", ["cache"], 1.0)
    replace_document(conn, "a.pdf", ["memory"], 2.0)

    assert search(conn, "cache") == []
    assert search(conn, "memory") == [("a.pdf", 1)]


def test_indexed_files_keeps_the_latest_mtime():
    conn = open_index(":memory:")
    replace_document(conn, "a.pdf", ["cache"], 1.0)
    replace_document(conn, "a.pdf", ["cache"], 2.0)

    assert indexed_files(conn) == {"a.pdf": 2.0}


def test_remove_document_clears_its_pages_and_mtime():
    conn = open_index(":memory:")
    replace_document(conn, "a.pdf", ["cache"], 1.0)
    remove_document(conn, "a.pdf")

    assert search(conn, "cache") == []
    assert indexed_files(conn) == {}


def test_search_matches_other_forms_of_a_word():
    conn = open_index(":memory:")
    replace_document(conn, "logic.pdf", ["the evaluation function assigns truth values"], 0.0)

    assert search(conn, "evaluate") == [("logic.pdf", 1)]


def test_search_with_snippets_highlights_matches_on_one_line():
    conn = open_index(":memory:")
    replace_document(conn, "sql.pdf", ["GROUP BY rules\nOnly one row output per group"], 0.0)

    assert search_with_snippets(conn, "group") == [("sql.pdf", 1, "[GROUP] BY rules Only one row output per [group]")]


def test_a_new_index_records_the_schema_version(tmp_path):
    conn = open_index(str(tmp_path / "index.db"))

    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION


def test_an_index_from_an_older_version_is_rebuilt(tmp_path):
    path = str(tmp_path / "index.db")
    old = sqlite3.connect(path)
    old.execute("CREATE VIRTUAL TABLE pages USING fts5(path UNINDEXED, page UNINDEXED, body)")
    old.execute("CREATE TABLE files (path TEXT PRIMARY KEY, mtime REAL NOT NULL)")
    old.execute("INSERT INTO files VALUES ('a.pdf', 1.0)")
    old.commit()
    old.close()

    conn = open_index(path)
    replace_document(conn, "logic.pdf", ["the evaluation function"], 0.0)

    assert indexed_files(conn) == {"logic.pdf": 0.0}
    assert search(conn, "evaluate") == [("logic.pdf", 1)]


def test_reopening_a_current_index_keeps_its_contents(tmp_path):
    path = str(tmp_path / "index.db")
    conn = open_index(path)
    replace_document(conn, "a.pdf", ["cache"], 1.0)
    conn.close()

    conn = open_index(path)

    assert indexed_files(conn) == {"a.pdf": 1.0}
    assert search(conn, "cache") == [("a.pdf", 1)]
