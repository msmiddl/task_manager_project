import tempfile
import unittest
from pathlib import Path

from taskhub.core import create_profile
from taskhub.storage import (
    get_user_by_id,
    initialize_storage,
    list_users,
)


class TestProfileSelectionWorkflow(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temporary_directory.name) / "test_taskhub.db"
        )
        initialize_storage(self.database_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_two_created_profiles_are_available_for_selection(self):
        alex = create_profile(self.database_path, "Alex")
        jordan = create_profile(self.database_path, "Jordan")

        profiles = list_users(self.database_path)

        self.assertEqual(
            [profile["username"] for profile in profiles],
            ["Alex", "Jordan"],
        )
        self.assertEqual(
            get_user_by_id(self.database_path, alex["user_id"]),
            alex,
        )
        self.assertEqual(
            get_user_by_id(self.database_path, jordan["user_id"]),
            jordan,
        )


if __name__ == "__main__":
    unittest.main()
