from core.index import indexed_files, open_index, remove_document, replace_document, search


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
