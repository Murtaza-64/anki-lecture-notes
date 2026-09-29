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
