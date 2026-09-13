from google import genai
from google.genai import types

from fintendo.core.config import settings
from fintendo.rag.embeddings import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    MODEL = "gemini-embedding-2"
    OUTPUT_DIMENSIONALITY = 768

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("text must not be empty.")

        response = self.client.models.embed_content(
            model=self.MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.OUTPUT_DIMENSIONALITY,
            ),
        )

        if not response.embeddings:
            raise RuntimeError(
                "Gemini returned no embeddings."
            )

        return response.embeddings[0].values