import os

import pymupdf

from core.index import open_index, search
from core.sync import sync_folder


def make_pdf(path, texts):
    with pymupdf.open() as doc:
        for text in texts:
            doc.new_page().insert_text((72, 72), text)
        doc.save(path)


def test_new_pdf_in_a_subfolder_is_indexed(tmp_path):
    (tmp_path / "week1").mkdir()
    pdf = tmp_path / "week1" / "a.pdf"
    make_pdf(pdf, ["cache memory"])
    conn = open_index(":memory:")

    assert sync_folder(conn, tmp_path) == {str(pdf): "indexed"}
    assert search(conn, "cache") == [(str(pdf), 1)]


def test_second_sync_without_changes_does_nothing(tmp_path):
    make_pdf(tmp_path / "a.pdf", ["cache memory"])
    conn = open_index(":memory:")
    sync_folder(conn, tmp_path)

    assert sync_folder(conn, tmp_path) == {}


def test_changed_pdf_is_reindexed(tmp_path):
    pdf = tmp_path / "a.pdf"
    make_pdf(pdf, ["cache memory"])
    conn = open_index(":memory:")
    sync_folder(conn, tmp_path)

    make_pdf(pdf, ["virtual memory"])
    os.utime(pdf, (1000, 1000))

    assert sync_folder(conn, tmp_path) == {str(pdf): "indexed"}
    assert search(conn, "cache") == []
    assert search(conn, "virtual") == [(str(pdf), 1)]


def test_deleted_pdf_is_removed(tmp_path):
    pdf = tmp_path / "a.pdf"
    make_pdf(pdf, ["cache memory"])
    conn = open_index(":memory:")
    sync_folder(conn, tmp_path)

    pdf.unlink()

    assert sync_folder(conn, tmp_path) == {str(pdf): "removed"}
    assert search(conn, "cache") == []


def test_unreadable_pdf_fails_without_stopping_the_rest(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a pdf")
    good = tmp_path / "good.pdf"
    make_pdf(good, ["cache memory"])
    conn = open_index(":memory:")

    assert sync_folder(conn, tmp_path) == {str(bad): "failed", str(good): "indexed"}
