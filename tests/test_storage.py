import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

from taskhub.storage import (
    add_group_member,
    create_group,
    create_assigned_task,
    complete_task,
    create_user,
    get_user_by_id,
    get_task_by_id,
    get_user_by_username,
    initialize_storage,
    is_group_member,
    list_group_members,
    list_tasks_for_group,
    list_groups_for_user,
    list_users,
    open_connection,
)


def create_legacy_taskhub_database(database_path: Path) -> None:
    """Create one valid pre-calendar TaskHub database for migration tests."""
    with closing(sqlite3.connect(database_path)) as connection:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE
            );
            CREATE TABLE groups (
                group_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                creator_id INTEGER NOT NULL,
                FOREIGN KEY (creator_id) REFERENCES users (user_id)
            );
            CREATE TABLE memberships (
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (group_id, user_id),
                FOREIGN KEY (group_id) REFERENCES groups (group_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
            CREATE TABLE tasks (
                task_id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                assignee_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'incomplete'
                    CHECK (status IN ('incomplete', 'complete')),
                FOREIGN KEY (group_id, assignee_id)
                    REFERENCES memberships (group_id, user_id)
            );
            INSERT INTO users (user_id, username)
            VALUES (1, 'Alex'), (2, 'Jordan');
            INSERT INTO groups (group_id, name, creator_id)
            VALUES (1, 'Roommates', 1);
            INSERT INTO memberships (group_id, user_id)
            VALUES (1, 1), (1, 2);
            INSERT INTO tasks (
                task_id,
                group_id,
                title,
                description,
                assignee_id,
                status
            )
            VALUES (
                1,
                1,
                'Wash dishes',
                'Wash and dry the dishes',
                2,
                'complete'
            );
            """
        )
        connection.commit()


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

    def test_missing_database_is_initialized_as_empty(self):
        missing_path = (
            Path(self.temporary_directory.name) / "missing_taskhub.db"
        )

        self.assertFalse(missing_path.exists())

        initialize_storage(missing_path)

        self.assertTrue(missing_path.exists())
        self.assertEqual(list_users(missing_path), [])

    def test_invalid_database_file_is_not_replaced(self):
        invalid_path = (
            Path(self.temporary_directory.name) / "invalid_taskhub.db"
        )
        original_contents = b"This is not a SQLite database."
        invalid_path.write_bytes(original_contents)

        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            initialize_storage(invalid_path)

        self.assertEqual(invalid_path.read_bytes(), original_contents)

    def test_existing_empty_file_is_not_silently_initialized(self):
        empty_path = (
            Path(self.temporary_directory.name) / "empty_taskhub.db"
        )
        empty_path.write_bytes(b"")

        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            initialize_storage(empty_path)

        self.assertEqual(empty_path.read_bytes(), b"")

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

    def test_create_and_retrieve_assigned_task(self):
        alex_id = create_user(self.database_path, "Alex")
        jordan_id = create_user(self.database_path, "Jordan")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        add_group_member(self.database_path, group_id, jordan_id)

        task_id = create_assigned_task(
            self.database_path,
            group_id,
            "Wash dishes",
            "Wash and dry the dishes",
            jordan_id,
            "2026-07-25",
            "high",
        )

        saved_task = get_task_by_id(self.database_path, task_id)
        self.assertEqual(
            saved_task,
            {
                "task_id": task_id,
                "group_id": group_id,
                "title": "Wash dishes",
                "description": "Wash and dry the dishes",
                "assignee_id": jordan_id,
                "status": "incomplete",
                "due_date": "2026-07-25",
                "priority": "high",
            },
        )

    def test_scheduled_task_fields_are_stored_and_retrieved(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        task_id = create_assigned_task(
            self.database_path,
            group_id,
            "Buy soap",
            "Buy dish soap",
            alex_id,
            "2026-07-25",
            "high",
        )

        initialize_storage(self.database_path)
        saved_task = get_task_by_id(self.database_path, task_id)

        self.assertEqual(saved_task["due_date"], "2026-07-25")
        self.assertEqual(saved_task["priority"], "high")

    def test_storage_accepts_only_approved_priorities(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        for priority in ("low", "medium", "high"):
            with self.subTest(priority=priority):
                task_id = create_assigned_task(
                    self.database_path,
                    group_id,
                    f"Task {priority}",
                    "Test the priority constraint",
                    alex_id,
                    "2026-07-25",
                    priority,
                )
                self.assertEqual(
                    get_task_by_id(self.database_path, task_id)[
                        "priority"
                    ],
                    priority,
                )

        with self.assertRaises(sqlite3.IntegrityError):
            with open_connection(self.database_path) as connection:
                connection.execute(
                    """
                    INSERT INTO tasks (
                        group_id,
                        title,
                        description,
                        assignee_id,
                        status,
                        due_date,
                        priority
                    )
                    VALUES (?, ?, ?, ?, 'incomplete', ?, ?)
                    """,
                    (
                        group_id,
                        "Urgent task",
                        "Unsupported priority",
                        alex_id,
                        "2026-07-25",
                        "urgent",
                    ),
                )

    def test_tasks_table_rejects_missing_due_date(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        with self.assertRaises(sqlite3.IntegrityError):
            with open_connection(self.database_path) as connection:
                connection.execute(
                    """
                    INSERT INTO tasks (
                        group_id,
                        title,
                        description,
                        assignee_id,
                        status,
                        priority
                    )
                    VALUES (?, ?, ?, ?, 'incomplete', 'medium')
                    """,
                    (
                        group_id,
                        "Missing date",
                        "The due date was omitted",
                        alex_id,
                    ),
                )

    def test_legacy_tasks_are_migrated_without_data_loss(self):
        legacy_path = (
            Path(self.temporary_directory.name) / "legacy_taskhub.db"
        )
        create_legacy_taskhub_database(legacy_path)

        initialize_storage(legacy_path, date(2026, 7, 21))
        migrated_task = get_task_by_id(legacy_path, 1)

        self.assertEqual(
            migrated_task,
            {
                "task_id": 1,
                "group_id": 1,
                "title": "Wash dishes",
                "description": "Wash and dry the dishes",
                "assignee_id": 2,
                "status": "complete",
                "due_date": "2026-07-21",
                "priority": "medium",
            },
        )
        self.assertEqual(
            [member["username"] for member in list_group_members(legacy_path, 1)],
            ["Alex", "Jordan"],
        )

        initialize_storage(legacy_path, date(2026, 8, 1))
        repeated_task = get_task_by_id(legacy_path, 1)

        self.assertEqual(repeated_task["due_date"], "2026-07-21")
        self.assertEqual(repeated_task["priority"], "medium")

    def test_failed_legacy_migration_rolls_back(self):
        legacy_path = (
            Path(self.temporary_directory.name) / "blocked_legacy.db"
        )
        create_legacy_taskhub_database(legacy_path)
        with closing(sqlite3.connect(legacy_path)) as connection:
            connection.execute(
                """
                CREATE TRIGGER block_task_updates
                BEFORE UPDATE ON tasks
                BEGIN
                    SELECT RAISE(ABORT, 'Migration blocked for test');
                END
                """
            )
            connection.commit()

        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            initialize_storage(legacy_path, date(2026, 7, 21))

        with closing(sqlite3.connect(legacy_path)) as connection:
            columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(tasks)"
                ).fetchall()
            }
            saved_task = connection.execute(
                "SELECT title, status FROM tasks WHERE task_id = 1"
            ).fetchone()

        self.assertEqual(columns, {
            "task_id",
            "group_id",
            "title",
            "description",
            "assignee_id",
            "status",
        })
        self.assertEqual(saved_task, ("Wash dishes", "complete"))

    def test_assigned_task_remains_after_reconnecting(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        task_id = create_assigned_task(
            self.database_path,
            group_id,
            "Buy soap",
            "Buy dish soap",
            alex_id,
        )

        saved_task = get_task_by_id(self.database_path, task_id)

        self.assertIsNotNone(saved_task)
        self.assertEqual(saved_task["status"], "incomplete")

    def test_task_rejects_missing_group_reference(self):
        alex_id = create_user(self.database_path, "Alex")

        with self.assertRaisesRegex(LookupError, "group"):
            create_assigned_task(
                self.database_path,
                999,
                "Buy soap",
                "Buy dish soap",
                alex_id,
            )

    def test_task_rejects_missing_assignee_reference(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        with self.assertRaisesRegex(LookupError, "assignee"):
            create_assigned_task(
                self.database_path,
                group_id,
                "Buy soap",
                "Buy dish soap",
                999,
            )

    def test_task_rejects_nonmember_assignee(self):
        alex_id = create_user(self.database_path, "Alex")
        jordan_id = create_user(self.database_path, "Jordan")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        with self.assertRaisesRegex(ValueError, "group member"):
            create_assigned_task(
                self.database_path,
                group_id,
                "Buy soap",
                "Buy dish soap",
                jordan_id,
            )

    def test_tasks_table_rejects_invalid_status(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )

        with self.assertRaises(sqlite3.IntegrityError):
            with open_connection(self.database_path) as connection:
                connection.execute(
                    """
                    INSERT INTO tasks (
                        group_id,
                        title,
                        description,
                        assignee_id,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        group_id,
                        "Buy soap",
                        "Buy dish soap",
                        alex_id,
                        "waiting",
                    ),
                )

    def test_missing_task_identifier_returns_none(self):
        self.assertIsNone(get_task_by_id(self.database_path, 999))

    def test_complete_task_persists_after_reconnecting(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        task_id = create_assigned_task(
            self.database_path,
            group_id,
            "Buy soap",
            "Buy dish soap",
            alex_id,
        )

        result = complete_task(self.database_path, task_id)
        saved_task = get_task_by_id(self.database_path, task_id)

        self.assertEqual(result, "completed")
        self.assertEqual(saved_task["status"], "complete")

    def test_repeated_completion_reports_already_complete(self):
        alex_id = create_user(self.database_path, "Alex")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        task_id = create_assigned_task(
            self.database_path,
            group_id,
            "Buy soap",
            "Buy dish soap",
            alex_id,
        )
        complete_task(self.database_path, task_id)

        second_result = complete_task(self.database_path, task_id)

        self.assertEqual(second_result, "already_complete")
        self.assertEqual(
            get_task_by_id(self.database_path, task_id)["status"],
            "complete",
        )

    def test_completion_reports_missing_task(self):
        result = complete_task(self.database_path, 999)

        self.assertEqual(result, "not_found")

    def test_list_group_tasks_includes_assignee_username(self):
        alex_id = create_user(self.database_path, "Alex")
        jordan_id = create_user(self.database_path, "Jordan")
        group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        add_group_member(self.database_path, group_id, jordan_id)
        task_id = create_assigned_task(
            self.database_path,
            group_id,
            "Wash dishes",
            "Wash and dry the dishes",
            jordan_id,
            "2026-07-25",
            "low",
        )

        tasks = list_tasks_for_group(self.database_path, group_id)

        self.assertEqual(
            tasks,
            [
                {
                    "task_id": task_id,
                    "group_id": group_id,
                    "title": "Wash dishes",
                    "description": "Wash and dry the dishes",
                    "assignee_id": jordan_id,
                    "assignee_username": "Jordan",
                    "status": "incomplete",
                    "due_date": "2026-07-25",
                    "priority": "low",
                }
            ],
        )

    def test_list_group_tasks_excludes_other_groups(self):
        alex_id = create_user(self.database_path, "Alex")
        first_group_id = create_group(
            self.database_path,
            "Roommates",
            alex_id,
        )
        second_group_id = create_group(
            self.database_path,
            "Class Project",
            alex_id,
        )
        create_assigned_task(
            self.database_path,
            first_group_id,
            "Wash dishes",
            "Wash and dry the dishes",
            alex_id,
            "2026-07-25",
            "high",
        )
        create_assigned_task(
            self.database_path,
            second_group_id,
            "Write report",
            "Write the project report",
            alex_id,
            "2026-08-01",
            "low",
        )

        tasks = list_tasks_for_group(
            self.database_path,
            first_group_id,
        )

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Wash dishes")
        self.assertEqual(tasks[0]["due_date"], "2026-07-25")
        self.assertEqual(tasks[0]["priority"], "high")


if __name__ == "__main__":
    unittest.main()
