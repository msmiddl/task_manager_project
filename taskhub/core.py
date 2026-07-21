from taskhub import storage
from taskhub.storage import DatabasePath, UserRecord


def validate_username(username: str) -> None:
    """Raise a clear error when a username breaks an approved rule."""
    if not username or username.isspace():
        raise ValueError("A username is required.")

    if len(username) < 2 or len(username) > 30:
        raise ValueError("The username must contain 2 to 30 characters.")


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
