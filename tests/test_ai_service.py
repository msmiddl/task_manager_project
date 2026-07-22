"""Tests for the isolated Google AI request."""

import inspect
import os
import sys
import types
import unittest
from unittest.mock import patch

from taskhub.ai_service import (
    AI_PRIORITY_UNAVAILABLE_MESSAGE,
    AI_UNAVAILABLE_MESSAGE,
    USERNAME_PROMPT,
    request_priority_recommendation,
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

    def test_priority_request_sends_only_approved_fields(self) -> None:
        class SuccessfulClient:
            received_contents = None

            def __init__(self, api_key: str) -> None:
                self.models = self

            def generate_content(self, *, model: str, contents: str):
                SuccessfulClient.received_contents = contents
                return types.SimpleNamespace(
                    text="high\nDue soon and important.",
                )

        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True),
            patch.dict(sys.modules, fake_google_modules(SuccessfulClient)),
        ):
            response = request_priority_recommendation(
                title="Submit report",
                description="Submit the final course report",
                current_date="2026-07-22",
                due_date="2026-07-24",
                baseline_priority="high",
            )

        self.assertEqual(response, "high\nDue soon and important.")
        prompt = SuccessfulClient.received_contents
        self.assertIn("Submit report", prompt)
        self.assertIn("Submit the final course report", prompt)
        self.assertIn("2026-07-22", prompt)
        self.assertIn("2026-07-24", prompt)
        self.assertIn("high", prompt)
        for excluded_word in (
            "username",
            "group name",
            "assignee",
            "password",
            "api key",
            "task history",
        ):
            self.assertNotIn(excluded_word, prompt.lower())

        self.assertEqual(
            set(inspect.signature(request_priority_recommendation).parameters),
            {
                "title",
                "description",
                "current_date",
                "due_date",
                "baseline_priority",
            },
        )

    def test_priority_request_missing_key_is_reported_safely(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                RuntimeError,
                AI_PRIORITY_UNAVAILABLE_MESSAGE,
            ):
                request_priority_recommendation(
                    "Submit report",
                    "Submit the final course report",
                    "2026-07-22",
                    "2026-07-24",
                    "high",
                )

    def test_priority_request_service_failure_is_reported_safely(
        self,
    ) -> None:
        class FailingClient:
            def __init__(self, api_key: str) -> None:
                self.models = self

            def generate_content(self, *, model: str, contents: str):
                raise FakeAPIError("private provider details")

        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True),
            patch.dict(sys.modules, fake_google_modules(FailingClient)),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                AI_PRIORITY_UNAVAILABLE_MESSAGE,
            ):
                request_priority_recommendation(
                    "Submit report",
                    "Submit the final course report",
                    "2026-07-22",
                    "2026-07-24",
                    "high",
                )


if __name__ == "__main__":
    unittest.main()
