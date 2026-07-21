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