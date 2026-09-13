from fintendo.core.config import settings
from fintendo.rag.embeddings import EmbeddingProvider
from fintendo.rag.qwen_embeddings import QwenEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.embedding_provider.strip().lower()

    if provider == "qwen_local":
        return QwenEmbeddingProvider()

    raise ValueError(
        f"Unsupported embedding provider: {settings.embedding_provider}"
    )