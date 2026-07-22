# Technical Design

## 1. Design summary

TaskHub will be a small local Python application with four main Python files:

1. `app.py` for the Streamlit interface.
2. `taskhub/core.py` for validation and business rules.
3. `taskhub/storage.py` for SQLite data access.
4. `taskhub/ai_service.py` for the isolated Google AI request.

The design separates interface, business logic, storage, and the external AI service. This keeps important rules independent from Streamlit inputs and outputs, allowing them to be tested with ordinary Python values.

The project will use functions and plain records rather than application classes or advanced architecture patterns. Exact function names may develop during implementation as long as each file retains its approved responsibility.

## 2. Proposed user interface

### Selected interface: Streamlit

TaskHub will use one Streamlit interface running locally and displayed in a web browser. It will not require cloud deployment.

Streamlit fits the project and the student’s experience because it provides text fields, buttons, selection boxes, forms, labels, and messages without requiring a large amount of interface code. It also supports a clear two-minute demonstration of user switching, group selection, task creation, and task completion.

The interface will:

- Collect user-entered values.
- Display saved profiles, groups, members, and tasks.
- Maintain the selected current-user and group identifiers during the active session.
- Call functions in `core.py`.
- Display success, empty-data, and safe error messages.

The interface will not contain SQL statements or duplicate the business rules defined in `core.py`.

### Options not selected

| Option | Reason not selected |
| --- | --- |
| Command line | It may help during development, but it will not become a second complete interface. |
| Jupyter notebook | It does not fit repeated user switching and an application-style workflow. |
| Desktop GUI | It would require more layout and event-handling code than the capstone needs. |

## 3. Main user flow

### 3.1 Start the application

1. The person starts TaskHub locally.
2. TaskHub opens or creates its local SQLite storage.
3. If no saved records exist, the interface displays an empty state and prompts the person to create a profile.
4. If an existing database cannot be opened or queried as valid TaskHub storage, TaskHub displays a controlled error and stops storage-dependent actions. It does not delete, overwrite, or repair the database automatically.
5. The current-user and group selections begin empty after every restart.

### 3.2 Create and select a profile

1. The person enters a username.
2. The interface passes the text to `core.py`.
3. Core logic validates the username and checks exact uniqueness through storage.
4. Storage saves the profile when valid.
5. The interface displays the saved profile or a specific error.
6. In a separate action, the person selects an existing profile.
7. The interface stores that profile’s identifier as the current user for the active session only.

### 3.3 Create and select a group

1. TaskHub displays the groups belonging to the current user.
2. The current user may enter a group name.
3. Core logic validates its length, content, and exact uniqueness.
4. Storage saves the group and creator membership together.
5. The interface refreshes the current user’s group list.
6. The current user selects one group for member and task actions.

### 3.4 Add a group member

1. The group creator enters an exact username.
2. Core logic confirms that the profile exists and is not already a member.
3. Storage adds the membership.
4. The interface displays the updated member list or a specific error.

### 3.5 Create and display a task

1. A group member enters a title and description.
2. The member selects one assignee from the group’s members.
3. Core logic validates the fields, current-user membership, and assignee membership.
4. Storage saves one task with status `incomplete`.
5. The interface reloads the group tasks.
6. Each task displays its title, description, assignee, and status.
7. A task assigned to the current user also displays `Assigned to you`.

### 3.6 Complete a task

1. The current user chooses one of their assigned incomplete tasks.
2. Core logic confirms that the task exists, belongs to an accessible group, is assigned to the current user, and is incomplete.
3. Storage changes the status to `complete`.
4. The interface reloads the task list.
5. A nonassignee or repeated completion attempt produces the specified message without changing data.

### 3.7 Request a username suggestion

1. The person requests a username suggestion.
2. `ai_service.py` requests one raw example from Google AI.
3. `core.py` validates the result against the normal username rules and the existing usernames supplied by storage.
4. The interface displays a valid unused suggestion without creating a profile.
5. If the request or validation fails, the interface displays an availability error while core features remain usable.

## 4. Project components

Exact function names are intentionally not prescribed. The responsibilities, inputs, and outputs below are required; functions should remain small and be named clearly during implementation.

### 4.1 `app.py`

**Responsibility:** Provide the Streamlit interface and maintain active-session selections.

**Main functions:** Small interface functions for profile actions, group actions, member actions, task actions, AI suggestions, and message display.

**Inputs:** Text entries, button actions, selected identifiers, and returned core results.

**Outputs:** Browser content, lists, task labels, success messages, empty-state messages, and safe errors.

**Boundary:** This file may import Streamlit and call core functions. It must not contain SQL statements, make direct AI requests, or redefine validation and permission rules.

### 4.2 `taskhub/core.py`

**Responsibility:** Apply validation and TaskHub business rules.

**Main functions:** Functions covering:

- Username validation and profile creation.
- Group-name validation, group creation, and group listing.
- Exact-username membership addition and creator permission.
- Task field validation and assigned-task creation.
- Group task access and current-user assignment labeling.
- Assignee-only, one-way task completion.
- AI username-result validation using existing usernames provided as input.

**Inputs:** User-entered values, selected record identifiers, existing records or storage results, and raw AI suggestion text.

**Outputs:** Plain result records or standard Python errors with safe messages.

**Boundary:** This file must not import Streamlit, call `input()`, print interface output, contain SQL, or directly call Google AI.

### 4.3 `taskhub/storage.py`

**Responsibility:** Own all SQLite access.

**Main functions:** Functions covering:

- Storage initialization.
- Profile creation, exact lookup, and listing.
- Group creation and creator membership in one transaction.
- Group lookup and current-user group listing.
- Membership creation, checking, and listing.
- Assigned-task creation, lookup, and group-task listing.
- One-way task completion.

Only functions that are required by an implemented core action should be added. Helper functions should not be created in advance without a current use.

**Inputs:** Validated values and identifiers received from `core.py`.

**Outputs:** Plain records, lists of records, created identifiers, or controlled storage errors.

**Boundary:** This file must not import Streamlit, call `input()`, print interface output, or call Google AI.

### 4.4 `taskhub/ai_service.py`

**Responsibility:** Make isolated Google AI username-suggestion and task-priority-recommendation requests.

**Main functions:** One function that requests and returns one raw username suggestion, plus one function that requests and returns one raw task-priority recommendation.

**Inputs:** Fixed request instructions, the approved validated priority-request fields when applicable, and API configuration read from the local environment.

**Outputs:** Raw suggestion or recommendation text, or a controlled AI-unavailable error.

**Boundary:** This file must not receive a password, username, group name, assignee data, other tasks, or task history; access SQLite; validate business rules; or create or update application data.

## 5. Data model

TaskHub will use integer identifiers for stored records and strings for user-entered text. Identifiers keep records distinct even when names are similar.

### 5.1 User

| Field | Python type | Required | Validation |
| --- | --- | --- | --- |
| `user_id` | `int` | Yes | Positive unique identifier created when saved. |
| `username` | `str` | Yes | 2–30 characters; not entirely whitespace; exact, case-sensitive uniqueness; spaces are significant. |

### 5.2 Group

| Field | Python type | Required | Validation |
| --- | --- | --- | --- |
| `group_id` | `int` | Yes | Positive unique identifier created when saved. |
| `name` | `str` | Yes | 2–25 characters; not entirely whitespace; exact, case-sensitive uniqueness; spaces are significant. |
| `creator_id` | `int` | Yes | References an existing user who is also a group member. |

### 5.3 Membership

| Field | Python type | Required | Validation |
| --- | --- | --- | --- |
| `group_id` | `int` | Yes | References an existing group. |
| `user_id` | `int` | Yes | References an existing user. |

The `group_id` and `user_id` pair must be unique.

### 5.4 Task

| Field | Python type | Required | Validation |
| --- | --- | --- | --- |
| `task_id` | `int` | Yes | Positive unique identifier created when saved. |
| `group_id` | `int` | Yes | References an existing group. |
| `title` | `str` | Yes | 1–20 characters and not entirely whitespace. |
| `description` | `str` | Yes | 1–100 characters and not entirely whitespace. |
| `assignee_id` | `int` | Yes | References a user who belongs to the task’s group. |
| `status` | `str` | Yes | Created as `incomplete`; may change once to `complete`; no other value is valid. |
| `due_date` | `str` | Yes | A real calendar date stored as ISO `YYYY-MM-DD` text. |
| `priority` | `str` | Yes | Exactly `low`, `medium`, or `high`. |

### 5.5 Active session

| Field | Python type | Required | Validation |
| --- | --- | --- | --- |
| `current_user_id` | `int` or `None` | No at startup | When present, references an existing profile. |
| `selected_group_id` | `int` or `None` | No at startup | When present, references a group containing the current user. |

These two selections reset whenever TaskHub restarts. Saved profiles, groups, memberships, and tasks do not reset.

### 5.6 Relationships

- One user can create many groups.
- One group has one creator.
- Users may belong to many groups, and groups may contain many users. Membership records connect them.
- One group can have many tasks.
- One member can be assigned many tasks.
- Every task belongs to one group and has one assignee.

## 6. Storage design

### 6.1 Comparison

| Option | Advantages | Limitations for TaskHub |
| --- | --- | --- |
| In-memory structures | Simplest for early experiments. | Data disappears when the program stops and cannot meet REQ-08. |
| CSV | Human-readable and simple for one flat table. | Multiple related files are difficult to keep consistent. |
| JSON | Can persist nested Python-like data in one file. | Relationship validation and partial-update handling require custom code. |
| SQLite | Local, included with Python, persistent, and suitable for related records. | Requires introductory SQL and connection error handling. |

### 6.2 Approved choice: SQLite

TaskHub will use one local SQLite database through Python’s standard `sqlite3` module. No separate database server or external database package is needed.

The database will contain four tables:

- `users`
- `groups`
- `memberships`
- `tasks`

Storage must support these rules in addition to the checks in `core.py`:

- Exact, case-sensitive username uniqueness.
- Exact, case-sensitive group-name uniqueness.
- Unique user-group membership pairs.
- Valid references from groups, memberships, and tasks to related records.
- Task statuses limited to `incomplete` and `complete`.
- Task priorities limited to `low`, `medium`, and `high`.
- Task due dates stored as ISO `YYYY-MM-DD` text.

SQLite relationship enforcement must be enabled whenever a connection is opened. This prevents a membership or task from pointing to a user or group that does not exist.

Creating a group and adding its creator membership must occur in one **transaction**, meaning both changes succeed or neither remains saved.

The current user and selected group remain in Streamlit session state and are not saved permanently.

### 6.3 Approved calendar-enhancement design

The calendar enhancement uses only Python's standard `datetime` and `calendar` modules with the existing Streamlit and SQLite dependencies.

- `app.py` owns the date picker, priority selector, task-list/calendar view selector, calendar grid, and previous/next-month session state.
- `taskhub/core.py` validates real ISO calendar dates and the three lowercase priority values. It calculates overdue and due-today labels using a supplied local date so tests remain deterministic, and filters selected-group tasks for a displayed year and month.
- `taskhub/storage.py` owns the two new task columns, schema migration, constraints, inserts, and retrieval. It does not calculate display labels.
- Existing group-access, assignment, and assignee-only completion rules are reused without modification.

The `tasks` table gains required `due_date` and `priority` values. New tasks must provide both. Priority is constrained to `low`, `medium`, or `high`; real-date validation remains centralized in core logic.

Existing databases are upgraded in a transaction without deleting or recreating tables. Every pre-enhancement task receives the local migration date in ISO format as its fallback due date and `medium` priority. Initialization detects whether each column already exists, applies only missing changes, validates the upgraded schema, and never overwrites scheduling values on repeated initialization. A failed migration produces the existing controlled saved-data-unavailable error.

Calendar month selection is temporary Streamlit session state. It begins at the current local month after application restart and resets when the current user or selected group changes. Navigation does not write to SQLite.

### 6.4 Approved smart-priority and dashboard design

The smart-priority enhancement keeps the existing four-component architecture and requires no storage migration or new dependency.

- `taskhub/core.py` calculates baseline priority, validates parsed AI recommendations, calculates group metrics and completion percentage, and filters and sorts task collections. Date-dependent helpers receive a supplied local date for deterministic tests.
- `taskhub/ai_service.py` sends one explicit priority-recommendation request using only validated title, description, today, due date, baseline priority, and fixed response instructions. It returns raw response text and converts configuration or provider failures into the existing controlled AI-unavailable error pattern.
- `app.py` owns the recommendation button and temporary recommendation snapshot, renders metrics and progress, maintains filters and sorting state, and displays task cards. It continues to call core functions rather than repeat calculations or permissions.
- `taskhub/storage.py` remains unchanged because due date and priority already persist and every new value is derived or session-only.

The existing linear Streamlit workflow is retained. The enhancement does not require a sidebar or full tab redesign. AI output uses exactly two nonblank plain-text lines: lowercase priority first and a reason of at most 120 characters second. Relevant task-input changes clear a recommendation without making another request. Task list is the default detailed view. Filters default to all tasks and all priorities, sorting defaults to earliest due date, and these controls reset when the selected user or group changes. The formerly proposed separate Upcoming tasks section is withdrawn.

## 7. Error-handling strategy

1. Validate lengths, whitespace, required values, uniqueness, membership, and permissions before saving.
2. Use a small set of standard Python errors:
   - `ValueError` for invalid or duplicate input.
   - `LookupError` for missing records.
   - `PermissionError` for prohibited actions.
   - `RuntimeError` for controlled storage or AI failures.
3. Catch expected errors in `app.py` and display their safe messages.
4. Do not display API keys, SQL statements, or technical stack traces in the interface.
5. Do not report or display a write as successful until storage confirms success.
6. Treat a missing database as an empty first-use state.
7. If an existing database cannot be opened or queried as valid TaskHub storage, show one controlled error and stop storage-dependent actions. Do not automatically replace or repair the file.
8. Keep AI failures inside the suggestion flow so core actions remain available.
9. During development, unexpected exceptions may remain visible in the terminal. A separate logging system is not required for the MVP.

## 8. Testing strategy

TaskHub will use Python’s standard `unittest` library. No additional testing framework is required.

### 8.1 Unit tests

`tests/test_core.py` will test:

- Boundary lengths and whitespace for usernames, group names, task titles, and descriptions.
- Exact comparisons, including capitalization and spaces.
- Duplicate username and group-name handling.
- Exact username lookup for membership.
- Duplicate membership and noncreator rejection.
- Required and eligible assignees.
- New tasks beginning incomplete.
- Assignee-only completion.
- Repeated completion and one-way status.
- Group access and the current-user assignment marker.
- Valid, invalid, blank, long, and duplicate AI suggestions using existing usernames passed as test input.

Current-user selection is primarily interface-session behavior. Its missing-profile cases will be verified by a storage test for a nonexistent profile identifier and a manual interface check that clears an invalid or stale session selection and displays a user-not-found or load error.

### 8.2 Storage tests

`tests/test_storage.py` will use a new temporary SQLite database for each test and verify:

- New storage starts empty.
- Profiles, groups, memberships, and tasks can be saved and retrieved.
- Exact uniqueness and unique membership pairs are enforced.
- Invalid record references and invalid status values are rejected.
- Group and creator membership are saved together.
- Task completion persists after reconnecting.
- A missing database becomes an empty first-use database.
- An unreadable or corrupted database produces a controlled error without being overwritten.

### 8.3 Workflow integration test

`tests/test_workflow.py` will verify the complete non-interface flow:

1. Create Alex and Jordan.
2. Select Alex for the test flow.
3. Create `Roommates`.
4. Add Jordan by exact username.
5. Create a task assigned to Jordan.
6. Confirm Alex cannot complete it.
7. Switch the test flow to Jordan.
8. Confirm the task is marked as assigned to the current user.
9. Complete the task.
10. Reopen storage and confirm the status remains complete.

### 8.4 AI service tests

`tests/test_ai_service.py` will verify:

- A controlled raw suggestion response can be returned.
- A missing API key produces an AI-unavailable error.
- A simulated connection or service failure produces an AI-unavailable error.
- A priority request sends only approved fields and returns controlled raw text.

The real AI call will be replaced with predetermined responses during automated tests. This controlled replacement is called a **mock** and prevents tests from depending on the internet or unpredictable AI output.

### 8.5 Manual tests

The manual checklist will verify:

- Streamlit controls and messages.
- Empty profile, group, and task states.
- Current-user and group selection behavior.
- The four required task fields.
- The `Assigned to you` label.
- Safe interface errors.
- One live AI username suggestion and one live task-priority recommendation.
- Core functions while AI access is unavailable.
- The complete two-user workflow within two minutes.

Tests will use temporary sample data such as Alex, Jordan, Roommates, and Wash dishes. Automated tests must not read or change the demonstration database.

## 9. Dependencies

### 9.1 Standard library

| Library | Purpose | Why needed | Essential? |
| --- | --- | --- | --- |
| `sqlite3` | Local relational storage. | Meets persistence and relationship needs without an external database. | Essential |
| `unittest` | Automated tests. | Sufficient for the approved test scope. | Essential for verification |
| `unittest.mock` | Controlled AI responses. | Prevents automated tests from requiring a live service. | Essential for AI tests |
| `tempfile` | Temporary test databases. | Protects demonstration data. | Essential for storage tests |
| `os` | Read the API key from the local environment. | Prevents storing the key in source code. | Essential for live AI use |

### 9.2 External libraries

| Library | Purpose | Why the standard library is not sufficient | Essential or optional |
| --- | --- | --- | --- |
| `streamlit` | Local browser interface. | A standard-library desktop interface would require more interface code. | Essential for the final interface |
| `google-genai` | Google AI username request. | It supplies the official service client and response handling. | Essential for REQ-09; optional for core actions |

Pandas is not required by the course and is not needed by the approved features.

## 10. Project structure

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
│   └── specification.md
├── .gitignore
├── README.md
└── requirements.txt
```

The local database file and API key configuration must be excluded from version control.

## 11. Requirement traceability

| Requirement | Responsible component | Expected test file |
| --- | --- | --- |
| REQ-01 Create profile | `core.py`, `storage.py`, profile interface in `app.py` | `test_core.py`, `test_storage.py` |
| REQ-02 Select current user | Session state and profile interface in `app.py`; profile existence from `storage.py` | `test_storage.py`, `test_workflow.py`, manual interface checklist |
| REQ-03 Display/create groups | `core.py`, `storage.py`, group interface in `app.py` | `test_core.py`, `test_storage.py`, `test_workflow.py` |
| REQ-04 Add group member | `core.py`, `storage.py`, member interface in `app.py` | `test_core.py`, `test_storage.py`, `test_workflow.py` |
| REQ-05 Create assigned task | `core.py`, `storage.py`, task interface in `app.py` | `test_core.py`, `test_storage.py`, `test_workflow.py` |
| REQ-06 Display group tasks | `core.py`, `storage.py`, task interface in `app.py` | `test_core.py`, `test_storage.py`, `test_workflow.py`, manual checklist |
| REQ-07 Complete task | `core.py`, `storage.py`, task interface in `app.py` | `test_core.py`, `test_storage.py`, `test_workflow.py` |
| REQ-08 Retain data | `storage.py` | `test_storage.py`, `test_workflow.py` |
| REQ-09 AI username suggestion | `ai_service.py`, `core.py`, AI interface in `app.py` | `test_ai_service.py`, `test_core.py`, manual live check |
| REQ-SPUI-01 Baseline priority | `core.py` | `test_core.py` |
| REQ-SPUI-02–04 AI priority recommendation | `ai_service.py`, `core.py`, `app.py` | `test_ai_service.py`, `test_core.py`, manual live check |
| REQ-SPUI-05–06 Dashboard and progress | `core.py`, `app.py` | `test_core.py`, manual checklist |
| REQ-SPUI-07 Priority and overdue indicators | `core.py`, `app.py` | `test_core.py`, manual checklist |
| REQ-SPUI-08–09 Filter and sort tasks | `core.py`, `app.py` | `test_core.py`, manual checklist |
| REQ-SPUI-10 Withdrawn upcoming-task section | None | Scope-revision review |
| REQ-SPUI-11–12 Task cards and feedback | `app.py` | Manual checklist |

## 12. Technical risks

| Risk | Impact | Response |
| --- | --- | --- |
| Streamlit reruns after interactions. | Current-user or group selection may reset unexpectedly during a session. | Keep their identifiers in session state; intentionally reset them only after an application restart. |
| SQL and Streamlit are both new. | Development may exceed the available time. | Finish and test core and storage behavior before interface polish. |
| A group and creator membership are two writes. | Partial saving could leave inconsistent data. | Use one transaction. |
| No authentication exists. | A person can select and act as another profile. | State this approved limitation clearly. |
| AI output or availability is unpredictable. | A username suggestion or priority recommendation may fail. | Isolate, validate, mock in tests, preserve manual workflows, and display a controlled error. |
| The database becomes unreadable. | Saved records cannot be used. | Stop storage actions and show an error without overwriting data. |
| Rules are copied into `app.py`. | Automated tests may not cover actual behavior. | Keep all validation and permission decisions in `core.py`. |

## 13. Design decisions requiring student approval

All identified design decisions have been approved:

1. Streamlit is the single final interface.
2. SQLite through the standard `sqlite3` module is the storage system.
3. The application uses the approved four-file design.
4. Functions and plain records are used instead of application classes.
5. Current-user and selected-group choices reset after an application restart.
6. Standard-library `unittest` is used for automated testing.
7. The official `google-genai` package is used for REQ-09.
8. The API key is read from the local environment and is not stored in source code or SQLite.
9. Pandas is not required or included.
10. A corrupted database produces a controlled error and is not repaired or overwritten automatically.
11. No specific number of modules, functions, unit tests, or integration tests is required by the instructor.
12. Exact function names may develop during implementation while file responsibilities remain fixed.

No additional design decision is currently blocking implementation.
