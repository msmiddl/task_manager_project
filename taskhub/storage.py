import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TypeAlias


DatabasePath: TypeAlias = str | Path
UserRecord: TypeAlias = dict[str, int | str]


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
