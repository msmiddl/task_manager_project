import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal, TypeAlias


DatabasePath: TypeAlias = str | Path
UserRecord: TypeAlias = dict[str, int | str]
GroupRecord: TypeAlias = dict[str, int | str]
TaskRecord: TypeAlias = dict[str, int | str]
CompletionResult: TypeAlias = Literal[
    "completed",
    "already_complete",
    "not_found",
]


@contextmanager
def open_connection(
    database_path: DatabasePath,
) -> Iterator[sqlite3.Connection]:
    """Open TaskHub storage with SQLite relationship checks enabled."""
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
    except sqlite3.Error as error:
        if connection is not None:
            connection.close()
        raise RuntimeError("Saved profile data is unavailable.") from error

    try:
        yield connection
    finally:
        connection.close()


def initialize_storage(database_path: DatabasePath) -> None:
    """Create the user-profile table when it does not already exist."""
    try:
        with open_connection(database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    creator_id INTEGER NOT NULL,
                    FOREIGN KEY (creator_id) REFERENCES users (user_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memberships (
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    PRIMARY KEY (group_id, user_id),
                    FOREIGN KEY (group_id) REFERENCES groups (group_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY,
                    group_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    assignee_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'incomplete'
                        CHECK (status IN ('incomplete', 'complete')),
                    FOREIGN KEY (group_id, assignee_id)
                        REFERENCES memberships (group_id, user_id)
                )
                """
            )
            connection.commit()
    except sqlite3.Error as error:
        raise RuntimeError("Saved profile data is unavailable.") from error


def create_user(database_path: DatabasePath, username: str) -> int:
    """Save one profile and return its new identifier."""
    try:
        with open_connection(database_path) as connection:
            cursor = connection.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,),
            )
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.IntegrityError as error:
        raise ValueError("That exact username already exists.") from error
    except sqlite3.Error as error:
        raise RuntimeError("The profile could not be saved.") from error


def get_user_by_username(
    database_path: DatabasePath,
    username: str,
) -> UserRecord | None:
    """Return the profile with an exact username, or None when absent."""
    try:
        with open_connection(database_path) as connection:
            row = connection.execute(
                """
                SELECT user_id, username
                FROM users
                WHERE username = ? COLLATE BINARY
                """,
                (username,),
            ).fetchone()
    except sqlite3.Error as error:
        raise RuntimeError("Saved profiles could not be loaded.") from error

    if row is None:
        return None

    return {"user_id": row["user_id"], "username": row["username"]}


def get_user_by_id(
    database_path: DatabasePath,
    user_id: int,
) -> UserRecord | None:
    """Return the profile with an identifier, or None when absent."""
    try:
        with open_connection(database_path) as connection:
            row = connection.execute(
                """
                SELECT user_id, username
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
    except sqlite3.Error as error:
        raise RuntimeError("Saved profiles could not be loaded.") from error

    if row is None:
        return None

    return {"user_id": row["user_id"], "username": row["username"]}


def list_users(database_path: DatabasePath) -> list[UserRecord]:
    """Return all saved profiles in creation order."""
    try:
        with open_connection(database_path) as connection:
            rows = connection.execute(
                """
                SELECT user_id, username
                FROM users
                ORDER BY user_id
                """
            ).fetchall()
    except sqlite3.Error as error:
        raise RuntimeError("Saved profiles could not be loaded.") from error

    return [
        {"user_id": row["user_id"], "username": row["username"]}
        for row in rows
    ]


def create_group(
    database_path: DatabasePath,
    name: str,
    creator_id: int,
) -> int:
    """Save a group and its creator membership in one transaction."""
    if get_user_by_id(database_path, creator_id) is None:
        raise LookupError("The group creator could not be found.")

    with open_connection(database_path) as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO groups (name, creator_id)
                VALUES (?, ?)
                """,
                (name, creator_id),
            )
            group_id = int(cursor.lastrowid)
            connection.execute(
                """
                INSERT INTO memberships (group_id, user_id)
                VALUES (?, ?)
                """,
                (group_id, creator_id),
            )
            connection.commit()
            return group_id
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ValueError(
                "That exact group name already exists."
            ) from error
        except sqlite3.Error as error:
            connection.rollback()
            raise RuntimeError("The group could not be saved.") from error


def list_groups_for_user(
    database_path: DatabasePath,
    user_id: int,
) -> list[GroupRecord]:
    """Return the groups containing one user profile."""
    try:
        with open_connection(database_path) as connection:
            rows = connection.execute(
                """
                SELECT groups.group_id, groups.name, groups.creator_id
                FROM groups
                JOIN memberships
                    ON memberships.group_id = groups.group_id
                WHERE memberships.user_id = ?
                ORDER BY groups.group_id
                """,
                (user_id,),
            ).fetchall()
    except sqlite3.Error as error:
        raise RuntimeError("Saved groups could not be loaded.") from error

    return [
        {
            "group_id": row["group_id"],
            "name": row["name"],
            "creator_id": row["creator_id"],
        }
        for row in rows
    ]


def add_group_member(
    database_path: DatabasePath,
    group_id: int,
    user_id: int,
) -> None:
    """Add one existing user to one existing group."""
    with open_connection(database_path) as connection:
        try:
            group_exists = connection.execute(
                "SELECT 1 FROM groups WHERE group_id = ?",
                (group_id,),
            ).fetchone()
            if group_exists is None:
                raise LookupError("The group could not be found.")

            user_exists = connection.execute(
                "SELECT 1 FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if user_exists is None:
                raise LookupError("The user could not be found.")

            connection.execute(
                """
                INSERT INTO memberships (group_id, user_id)
                VALUES (?, ?)
                """,
                (group_id, user_id),
            )
            connection.commit()
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ValueError(
                "That user is already a member of the group."
            ) from error
        except sqlite3.Error as error:
            connection.rollback()
            raise RuntimeError(
                "The group membership could not be saved."
            ) from error


def is_group_member(
    database_path: DatabasePath,
    group_id: int,
    user_id: int,
) -> bool:
    """Return whether a user belongs to a group."""
    try:
        with open_connection(database_path) as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM memberships
                WHERE group_id = ? AND user_id = ?
                """,
                (group_id, user_id),
            ).fetchone()
    except sqlite3.Error as error:
        raise RuntimeError("Group membership could not be checked.") from error

    return row is not None


def list_group_members(
    database_path: DatabasePath,
    group_id: int,
) -> list[UserRecord]:
    """Return all profiles belonging to a group."""
    try:
        with open_connection(database_path) as connection:
            rows = connection.execute(
                """
                SELECT users.user_id, users.username
                FROM users
                JOIN memberships
                    ON memberships.user_id = users.user_id
                WHERE memberships.group_id = ?
                ORDER BY users.user_id
                """,
                (group_id,),
            ).fetchall()
    except sqlite3.Error as error:
        raise RuntimeError("Group members could not be loaded.") from error

    return [
        {"user_id": row["user_id"], "username": row["username"]}
        for row in rows
    ]


def create_assigned_task(
    database_path: DatabasePath,
    group_id: int,
    title: str,
    description: str,
    assignee_id: int,
) -> int:
    """Save one assigned task with an incomplete status."""
    with open_connection(database_path) as connection:
        try:
            group_exists = connection.execute(
                "SELECT 1 FROM groups WHERE group_id = ?",
                (group_id,),
            ).fetchone()
            if group_exists is None:
                raise LookupError("The task group could not be found.")

            assignee_exists = connection.execute(
                "SELECT 1 FROM users WHERE user_id = ?",
                (assignee_id,),
            ).fetchone()
            if assignee_exists is None:
                raise LookupError("The task assignee could not be found.")

            membership_exists = connection.execute(
                """
                SELECT 1
                FROM memberships
                WHERE group_id = ? AND user_id = ?
                """,
                (group_id, assignee_id),
            ).fetchone()
            if membership_exists is None:
                raise ValueError(
                    "The task assignee must be a group member."
                )

            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    group_id,
                    title,
                    description,
                    assignee_id,
                    status
                )
                VALUES (?, ?, ?, ?, 'incomplete')
                """,
                (group_id, title, description, assignee_id),
            )
            connection.commit()
            return int(cursor.lastrowid)
        except sqlite3.Error as error:
            connection.rollback()
            raise RuntimeError("The task could not be saved.") from error


def get_task_by_id(
    database_path: DatabasePath,
    task_id: int,
) -> TaskRecord | None:
    """Return a task by identifier, or None when absent."""
    try:
        with open_connection(database_path) as connection:
            row = connection.execute(
                """
                SELECT
                    task_id,
                    group_id,
                    title,
                    description,
                    assignee_id,
                    status
                FROM tasks
                WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
    except sqlite3.Error as error:
        raise RuntimeError("Saved tasks could not be loaded.") from error

    if row is None:
        return None

    return {
        "task_id": row["task_id"],
        "group_id": row["group_id"],
        "title": row["title"],
        "description": row["description"],
        "assignee_id": row["assignee_id"],
        "status": row["status"],
    }


def list_tasks_for_group(
    database_path: DatabasePath,
    group_id: int,
) -> list[dict[str, int | str]]:
    """Return one group's tasks with assignee display names."""
    try:
        with open_connection(database_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    tasks.task_id,
                    tasks.group_id,
                    tasks.title,
                    tasks.description,
                    tasks.assignee_id,
                    users.username AS assignee_username,
                    tasks.status
                FROM tasks
                JOIN users ON users.user_id = tasks.assignee_id
                WHERE tasks.group_id = ?
                ORDER BY tasks.task_id
                """,
                (group_id,),
            ).fetchall()
    except sqlite3.Error as error:
        raise RuntimeError("Group tasks could not be loaded.") from error

    return [
        {
            "task_id": row["task_id"],
            "group_id": row["group_id"],
            "title": row["title"],
            "description": row["description"],
            "assignee_id": row["assignee_id"],
            "assignee_username": row["assignee_username"],
            "status": row["status"],
        }
        for row in rows
    ]


def complete_task(
    database_path: DatabasePath,
    task_id: int,
) -> CompletionResult:
    """Persist a one-way task completion and describe the outcome."""
    with open_connection(database_path) as connection:
        try:
            row = connection.execute(
                "SELECT status FROM tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()

            if row is None:
                return "not_found"

            if row["status"] == "complete":
                return "already_complete"

            connection.execute(
                """
                UPDATE tasks
                SET status = 'complete'
                WHERE task_id = ? AND status = 'incomplete'
                """,
                (task_id,),
            )
            connection.commit()
            return "completed"
        except sqlite3.Error as error:
            connection.rollback()
            raise RuntimeError(
                "The task completion could not be saved."
            ) from error
