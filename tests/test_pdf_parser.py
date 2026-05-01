"""Tests for app.ingestion.pdf_parser."""

from pathlib import Path

import pytest
from pypdf import PdfWriter

from app.ingestion.pdf_parser import (
    extract_text_from_pdf,
    extract_texts_from_directory,
)


def _write_pdf(path: Path, text: str) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as f:
        writer.write(f)

    # PdfWriter blank pages have no text. Re-create using a text page via
    # a minimal approach: use reportlab if available, otherwise fall back to
    # writing a page with text annotations through pypdf's PageObject.
    # The simplest cross-platform path is to construct a PDF with embedded
    # text using pypdf's `add_blank_page` plus content stream injection.
    from pypdf.generic import ContentStream, NameObject, DecodedStreamObject

    reader_writer = PdfWriter()
    page = reader_writer.add_blank_page(width=612, height=792)

    content = (
        f"BT\n/F1 24 Tf\n72 720 Td\n({text}) Tj\nET"
    ).encode("latin-1")

    stream = DecodedStreamObject()
    stream.set_data(content)
    page[NameObject("/Contents")] = stream

    from pypdf.generic import DictionaryObject, ArrayObject

    font_dict = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    resources = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): font_dict}
            )
        }
    )
    page[NameObject("/Resources")] = resources

    with open(path, "wb") as f:
        reader_writer.write(f)


def test_extract_text_returns_string(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    _write_pdf(pdf_path, "Hello World Test Document")

    result = extract_text_from_pdf(str(pdf_path))

    assert isinstance(result, str)
    assert "Hello World" in result


def test_extract_text_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.pdf"
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(str(missing))


def test_extract_texts_from_directory(tmp_path: Path) -> None:
    _write_pdf(tmp_path / "a.pdf", "First Document Content")
    _write_pdf(tmp_path / "b.pdf", "Second Document Content")

    results = extract_texts_from_directory(str(tmp_path))

    assert isinstance(results, dict)
    assert len(results) == 2
    assert "a.pdf" in results
    assert "b.pdf" in results
