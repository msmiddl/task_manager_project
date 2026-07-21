import tempfile
import unittest
from pathlib import Path

from taskhub.storage import (
    add_group_member,
    create_group,
    create_user,
    get_user_by_id,
    get_user_by_username,
    initialize_storage,
    is_group_member,
    list_group_members,
    list_groups_for_user,
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

    def test_create_group_adds_creator_membership(self):
        alex_id = create_user(self.database_path, "Alex")

        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        self.assertEqual(
            list_groups_for_user(self.database_path, alex_id),
            [
                {
                    "group_id": group_id,
                    "name": "Roommates",
                    "creator_id": alex_id,
                }
            ],
        )

    def test_group_remains_after_reconnecting(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        saved_groups = list_groups_for_user(
            self.database_path,
            alex_id,
        )

        self.assertEqual(saved_groups[0]["group_id"], group_id)
        self.assertEqual(saved_groups[0]["name"], "Roommates")

    def test_exact_duplicate_group_name_is_rejected(self):
        alex_id = create_user(self.database_path, "Alex")
        create_group(self.database_path, "Roommates", alex_id)

        with self.assertRaisesRegex(ValueError, "already exists"):
            create_group(self.database_path, "Roommates", alex_id)

        self.assertEqual(
            len(list_groups_for_user(self.database_path, alex_id)),
            1,
        )

    def test_group_name_comparison_is_case_sensitive(self):
        alex_id = create_user(self.database_path, "Alex")
        create_group(self.database_path, "Roommates", alex_id)
        create_group(self.database_path, "roommates", alex_id)

        group_names = [
            group["name"]
            for group in list_groups_for_user(
                self.database_path,
                alex_id,
            )
        ]

        self.assertEqual(group_names, ["Roommates", "roommates"])

    def test_group_creation_rejects_missing_creator(self):
        with self.assertRaisesRegex(LookupError, "creator"):
            create_group(self.database_path, "Roommates", 999)

    def test_membership_failure_rolls_back_group(self):
        alex_id = create_user(self.database_path, "Alex")

        with open_connection(self.database_path) as connection:
            connection.execute("DROP TABLE memberships")
            connection.commit()

        with self.assertRaises(RuntimeError):
            create_group(self.database_path, "Roommates", alex_id)

        with open_connection(self.database_path) as connection:
            group_count = connection.execute(
                "SELECT COUNT(*) FROM groups"
            ).fetchone()[0]

        self.assertEqual(group_count, 0)

    def test_add_and_list_group_member(self):
        alex_id = create_user(self.database_path, "Alex")
        jordan_id = create_user(self.database_path, "Jordan")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        add_group_member(self.database_path, group_id, jordan_id)

        self.assertTrue(
            is_group_member(self.database_path, group_id, alex_id)
        )
        self.assertTrue(
            is_group_member(self.database_path, group_id, jordan_id)
        )
        self.assertEqual(
            list_group_members(self.database_path, group_id),
            [
                {"user_id": alex_id, "username": "Alex"},
                {"user_id": jordan_id, "username": "Jordan"},
            ],
        )

    def test_duplicate_group_membership_is_rejected(self):
        alex_id = create_user(self.database_path, "Alex")
        jordan_id = create_user(self.database_path, "Jordan")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        add_group_member(self.database_path, group_id, jordan_id)

        with self.assertRaisesRegex(ValueError, "already a member"):
            add_group_member(self.database_path, group_id, jordan_id)

        self.assertEqual(
            len(list_group_members(self.database_path, group_id)),
            2,
        )

    def test_membership_rejects_missing_user_reference(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        with self.assertRaisesRegex(LookupError, "user"):
            add_group_member(self.database_path, group_id, 999)

    def test_membership_rejects_missing_group_reference(self):
        jordan_id = create_user(self.database_path, "Jordan")

        with self.assertRaisesRegex(LookupError, "group"):
            add_group_member(self.database_path, 999, jordan_id)

    def test_group_membership_remains_after_reconnecting(self):
        alex_id = create_user(self.database_path, "Alex")
        jordan_id = create_user(self.database_path, "Jordan")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        add_group_member(self.database_path, group_id, jordan_id)

        saved_members = list_group_members(
            self.database_path,
            group_id,
        )

        self.assertEqual(
            [member["username"] for member in saved_members],
            ["Alex", "Jordan"],
        )

    def test_nonmember_check_returns_false(self):
        alex_id = create_user(self.database_path, "Alex")
        jordan_id = create_user(self.database_path, "Jordan")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        self.assertFalse(
            is_group_member(self.database_path, group_id, jordan_id)
        )


if __name__ == "__main__":
    unittest.main()
