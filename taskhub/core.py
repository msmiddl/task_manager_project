from datetime import date

from taskhub import storage
from taskhub.storage import DatabasePath, UserRecord


def validate_username(username: str) -> None:
    """Raise a clear error when a username breaks an approved rule."""
    if not username or username.isspace():
        raise ValueError("A username is required.")

    if len(username) < 2 or len(username) > 30:
        raise ValueError("The username must contain 2 to 30 characters.")


def validate_ai_username_suggestion(
    raw_suggestion: str,
    existing_usernames: list[str],
) -> str:
    """Return a valid unused AI suggestion or raise a safe error."""
    unavailable_message = "AI username suggestion is unavailable."

    try:
        validate_username(raw_suggestion)
    except ValueError as error:
        raise ValueError(unavailable_message) from error

    if raw_suggestion in existing_usernames:
        raise ValueError(unavailable_message)

    return raw_suggestion


def create_profile(
    database_path: DatabasePath,
    username: str,
) -> UserRecord:
    """Validate and save one profile without selecting a current user."""
    validate_username(username)

    if storage.get_user_by_username(database_path, username) is not None:
        raise ValueError("That exact username already exists.")

    user_id = storage.create_user(database_path, username)
    return {"user_id": user_id, "username": username}


def validate_group_name(name: str) -> None:
    """Raise a clear error when a group name breaks an approved rule."""
    if not name or name.isspace():
        raise ValueError("A group name is required.")

    if len(name) < 2 or len(name) > 25:
        raise ValueError("The group name must contain 2 to 25 characters.")


def create_group(
    database_path: DatabasePath,
    name: str,
    current_user_id: int,
) -> storage.GroupRecord:
    """Validate and save a group for the selected current user."""
    validate_group_name(name)

    group_id = storage.create_group(
        database_path,
        name,
        current_user_id,
    )
    return {
        "group_id": group_id,
        "name": name,
        "creator_id": current_user_id,
    }


def list_user_groups(
    database_path: DatabasePath,
    current_user_id: int,
) -> list[storage.GroupRecord]:
    """Return only groups containing the selected current user."""
    return storage.list_groups_for_user(database_path, current_user_id)


def add_group_member_by_username(
    database_path: DatabasePath,
    group_id: int,
    current_user_id: int,
    username: str,
) -> UserRecord:
    """Let a group creator add one profile by exact username."""
    accessible_groups = storage.list_groups_for_user(
        database_path,
        current_user_id,
    )
    selected_group = next(
        (
            group
            for group in accessible_groups
            if group["group_id"] == group_id
        ),
        None,
    )

    if (
        selected_group is None
        or selected_group["creator_id"] != current_user_id
    ):
        raise PermissionError("Only the group creator can add members.")

    user = storage.get_user_by_username(database_path, username)
    if user is None:
        raise LookupError("That exact username was not found.")

    if storage.is_group_member(
        database_path,
        group_id,
        int(user["user_id"]),
    ):
        raise ValueError("That user is already a member of the group.")

    storage.add_group_member(
        database_path,
        group_id,
        int(user["user_id"]),
    )
    return user


def validate_task_fields(title: str, description: str) -> None:
    """Raise a clear error when task text breaks an approved rule."""
    if not title or title.isspace():
        raise ValueError("A task title is required.")
    if len(title) > 20:
        raise ValueError("The task title must contain 1 to 20 characters.")

    if not description or description.isspace():
        raise ValueError("A task description is required.")
    if len(description) > 100:
        raise ValueError(
            "The task description must contain 1 to 100 characters."
        )


def validate_task_schedule(
    due_date: str | None,
    priority: str | None,
) -> None:
    """Raise a clear error for invalid scheduling values."""
    if due_date is None or due_date == "":
        raise ValueError("A task due date is required.")

    try:
        parsed_due_date = date.fromisoformat(due_date)
    except (TypeError, ValueError) as error:
        raise ValueError("The task has an invalid due date.") from error

    if parsed_due_date.isoformat() != due_date:
        raise ValueError("The task has an invalid due date.")

    if priority is None or priority == "":
        raise ValueError("A task priority is required.")

    if priority not in ("low", "medium", "high"):
        raise ValueError("The task has an invalid priority.")


def calculate_baseline_priority(
    due_date: str | None,
    current_date: date,
) -> str:
    """Return a local priority baseline for a valid task due date."""
    validate_task_schedule(due_date, "medium")

    parsed_due_date = date.fromisoformat(str(due_date))
    days_until_due = (parsed_due_date - current_date).days

    if days_until_due <= 3:
        return "high"
    if days_until_due <= 7:
        return "medium"
    return "low"


def prepare_priority_recommendation_request(
    title: str,
    description: str,
    due_date: str | None,
    current_date: date,
) -> dict[str, str]:
    """Validate and return only fields approved for the AI request."""
    validate_task_fields(title, description)
    baseline_priority = calculate_baseline_priority(
        due_date,
        current_date,
    )
    return {
        "title": title,
        "description": description,
        "current_date": current_date.isoformat(),
        "due_date": str(due_date),
        "baseline_priority": baseline_priority,
    }


def validate_ai_priority_recommendation(
    raw_response: str,
    baseline_priority: str,
) -> dict[str, str]:
    """Return one normalized, allowed AI priority recommendation."""
    unavailable_message = "AI priority recommendation is unavailable."
    if not isinstance(raw_response, str):
        raise ValueError(unavailable_message)

    response_lines = [
        line.strip()
        for line in raw_response.splitlines()
        if line.strip()
    ]
    if len(response_lines) != 2:
        raise ValueError(unavailable_message)

    priority = response_lines[0].lower()
    reason = response_lines[1]
    priority_levels = {"low": 0, "medium": 1, "high": 2}

    if priority not in priority_levels:
        raise ValueError(unavailable_message)
    if not reason or len(reason) > 120:
        raise ValueError(unavailable_message)
    if baseline_priority not in priority_levels:
        raise ValueError(unavailable_message)
    if abs(
        priority_levels[priority] - priority_levels[baseline_priority]
    ) > 1:
        raise ValueError(unavailable_message)
    if baseline_priority == "high" and priority != "high":
        raise ValueError(unavailable_message)

    return {"priority": priority, "reason": reason}


def calculate_group_task_metrics(
    tasks: list[dict[str, int | str | bool]],
    current_date: date,
) -> dict[str, int]:
    """Return selected-group task counts for the dashboard."""
    complete_count = 0
    due_soon_count = 0

    for task in tasks:
        if task["status"] == "complete":
            complete_count += 1
            continue

        due_date = date.fromisoformat(str(task["due_date"]))
        days_until_due = (due_date - current_date).days
        if 0 <= days_until_due <= 6:
            due_soon_count += 1

    total_count = len(tasks)
    incomplete_count = total_count - complete_count
    return {
        "total": total_count,
        "incomplete": incomplete_count,
        "complete": complete_count,
        "due_soon": due_soon_count,
    }


def calculate_completion_progress(
    tasks: list[dict[str, int | str | bool]],
) -> dict[str, int | float]:
    """Return bounded completion values for the dashboard."""
    total_count = len(tasks)
    completed_count = sum(
        1 for task in tasks if task["status"] == "complete"
    )

    if total_count == 0:
        completion_ratio = 0.0
    else:
        completion_ratio = completed_count / total_count

    bounded_ratio = max(0.0, min(completion_ratio, 1.0))
    return {
        "completed": completed_count,
        "total": total_count,
        "ratio": bounded_ratio,
        "percentage": bounded_ratio * 100,
    }


def filter_tasks(
    tasks: list[dict[str, int | str | bool]],
    status_filter: str,
    priority_filter: str,
) -> list[dict[str, int | str | bool]]:
    """Return a new task list matching both approved filters."""
    status_filters = (
        "All tasks",
        "Assigned to me",
        "Incomplete",
        "Complete",
    )
    priority_filters = (
        "All priorities",
        "High",
        "Medium",
        "Low",
    )
    if status_filter not in status_filters:
        raise ValueError("The task status filter is invalid.")
    if priority_filter not in priority_filters:
        raise ValueError("The task priority filter is invalid.")

    filtered_tasks = []
    for task in tasks:
        status_matches = status_filter == "All tasks"
        if status_filter == "Assigned to me":
            status_matches = bool(task["assigned_to_current_user"])
        elif status_filter in ("Incomplete", "Complete"):
            status_matches = task["status"] == status_filter.lower()

        priority_matches = priority_filter == "All priorities"
        if priority_filter != "All priorities":
            priority_matches = task["priority"] == priority_filter.lower()

        if status_matches and priority_matches:
            filtered_tasks.append(task)

    return filtered_tasks


def sort_tasks(
    tasks: list[dict[str, int | str | bool]],
    sort_by: str,
) -> list[dict[str, int | str | bool]]:
    """Return a new task list in one approved display order."""
    if sort_by == "Due date":
        return sorted(
            tasks,
            key=lambda task: (
                date.fromisoformat(str(task["due_date"])),
                int(task["task_id"]),
            ),
        )

    if sort_by == "Priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda task: (
                priority_order[str(task["priority"])],
                int(task["task_id"]),
            ),
        )

    if sort_by == "Assignee":
        return sorted(
            tasks,
            key=lambda task: (
                str(task["assignee_username"]),
                int(task["task_id"]),
            ),
        )

    if sort_by == "Status":
        status_order = {"incomplete": 0, "complete": 1}
        return sorted(
            tasks,
            key=lambda task: (
                status_order[str(task["status"])],
                int(task["task_id"]),
            ),
        )

    raise ValueError("The task sort option is invalid.")


def create_assigned_task(
    database_path: DatabasePath,
    group_id: int,
    current_user_id: int,
    title: str,
    description: str,
    assignee_id: int | None,
    due_date: str | None = None,
    priority: str | None = None,
) -> storage.TaskRecord:
    """Validate and save one task assigned to a group member."""
    validate_task_fields(title, description)

    if assignee_id is None:
        raise ValueError("A task assignee is required.")

    validate_task_schedule(due_date, priority)

    if not storage.is_group_member(
        database_path,
        group_id,
        current_user_id,
    ):
        raise PermissionError(
            "Only a group member can create a task in that group."
        )

    if not storage.is_group_member(
        database_path,
        group_id,
        assignee_id,
    ):
        raise ValueError("The task assignee must be a group member.")

    task_id = storage.create_assigned_task(
        database_path,
        group_id,
        title,
        description,
        assignee_id,
        due_date,
        priority,
    )
    return {
        "task_id": task_id,
        "group_id": group_id,
        "title": title,
        "description": description,
        "assignee_id": assignee_id,
        "status": "incomplete",
        "due_date": due_date,
        "priority": priority,
    }


def calculate_task_date_state(
    due_date: str,
    status: str,
    current_date: date,
) -> str:
    """Return the temporary display label for one task's due date."""
    if status == "complete":
        return ""

    parsed_due_date = date.fromisoformat(due_date)
    if parsed_due_date < current_date:
        return "Overdue"
    if parsed_due_date == current_date:
        return "Due today"
    return ""


def format_priority_display(priority: str) -> str:
    """Return the approved accessible icon-and-text priority label."""
    priority_labels = {
        "high": "🔴 High",
        "medium": "🟡 Medium",
        "low": "🟢 Low",
    }
    try:
        return priority_labels[priority]
    except KeyError as error:
        raise ValueError("The task has an invalid priority.") from error


def calculate_overdue_warning(
    due_date: str,
    status: str,
    current_date: date,
) -> str:
    """Return the approved warning only for incomplete past tasks."""
    if status != "incomplete":
        return ""

    parsed_due_date = date.fromisoformat(due_date)
    if parsed_due_date < current_date:
        return "⚠️ Overdue"
    return ""


def get_group_tasks(
    database_path: DatabasePath,
    group_id: int,
    current_user_id: int,
    current_date: date | None = None,
) -> list[dict[str, int | str | bool]]:
    """Return accessible group tasks with temporary display markers."""
    if not storage.is_group_member(
        database_path,
        group_id,
        current_user_id,
    ):
        raise PermissionError(
            "Only a group member can view that group's tasks."
        )

    reference_date = current_date or date.today()
    tasks = storage.list_tasks_for_group(database_path, group_id)
    return [
        {
            **task,
            "assigned_to_current_user": (
                task["assignee_id"] == current_user_id
            ),
            "date_state": calculate_task_date_state(
                str(task["due_date"]),
                str(task["status"]),
                reference_date,
            ),
            "overdue_warning": calculate_overdue_warning(
                str(task["due_date"]),
                str(task["status"]),
                reference_date,
            ),
        }
        for task in tasks
    ]


def get_group_tasks_for_month(
    database_path: DatabasePath,
    group_id: int,
    current_user_id: int,
    year: int,
    month: int,
    current_date: date | None = None,
) -> list[dict[str, int | str | bool]]:
    """Return accessible group tasks due in one calendar month."""
    tasks = get_group_tasks(
        database_path,
        group_id,
        current_user_id,
        current_date,
    )
    month_tasks = []
    for task in tasks:
        due_date = date.fromisoformat(str(task["due_date"]))
        if due_date.year == year and due_date.month == month:
            month_tasks.append(task)

    return month_tasks


def get_assigned_incomplete_tasks(
    database_path: DatabasePath,
    group_id: int,
    current_user_id: int,
) -> list[dict[str, int | str | bool]]:
    """Return incomplete group tasks assigned to the current user."""
    tasks = get_group_tasks(database_path, group_id, current_user_id)
    return [
        task
        for task in tasks
        if task["assigned_to_current_user"]
        and task["status"] == "incomplete"
    ]


def complete_assigned_task(
    database_path: DatabasePath,
    task_id: int,
    current_user_id: int,
) -> str:
    """Complete an accessible task only for its selected assignee."""
    task = storage.get_task_by_id(database_path, task_id)
    if task is None:
        raise LookupError("The task was not found.")

    group_id = int(task["group_id"])
    if not storage.is_group_member(
        database_path,
        group_id,
        current_user_id,
    ):
        raise PermissionError("The current user cannot access that task.")

    if task["assignee_id"] != current_user_id:
        raise PermissionError(
            "Only the task assignee can mark it complete."
        )

    if task["status"] == "complete":
        return "Task is already complete."

    result = storage.complete_task(database_path, task_id)
    if result == "completed":
        return "Task marked complete."
    if result == "already_complete":
        return "Task is already complete."

    raise LookupError("The task was not found.")
