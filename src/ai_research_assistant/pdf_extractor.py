
from io import BytesIO

import requests
import pymupdf


def download_pdf(pdf_url: str) -> BytesIO:
    if not pdf_url or not pdf_url.strip():
        raise ValueError("PDF URL cannot be empty.")

    response = requests.get(
        pdf_url,
        timeout=(10, 60)
    )

    response.raise_for_status()

    if not response.content:
        raise ValueError("Downloaded PDF is empty.")

    content_type = response.headers.get("Content-Type", "").lower()

    if "application/pdf" not in content_type:
        # Some servers do not return the correct content type.
        # PyMuPDF will perform the actual PDF validation.
        if not response.content.startswith(b"%PDF"):
            raise ValueError(
                "The downloaded file does not appear to be a PDF."
            )

    return BytesIO(response.content)


def extract_text(pdf_file: BytesIO) -> str:
    if pdf_file is None:
        raise ValueError("PDF file cannot be None.")

    pdf_bytes = pdf_file.getvalue()

    if not pdf_bytes:
        raise ValueError("PDF file is empty.")

    pages_text = []

    try:
        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as document:

            if document.is_encrypted:
                raise ValueError("PDF is encrypted.")

            for page in document:
                pages_text.append(page.get_text())

    except pymupdf.FileDataError as error:
        raise ValueError(
            "Could not open the PDF. The file may be corrupted."
        ) from error

    paper_text = "\n".join(pages_text).strip()

    if not paper_text:
        raise ValueError(
            "No extractable text was found in the PDF."
        )

    return paper_text
