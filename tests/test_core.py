import tempfile
import unittest
from pathlib import Path

from taskhub.core import (
    add_group_member_by_username,
    create_group,
    create_profile,
    list_user_groups,
    validate_group_name,
    validate_username,
)
from taskhub.storage import (
    add_group_member,
    initialize_storage,
    list_group_members,
    list_users,
)


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


class TestGroupCore(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temporary_directory.name) / "test_taskhub.db"
        )
        initialize_storage(self.database_path)
        self.alex = create_profile(self.database_path, "Alex")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_group_name_length_boundaries_are_valid(self):
        validate_group_name("AB")
        validate_group_name("A" * 25)

    def test_group_name_outside_boundaries_is_rejected(self):
        for name in ("A", "A" * 26):
            with self.subTest(name_length=len(name)):
                with self.assertRaisesRegex(ValueError, "2 to 25"):
                    validate_group_name(name)

    def test_empty_and_whitespace_group_names_are_rejected(self):
        for name in ("", "   "):
            with self.subTest(name=repr(name)):
                with self.assertRaisesRegex(ValueError, "required"):
                    create_group(
                        self.database_path,
                        name,
                        self.alex["user_id"],
                    )

        self.assertEqual(
            list_user_groups(
                self.database_path,
                self.alex["user_id"],
            ),
            [],
        )

    def test_create_group_makes_current_user_creator_and_member(self):
        group = create_group(
            self.database_path,
            "Roommates",
            self.alex["user_id"],
        )

        self.assertEqual(group["name"], "Roommates")
        self.assertEqual(group["creator_id"], self.alex["user_id"])
        self.assertEqual(
            list_user_groups(
                self.database_path,
                self.alex["user_id"],
            ),
            [group],
        )

    def test_exact_duplicate_group_name_is_rejected(self):
        create_group(
            self.database_path,
            "Roommates",
            self.alex["user_id"],
        )

        with self.assertRaisesRegex(ValueError, "already exists"):
            create_group(
                self.database_path,
                "Roommates",
                self.alex["user_id"],
            )

        self.assertEqual(
            len(
                list_user_groups(
                    self.database_path,
                    self.alex["user_id"],
                )
            ),
            1,
        )

    def test_capitalization_and_spaces_are_preserved(self):
        first_group = create_group(
            self.database_path,
            "Roommates",
            self.alex["user_id"],
        )
        second_group = create_group(
            self.database_path,
            "roommates",
            self.alex["user_id"],
        )
        spaced_group = create_group(
            self.database_path,
            " Roommates ",
            self.alex["user_id"],
        )

        self.assertEqual(first_group["name"], "Roommates")
        self.assertEqual(second_group["name"], "roommates")
        self.assertEqual(spaced_group["name"], " Roommates ")

    def test_group_lists_include_only_selected_users_groups(self):
        jordan = create_profile(self.database_path, "Jordan")
        alex_group = create_group(
            self.database_path,
            "Roommates",
            self.alex["user_id"],
        )
        jordan_group = create_group(
            self.database_path,
            "Class Project",
            jordan["user_id"],
        )

        self.assertEqual(
            list_user_groups(
                self.database_path,
                self.alex["user_id"],
            ),
            [alex_group],
        )
        self.assertEqual(
            list_user_groups(
                self.database_path,
                jordan["user_id"],
            ),
            [jordan_group],
        )


class TestGroupMemberCore(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temporary_directory.name) / "test_taskhub.db"
        )
        initialize_storage(self.database_path)
        self.alex = create_profile(self.database_path, "Alex")
        self.jordan = create_profile(self.database_path, "Jordan")
        self.taylor = create_profile(self.database_path, "Taylor")
        self.group = create_group(
            self.database_path,
            "Roommates",
            self.alex["user_id"],
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def member_names(self):
        members = list_group_members(
            self.database_path,
            self.group["group_id"],
        )
        return [member["username"] for member in members]

    def test_creator_adds_existing_user_by_exact_username(self):
        added_member = add_group_member_by_username(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Jordan",
        )

        self.assertEqual(added_member, self.jordan)
        self.assertEqual(self.member_names(), ["Alex", "Jordan"])

    def test_wrong_capitalization_is_rejected(self):
        with self.assertRaisesRegex(LookupError, "not found"):
            add_group_member_by_username(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                "jordan",
            )

        self.assertEqual(self.member_names(), ["Alex"])

    def test_missing_username_is_rejected(self):
        with self.assertRaisesRegex(LookupError, "not found"):
            add_group_member_by_username(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                "Unknown",
            )

        self.assertEqual(self.member_names(), ["Alex"])

    def test_duplicate_member_is_rejected(self):
        add_group_member_by_username(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Jordan",
        )

        with self.assertRaisesRegex(ValueError, "already a member"):
            add_group_member_by_username(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                "Jordan",
            )

        self.assertEqual(self.member_names(), ["Alex", "Jordan"])

    def test_creator_cannot_be_added_twice(self):
        with self.assertRaisesRegex(ValueError, "already a member"):
            add_group_member_by_username(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                "Alex",
            )

        self.assertEqual(self.member_names(), ["Alex"])

    def test_noncreator_cannot_add_member(self):
        add_group_member(
            self.database_path,
            self.group["group_id"],
            self.jordan["user_id"],
        )

        with self.assertRaisesRegex(PermissionError, "creator"):
            add_group_member_by_username(
                self.database_path,
                self.group["group_id"],
                self.jordan["user_id"],
                "Taylor",
            )

        self.assertEqual(self.member_names(), ["Alex", "Jordan"])


if __name__ == "__main__":
    unittest.main()
