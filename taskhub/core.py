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


def get_group_tasks(
    database_path: DatabasePath,
    group_id: int,
    current_user_id: int,
) -> list[dict[str, int | str | bool]]:
    """Return accessible group tasks with current-user markers."""
    if not storage.is_group_member(
        database_path,
        group_id,
        current_user_id,
    ):
        raise PermissionError(
            "Only a group member can view that group's tasks."
        )

    tasks = storage.list_tasks_for_group(database_path, group_id)
    return [
        {
            **task,
            "assigned_to_current_user": (
                task["assignee_id"] == current_user_id
            ),
        }
        for task in tasks
    ]


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
