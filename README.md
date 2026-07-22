# TaskHub

TaskHub is a beginner Python capstone for organizing scheduled tasks in small groups. It runs locally in a Streamlit browser interface and stores profiles, groups, memberships, tasks, assignees, due dates, priorities, and completion statuses in SQLite.

## Features

- Create and select local user profiles.
- Create groups and add existing profiles by exact username.
- Create tasks with one required group-member assignee, due date, and priority.
- Display task details with readable dates and Low, Medium, or High priority.
- Identify incomplete tasks that are overdue or due today.
- View the selected group's tasks in a navigable monthly calendar.
- Label tasks assigned to the selected current profile.
- Allow only the selected assignee profile to mark a task complete.
- Keep application data after TaskHub closes.
- Request an optional AI-generated username suggestion.

## Requirements

- Python 3.11 or newer
- Internet access for installing packages
- Internet access and a Google Gemini API key only for live AI suggestions

The core profile, group, and task features remain usable without AI access.

## Installation on Windows PowerShell

Open PowerShell in the folder containing `app.py`, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

The activated terminal begins with `(.venv)`. Run the activation command again whenever a new PowerShell window is opened for this project.

## Google API key

The AI suggestion button requires a Google Gemini API key. Set it only in the PowerShell session that will start TaskHub:

```powershell
$env:GEMINI_API_KEY="your-real-api-key"
```

Never put the real key in source code, SQLite data, Git commits, screenshots, demonstrations, or submitted project files. Do not share terminal output containing the key.

Remove it from the current terminal with:

```powershell
Remove-Item Env:GEMINI_API_KEY
```

## Run TaskHub

From the project root with the virtual environment activated:

```powershell
py -m streamlit run app.py
```

Use the local URL shown in the terminal. Keep that terminal open while using TaskHub. Press `Ctrl+C` in the terminal to stop the application.

## Run tests and project checks

Run the complete automated test suite:

```powershell
py -m unittest discover -s tests -v
```

Run the workflow integration test by itself:

```powershell
py -m unittest tests.test_workflow -v
```

Run the approved dependency-free project checks:

```powershell
py -m compileall app.py taskhub tests
git diff --check
```

No external formatter or linter is configured.

## Saved data and sessions

TaskHub stores local application data in `data/taskhub.db`. Valid saved profiles, groups, memberships, assignments, due dates, priorities, and completion statuses remain after the application closes and reopens.

The selected current user and selected group exist only in Streamlit session state. They intentionally reset when TaskHub restarts and must be selected again.

A missing database is treated as a new empty application. An existing unreadable or invalid database produces a controlled error and is not repaired or overwritten automatically. Back up important data before changing files in `data/`.

### Verify an existing database copy

TaskHub upgrades older task records without deleting them. A task created before scheduling was added receives the local migration date as its fallback due date and `medium` priority. Repeated startup does not replace existing scheduling values.

Use a copy—not the live database—for a final migration check:

```powershell
Copy-Item data/taskhub.db data/taskhub-migration-check.db -Force
py -c "import sqlite3; c=sqlite3.connect('data/taskhub-migration-check.db'); print('Before:', [c.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0] for t in ('users','groups','memberships','tasks')]); c.close()"
py -c "from pathlib import Path; from taskhub.storage import initialize_storage; initialize_storage(Path('data/taskhub-migration-check.db')); print('Copied database initialized successfully')"
py -c "import sqlite3; c=sqlite3.connect('data/taskhub-migration-check.db'); print('After:', [c.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0] for t in ('users','groups','memberships','tasks')]); print('Tasks missing schedules:', c.execute('SELECT COUNT(*) FROM tasks WHERE due_date IS NULL OR priority IS NULL').fetchone()[0]); c.close()"
```

The table counts printed before and after initialization must match, and `Tasks missing schedules` must be `0`. The copied file is ignored by the project’s database ignore rule and may be removed after verification.

## Example workflow

1. Create profiles named `Alex` and `Jordan`.
2. Select Alex as the current user.
3. Create a group named `Roommates`.
4. Add Jordan using the exact username `Jordan`.
5. Create `Wash dishes`, enter a description, assign it to Jordan, choose a due date, and choose High priority.
6. Confirm the task list shows its readable due date, High priority, and any applicable overdue or due-today label.
7. Open Calendar, navigate to the due month, and confirm the task appears on the correct date with its title, priority, assignee, and status.
8. Confirm Alex cannot mark Jordan's task complete.
9. Select Jordan and then select Roommates again.
10. Confirm the task displays `Assigned to you`, then mark it complete.
11. Confirm the completed task retains its due date and priority but no longer shows an overdue or due-today label.
12. Restart TaskHub, reselect Jordan and Roommates, and confirm the task and its scheduling values remain saved.

## Privacy and security limitations

TaskHub has no authentication. Selecting a profile does not prove the operator is that person, and any local operator can select any saved profile. Permission rules apply to the selected profile only.

Do not enter personal, private, or sensitive information in usernames, group names, task titles, or task descriptions. TaskHub does not detect sensitive information and is not suitable for untrusted users or confidential data. It does not collect or transmit passwords.

The application runs locally and does not synchronize between devices. Tasks cannot be edited, deleted, reassigned, or returned to incomplete.

## Manual verification

Use [docs/manual-test-checklist.md](docs/manual-test-checklist.md) for final interface, persistence, privacy, AI, and demonstration checks.

## Project documents

- [Project specification](docs/specification.md)
- [Technical design](docs/design.md)
- [Implementation tasks](docs/tasks.md)
- [Project guide](PROJECT_GUIDE.md)

The specification is the source of truth for application behavior.
