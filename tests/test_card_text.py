from core.card_text import build_query, clean_card_text
from core.index import open_index, replace_document, search


def test_removes_tags_and_keeps_words_apart():
    front = "<b>Bold</b>&nbsp;<i>italic</i>&nbsp;<br><ul><li>bullet point 1</li><li>bullet point 2</li></ul>"

    assert clean_card_text(front) == "Bold italic bullet point 1 bullet point 2"


def test_drops_tag_attributes():
    cells = '<td style="width:20%;  padding: 2px; border: 1px solid;">data1</td><td style="width:20%;">data2</td>'

    assert clean_card_text(cells) == "data1 data2"


def test_converts_entities_after_removing_tags():
    assert clean_card_text("a &lt; b and c &gt; d") == "a < b and c > d"


def test_removes_images():
    assert clean_card_text('see <img src="paste-1.png"> here') == "see here"


def test_removes_inline_maths():
    assert clean_card_text(r"value \(\infty = \frac{-1}{32}\) here") == "value here"


def test_removes_display_maths_across_lines():
    assert clean_card_text("before \\[x\n+ y\\] after") == "before after"


def test_keeps_text_between_two_formulas():
    assert clean_card_text(r"\(a\) and \(b\)") == "and"


def test_build_query_quotes_words_and_joins_them_with_or():
    assert build_query("cache memory") == '"cache" OR "memory"'


def test_build_query_lowercases_and_drops_repeated_words():
    assert build_query("Cache memory cache") == '"cache" OR "memory"'


def test_build_query_quotes_operator_words_and_drops_punctuation():
    assert build_query("A AND NOT b: c") == '"a" OR "and" OR "not" OR "b" OR "c"'


def test_build_query_adds_the_joined_form_of_hyphenated_words():
    assert build_query("non-negative") == '"non" OR "negative" OR "nonnegative"'


def test_build_query_without_words_is_empty():
    assert build_query("& <>") == ""


def test_build_query_output_is_a_valid_fts5_query():
    conn = open_index(":memory:")
    replace_document(conn, "a.pdf", ["p AND q is not true"], 0.0)

    assert search(conn, build_query("p AND NOT q: one-to-one")) == [("a.pdf", 1)]
