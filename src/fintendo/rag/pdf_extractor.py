from io import BytesIO

from pypdf import PdfReader


class PDFTextExtractor:
    def extract(self, content: bytes) -> str:
        if not content:
            raise ValueError(
                "PDF content must not be empty."
            )

        reader = PdfReader(BytesIO(content))

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text.strip())

        extracted_text = "\n\n".join(pages).strip()

        if not extracted_text:
            raise ValueError(
                "No readable text found in PDF."
            )

        return extracted_text