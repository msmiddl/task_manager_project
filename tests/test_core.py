import tempfile
import unittest
from datetime import date
from pathlib import Path

from taskhub.core import (
    add_group_member_by_username,
    complete_assigned_task,
    create_group,
    create_assigned_task,
    create_profile,
    get_group_tasks,
    get_group_tasks_for_month,
    get_assigned_incomplete_tasks,
    list_user_groups,
    validate_group_name,
    validate_ai_username_suggestion,
    validate_task_schedule,
    validate_task_fields,
    validate_username,
)
from taskhub.storage import (
    add_group_member,
    initialize_storage,
    get_task_by_id,
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


class TestAIUsernameSuggestionCore(unittest.TestCase):
    def test_valid_unused_suggestion_is_returned(self):
        suggestion = validate_ai_username_suggestion(
            "SunnyCoder",
            ["Alex", "Jordan"],
        )

        self.assertEqual(suggestion, "SunnyCoder")

    def test_blank_and_whitespace_suggestions_are_rejected(self):
        for suggestion in ("", "   "):
            with self.subTest(suggestion=repr(suggestion)):
                with self.assertRaisesRegex(ValueError, "unavailable"):
                    validate_ai_username_suggestion(suggestion, [])

    def test_suggestions_outside_length_boundaries_are_rejected(self):
        for suggestion in ("A", "A" * 31):
            with self.subTest(suggestion_length=len(suggestion)):
                with self.assertRaisesRegex(ValueError, "unavailable"):
                    validate_ai_username_suggestion(suggestion, [])

    def test_exact_duplicate_suggestion_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unavailable"):
            validate_ai_username_suggestion("Alex", ["Alex", "Jordan"])

    def test_capitalization_is_significant_for_duplicates(self):
        suggestion = validate_ai_username_suggestion("alex", ["Alex"])

        self.assertEqual(suggestion, "alex")


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


class TestAssignedTaskCore(unittest.TestCase):
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
        add_group_member(
            self.database_path,
            self.group["group_id"],
            self.jordan["user_id"],
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_task_field_boundaries_are_valid(self):
        validate_task_fields("A", "B")
        validate_task_fields("A" * 20, "B" * 100)

    def test_valid_due_dates_are_accepted(self):
        for due_date in (
            "2020-01-01",
            "2026-07-21",
            "2030-12-31",
            "2028-02-29",
        ):
            with self.subTest(due_date=due_date):
                validate_task_schedule(due_date, "medium")

    def test_missing_due_date_is_rejected(self):
        for due_date in (None, ""):
            with self.subTest(due_date=due_date):
                with self.assertRaisesRegex(ValueError, "due date.*required"):
                    validate_task_schedule(due_date, "medium")

    def test_invalid_due_dates_are_rejected(self):
        for due_date in (
            "2026-02-30",
            "2026-2-3",
            "07/25/2026",
            "20260725",
            "not-a-date",
        ):
            with self.subTest(due_date=due_date):
                with self.assertRaisesRegex(ValueError, "invalid due date"):
                    validate_task_schedule(due_date, "medium")

    def test_approved_priorities_are_accepted(self):
        for priority in ("low", "medium", "high"):
            with self.subTest(priority=priority):
                validate_task_schedule("2026-07-25", priority)

    def test_missing_priority_is_rejected(self):
        for priority in (None, ""):
            with self.subTest(priority=priority):
                with self.assertRaisesRegex(ValueError, "priority.*required"):
                    validate_task_schedule("2026-07-25", priority)

    def test_unsupported_priorities_are_rejected(self):
        for priority in ("urgent", "Medium", "HIGH", " "):
            with self.subTest(priority=priority):
                with self.assertRaisesRegex(ValueError, "invalid priority"):
                    validate_task_schedule("2026-07-25", priority)

    def test_invalid_schedule_does_not_create_a_task(self):
        invalid_schedules = (
            (None, "medium", "due date"),
            ("2026-07-25", None, "priority"),
            ("2026-02-30", "medium", "due date"),
            ("2026-07-25", "urgent", "priority"),
        )

        for due_date, priority, field_name in invalid_schedules:
            with self.subTest(field=field_name):
                with self.assertRaisesRegex(ValueError, field_name):
                    create_assigned_task(
                        self.database_path,
                        self.group["group_id"],
                        self.alex["user_id"],
                        "Wash dishes",
                        "Wash and dry the dishes",
                        self.jordan["user_id"],
                        due_date,
                        priority,
                    )

        self.assertIsNone(get_task_by_id(self.database_path, 1))

    def test_task_fields_over_maximum_are_rejected(self):
        invalid_fields = (
            ("A" * 21, "Description", "title"),
            ("Title", "B" * 101, "description"),
        )

        for title, description, field_name in invalid_fields:
            with self.subTest(field=field_name):
                with self.assertRaisesRegex(ValueError, field_name):
                    validate_task_fields(title, description)

    def test_empty_and_whitespace_task_fields_are_rejected(self):
        invalid_fields = (
            ("", "Description", "title"),
            ("   ", "Description", "title"),
            ("Title", "", "description"),
            ("Title", "   ", "description"),
        )

        for title, description, field_name in invalid_fields:
            with self.subTest(field=field_name):
                with self.assertRaisesRegex(ValueError, field_name):
                    create_assigned_task(
                        self.database_path,
                        self.group["group_id"],
                        self.alex["user_id"],
                        title,
                        description,
                        self.jordan["user_id"],
                    )

        self.assertIsNone(get_task_by_id(self.database_path, 1))

    def test_missing_assignee_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "assignee"):
            create_assigned_task(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                "Wash dishes",
                "Wash and dry the dishes",
                None,
            )

        self.assertIsNone(get_task_by_id(self.database_path, 1))

    def test_nonmember_assignee_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "group member"):
            create_assigned_task(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                "Wash dishes",
                "Wash and dry the dishes",
                self.taylor["user_id"],
                "2026-07-25",
                "medium",
            )

        self.assertIsNone(get_task_by_id(self.database_path, 1))

    def test_nonmember_creator_is_rejected(self):
        with self.assertRaisesRegex(PermissionError, "group member"):
            create_assigned_task(
                self.database_path,
                self.group["group_id"],
                self.taylor["user_id"],
                "Wash dishes",
                "Wash and dry the dishes",
                self.jordan["user_id"],
                "2026-07-25",
                "medium",
            )

        self.assertIsNone(get_task_by_id(self.database_path, 1))

    def test_one_member_group_allows_self_assignment(self):
        solo_group = create_group(
            self.database_path,
            "Solo",
            self.taylor["user_id"],
        )

        task = create_assigned_task(
            self.database_path,
            solo_group["group_id"],
            self.taylor["user_id"],
            "Buy soap",
            "Buy dish soap",
            self.taylor["user_id"],
            "2026-07-25",
            "low",
        )

        self.assertEqual(task["assignee_id"], self.taylor["user_id"])
        self.assertEqual(task["status"], "incomplete")

    def test_valid_task_is_created_incomplete(self):
        task = create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Wash dishes",
            "Wash and dry the dishes",
            self.jordan["user_id"],
            "2026-07-25",
            "high",
        )

        self.assertEqual(task["group_id"], self.group["group_id"])
        self.assertEqual(task["title"], "Wash dishes")
        self.assertEqual(task["description"], "Wash and dry the dishes")
        self.assertEqual(task["assignee_id"], self.jordan["user_id"])
        self.assertEqual(task["status"], "incomplete")
        self.assertEqual(task["due_date"], "2026-07-25")
        self.assertEqual(task["priority"], "high")

    def test_group_tasks_mark_only_current_users_assignments(self):
        create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Buy soap",
            "Buy dish soap",
            self.alex["user_id"],
            "2026-07-24",
            "medium",
        )
        create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Wash dishes",
            "Wash and dry the dishes",
            self.jordan["user_id"],
            "2026-07-25",
            "high",
        )

        tasks = get_group_tasks(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
        )

        self.assertTrue(tasks[0]["assigned_to_current_user"])
        self.assertFalse(tasks[1]["assigned_to_current_user"])
        self.assertEqual(tasks[0]["assignee_username"], "Alex")
        self.assertEqual(tasks[1]["assignee_username"], "Jordan")

    def test_group_tasks_calculate_incomplete_task_date_states(self):
        schedules = (
            ("Past task", "2026-07-20", "Overdue"),
            ("Today task", "2026-07-21", "Due today"),
            ("Future task", "2026-07-22", ""),
        )
        for title, due_date, expected_state in schedules:
            with self.subTest(title=title):
                create_assigned_task(
                    self.database_path,
                    self.group["group_id"],
                    self.alex["user_id"],
                    title,
                    "Check its calculated date state",
                    self.alex["user_id"],
                    due_date,
                    "medium",
                )

        tasks = get_group_tasks(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            date(2026, 7, 21),
        )

        self.assertEqual(
            [task["date_state"] for task in tasks],
            [state for _, _, state in schedules],
        )

    def test_completed_tasks_have_no_date_state(self):
        for title, due_date in (
            ("Past complete", "2026-07-20"),
            ("Today complete", "2026-07-21"),
        ):
            task = create_assigned_task(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                title,
                "Complete before checking the date state",
                self.alex["user_id"],
                due_date,
                "high",
            )
            complete_assigned_task(
                self.database_path,
                task["task_id"],
                self.alex["user_id"],
            )

        tasks = get_group_tasks(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            date(2026, 7, 21),
        )

        self.assertEqual(
            [task["date_state"] for task in tasks],
            ["", ""],
        )

    def test_date_state_is_recalculated_for_the_supplied_date(self):
        create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Boundary task",
            "Recalculate without changing storage",
            self.alex["user_id"],
            "2026-07-22",
            "low",
        )

        due_today = get_group_tasks(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            date(2026, 7, 22),
        )
        overdue = get_group_tasks(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            date(2026, 7, 23),
        )

        self.assertEqual(due_today[0]["date_state"], "Due today")
        self.assertEqual(overdue[0]["date_state"], "Overdue")
        self.assertNotIn(
            "date_state",
            get_task_by_id(self.database_path, due_today[0]["task_id"]),
        )

    def test_empty_group_has_no_calculated_task_states(self):
        self.assertEqual(
            get_group_tasks(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                date(2026, 7, 21),
            ),
            [],
        )

    def test_calendar_month_returns_tasks_with_required_details(self):
        incomplete_task = create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Buy soap",
            "Buy dish soap",
            self.alex["user_id"],
            "2026-07-10",
            "low",
        )
        completed_task = create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Wash dishes",
            "Wash and dry the dishes",
            self.jordan["user_id"],
            "2026-07-25",
            "high",
        )
        complete_assigned_task(
            self.database_path,
            completed_task["task_id"],
            self.jordan["user_id"],
        )

        tasks = get_group_tasks_for_month(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            2026,
            7,
            date(2026, 7, 15),
        )

        self.assertEqual(
            [task["task_id"] for task in tasks],
            [incomplete_task["task_id"], completed_task["task_id"]],
        )
        self.assertEqual(tasks[0]["priority"], "low")
        self.assertEqual(tasks[0]["assignee_username"], "Alex")
        self.assertEqual(tasks[0]["status"], "incomplete")
        self.assertEqual(tasks[1]["status"], "complete")

    def test_calendar_month_observes_year_and_month_boundaries(self):
        for title, due_date in (
            ("Year end", "2026-12-31"),
            ("Year start", "2027-01-01"),
            ("Leap day", "2028-02-29"),
        ):
            create_assigned_task(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                title,
                "Check a calendar boundary",
                self.alex["user_id"],
                due_date,
                "medium",
            )

        december = get_group_tasks_for_month(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            2026,
            12,
            date(2026, 12, 1),
        )
        january = get_group_tasks_for_month(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            2027,
            1,
            date(2027, 1, 1),
        )
        leap_february = get_group_tasks_for_month(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            2028,
            2,
            date(2028, 2, 1),
        )

        self.assertEqual([task["title"] for task in december], ["Year end"])
        self.assertEqual([task["title"] for task in january], ["Year start"])
        self.assertEqual(
            [task["title"] for task in leap_february],
            ["Leap day"],
        )

    def test_calendar_month_returns_empty_list_when_no_tasks_are_due(self):
        self.assertEqual(
            get_group_tasks_for_month(
                self.database_path,
                self.group["group_id"],
                self.alex["user_id"],
                2026,
                7,
                date(2026, 7, 1),
            ),
            [],
        )

    def test_calendar_month_is_group_scoped_and_read_only(self):
        task = create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Roommate task",
            "This belongs to Roommates",
            self.alex["user_id"],
            "2026-07-10",
            "medium",
        )
        other_group = create_group(
            self.database_path,
            "Class Project",
            self.alex["user_id"],
        )
        create_assigned_task(
            self.database_path,
            other_group["group_id"],
            self.alex["user_id"],
            "Class task",
            "This belongs to Class Project",
            self.alex["user_id"],
            "2026-07-11",
            "high",
        )
        saved_before = get_task_by_id(
            self.database_path,
            task["task_id"],
        )

        tasks = get_group_tasks_for_month(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            2026,
            7,
            date(2026, 7, 1),
        )

        self.assertEqual([item["title"] for item in tasks], ["Roommate task"])
        self.assertEqual(
            get_task_by_id(self.database_path, task["task_id"]),
            saved_before,
        )

    def test_nonmember_cannot_retrieve_calendar_month(self):
        with self.assertRaisesRegex(PermissionError, "group member"):
            get_group_tasks_for_month(
                self.database_path,
                self.group["group_id"],
                self.taylor["user_id"],
                2026,
                7,
                date(2026, 7, 1),
            )

    def test_nonmember_cannot_retrieve_group_tasks(self):
        with self.assertRaisesRegex(PermissionError, "group member"):
            get_group_tasks(
                self.database_path,
                self.group["group_id"],
                self.taylor["user_id"],
            )

    def test_assignee_can_complete_incomplete_task(self):
        task = create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Wash dishes",
            "Wash and dry the dishes",
            self.jordan["user_id"],
            "2026-07-25",
            "medium",
        )

        message = complete_assigned_task(
            self.database_path,
            task["task_id"],
            self.jordan["user_id"],
        )

        self.assertEqual(message, "Task marked complete.")
        self.assertEqual(
            get_task_by_id(
                self.database_path,
                task["task_id"],
            )["status"],
            "complete",
        )

    def test_nonassignee_cannot_complete_task(self):
        task = create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Wash dishes",
            "Wash and dry the dishes",
            self.jordan["user_id"],
            "2026-07-25",
            "medium",
        )

        with self.assertRaisesRegex(PermissionError, "assignee"):
            complete_assigned_task(
                self.database_path,
                task["task_id"],
                self.alex["user_id"],
            )

        self.assertEqual(
            get_task_by_id(
                self.database_path,
                task["task_id"],
            )["status"],
            "incomplete",
        )

    def test_missing_task_cannot_be_completed(self):
        with self.assertRaisesRegex(LookupError, "not found"):
            complete_assigned_task(
                self.database_path,
                999,
                self.alex["user_id"],
            )

    def test_inaccessible_group_task_cannot_be_completed(self):
        private_group = create_group(
            self.database_path,
            "Private",
            self.taylor["user_id"],
        )
        private_task = create_assigned_task(
            self.database_path,
            private_group["group_id"],
            self.taylor["user_id"],
            "Private task",
            "Only Taylor can access this",
            self.taylor["user_id"],
            "2026-07-25",
            "low",
        )

        with self.assertRaisesRegex(PermissionError, "access"):
            complete_assigned_task(
                self.database_path,
                private_task["task_id"],
                self.jordan["user_id"],
            )

        self.assertEqual(
            get_task_by_id(
                self.database_path,
                private_task["task_id"],
            )["status"],
            "incomplete",
        )

    def test_repeated_completion_returns_information(self):
        task = create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Wash dishes",
            "Wash and dry the dishes",
            self.jordan["user_id"],
            "2026-07-25",
            "medium",
        )
        complete_assigned_task(
            self.database_path,
            task["task_id"],
            self.jordan["user_id"],
        )

        second_message = complete_assigned_task(
            self.database_path,
            task["task_id"],
            self.jordan["user_id"],
        )

        self.assertEqual(second_message, "Task is already complete.")

    def test_no_assigned_incomplete_tasks_returns_empty_list(self):
        create_assigned_task(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
            "Wash dishes",
            "Wash and dry the dishes",
            self.jordan["user_id"],
            "2026-07-25",
            "medium",
        )

        tasks = get_assigned_incomplete_tasks(
            self.database_path,
            self.group["group_id"],
            self.alex["user_id"],
        )

        self.assertEqual(tasks, [])


if __name__ == "__main__":
    unittest.main()
