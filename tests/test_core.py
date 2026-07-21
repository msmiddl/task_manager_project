import tempfile
import unittest
from pathlib import Path

from taskhub.core import create_profile, validate_username
from taskhub.storage import initialize_storage, list_users


class TestProfileCore(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temporary_directory.name) / "test_taskhub.db"
        )
        initialize_storage(self.database_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_create_valid_profile(self):
        profile = create_profile(self.database_path, "Alex")

        self.assertEqual(profile["username"], "Alex")
        self.assertEqual(len(list_users(self.database_path)), 1)

    def test_profile_creation_does_not_select_current_user(self):
        profile = create_profile(self.database_path, "Alex")

        self.assertNotIn("current_user", profile)

    def test_username_length_boundaries_are_valid(self):
        validate_username("Al")
        validate_username("A" * 30)

    def test_username_outside_length_boundaries_is_rejected(self):
        for username in ("A", "A" * 31):
            with self.subTest(username_length=len(username)):
                with self.assertRaisesRegex(ValueError, "2 to 30"):
                    validate_username(username)

    def test_empty_and_whitespace_usernames_are_rejected(self):
        for username in ("", "   "):
            with self.subTest(username=repr(username)):
                with self.assertRaisesRegex(ValueError, "required"):
                    create_profile(self.database_path, username)

        self.assertEqual(list_users(self.database_path), [])

    def test_exact_duplicate_is_rejected(self):
        create_profile(self.database_path, "Alex")

        with self.assertRaisesRegex(ValueError, "already exists"):
            create_profile(self.database_path, "Alex")

        self.assertEqual(len(list_users(self.database_path)), 1)

    def test_capitalization_and_spaces_are_preserved(self):
        first_profile = create_profile(self.database_path, "Alex")
        second_profile = create_profile(self.database_path, "alex")
        spaced_profile = create_profile(self.database_path, " Alex ")

        self.assertEqual(first_profile["username"], "Alex")
        self.assertEqual(second_profile["username"], "alex")
        self.assertEqual(spaced_profile["username"], " Alex ")


if __name__ == "__main__":
    unittest.main()