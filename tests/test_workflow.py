import tempfile
import unittest
from datetime import date
from pathlib import Path

from taskhub.core import (
    add_group_member_by_username,
    complete_assigned_task,
    create_assigned_task,
    create_group,
    create_profile,
    get_group_tasks,
    get_group_tasks_for_month,
    list_user_groups,
)
from taskhub.storage import (
    get_task_by_id,
    initialize_storage,
    list_group_members,
    list_users,
)


class TestCompleteWorkflow(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temporary_directory.name) / "test_taskhub.db"
        )
        initialize_storage(self.database_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_complete_group_task_workflow_persists(self):
        alex = create_profile(self.database_path, "Alex")
        jordan = create_profile(self.database_path, "Jordan")
        current_user_id = int(alex["user_id"])

        group = create_group(
            self.database_path,
            "Roommates",
            current_user_id,
        )
        add_group_member_by_username(
            self.database_path,
            int(group["group_id"]),
            current_user_id,
            "Jordan",
        )
        task = create_assigned_task(
            self.database_path,
            int(group["group_id"]),
            current_user_id,
            "Wash dishes",
            "Wash and dry the dishes",
            int(jordan["user_id"]),
            "2026-07-25",
            "high",
        )

        with self.assertRaisesRegex(PermissionError, "assignee"):
            complete_assigned_task(
                self.database_path,
                int(task["task_id"]),
                current_user_id,
            )

        self.assertEqual(
            get_task_by_id(self.database_path, int(task["task_id"]))[
                "status"
            ],
            "incomplete",
        )

        current_user_id = int(jordan["user_id"])
        jordan_tasks = get_group_tasks(
            self.database_path,
            int(group["group_id"]),
            current_user_id,
            date(2026, 7, 25),
        )

        self.assertTrue(jordan_tasks[0]["assigned_to_current_user"])
        self.assertEqual(jordan_tasks[0]["due_date"], "2026-07-25")
        self.assertEqual(jordan_tasks[0]["priority"], "high")
        self.assertEqual(jordan_tasks[0]["date_state"], "Due today")
        calendar_tasks = get_group_tasks_for_month(
            self.database_path,
            int(group["group_id"]),
            current_user_id,
            2026,
            7,
            date(2026, 7, 25),
        )
        self.assertEqual(
            [calendar_task["task_id"] for calendar_task in calendar_tasks],
            [task["task_id"]],
        )
        self.assertEqual(
            complete_assigned_task(
                self.database_path,
                int(task["task_id"]),
                current_user_id,
            ),
            "Task marked complete.",
        )
        completed_tasks = get_group_tasks(
            self.database_path,
            int(group["group_id"]),
            current_user_id,
            date(2026, 7, 25),
        )
        self.assertEqual(completed_tasks[0]["date_state"], "")

        initialize_storage(self.database_path)

        profiles = list_users(self.database_path)
        self.assertEqual(
            [profile["username"] for profile in profiles],
            ["Alex", "Jordan"],
        )
        self.assertEqual(
            list_user_groups(self.database_path, current_user_id),
            [group],
        )
        self.assertEqual(
            [
                member["username"]
                for member in list_group_members(
                    self.database_path,
                    int(group["group_id"]),
                )
            ],
            ["Alex", "Jordan"],
        )

        saved_task = get_task_by_id(
            self.database_path,
            int(task["task_id"]),
        )
        self.assertEqual(
            saved_task,
            {
                "task_id": task["task_id"],
                "group_id": group["group_id"],
                "title": "Wash dishes",
                "description": "Wash and dry the dishes",
                "assignee_id": jordan["user_id"],
                "status": "complete",
                "due_date": "2026-07-25",
                "priority": "high",
            },
        )
        reopened_calendar_tasks = get_group_tasks_for_month(
            self.database_path,
            int(group["group_id"]),
            current_user_id,
            2026,
            7,
            date(2026, 7, 26),
        )
        self.assertEqual(len(reopened_calendar_tasks), 1)
        self.assertEqual(reopened_calendar_tasks[0]["status"], "complete")
        self.assertEqual(reopened_calendar_tasks[0]["due_date"], "2026-07-25")
        self.assertEqual(reopened_calendar_tasks[0]["priority"], "high")
        self.assertEqual(reopened_calendar_tasks[0]["date_state"], "")


if __name__ == "__main__":
    unittest.main()
