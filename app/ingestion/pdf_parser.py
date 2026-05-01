"""PDF text extraction utilities."""

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(str(path))

    page_texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            page_texts.append(text)

    full_text = "\n".join(page_texts)

    cleaned_lines = [line.strip() for line in full_text.splitlines()]
    non_empty_lines = [line for line in cleaned_lines if line]
    return "\n".join(non_empty_lines)


def extract_texts_from_directory(dir_path: str) -> dict[str, str]:
    directory = Path(dir_path)
    if not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    results: dict[str, str] = {}
    for pdf_file in sorted(directory.glob("*.pdf")):
        try:
            results[pdf_file.name] = extract_text_from_pdf(str(pdf_file))
        except Exception as exc:
            print(f"Warning: failed to parse {pdf_file.name}: {exc}")

    return results
