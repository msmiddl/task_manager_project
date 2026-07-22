"""Isolated access to TaskHub's approved Google AI requests."""

import os


AI_UNAVAILABLE_MESSAGE = "AI username suggestions are unavailable."
AI_PRIORITY_UNAVAILABLE_MESSAGE = "AI priority recommendation is unavailable."
AI_MODEL = "gemini-3.1-flash-lite"
USERNAME_PROMPT = (
    "Return one example username containing 2 to 30 characters. "
    "Return only the username with no explanation."
)


def _request_text(contents: str, unavailable_message: str) -> str:
    """Send one isolated request and convert provider failures safely."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(unavailable_message)

    try:
        from google import genai
        from google.genai import errors
    except ImportError as error:
        raise RuntimeError(unavailable_message) from error

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=AI_MODEL,
            contents=contents,
        )
    except (errors.APIError, OSError) as error:
        raise RuntimeError(unavailable_message) from error

    return response.text


def request_username_suggestion() -> str:
    """Request and return one raw username suggestion from Google AI."""
    return _request_text(USERNAME_PROMPT, AI_UNAVAILABLE_MESSAGE)


def request_priority_recommendation(
    title: str,
    description: str,
    current_date: str,
    due_date: str,
    baseline_priority: str,
) -> str:
    """Request one raw two-line task-priority recommendation."""
    prompt = (
        "Recommend a task priority using the supplied task details.\n"
        "Respond with exactly two plain-text lines and no Markdown.\n"
        "Line 1 must be exactly low, medium, or high.\n"
        "Line 2 must be one concise reason of at most 120 characters.\n"
        "Begin with the baseline and adjust by at most one level based "
        "only on apparent importance in the task text.\n"
        "If the baseline is high, it must remain high.\n"
        "Do not claim knowledge absent from the supplied details.\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Today: {current_date}\n"
        f"Due date: {due_date}\n"
        f"Baseline priority: {baseline_priority}"
    )
    return _request_text(prompt, AI_PRIORITY_UNAVAILABLE_MESSAGE)
