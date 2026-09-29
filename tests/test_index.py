from core.index import add_document, open_index, search


def test_search_finds_the_file_and_page_number():
    conn = open_index(":memory:")
    add_document(conn, "arch.pdf", ["intro slide", "cache memory is fast"])

    assert search(conn, "cache") == [("arch.pdf", 2)]


def test_search_with_several_words_needs_all_of_them():
    conn = open_index(":memory:")
    add_document(conn, "arch.pdf", ["cache memory", "main memory"])

    assert search(conn, "cache memory") == [("arch.pdf", 1)]


def test_search_for_a_missing_word_returns_nothing():
    conn = open_index(":memory:")
    add_document(conn, "arch.pdf", ["cache memory"])

    assert search(conn, "normalisation") == []


def test_search_ranks_a_rarer_word_first():
    conn = open_index(":memory:")
    add_document(conn, "arch.pdf", ["memory layout", "memory bus", "memory cells", "cache lines"])

    assert search(conn, "memory OR cache")[0] == ("arch.pdf", 4)


def test_search_ranks_more_mentions_first():
    conn = open_index(":memory:")
    add_document(
        conn,
        "arch.pdf",
        ["cache lines here", "cache cache lines", "virtual memory", "main memory", "memory bus"],
    )

    assert search(conn, "cache") == [("arch.pdf", 2), ("arch.pdf", 1)]


def test_search_returns_at_most_limit_results():
    conn = open_index(":memory:")
    add_document(conn, "arch.pdf", ["cache"] * 5)

    assert len(search(conn, "cache", limit=3)) == 3

