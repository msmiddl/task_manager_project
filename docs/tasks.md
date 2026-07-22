# Implementation Tasks

This plan divides TaskHub into small, ordered coding sessions. Each behavior is tested when it is introduced. The first usable feature—creating and displaying a saved user profile—appears in Phase 3 before group, task, or AI work begins.

No optional or non-goal features are included. REQ-09 is isolated from the core application, but it is still required for the completed MVP.

## Phase 1: Repository and environment

### T01 — Confirm the repository baseline

- **Requirement IDs supported:** Project-wide support
- **Description:** Confirm that the project is being developed inside the correct Git repository. Record the current branch and existing files before adding application code. Confirm that the existing `README.md` and approved project documents are present. Do not change or remove unrelated student files.
- **Files expected to change:** None
- **Dependencies on earlier tasks:** None
- **Verification method:** Run repository-status and file-list commands from the project root; confirm that the intended repository and branch are shown.
- **Completion criteria:** The student can identify the project root, active branch, and existing files, and no unrelated work has been overwritten.

### T02 — Define the local Python environment

- **Requirement IDs supported:** REQ-09 and project-wide execution
- **Description:** Record the two approved external packages, Streamlit and `google-genai`, in the dependency file. Add ignore rules for the virtual environment, Python cache files, the local database, and local secret files. Create the environment locally and install the dependencies.
- **Files expected to change:** `requirements.txt`, `.gitignore`
- **Dependencies on earlier tasks:** T01
- **Verification method:** Activate the environment and verify that Python can import Streamlit and the Google Gen AI package. Check that database and secret files are ignored.
- **Completion criteria:** The approved dependencies import successfully, and generated data and secrets will not be committed.

## Phase 2: Project skeleton

### T03 — Create the approved folder and module skeleton

- **Requirement IDs supported:** Project-wide support
- **Description:** Create only the approved application package, test folder, data folder, and empty module files. Add a minimal Streamlit page that proves the application can start. Do not add business rules or database tables yet.
- **Files expected to change:** `app.py`, `taskhub/__init__.py`, `taskhub/core.py`, `taskhub/storage.py`, `taskhub/ai_service.py`, `tests/__init__.py`, `data/`
- **Dependencies on earlier tasks:** T02
- **Verification method:** Import each module from Python and start the Streamlit page locally.
- **Completion criteria:** All four main Python files import without errors, and the local page opens with a TaskHub heading or other placeholder text.

## Phase 3: First vertical slice

The first vertical slice implements one complete profile-creation path:

**username input → validation → profile-creation rule → SQLite save → displayed profile → automated test**

### T04 — Store and retrieve user profiles

- **Requirement IDs supported:** REQ-01, REQ-08
- **Description:** Add storage initialization for the `users` table, exact unique usernames, profile creation, exact username lookup, and profile listing. Enable SQLite relationship enforcement whenever a connection is opened, even though later tables will use it more directly. Use a temporary database in tests.
- **Files expected to change:** `taskhub/storage.py`, `tests/test_storage.py`
- **Dependencies on earlier tasks:** T03
- **Verification method:** Automated storage tests create `Alex`, retrieve it, reopen the database, and confirm it remains. Tests also confirm that exact duplicate `Alex` is rejected while `alex` is distinct.
- **Completion criteria:** User profiles can be saved, listed, looked up exactly, and retained after reconnecting; all new storage tests pass.

### T05 — Validate and create a profile through core logic

- **Requirement IDs supported:** REQ-01
- **Description:** Add core behavior for validating usernames and coordinating profile creation with storage. Enforce 2–30 total characters, reject empty or whitespace-only values, preserve capitalization and spaces, and reject only exact duplicates. Profile creation does not include current-user selection; that separate interface behavior begins in T07.
- **Files expected to change:** `taskhub/core.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T04
- **Verification method:** Automated tests cover lengths 1, 2, 30, and 31; blank and whitespace-only values; `Alex` versus `alex`; and exact duplicates. No current-user session state is introduced by this task.
- **Completion criteria:** Valid profiles are created through core logic, invalid profiles do not change storage, and all profile core tests pass.

### T06 — Complete the profile-creation vertical slice in Streamlit

- **Requirement IDs supported:** REQ-01, REQ-08
- **Description:** Add a username input and create-profile action to the interface. Call core logic, display saved profiles, and show safe success or validation messages. The interface must not repeat username rules or execute SQL.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T05
- **Verification method:** Manual vertical-slice check: enter `Alex`, see it saved and displayed, restart the application, and confirm it remains. Submit a blank value and an exact duplicate and confirm that no extra profile appears.
- **Completion criteria:** The full input-to-output path works locally, saved data survives restart, invalid input is rejected visibly, and the T04–T05 automated tests still pass.

## Phase 4: Remaining MVP requirements

### T07 — Select the current user for the active session

- **Requirement IDs supported:** REQ-02
- **Description:** Display existing profiles in a Streamlit selection control and store the chosen user identifier in session state. Show the required empty state when no profiles exist. Do not automatically select a newly created profile, and do not persist the selection after application restart. If a session identifier no longer matches an existing profile or profiles cannot be loaded, clear the selection and display the approved error.
- **Files expected to change:** `app.py`, `tests/test_storage.py`, `tests/test_workflow.py`
- **Dependencies on earlier tasks:** T06
- **Verification method:** Begin a workflow test that creates two profiles and confirms both exist. Add a storage test for a nonexistent profile identifier. Manually select each profile, test an invalid or stale session identifier, simulate a profile-load failure, refresh through normal Streamlit interactions, and restart the application to confirm the selection resets.
- **Completion criteria:** A valid existing profile can be selected for the active session; no-profile, missing-profile, and load-error behavior is clear; invalid selections are cleared; and restarting requires a new selection.

### T08 — Store groups and creator memberships

- **Requirement IDs supported:** REQ-03, REQ-08
- **Description:** Add the `groups` and `memberships` tables and storage behavior for group creation. Save the new group and its creator membership in one transaction. Add exact global group-name uniqueness and storage queries for groups belonging to one user.
- **Files expected to change:** `taskhub/storage.py`, `tests/test_storage.py`
- **Dependencies on earlier tasks:** T04
- **Verification method:** Automated tests create a group, confirm its creator is a member, retrieve it through the creator’s group list, and reopen storage to confirm persistence. A forced failure verifies that no partial group remains.
- **Completion criteria:** Groups and creator memberships save together, exact duplicates are rejected, user-specific group listing works, and all group storage tests pass.

### T09 — Apply group creation and listing rules

- **Requirement IDs supported:** REQ-03
- **Description:** Add core behavior for group names and current-user group listing. Enforce 2–25 total characters, reject blank and whitespace-only names, preserve capitalization and spaces, and reject exact duplicates.
- **Files expected to change:** `taskhub/core.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T08
- **Verification method:** Automated tests cover lengths 1, 2, 25, and 26; whitespace; `Roommates` versus `roommates`; exact duplicates; creator membership; and group lists containing only the selected user’s groups.
- **Completion criteria:** Core group rules match REQ-03, invalid requests do not change storage, and all group core tests pass.

### T10 — Add group creation and selection to the interface

- **Requirement IDs supported:** REQ-03
- **Description:** Display the current user’s groups, provide group-name input, and allow one accessible group to be selected in session state. Show the no-groups message when appropriate. Reset the selected group when the current user changes or the application restarts.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T07, T09
- **Verification method:** Manually select Alex, create `Roommates`, confirm it appears, select it, switch users, and confirm an inaccessible group is not selectable.
- **Completion criteria:** Group creation, listing, selection, empty-state behavior, and user-switch reset all work without SQL or duplicated validation in `app.py`.

### T11 — Store additional group memberships

- **Requirement IDs supported:** REQ-04, REQ-08
- **Description:** Add only the storage operations needed to add an existing user to a group, check a membership, and list group members. Enforce a unique user-group pair and valid user and group references.
- **Files expected to change:** `taskhub/storage.py`, `tests/test_storage.py`
- **Dependencies on earlier tasks:** T08
- **Verification method:** Automated tests add Jordan to Roommates, list both members, reject a duplicate membership, reject missing record references, and confirm membership after reconnecting.
- **Completion criteria:** Memberships can be added, checked, listed, and persisted without duplicates or invalid references.

### T12 — Apply member-addition permissions and exact lookup

- **Requirement IDs supported:** REQ-04
- **Description:** Add core behavior that permits only the group creator to add a profile by exact username. Reject missing usernames, capitalization mismatches, all existing memberships including the creator, and noncreator attempts.
- **Files expected to change:** `taskhub/core.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T11
- **Verification method:** Automated tests cover a successful Jordan addition, `Jordan` versus `jordan`, a missing user, duplicate Jordan, duplicate creator, and a noncreator attempt.
- **Completion criteria:** Only the creator can add one exact existing username, all invalid cases leave membership unchanged, and tests pass.

### T13 — Add group-member management to the interface

- **Requirement IDs supported:** REQ-04
- **Description:** Show the selected group’s current members. Show exact-username member entry only when the current user is the group creator. Display success, not-found, duplicate, and permission messages without displaying a list of users available to add.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T10, T12
- **Verification method:** Manually add Jordan as Alex, confirm Jordan appears once, try the wrong capitalization, switch to Jordan, and confirm that the normal interface does not offer creator-only addition.
- **Completion criteria:** The approved exact-username membership flow works and no unapproved available-user list appears.

### T14 — Store assigned tasks

- **Requirement IDs supported:** REQ-05, REQ-08
- **Description:** Add the `tasks` table and storage behavior for creating one assigned task. Require valid group and assignee references, restrict status to `incomplete` or `complete`, and always create tasks as `incomplete`. Add task lookup needed by later completion logic.
- **Files expected to change:** `taskhub/storage.py`, `tests/test_storage.py`
- **Dependencies on earlier tasks:** T11
- **Verification method:** Automated tests save and reopen an assigned task, confirm its fields and initial status, and reject missing references or invalid stored statuses.
- **Completion criteria:** Valid assigned tasks persist with status `incomplete`, invalid relationships and statuses are rejected, and storage tests pass.

### T15 — Apply assigned-task creation rules

- **Requirement IDs supported:** REQ-05
- **Description:** Add core behavior for task creation. Enforce a 1–20 character non-whitespace title, a 1–100 character non-whitespace description, a required assignee, current-user group membership, and assignee membership in the same group.
- **Files expected to change:** `taskhub/core.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T14
- **Verification method:** Automated tests cover every boundary, whitespace-only fields, missing assignee, nonmember assignee, nonmember creator, a one-member self-assignment, and successful creation beginning incomplete.
- **Completion criteria:** Only valid assigned tasks are created, no task is created unassigned, and all creation-rule tests pass.

### T16 — Add task creation to the interface

- **Requirement IDs supported:** REQ-05
- **Description:** Add task-title and description inputs and an assignee selector populated only from selected-group members. Submit through core logic and show safe success or validation messages.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T13, T15
- **Verification method:** Manually create a valid task for Jordan, confirm no blank assignee can be submitted, and verify that users outside the group cannot be selected.
- **Completion criteria:** A group member can create one valid assigned task from the interface, and invalid task input does not create a record.

### T17 — Retrieve tasks with assignee display data

- **Requirement IDs supported:** REQ-06
- **Description:** Add the storage query for all tasks in one group, including the assignee username. Add core behavior that verifies current-user membership and marks which returned tasks belong to the current user.
- **Files expected to change:** `taskhub/storage.py`, `taskhub/core.py`, `tests/test_storage.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T14, T15
- **Verification method:** Storage tests confirm only the selected group’s tasks and assignee names are returned. Core tests confirm nonmember access is rejected and only the current user’s tasks receive the assignment marker.
- **Completion criteria:** Task display data is complete, restricted to accessible groups, and correctly identifies current-user assignments.

### T18 — Display group tasks in Streamlit

- **Requirement IDs supported:** REQ-06
- **Description:** Display all selected-group tasks with title, description, assignee, and status. Display `Assigned to you` only when the core result marks the task as the current user’s. Show a no-tasks message for an empty group.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T16, T17
- **Verification method:** Manually view tasks assigned to Alex and Jordan as each current user, confirm all four fields, confirm the label moves correctly, and confirm the empty state in a group with no tasks.
- **Completion criteria:** REQ-06 is observable in the interface and no inaccessible group tasks are displayed.

### T19 — Persist the one-way completion update

- **Requirement IDs supported:** REQ-07, REQ-08
- **Description:** Add the storage update that changes an existing incomplete task to complete and never changes a completed task back to incomplete. Return enough information for core logic to distinguish a missing task from an unchanged completed task.
- **Files expected to change:** `taskhub/storage.py`, `tests/test_storage.py`
- **Dependencies on earlier tasks:** T14
- **Verification method:** Automated tests complete a task, reconnect, confirm it remains complete, repeat completion without a second change, and try a missing task identifier.
- **Completion criteria:** Completion is one-way, persistent, and distinguishable from missing-task behavior.

### T20 — Apply assignee-only completion rules

- **Requirement IDs supported:** REQ-07
- **Description:** Add core behavior that checks task existence, accessible-group membership, assignee identity, and current status before calling the storage update. Return the approved already-complete message on a repeated assignee attempt.
- **Files expected to change:** `taskhub/core.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T17, T19
- **Verification method:** Automated tests cover successful assignee completion, nonassignee rejection, missing task, inaccessible group, already-complete task, and no assigned incomplete tasks.
- **Completion criteria:** Only the current assignee can complete an incomplete accessible task, and every rejection leaves status unchanged.

### T21 — Add task completion controls to the interface

- **Status:** Complete
- **Requirement IDs supported:** REQ-07
- **Description:** Show completion controls only for the current user’s assigned incomplete tasks. Call core completion logic, reload the task list after success, and show already-complete or permission messages if the underlying state changed before submission.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T18, T20
- **Verification method:** Manually confirm Alex cannot complete Jordan’s task through the normal interface, select Jordan, complete it, see the updated status, and confirm no action returns it to incomplete.
- **Completion criteria:** The approved completion flow is visible, one-way, and limited to the selected assignee profile.

### T22 — Isolate the Google AI request

- **Status:** Complete
- **Requirement IDs supported:** REQ-09
- **Description:** Add one AI-service function that reads the API key from the environment, sends a fixed username-only prompt, and returns raw suggestion text. Convert missing configuration and service failures into a controlled AI-unavailable error. Do not access storage or validate uniqueness in this file.
- **Files expected to change:** `taskhub/ai_service.py`, `tests/test_ai_service.py`
- **Dependencies on earlier tasks:** T02, T03
- **Verification method:** Automated tests use mocked responses to verify raw text, missing-key handling, and simulated service failure without making a live request.
- **Completion criteria:** The AI module has one isolated responsibility, automated tests need no internet, and no password or database data is supplied to the service.

### T23 — Validate and display an AI username suggestion

- **Status:** Complete
- **Requirement IDs supported:** REQ-09
- **Description:** Add core validation for raw AI output using the existing usernames provided as input. Reject blank, whitespace-only, shorter-than-2, longer-than-30, and exact duplicate suggestions. Add a Streamlit action that displays a valid suggestion without creating a profile and displays a controlled error otherwise.
- **Files expected to change:** `taskhub/core.py`, `app.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T05, T22
- **Verification method:** Automated core tests use predetermined valid and invalid suggestions. A manual live check requests one suggestion and confirms that no profile is created automatically.
- **Completion criteria:** A valid unused suggestion can be displayed, invalid or failed suggestions show a controlled error, and all core features remain usable when AI access is unavailable.

## Phase 5: Error handling and edge cases

### T24 — Handle missing and corrupted storage safely

- **Status:** Complete
- **Requirement IDs supported:** REQ-08
- **Description:** Finalize storage startup behavior. A missing database becomes an empty first-use database. An existing file that cannot be opened or queried as valid TaskHub storage produces a controlled error and is not deleted, overwritten, or repaired.
- **Files expected to change:** `taskhub/storage.py`, `tests/test_storage.py`
- **Dependencies on earlier tasks:** T08, T11, T14, T19
- **Verification method:** Automated tests use temporary missing and deliberately invalid files. Confirm the missing case initializes normally and the invalid file remains unchanged after the controlled error.
- **Completion criteria:** Empty first use and corrupted storage produce different observable outcomes, and no damaged file is silently replaced.

### T25 — Complete interface empty states and safe error messages

- **Status:** Complete
- **Requirement IDs supported:** REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09
- **Description:** Review each interface action and ensure expected `ValueError`, `LookupError`, `PermissionError`, and `RuntimeError` messages are caught and displayed safely. Add missing profile, group, member, task, completion, storage, and AI empty/error states. Do not add a logging system.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T21, T23, T24
- **Verification method:** Follow a manual error checklist and confirm that no API key, SQL statement, or stack trace appears in the browser. Run all automated tests to ensure no behavior changed.
- **Completion criteria:** Every specified empty or error case has a visible safe outcome, failed writes are never shown as successful, and the test suite still passes.

### T26 — Complete the end-to-end workflow and persistence test

- **Status:** Complete
- **Requirement IDs supported:** REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08
- **Description:** Finish one integration test using a temporary database: create Alex and Jordan, create Roommates as Alex, add Jordan, create a task for Jordan, reject Alex’s completion attempt, switch to Jordan, verify the assignment marker, complete the task, reconnect, and confirm persistence.
- **Files expected to change:** `tests/test_workflow.py`
- **Dependencies on earlier tasks:** T12, T15, T17, T20, T24
- **Verification method:** Run the workflow test alone and then with the full test suite.
- **Completion criteria:** The complete non-interface MVP flow passes from a clean temporary database and remains correct after reconnecting.

## Phase 6: Documentation and final checks

### T27 — Write setup, run, test, and privacy instructions

- **Status:** Complete
- **Requirement IDs supported:** REQ-08, REQ-09 and project-wide delivery
- **Description:** Document environment setup, dependency installation, application startup, test execution, API-key configuration, local-database behavior, reset session selections, the absence of authentication, and the rule not to enter sensitive information. Create the manual test checklist used in the final review.
- **Files expected to change:** `README.md`, `docs/manual-test-checklist.md`
- **Dependencies on earlier tasks:** T25, T26
- **Verification method:** Follow the README from a clean environment or have another person follow it. Complete the checklist without relying on undocumented steps.
- **Completion criteria:** A beginner can install, run, test, and demonstrate TaskHub from the written instructions without exposing a secret.

### T28 — Run final requirement and demonstration checks

- **Status:** Complete
- **Requirement IDs supported:** REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09
- **Description:** Run the complete automated suite, perform the manual interface and live-AI checklist, verify the two-minute demonstration, and compare the delivered behavior against the specification and traceability table. Fix only defects in approved behavior; do not add features.
- **Files expected to change:** Any approved MVP file only if a verified defect is found; `docs/manual-test-checklist.md` for recorded results
- **Dependencies on earlier tasks:** T27
- **Verification method:** All automated tests pass, every manual checklist item has a result, the live AI failure path is also checked, and the demonstration completes within two minutes.
- **Completion criteria:** Every requirement has passing evidence, no non-goal has been added, no API key or database file is tracked, and the project meets the specification’s Definition of Done.

## Phase 7: Calendar and priority enhancement

### T29 — Integrate the calendar enhancement into project documentation

- **Status:** Complete
- **Requirement IDs supported:** CAL-01, CAL-02, CAL-03, CAL-04, CAL-05, CAL-06, CAL-07
- **Description:** Approve the feature supplement, remove conflicts with the original non-goals, record the migration fallback, extend the technical design, and add an ordered implementation plan. Do not change application code.
- **Files expected to change:** `docs/specification.md`, `docs/design.md`, `docs/tasks.md`, `docs/taskhub-calendar-priority-feature-spec.md`
- **Dependencies on earlier tasks:** T28
- **Verification method:** Review all four documents for consistent scope, migration behavior, dependencies, and requirement traceability.
- **Completion criteria:** The enhancement is approved, every CAL requirement maps to ordered tasks, and no implementation decision remains unresolved.

### T30 — Migrate and store task scheduling fields

- **Status:** Complete
- **Requirement IDs supported:** CAL-01, CAL-02, CAL-03, CAL-07
- **Description:** Add transactional, repeatable storage migration for `due_date` and `priority`. Preserve existing tasks, assign the local migration date and `medium` to old records, add storage constraints, and include both fields in task creation and retrieval.
- **Files expected to change:** `taskhub/storage.py`, `tests/test_storage.py`
- **Dependencies on earlier tasks:** T29
- **Verification method:** Storage tests cover a new database, migration of an old database with tasks, preserved relationships and statuses, repeated initialization, all priorities, persistence, and controlled migration failure.
- **Completion criteria:** Existing and new databases safely expose persistent due dates and priorities without data loss.

### T31 — Validate dated and prioritized task creation

- **Status:** Complete
- **Requirement IDs supported:** CAL-01, CAL-02
- **Description:** Add core validation for required real ISO dates and lowercase priorities, then pass validated values through assigned-task creation. Allow past, current, future, and leap-day dates while rejecting missing or malformed values.
- **Files expected to change:** `taskhub/core.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T30
- **Verification method:** Core tests cover missing values, invalid formats, nonexistent dates, leap-day boundaries, all priorities, unsupported capitalization, permissions, and successful incomplete task creation.
- **Completion criteria:** Only tasks with one valid due date and supported priority reach storage, with existing creation rules unchanged.

### T32 — Add scheduling inputs to task creation

- **Requirement IDs supported:** CAL-01, CAL-02
- **Description:** Add a required Streamlit date input and a Low/Medium/High priority selector defaulting to Medium. Submit normalized values through core and display safe errors without adding another interface or dependency.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T31
- **Verification method:** Manually create past, current, and future tasks at each priority; confirm the default and required-input behavior.
- **Completion criteria:** A group member can create a dated, prioritized task through the existing form.

### T33 — Retrieve scheduling data and calculate date states

- **Requirement IDs supported:** CAL-03, CAL-04
- **Description:** Include due date and priority in selected-group task results and add deterministic core calculation of `Overdue`, `Due today`, or no date label using a supplied local date. Completed tasks receive no date-state label.
- **Files expected to change:** `taskhub/storage.py`, `taskhub/core.py`, `tests/test_storage.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T31
- **Verification method:** Tests cover group isolation, all date states, completed tasks, and recalculation with different supplied dates.
- **Completion criteria:** Accessible task records contain both scheduling fields and the correct nonpersistent date-state result.

### T34 — Display enhanced task-list fields and labels

- **Requirement IDs supported:** CAL-03, CAL-04
- **Description:** Display a consistent human-readable due date, visible priority text, and overdue/due-today text in the existing task list. Preserve current empty, assignment, completion, and error behavior.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T32, T33
- **Verification method:** Manually inspect incomplete past/today/future tasks and completed past tasks at multiple priorities.
- **Completion criteria:** Every displayed task shows due date and priority, and only eligible incomplete tasks show a date-state label.

### T35 — Filter selected-group tasks by calendar month

- **Requirement IDs supported:** CAL-05
- **Description:** Add a simple core function that returns selected-group tasks for a supplied year and month while reusing group-access rules. Do not mutate storage or add cross-group filtering.
- **Files expected to change:** `taskhub/core.py`, `tests/test_core.py`
- **Dependencies on earlier tasks:** T33
- **Verification method:** Tests cover ordinary months, empty months, month boundaries, December-to-January, leap years, both statuses, and nonmember rejection.
- **Completion criteria:** Calendar data is deterministic, group-scoped, and read-only.

### T36 — Add the internal monthly calendar and navigation

- **Requirement IDs supported:** CAL-05, CAL-06
- **Description:** Add Task list/Calendar view selection, a monthly grid built with standard-library calendar data, task details on due dates, empty-month messaging, and previous/next navigation in session state. Reset calendar state when user or group changes.
- **Files expected to change:** `app.py`
- **Dependencies on earlier tasks:** T34, T35
- **Verification method:** Manually verify placement, required entry details, empty months, December/January navigation, user/group switching, restart reset, and absence of data mutation.
- **Completion criteria:** Members can safely view and navigate the selected group's calendar without changing saved tasks.

### T37 — Complete calendar workflow, documentation, and final checks

- **Requirement IDs supported:** CAL-01, CAL-02, CAL-03, CAL-04, CAL-05, CAL-06, CAL-07
- **Description:** Extend the workflow test through dated prioritized creation, display, completion, and reopen; update README and the manual checklist; test migration on a copy of an existing database; and perform final requirement review.
- **Files expected to change:** `tests/test_workflow.py`, `README.md`, `docs/manual-test-checklist.md`
- **Dependencies on earlier tasks:** T30, T31, T34, T36
- **Verification method:** Run focused and full suites, complete the calendar manual checklist, and verify a copied existing database upgrades without loss.
- **Completion criteria:** CAL-01 through CAL-07 have passing automated and manual evidence, original behavior still passes, and documentation describes the enhancement accurately.

## Requirement-to-task traceability

| Requirement | Supporting tasks |
| --- | --- |
| REQ-01 — Create a local user profile | T04, T05, T06, T25, T26, T28 |
| REQ-02 — Select the current user | T07, T25, T26, T28 |
| REQ-03 — Display and create groups | T08, T09, T10, T25, T26, T28 |
| REQ-04 — Add an existing user to a group | T11, T12, T13, T25, T26, T28 |
| REQ-05 — Create an assigned task | T14, T15, T16, T25, T26, T28 |
| REQ-06 — Display group tasks and current-user assignments | T17, T18, T25, T26, T28 |
| REQ-07 — Mark an assigned task complete | T19, T20, T21, T25, T26, T28 |
| REQ-08 — Retain application data | T04, T06, T08, T11, T14, T19, T24, T26, T27, T28 |
| REQ-09 — Suggest an example username using AI | T02, T22, T23, T25, T27, T28 |
| CAL-01 — Create a task with a due date | T29, T30, T31, T32, T37 |
| CAL-02 — Create a task with a priority | T29, T30, T31, T32, T37 |
| CAL-03 — Display due dates and priorities | T29, T30, T33, T34, T37 |
| CAL-04 — Identify overdue and due-today tasks | T29, T33, T34, T37 |
| CAL-05 — Display a monthly group calendar | T29, T35, T36, T37 |
| CAL-06 — Navigate calendar months | T29, T36, T37 |
| CAL-07 — Retain and migrate scheduling data | T29, T30, T37 |
