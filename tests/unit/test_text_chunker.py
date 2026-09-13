import pytest

from fintendo.rag.chunker import TextChunker


def test_chunker_splits_long_text():
    chunker = TextChunker(
        chunk_size=100,
        overlap=20,
    )

    text = "a" * 250

    chunks = chunker.split(text)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2


def test_chunker_preserves_overlap():
    chunker = TextChunker(
        chunk_size=100,
        overlap=20,
    )

    text = "a" * 180

    chunks = chunker.split(text)

    assert len(chunks) == 2
    assert chunks[0].content[-20:] == chunks[1].content[:20]


def test_chunker_handles_short_text():
    chunker = TextChunker(
        chunk_size=100,
        overlap=20,
    )

    chunks = chunker.split("short text")

    assert len(chunks) == 1
    assert chunks[0].content == "short text"


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (100, 100),
        (100, 150),
    ],
)
def test_chunker_rejects_invalid_configuration(
    chunk_size: int,
    overlap: int,
):
    with pytest.raises(ValueError):
        TextChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )


def test_chunker_rejects_empty_text():
    chunker = TextChunker()

    with pytest.raises(ValueError):
        chunker.split("")