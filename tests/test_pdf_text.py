import pymupdf

from core.pdf_text import clean_text, extract_pages


def test_one_string_per_page_in_order_including_blank_pages(tmp_path):
    pdf_path = tmp_path / "lecture.pdf"
    with pymupdf.open() as doc:
        doc.new_page().insert_text((72, 72), "first page")
        doc.new_page()
        doc.new_page().insert_text((72, 72), "third page")
        doc.save(pdf_path)

    pages = extract_pages(pdf_path)

    assert [text.strip() for text in pages] == ["first page", "", "third page"]


def test_clean_text_expands_ligatures():
    assert clean_text("Reﬂexivity ﬁnd") == "Reflexivity find"


def test_clean_text_joins_words_split_across_lines():
    assert clean_text("the calcu-\nlus of") == "the calculus of"


def test_clean_text_leaves_other_hyphens_alone():
    assert clean_text("one-to-one") == "one-to-one"
    assert clean_text("a -\nb") == "a -\nb"
