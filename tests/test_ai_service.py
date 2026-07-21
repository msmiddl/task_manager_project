"""Tests for the isolated Google AI request."""

import os
import sys
import types
import unittest
from unittest.mock import patch

from taskhub.ai_service import (
    AI_UNAVAILABLE_MESSAGE,
    USERNAME_PROMPT,
    request_username_suggestion,
)


class FakeAPIError(Exception):
    """Stand-in for a Google service error."""


def fake_google_modules(client_class: type) -> dict[str, types.ModuleType]:
    """Build small fake Google modules so tests never contact the internet."""
    google_module = types.ModuleType("google")
    genai_module = types.ModuleType("google.genai")
    errors_module = types.ModuleType("google.genai.errors")

    genai_module.Client = client_class
    errors_module.APIError = FakeAPIError
    genai_module.errors = errors_module
    google_module.genai = genai_module

    return {
        "google": google_module,
        "google.genai": genai_module,
        "google.genai.errors": errors_module,
    }


class TestAIService(unittest.TestCase):
    def test_returns_raw_username_text(self) -> None:
        class SuccessfulClient:
            received_api_key = None
            received_model = None
            received_contents = None

            def __init__(self, api_key: str) -> None:
                SuccessfulClient.received_api_key = api_key
                self.models = self

            def generate_content(self, *, model: str, contents: str):
                SuccessfulClient.received_model = model
                SuccessfulClient.received_contents = contents
                return types.SimpleNamespace(text="  SunnyCoder  ")

        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True),
            patch.dict(sys.modules, fake_google_modules(SuccessfulClient)),
        ):
            suggestion = request_username_suggestion()

        self.assertEqual(suggestion, "  SunnyCoder  ")
        self.assertEqual(SuccessfulClient.received_api_key, "test-key")
        self.assertEqual(
            SuccessfulClient.received_model,
            "gemini-3.1-flash-lite",
        )
        self.assertEqual(SuccessfulClient.received_contents, USERNAME_PROMPT)
        self.assertNotIn("password", USERNAME_PROMPT.lower())

    def test_missing_api_key_is_reported_safely(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, AI_UNAVAILABLE_MESSAGE):
                request_username_suggestion()

    def test_service_failure_is_reported_safely(self) -> None:
        class FailingClient:
            def __init__(self, api_key: str) -> None:
                self.models = self

            def generate_content(self, *, model: str, contents: str):
                raise FakeAPIError("private provider details")

        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True),
            patch.dict(sys.modules, fake_google_modules(FailingClient)),
        ):
            with self.assertRaisesRegex(RuntimeError, AI_UNAVAILABLE_MESSAGE):
                request_username_suggestion()


if __name__ == "__main__":
    unittest.main()
