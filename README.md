# TaskHub

## Project summary

TaskHub is a beginner Python capstone project for organizing assigned tasks within small groups. The planned application will let people create local user profiles, form groups, assign tasks to group members, and track whether tasks are incomplete or complete.

TaskHub is designed to run locally. It is not intended to be a production or cloud-hosted application.

## Problem solved

Small groups often coordinate responsibilities through verbal reminders, shared notes, or no organized system. This can make it difficult to know:

- Which tasks still need to be completed
- Who is responsible for each task
- Whether assigned work has been completed

TaskHub is intended to keep this information in one local application.

## Main features

The approved MVP plans to include:

- Create local user profiles with unique usernames
- Select a profile as the current user for the active session
- Create groups and display the current user’s groups
- Add an existing profile to a group by exact username
- Create an incomplete task with a required assignee
- Display each task’s title, description, assignee, and status
- Label tasks assigned to the current user
- Allow only the selected assignee profile to mark a task complete
- Keep profiles, groups, memberships, and tasks after the application closes
- Request an AI-generated username suggestion as an optional user action

These are planned features. Implementing the AI suggestion is required for the MVP, although a person may choose not to request a suggestion while using TaskHub. Feature implementation status must be verified against the code and tests before any feature is described as working.

## Current status

**TaskHub is under development.**

The project specification, technical design, implementation task plan, and project guide have been created. Application code and automated tests have not yet been completed in this workspace.

Development should follow the ordered tasks in [docs/tasks.md](docs/tasks.md), beginning with T01.

## Planned technology

| Technology | Planned purpose |
| --- | --- |
| Python | Application language |
| Streamlit | Local browser-based interface |
| SQLite through `sqlite3` | Local persistent storage |
| `unittest` | Automated testing |
| Google Gen AI Python SDK | AI username suggestion |

Pandas is not required for the approved project.

## Project structure

The planned structure is:

```text
task_manager_project/
├── app.py
├── taskhub/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── core.py
│   └── storage.py
├── tests/
│   ├── __init__.py
│   ├── test_ai_service.py
│   ├── test_core.py
│   ├── test_storage.py
│   └── test_workflow.py
├── data/
├── docs/
│   ├── design.md
│   ├── specification.md
│   └── tasks.md
├── PROJECT_GUIDE.md
├── .gitignore
├── README.md
└── requirements.txt
```

Some planned files and folders may not exist until their implementation task is completed.

## Installation

The following commands are intended for Windows PowerShell after the project skeleton and `requirements.txt` have been created:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

The AI feature will require a Google API key in the local environment. Do not place the key in source code, SQLite data, screenshots, or committed files.

## How to run

After `app.py` has been implemented, run:

```powershell
py -m streamlit run app.py
```

This command is not expected to work until the project skeleton and Streamlit application are created.

## How to run tests

After the test files have been implemented, run the complete suite with:

```powershell
py -m unittest discover -s tests -v
```

Run one test module while developing a specific behavior:

```powershell
py -m unittest tests.test_core -v
```

Do not report tests as passing unless the command was actually executed successfully.

## Example usage

The following is a placeholder example of the planned workflow. It is not proof that the application is implemented:

1. Create profiles named `Alex` and `Jordan`.
2. Select `Alex` as the current user.
3. Create a group named `Roommates`.
4. Add `Jordan` to the group by entering the exact username.
5. Create a task named `Wash dishes` and assign it to Jordan.
6. Select Jordan as the current user.
7. View the task with an `Assigned to you` label.
8. Mark the task complete.
9. Restart TaskHub and confirm the completed task remains saved.

The current-user and selected-group choices are expected to reset after restart even though saved application data remains.

## Requirements and design documents

- [Project specification](docs/specification.md) — approved behavior and acceptance criteria
- [Technical design](docs/design.md) — approved modules, storage, interface, and testing design
- [Implementation tasks](docs/tasks.md) — ordered development sessions and requirement traceability
- [Project guide](PROJECT_GUIDE.md) — coding workflow and AI-assistant rules

The specification is the source of truth for application behavior.

## Limitations

The approved MVP has these intentional limitations:

- It runs locally and is not deployed to the cloud.
- It does not authenticate users or store passwords.
- A person can select any existing local profile.
- It does not synchronize between devices or users in real time.
- Tasks cannot be edited, deleted, reassigned, or returned to incomplete.
- Every task must have an assignee when it is created.
- It does not include notifications, due dates, priorities, recurring tasks, or calendar integration.
- The AI feature depends on an API key, internet access, and an external service.
- The application is not suitable for private or sensitive information.

## Future improvements

Future work may be considered only after the approved MVP is implemented and tested. Possible later improvements include:

- Password authentication
- Formal group invitations
- Task editing, deletion, and reassignment
- Due dates and priorities
- Recurring tasks
- Notifications
- Calendar integration
- Member preferences and workload tracking
- AI-assisted task assignment
- Real-time synchronization or cloud deployment

Future improvements are not part of the current implementation plan.
