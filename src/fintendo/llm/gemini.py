from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from fintendo.core.config import settings

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )
        self.model = settings.gemini_model

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response_model.model_validate_json(response.text)

    def generate_structured_with_web_search(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ],
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        text = response.text.strip()

        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```").strip()

        if text.endswith("```"):
            text = text.removesuffix("```").strip()

        return response_model.model_validate_json(text)