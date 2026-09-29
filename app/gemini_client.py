from functools import lru_cache
import time

from google import genai
from google.genai import types

from .config import get_settings


@lru_cache
def get_client():

    settings = get_settings()

    if not settings.gemini_api_key:
        return None

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_text(
    prompt: str,
    model: str,
    max_output_tokens: int = 4000,
) -> str:

    settings = get_settings()

    client = get_client()

    # If Gemini is not configured
    if client is None:

        if settings.ai_demo_mode:
            return ""

        raise RuntimeError(
            "Gemini API key is not configured. "
            "Add GEMINI_API_KEY to your .env file."
        )

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    max_output_tokens=max_output_tokens,
                ),
            )
            break
        except Exception as exc:
            if getattr(exc, "code", None) != 503 or attempt == 2:
                raise

            time.sleep(2**attempt)

    text = (
        response.text
        or ""
    ).strip()

    if not text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text