import tempfile
import unittest
from pathlib import Path

from taskhub.storage import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    initialize_storage,
    list_users,
    open_connection,
)


class TestUserStorage(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temporary_directory.name) / "test_taskhub.db"
        )
        initialize_storage(self.database_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_create_and_retrieve_user(self):
        user_id = create_user(self.database_path, "Alex")

        saved_user = get_user_by_username(self.database_path, "Alex")

        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user["user_id"], user_id)
        self.assertEqual(saved_user["username"], "Alex")

    def test_new_database_has_no_users(self):
        self.assertEqual(list_users(self.database_path), [])

    def test_exact_duplicate_username_is_rejected(self):
        create_user(self.database_path, "Alex")

        with self.assertRaisesRegex(ValueError, "already exists"):
            create_user(self.database_path, "Alex")

        self.assertEqual(len(list_users(self.database_path)), 1)

    def test_capitalization_is_significant(self):
        create_user(self.database_path, "Alex")
        create_user(self.database_path, "alex")

        usernames = [
            user["username"] for user in list_users(self.database_path)
        ]

        self.assertEqual(usernames, ["Alex", "alex"])

    def test_user_remains_after_reconnecting(self):
        create_user(self.database_path, "Alex")

        saved_user = get_user_by_username(self.database_path, "Alex")

        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user["username"], "Alex")

    def test_missing_username_returns_none(self):
        self.assertIsNone(
            get_user_by_username(self.database_path, "Unknown")
        )

    def test_retrieve_user_by_identifier(self):
        user_id = create_user(self.database_path, "Alex")

        saved_user = get_user_by_id(self.database_path, user_id)

        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user["user_id"], user_id)
        self.assertEqual(saved_user["username"], "Alex")

    def test_missing_user_identifier_returns_none(self):
        self.assertIsNone(get_user_by_id(self.database_path, 999))

    def test_foreign_keys_are_enabled(self):
        with open_connection(self.database_path) as connection:
            result = connection.execute("PRAGMA foreign_keys").fetchone()

        self.assertEqual(result[0], 1)


if __name__ == "__main__":
    unittest.main()
