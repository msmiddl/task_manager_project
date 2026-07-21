# TaskHub Calendar and Priority Feature Specification

## 1. Document purpose

This document specifies a post-MVP enhancement to the existing TaskHub application. The enhancement adds due dates, priority levels, and an in-app calendar view while preserving the existing profile, group, assignment, completion, permission, and persistence behavior.

This specification supplements the approved TaskHub project specification. Where this document does not explicitly change a rule, the original rule remains in effect.

## 2. Feature summary

TaskHub will allow a group member to give each new task:

- One required due date.
- One required priority level: `Low`, `Medium`, or `High`.

Members will be able to view these values in the existing group task list and in a monthly calendar. The calendar will show tasks on their due dates and allow the person to move between months. Due dates and priorities will be stored in the existing local SQLite database.

The feature does not synchronize with an external calendar service.

## 3. User value

The current application identifies what work must be done and who is responsible, but it does not show when work is due or which tasks are most important. Due dates and priorities will help group members plan their work, notice overdue responsibilities, and decide what to complete first.

## 4. Terms

- **Due date:** The local calendar date by which a task should be completed. It does not include a time of day or time zone.
- **Priority:** A fixed label indicating a task's relative importance: `Low`, `Medium`, or `High`.
- **Overdue task:** An incomplete task whose due date is before the current local date.
- **Due today:** A task whose due date equals the current local date.
- **Calendar view:** An in-app monthly display of tasks arranged by due date.
- **Task list:** The existing group task display enhanced with due-date and priority information.

## 5. Goals

The enhancement will allow a group member to:

1. Select a due date when creating a task.
2. Select a Low, Medium, or High priority when creating a task.
3. See the due date and priority in the existing task list.
4. Recognize incomplete tasks that are overdue or due today.
5. View a selected group's tasks in an in-app monthly calendar.
6. Move between calendar months without changing stored task data.
7. Retain due dates and priorities after the application closes.
8. Continue using all existing TaskHub features and permissions.

## 6. Scope

### 6.1 Included

- A required due-date field during task creation.
- A required priority selector with exactly three stored values: `low`, `medium`, and `high`.
- A human-readable display of Low, Medium, and High in the interface.
- Due date and priority in the group task list.
- A monthly calendar for the selected group.
- Month navigation.
- Clear visual labels for overdue and due-today incomplete tasks.
- Display of both incomplete and complete tasks in the calendar.
- Persistence of due date and priority in SQLite.
- Migration of existing task records so the current database remains usable.
- Automated tests for storage, validation, business rules, and retrieval.
- Manual interface tests for task creation, calendar display, month navigation, and visual states.

### 6.2 Excluded

- Google Calendar, Outlook Calendar, Apple Calendar, or other external synchronization.
- Reminders, email, push notifications, or alarms.
- Due times, time zones, or all-day versus timed events.
- Recurring tasks.
- Date ranges, start dates, or multi-day tasks.
- Custom priority names, colors, or numeric scores.
- Automatic priority recommendations.
- Automatic rescheduling.
- Drag-and-drop calendar editing.
- Editing a task's due date or priority after creation.
- Filtering across every group in one combined calendar.
- Changes to existing task-assignment or completion permissions.

## 7. Business rules

1. Every newly created task must have exactly one valid due date and one valid priority.
2. A due date may be today, in the future, or in the past. Allowing past dates supports recording already-overdue work and avoids date-dependent creation failures.
3. A due date is stored as an ISO calendar-date string in `YYYY-MM-DD` format.
4. Priority is stored as lowercase `low`, `medium`, or `high` and displayed as Low, Medium, or High.
5. The priority selector defaults to `medium`, but the due date must be intentionally selected or confirmed by the person creating the task.
6. Only incomplete tasks can be labeled overdue or due today.
7. A task becomes overdue when its due date is earlier than the current local date and its status is `incomplete`.
8. Completing an overdue task removes the overdue label but does not change its due date.
9. Calendar access follows the existing group-access rule: only a member of a group may view that group's tasks.
10. Any group member may create a dated, prioritized task under the existing task-creation rule.
11. Only the assigned profile may mark the task complete under the existing completion rule.
12. Calendar navigation and switching between task-list and calendar views do not alter saved task data.

## 8. User workflows

### 8.1 Create a dated, prioritized task

1. A current user selects one of their groups.
2. The user enters the existing required title and description.
3. The user selects one assignee from the group's members.
4. The user selects a due date using a date input.
5. The user selects Low, Medium, or High priority.
6. The application validates all existing and new task fields.
7. The application saves one incomplete task with its due date and priority.
8. The interface confirms creation or displays one clear error.

### 8.2 View the enhanced task list

1. A member selects a group.
2. The application loads all tasks for that group.
3. Each task displays its existing fields plus due date and priority.
4. An incomplete task due before today displays `Overdue`.
5. An incomplete task due today displays `Due today`.
6. A completed task continues to display its due date and priority but shows neither date-status label.

### 8.3 View tasks on the calendar

1. A member selects a group and opens the Calendar view.
2. The current month is displayed initially.
3. Tasks whose due dates fall within the displayed month appear on the correct date.
4. Each calendar task entry shows at least the title, priority, assignee, and completion status.
5. The member moves to the previous or next month when needed.
6. If the displayed month contains no tasks, the calendar remains visible and a no-tasks message is shown.

## 9. Functional requirements

### CAL-01 — Create a task with a due date

**Description:** The application shall require one valid due date when a group member creates a task. The date shall be saved with the task without changing the existing title, description, assignee, membership, or initial-status rules.

**Acceptance criteria:**

- **Normal case — Given** Alex is creating a valid task in a selected group, **when** Alex selects July 25, 2026 and submits the task, **then** one incomplete task is created with due date `2026-07-25`.
- **Today case — Given** task creation is available, **when** the selected due date is the current local date, **then** the task is created successfully.
- **Past-date case — Given** task creation is available, **when** a valid past date is selected, **then** the task is created and is immediately considered overdue while incomplete.
- **Missing-date case — Given** all other fields are valid, **when** no due date is supplied, **then** no task is created and a due-date-required error is displayed.
- **Invalid-date case — Given** core logic receives a nonexistent or incorrectly formatted date, **when** creation is attempted, **then** no task is created and an invalid-due-date error is returned.
- **Storage-error case — Given** the task cannot be saved, **when** valid input is submitted, **then** failure is reported and the task is not presented as created.

### CAL-02 — Create a task with a priority

**Description:** The application shall require exactly one priority value. The interface shall offer Low, Medium, and High, with Medium selected by default. Core logic and storage shall reject every other value.

**Acceptance criteria:**

- **Normal cases — Given** task creation is available, **when** Low, Medium, or High is submitted with otherwise valid data, **then** the matching lowercase value is stored.
- **Default case — Given** the task form is first displayed, **when** the user does not change the priority selector, **then** Medium is submitted.
- **Missing-priority case — Given** core logic receives no priority, **when** creation is attempted, **then** no task is created and a priority-required error is returned.
- **Invalid-priority case — Given** core logic receives `urgent`, different capitalization, or another unsupported value, **when** creation is attempted, **then** no task is created and an invalid-priority error is returned.

### CAL-03 — Display due dates and priorities in the task list

**Description:** Every task in the selected group's task list shall display its due date and priority in addition to the existing title, description, assignee, and status fields.

**Acceptance criteria:**

- **Normal case — Given** a selected group has dated tasks of different priorities, **when** a member views the task list, **then** every task shows a human-readable due date and Low, Medium, or High priority.
- **Group-isolation case — Given** two groups have dated tasks, **when** a member selects one group, **then** only that group's tasks are displayed.
- **Empty case — Given** the selected group has no tasks, **when** the list is opened, **then** the existing no-tasks message is displayed.
- **Load-error case — Given** task data cannot be loaded, **when** the task list is opened, **then** no partial list is shown and one controlled task-load error is displayed.

### CAL-04 — Identify overdue and due-today tasks

**Description:** The application shall calculate date status using the current local date at display time. It shall label incomplete past-due tasks `Overdue` and incomplete tasks due on the current date `Due today`.

**Acceptance criteria:**

- **Overdue case — Given** an incomplete task was due yesterday, **when** it is displayed, **then** it shows `Overdue`.
- **Due-today case — Given** an incomplete task is due today, **when** it is displayed, **then** it shows `Due today`.
- **Future case — Given** an incomplete task is due after today, **when** it is displayed, **then** it shows neither label.
- **Completed case — Given** a completed task has a past or current due date, **when** it is displayed, **then** it shows neither `Overdue` nor `Due today`.
- **Boundary case — Given** the local date changes between application reruns, **when** tasks are displayed again, **then** labels are recalculated without modifying stored records.

### CAL-05 — Display a monthly calendar for the selected group

**Description:** The application shall provide an in-app monthly calendar showing the selected group's tasks on their due dates. The calendar shall initially show the current month and shall include both incomplete and complete tasks.

**Acceptance criteria:**

- **Normal case — Given** the selected group has tasks due on July 10 and July 25, **when** July 2026 is displayed, **then** each task appears on its correct date.
- **Required-detail case — Given** a task appears on the calendar, **when** the member views its entry, **then** the title, priority, assignee, and completion status are visible.
- **Month-boundary case — Given** tasks are due on the last day of one month and first day of the next, **when** each month is displayed, **then** only the task belonging to that displayed month appears.
- **Access case — Given** Alex is not a member of another group, **when** Alex uses the normal workflow, **then** that group's calendar cannot be selected or viewed.
- **Empty-month case — Given** the selected month has no tasks, **when** it is displayed, **then** the calendar remains usable and a no-tasks-for-this-month message appears.
- **Load-error case — Given** task data cannot be loaded, **when** the calendar is opened, **then** no partial calendar task data is shown and one controlled error is displayed.

### CAL-06 — Navigate calendar months

**Description:** The application shall allow the member to move to the previous or next calendar month. The chosen month is interface session state and does not need to persist after an application restart.

**Acceptance criteria:**

- **Previous case — Given** July 2026 is displayed, **when** Previous month is selected, **then** June 2026 is displayed.
- **Next case — Given** December 2026 is displayed, **when** Next month is selected, **then** January 2027 is displayed.
- **No-mutation case — Given** tasks exist, **when** a member moves between months, **then** no stored task is created, edited, completed, or deleted.
- **Restart case — Given** a noncurrent month was selected, **when** the application restarts, **then** the calendar returns to the current month.

### CAL-07 — Retain and migrate task scheduling data

**Description:** The application shall retain due dates and priorities with all existing task data. Storage initialization shall upgrade an existing TaskHub database without deleting profiles, groups, memberships, tasks, assignments, or completion statuses.

**Acceptance criteria:**

- **Persistence case — Given** a task has a due date and priority, **when** the application closes and reopens, **then** both values remain unchanged.
- **Relationship case — Given** a saved task is reopened, **when** it is loaded, **then** its existing group, title, description, assignee, and completion status also remain unchanged.
- **Migration case — Given** an existing database contains tasks created before this enhancement, **when** updated storage initialization runs, **then** the database opens without data loss and each old task receives a documented fallback due date and `medium` priority.
- **Repeat-initialization case — Given** the database has already been upgraded, **when** initialization runs again, **then** it does not overwrite due dates or priorities.
- **Migration-failure case — Given** the database cannot be upgraded safely, **when** initialization runs, **then** a controlled saved-data-unavailable error is shown and the database is not silently replaced.

## 10. Compatibility and migration decision

The existing `tasks` table contains records without due dates or priorities. The implementation must add both columns safely.

Recommended migration behavior:

- Add `due_date` as a text column using ISO `YYYY-MM-DD` values.
- Add `priority` with allowed values `low`, `medium`, or `high`.
- Give existing tasks `medium` priority.
- Give existing tasks a single documented fallback due date chosen at migration time, such as the local migration date.
- Apply stronger validation to all newly created tasks through core logic.
- Do not delete and recreate the database.

The fallback due-date decision should be recorded in the design document before implementation because the old data contains no information from which a real due date can be inferred.

## 11. Interface requirements

1. The existing Create task section shall include a date input labeled `Due date`.
2. The existing Create task section shall include a priority selector labeled `Priority` with Low, Medium, and High options.
3. Medium shall be the initial priority selection.
4. The group task area shall allow switching between `Task list` and `Calendar` views.
5. Dates shall use one consistent human-readable format throughout the interface.
6. Priority shall not be communicated by color alone; its text label must always be visible.
7. Overdue and due-today states shall use visible text, not color alone.
8. The interface shall call core logic and shall not contain SQL or duplicate validation rules.
9. Changing current user or selected group shall reset calendar view state as needed so inaccessible group data is not retained on screen.

## 12. Data requirements

Each task record returned by storage and core logic shall include:

- `task_id`
- `group_id`
- `title`
- `description`
- `assignee_id`
- `assignee_username` where the existing query supplies it
- `status`
- `due_date`
- `priority`

Storage constraints should reject unsupported priority values. Date-format and real-calendar-date validation belong in core logic and should also be tested at the storage boundary where practical.

## 13. Non-functional requirements

### 13.1 Usability

- A beginner user should be able to create a scheduled task without typing a date format manually.
- Calendar navigation labels must be understandable without instructions.
- Empty states and errors must be distinguishable from successful empty results.

### 13.2 Reliability and data integrity

- Invalid due dates or priorities must not create partial task records.
- Database migration must run transactionally where SQLite permits it.
- Initialization must be safe to run more than once.
- Existing application data must not be discarded to complete the upgrade.

### 13.3 Performance

- The calendar should load only the selected group's tasks.
- For the expected local capstone data size, task-list and calendar views should appear without a noticeable delay.

### 13.4 Maintainability

- Date and priority validation shall be centralized in `taskhub/core.py`.
- SQLite schema, migration, and queries shall remain in `taskhub/storage.py`.
- Streamlit widgets and display behavior shall remain in `app.py`.
- The enhancement shall not require a new external package unless the later design review proves Streamlit cannot provide an acceptable calendar using the current dependency set.

### 13.5 Accessibility

- Priority, status, overdue state, and due-today state must have text labels.
- Calendar entries must remain understandable when color is unavailable.

## 14. Testing requirements

Automated tests shall cover:

- All three accepted priority values and unsupported values.
- Valid past, current, future, leap-day, and invalid calendar dates.
- Missing due date and missing priority.
- Creation and retrieval of the two new fields.
- Persistence after reconnecting to SQLite.
- Migration of an existing database containing old task records.
- Repeated initialization after migration.
- Overdue, due-today, future, and completed-task date-state calculations using an injected or supplied test date rather than the computer's real date.
- Calendar month filtering, including December-to-January and leap-year boundaries.
- Existing task permissions and completion behavior after the schema change.
- A full workflow that creates, displays, completes, and reopens a dated, prioritized task.

The manual checklist shall cover:

- Date-picker and priority-selector behavior.
- Task-list display.
- Calendar placement and month navigation.
- Empty month and empty group behavior.
- Overdue and due-today labels.
- Completed task appearance.
- User and group switching.
- Restart persistence.
- Upgrade of a copy of an existing database before upgrading the real local database.

## 15. Requirement traceability

| Requirement | Responsible components | Primary verification |
| --- | --- | --- |
| CAL-01 Due date at creation | `core.py`, `storage.py`, `app.py` | Core, storage, workflow, and manual tests |
| CAL-02 Priority at creation | `core.py`, `storage.py`, `app.py` | Core, storage, workflow, and manual tests |
| CAL-03 Enhanced task list | `storage.py`, `core.py`, `app.py` | Storage, core, workflow, and manual tests |
| CAL-04 Date-state labels | `core.py`, `app.py` | Core and manual tests |
| CAL-05 Monthly calendar | `storage.py`, `core.py`, `app.py` | Core, workflow, and manual tests |
| CAL-06 Month navigation | `app.py` session state | Manual interface tests |
| CAL-07 Persistence and migration | `storage.py` | Storage and workflow tests |

## 16. Dependencies and constraints

- Python remains the application language.
- Streamlit remains the only final user interface.
- SQLite through Python's `sqlite3` remains the data store.
- `unittest` remains the automated test framework.
- Python's standard `datetime` and `calendar` modules are sufficient for date validation, calculations, and calendar layout.
- No network access is required for this feature.
- Existing AI username behavior remains isolated and unchanged.

## 17. Approved implementation decisions

The following decisions were approved before implementation:

1. Every new task requires a due date.
2. Priorities are limited to Low, Medium, and High.
3. Medium is the default priority.
4. Past due dates are allowed.
5. The calendar shows one selected group at a time.
6. Both incomplete and complete tasks appear on the calendar.
7. The calendar is internal to TaskHub and does not sync externally.
8. Due dates and priorities cannot be edited after creation because task editing remains outside scope.
9. Old tasks are preserved and receive migration fallback values.

Existing tasks receive the local calendar date on which migration runs as their fallback due date and receive `medium` priority. If any approved decision changes, the affected business rules and acceptance criteria must be revised before coding continues.

## 18. Definition of done

The enhancement is complete when:

1. CAL-01 through CAL-07 meet every acceptance criterion.
2. Existing TaskHub automated tests still pass.
3. New automated tests pass without using the live date for deterministic business-rule checks.
4. The manual calendar and priority checklist passes.
5. A copy of an existing TaskHub database upgrades without losing existing records or relationships.
6. Due dates and priorities persist after restart.
7. The original specification's non-goal statements are updated so they no longer incorrectly exclude the implemented feature.
8. The design, implementation task plan, README, and manual checklist are updated consistently before the feature is described as complete.
