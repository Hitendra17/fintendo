from google.genai import types

from fintendo.llm.gemini import GeminiClient


def main() -> None:
    client = GeminiClient()

    prompt = """
Research Dabur India Limited (DABUR) using Google Search.

Find as many relevant recent developments as you can identify, ideally
10-20 high-quality sources.

Do not artificially limit the results to 5.

For each result provide:

- headline
- publisher
- publication date if available
- URL
- one-sentence explanation of why it is relevant to an investor researching Dabur

Only include information you actually find through web search.
Do not invent or guess URLs.
Prefer recent developments and credible publishers.
"""

    response = client.client.models.generate_content(
        model=client.model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ],
        ),
    )

    print("\n" + "=" * 80)
    print("GEMINI RAW WEB SEARCH RESPONSE")
    print("=" * 80)
    print(response)


if __name__ == "__main__":
    main()