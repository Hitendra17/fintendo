from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    content: str


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if overlap < 0:
            raise ValueError("overlap must not be negative.")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[TextChunk]:
        if not text.strip():
            raise ValueError("text must not be empty.")

        chunks: list[TextChunk] = []

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text),
            )

            content = text[start:end].strip()

            if content:
                chunks.append(
                    TextChunk(
                        chunk_index=chunk_index,
                        content=content,
                    )
                )

            if end == len(text):
                break

            start = end - self.overlap
            chunk_index += 1

        return chunks