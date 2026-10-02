from core.card_text import clean_card_text


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
