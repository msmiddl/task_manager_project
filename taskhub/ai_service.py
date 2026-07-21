"""Isolated access to the Google AI username-suggestion service."""

import os


AI_UNAVAILABLE_MESSAGE = "AI username suggestions are unavailable."
USERNAME_PROMPT = (
    "Return one example username containing 2 to 30 characters. "
    "Return only the username with no explanation."
)


def request_username_suggestion() -> str:
    """Request and return one raw username suggestion from Google AI."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(AI_UNAVAILABLE_MESSAGE)

    try:
        from google import genai
        from google.genai import errors
    except ImportError as error:
        raise RuntimeError(AI_UNAVAILABLE_MESSAGE) from error

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=USERNAME_PROMPT,
        )
    except (errors.APIError, OSError) as error:
        raise RuntimeError(AI_UNAVAILABLE_MESSAGE) from error

    return response.text
