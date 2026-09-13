from sentence_transformers import SentenceTransformer

from fintendo.rag.embeddings import EmbeddingProvider


class QwenEmbeddingProvider(EmbeddingProvider):
    MODEL_NAME = "Qwen/Qwen3-Embedding-4B"

    def __init__(self) -> None:
        self.model = SentenceTransformer(self.MODEL_NAME)

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("text must not be empty.")

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()