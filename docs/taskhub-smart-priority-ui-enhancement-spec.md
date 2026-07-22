# TaskHub Smart Priority and Interface Enhancement Specification

## 1. Overview

This post-MVP enhancement makes TaskHub more useful and visually polished by adding one focused AI feature and several small interface improvements. It builds on the approved task due-date, fixed-priority, and internal-calendar enhancement.

The enhancement includes:

1. Optional AI priority recommendations.
2. Group dashboard metrics.
3. A group completion progress bar.
4. Consistent priority indicators and overdue warnings.
5. Task filtering and sorting.
6. Cleaner task cards.
7. Clear success and empty-state messages.

The work must reuse existing TaskHub business logic and storage wherever possible. Interface code shall coordinate and display data rather than duplicate validation, permission, or persistence rules.

## 2. Relationship to existing scope

This specification is an extension of the approved TaskHub MVP and calendar-priority specification. Existing requirements remain unchanged unless this document explicitly extends them.

This specification does not authorize:

- Task editing, deletion, or reassignment.
- Returning completed tasks to incomplete.
- Recurring tasks, reminders, or notifications.
- External calendar synchronization.
- AI task assignment.
- Automatic AI requests.
- Member workload or preference analysis.
- Cloud deployment or real-time synchronization.
- A new UI framework or new dependency.

If an existing project document conflicts with this approved enhancement, implementation must stop until the documents are reconciled. In particular, the main specification currently limits AI to username suggestions; that statement must be updated before this feature is marked complete.

## 3. Design principles

- **Beginner-appropriate:** Prefer small functions and existing Python and Streamlit capabilities.
- **User-controlled AI:** AI recommends but never creates or changes a task automatically.
- **Core independence:** AI failure must not block normal task creation.
- **Deterministic calculations:** Counts, date categories, progress, filtering, and sorting are calculated locally rather than by AI.
- **No duplicated business rules:** Existing validation and permission functions remain the source of truth.
- **No unnecessary persistence:** Display settings and AI explanations remain session-only unless already approved elsewhere.
- **One task at a time:** Each implementation task in Section 16 must be completed and verified separately.

## 4. Definitions

- **Today:** The application's local calendar date.
- **Overdue task:** An incomplete task with a due date before today.
- **Due today:** A task whose due date equals today.
- **Due soon:** An incomplete task due from today through six days after today, inclusive.
- **Completion percentage:** Completed tasks divided by all tasks in the selected group, multiplied by 100.
- **Baseline priority:** A locally calculated priority based on the due date.
- **AI recommendation:** A validated `low`, `medium`, or `high` suggestion and short reason returned by the AI service.
- **Effective priority:** The value currently selected in the task-creation form and saved if the form is submitted.

## 5. Shared display rules

### 5.1 Priority display

TaskHub shall use the same indicator wherever a task priority appears:

| Stored value | Display |
| --- | --- |
| `high` | 🔴 High |
| `medium` | 🟡 Medium |
| `low` | 🟢 Low |

Color or emoji shall not be the only information provided; the text label must also be shown.

### 5.2 Date display

- Dates shall be stored and compared using the approved calendar feature's date representation.
- Displayed dates shall use one consistent human-readable format throughout the interface.
- Only incomplete tasks may be labeled overdue.
- Completed tasks with past due dates shall remain complete and shall not display an overdue warning.

### 5.3 Stable task order

When two tasks have equal values for the selected sort field, their task identifier or existing creation order shall be used as a stable final tie-breaker.

## 6. Functional requirements

### REQ-SPUI-01 — Calculate a baseline priority

**Description:** TaskHub shall calculate a baseline priority locally from today and a valid due date.

| Days until due | Baseline |
| --- | --- |
| 0–3 | `high` |
| 4–7 | `medium` |
| 8 or more | `low` |

If an overdue date reaches this calculation through an already valid workflow, the baseline is `high`. This does not independently permit invalid task dates.

**Acceptance criteria:**

- Due today and due in three days produce `high`.
- Due in four and seven days produce `medium`.
- Due in eight or more days produces `low`.
- Missing or invalid due dates produce a validation error and no AI request.
- The calculation works without internet access.

### REQ-SPUI-02 — Request an AI priority recommendation

**Description:** During task creation, a group member may explicitly request an AI priority recommendation. TaskHub may send only the validated title, validated description, today, due date, baseline priority, and response instructions.

The prompt shall instruct the AI to:

- Return only `low`, `medium`, or `high` plus a concise reason.
- Begin with the calculated baseline.
- Adjust by no more than one priority level based on apparent importance.
- Never lower a `high` baseline for a task due within three days.
- Avoid claiming knowledge that is not present in the submitted task text.

**Acceptance criteria:**

- No AI request occurs until the person clicks the recommendation control.
- Invalid title, description, or due date prevents the request and identifies the invalid field.
- A request contains no username, group name, assignee data, password, API key, other task, or task history.
- The existing approved AI dependency is reused; no new dependency is required.

### REQ-SPUI-03 — Validate and apply an AI recommendation

**Description:** A result is valid only if its trimmed, case-normalized priority is `low`, `medium`, or `high`, and its trimmed reason is nonblank and no more than 120 characters.

A valid result shall be labeled **AI recommendation**, displayed with its reason, and may update the effective priority selection. The person may override it before task submission. The recommendation alone shall never save or create a task.

**Acceptance criteria:**

- Valid results for all three priority values are accepted.
- Capitalization and outer whitespace are normalized.
- An unknown priority, blank reason, or reason over 120 characters is rejected.
- The person can accept or override a valid recommendation.
- Requesting or receiving a recommendation does not create a task.
- Only the final effective priority is persisted; the recommendation reason and origin are not stored.

### REQ-SPUI-04 — Handle unavailable or stale AI results

**Description:** Missing configuration, service failure, timeout, invalid output, or unexpected AI errors shall display a controlled message without losing task-form data or blocking manual priority selection.

Changing the title, description, or due date after a recommendation makes it stale. The interface shall clear it or mark it visibly stale and shall not automatically request another result.

**Acceptance criteria:**

- AI failure preserves valid title, description, due date, assignee, and manual priority input.
- Manual task creation remains available after AI failure.
- Error messages do not expose credentials or raw secrets.
- Changing title, description, or due date invalidates the previous recommendation.
- Changing assignee alone does not invalidate it because assignee data is not an AI input.
- No input change triggers an automatic AI request.

### REQ-SPUI-05 — Display group dashboard metrics

**Description:** For the selected group, TaskHub shall display four summary metrics calculated from that group's tasks:

- Total tasks.
- Incomplete tasks.
- Complete tasks.
- Due soon tasks.

**Acceptance criteria:**

- Only tasks from the selected group contribute to the metrics.
- `total = incomplete + complete`.
- Due soon counts only incomplete tasks due from today through six days after today.
- Overdue tasks are not included in due soon.
- A group with no tasks displays zero for all four metrics rather than an error.
- A task-loading failure displays an error and does not present misleading zero values.

### REQ-SPUI-06 — Display completion progress

**Description:** TaskHub shall display the selected group's completed count, total count, and completion percentage using a Streamlit progress indicator.

**Acceptance criteria:**

- Zero total tasks produces `0 of 0 tasks complete` and a zero-percent progress bar.
- Three completed tasks out of eight produces `3 of 8 tasks complete` and 37.5 percent before any display rounding.
- All tasks complete produces 100 percent.
- The progress value updates after an authorized task is marked complete.
- The displayed value is never below 0 percent or above 100 percent.

### REQ-SPUI-07 — Display priority and overdue indicators

**Description:** Every task card shall display the consistent priority indicator from Section 5.1. An incomplete task due before today shall additionally display `⚠️ Overdue`.

**Acceptance criteria:**

- High, medium, and low tasks display both their correct icon/color cue and text.
- An incomplete task due yesterday is labeled overdue.
- An incomplete task due today is not labeled overdue.
- A completed task with a past due date is not labeled overdue.
- The indicator does not change stored task data.

### REQ-SPUI-08 — Filter displayed tasks

**Description:** The task view shall provide one status/ownership filter and one priority filter.

The status/ownership choices are:

- All tasks.
- Assigned to me.
- Incomplete.
- Complete.

The priority choices are:

- All priorities.
- High.
- Medium.
- Low.

The two filters combine using AND logic. Filters affect only the displayed collection and never modify stored tasks.

**Acceptance criteria:**

- All tasks and all priorities display every task in the selected group.
- Assigned to me displays only tasks assigned to the current user.
- Incomplete and High displays only tasks satisfying both conditions.
- A filter with no matches displays a no-matching-tasks message rather than an error.
- Changing or clearing a filter does not change the database.
- Selecting a different group resets filters to their documented defaults or reapplies them only to the newly selected group; it must never display tasks from the previous group.

### REQ-SPUI-09 — Sort displayed tasks

**Description:** The task view shall provide these sort choices:

- Due date: earliest first.
- Priority: high, then medium, then low.
- Assignee: username in case-sensitive ascending order consistent with existing username rules.
- Status: incomplete before complete.

Sorting occurs after filtering and affects only display order.

**Acceptance criteria:**

- Each option produces its defined order.
- Equal values use the stable tie-breaker from Section 5.3.
- Sorting an empty or one-task list succeeds without error.
- Sorting never modifies stored tasks.

### REQ-SPUI-10 — Withdrawn

**Status:** Withdrawn by approved scope revision.

The separate Upcoming tasks dashboard section is no longer required. The
dashboard retains group metrics and completion progress, and the Task list is
the default detailed view. Requirement numbering is preserved so later
requirement identifiers remain stable.

### REQ-SPUI-11 — Display clean task cards

**Description:** Each displayed task shall use a consistent bordered container or equivalent Streamlit layout showing:

- Title.
- Description.
- Assignee.
- Due date.
- Priority indicator.
- Status.
- `Assigned to you` when applicable.
- Overdue warning when applicable.
- Existing completion control only when the current user is allowed to use it.

**Acceptance criteria:**

- All required fields are visible without relying only on color.
- Tasks assigned to the current user show `Assigned to you`; other tasks do not.
- Existing completion permissions remain unchanged.
- Cards do not add edit, delete, reassign, or return-to-incomplete controls.
- Long descriptions within the existing approved limit remain readable.

### REQ-SPUI-12 — Display success and empty-state messages

**Description:** The interface shall provide understandable feedback after successful actions and helpful messages for valid empty results.

Required success messages include:

- Profile created.
- Group created.
- Member added.
- Task created.
- Task marked complete.

Required empty states include:

- No profiles yet.
- No groups for the current user.
- No tasks in the selected group.
- No tasks match the selected filters.
- No assigned incomplete tasks available for completion.

**Acceptance criteria:**

- A success message appears only after the corresponding operation succeeds.
- A failed save or validation does not display success.
- Empty states are visually distinct from errors.
- Empty-state messages identify a reasonable next action where one exists.
- Existing controlled error messages remain available.

## 7. Interface organization

The preferred Streamlit organization is:

- **Sidebar:** Current-user and selected-group controls.
- **Dashboard area:** Metrics and completion progress.
- **Tasks tab:** Task creation, AI recommendation, filters, sorting, and task cards.
- **Calendar tab:** Existing approved internal calendar behavior.
- **Members tab:** Existing group-membership behavior.

This layout is a preferred implementation, not permission to redesign working workflows. If the current interface already has a clear tab structure, the enhancement should fit into it with the smallest correct changes.

## 8. Business logic and interface boundaries

Business or core functions should perform:

- Baseline-priority calculation.
- AI response validation.
- Date classification.
- Metric calculation.
- Completion-percentage calculation.
- Task filtering.
- Task sorting.

The interface should perform:

- Reading Streamlit widget values.
- Calling existing core, storage, and AI-service functions.
- Maintaining temporary display state.
- Rendering metrics, progress, cards, labels, filters, and messages.
- Translating controlled exceptions or results into understandable feedback.

Storage remains responsible only for persistence and retrieval. The AI service wrapper remains isolated from core task creation.

### 8.1 Approved implementation decisions

- The existing linear Streamlit workflow remains in place. Dashboard metrics, filters, and cards are added around the working controls; a full sidebar/tab redesign is not required.
- The AI service returns two plain-text lines: the normalized priority on line one and the concise reason on line two. Additional nonblank lines are invalid. The prompt forbids a pipe-delimited or Markdown response so parsing stays beginner-friendly.
- An overdue baseline and a baseline due within zero through three days remain `high`; AI may not lower either one.
- Requesting a recommendation displays it and updates the temporary priority selector. The person may change the selector before creating the task, and only that final selector value is saved.
- The title, description, due date, recommended priority, reason, and recommendation-input snapshot remain only in Streamlit session state. They are never written to SQLite.
- Changing title, description, or due date clears the recommendation through an interface callback. Changing only the assignee or manual priority does not clear it and never triggers a new request.
- Derived collection helpers accept a supplied local date when date boundaries matter. This keeps automated tests deterministic.
- Filters default to `All tasks` and `All priorities`; sorting defaults to `Due date: earliest first`. These controls reset when the selected user or group changes.
- Due soon means today through six days after today.

## 9. Data and persistence

This enhancement requires no new persistent data beyond the calendar feature's existing due-date and priority fields.

The following are temporary session or derived data and shall not require database columns:

- Dashboard counts.
- Completion percentage.
- Active filters and sort selection.
- Baseline recommendation.
- AI-recommended priority and reason.
- Inputs associated with the current recommendation.
- Success-message state.

## 10. Privacy and security

- AI requests may contain only the fields listed in REQ-SPUI-02.
- TaskHub shall continue warning users not to enter private or sensitive information in task text.
- API keys shall remain in approved environment configuration and shall never appear in the database, UI, logs intended for submission, or error messages.
- AI recommendations shall be labeled as recommendations, not facts or commands.
- The feature is not intended for medical, legal, financial, emergency, or safety-critical prioritization.
- Existing lack-of-authentication warnings remain unchanged.

## 11. Error handling

- Empty valid results must be distinguished from load failures.
- A failed AI request must not clear valid task-form inputs.
- A failed data load must not be presented as zero metrics or a normal empty state.
- Filter and sort helpers must handle empty lists.
- Interface feedback must not expose stack traces, API keys, or internal database details to normal users.
- Recoverable interface errors must allow the person to continue using the app.

## 12. Automated testing requirements

Automated tests shall cover:

- Baseline boundaries at 0, 3, 4, 7, and 8 days.
- AI response normalization and rejection cases.
- Missing AI configuration and simulated service errors without live networking.
- Verification that only permitted fields reach a fake AI client.
- Metric calculations for empty, mixed-status, due-soon, and overdue task sets.
- Progress calculations for 0/0, partial, and complete groups.
- Overdue classification boundaries and completed-past-due behavior.
- Every status/ownership filter.
- Every priority filter.
- Combined filter behavior.
- Every sort option and stable tie-breaking.
- No mutation of the original task collection by filtering or sorting.
- Recommendation invalidation when relevant inputs change, where testable outside Streamlit.

Tests shall use fixed dates rather than the machine's actual date whenever boundary behavior is being verified. Automated tests shall not require a live API key, live AI call, or simulated keyboard input.

## 13. Manual verification requirements

The manual checklist shall verify:

- One successful live AI recommendation when configured.
- AI failure followed by successful manual task creation.
- Acceptance and override of a recommendation.
- All four dashboard metrics and the progress bar.
- High, medium, low, and overdue visual indicators.
- Every filter and sort option.
- Task-card fields and completion permissions.
- Required success messages.
- Required empty-state messages.
- Correct behavior after changing current user or selected group.
- No leakage of credentials or excluded identity fields in the inspected AI request.

## 14. Dependency and architecture constraints

- No new dependency is approved by this specification.
- Existing `google-genai`, Streamlit, SQLite, and `unittest` choices shall be retained.
- No database migration is required solely for this UI enhancement after due date and priority already exist.
- The application shall not be reorganized into a new architecture during these feature tasks.
- Helper functions may be added to existing modules when consistent with the approved design.

## 15. Requirement-to-component mapping

| Requirement | Primary component |
| --- | --- |
| REQ-SPUI-01 | Core business logic |
| REQ-SPUI-02–04 | AI service, core validation, interface |
| REQ-SPUI-05–06 | Core calculations, interface |
| REQ-SPUI-07 | Core date classification, interface |
| REQ-SPUI-08–09 | Core collection helpers, interface |
| REQ-SPUI-10 | Withdrawn; no component |
| REQ-SPUI-11–12 | Interface |

## 16. Implementation task plan

Only one task shall be implemented at a time.

| Task ID | Task | Connected requirements | Expected tests |
| --- | --- | --- | --- |
| SPUI-T01 | Reconcile project documentation and traceability | All | Documentation consistency review |
| SPUI-T02 | Add baseline-priority calculation | REQ-SPUI-01 | Boundary and invalid-date unit tests |
| SPUI-T03 | Add AI priority request and response validation | REQ-SPUI-02–04 | Mocked service, privacy, validation, and failure tests |
| SPUI-T04 | Integrate AI recommendation into task creation | REQ-SPUI-03–04 | Override, no-auto-create, failure-preservation tests where practical; manual UI checks |
| SPUI-T05 | Add dashboard metric and progress helpers | REQ-SPUI-05–06 | Empty, mixed, boundary, and percentage unit tests |
| SPUI-T06 | Render dashboard metrics and progress | REQ-SPUI-05–06 | Manual dashboard verification |
| SPUI-T07 | Add priority and overdue presentation | REQ-SPUI-07 | Date-classification unit tests and manual visual checks |
| SPUI-T08 | Add filtering and sorting helpers | REQ-SPUI-08–09 | All options, combined filters, ties, empty lists, and nonmutation tests |
| SPUI-T09 | Add task filter and sort controls | REQ-SPUI-08–09 | Manual state, group-switch, and no-match checks |
| SPUI-T10 | Withdrawn: upcoming-task grouping and display | REQ-SPUI-10 (withdrawn) | No implementation required |
| SPUI-T11 | Render consistent task cards | REQ-SPUI-11 | Manual fields, labels, permissions, and readability checks |
| SPUI-T12 | Add success and empty-state feedback | REQ-SPUI-12 | Manual success/failure/empty checks; helper tests if logic is extracted |
| SPUI-T13 | Complete regression, privacy, and documentation verification | All | Full suite, compile check, diff check, live manual checklist |

SPUI-T01 is first because the existing specification restricts AI to username suggestions. SPUI-T02 through SPUI-T04 establish the new smart-priority behavior. Later display tasks can then reuse the approved priority and date logic.

## 17. Per-task implementation process

For every task in Section 16:

1. Read the relevant project documents and existing functions.
2. Identify the next logical incomplete task.
3. State its task ID and connected requirement IDs.
4. Explain expected behavior.
5. List expected file changes.
6. Identify required automated and manual tests.
7. Add or update tests first where practical.
8. Implement the smallest correct solution.
9. Run the focused tests.
10. Run the complete automated test suite.
11. Run the approved compile, lint, and formatting checks.
12. Explain the changes and executed results.
13. Update task status only when all required work passes.

Do not implement multiple task IDs in one step. Do not add dependencies, remove tests, redesign the project, or claim commands passed unless they were executed. Stop and report inconsistencies instead of guessing.

## 18. Definition of Done

The enhancement is complete when:

1. All eleven active requirements meet their acceptance criteria; REQ-SPUI-10 remains withdrawn.
2. AI recommendation is explicit, validated, optional, overridable, and nonblocking.
3. AI requests contain only approved fields.
4. Dashboard metrics and progress are correct for empty and populated groups.
5. Priority and overdue indicators are consistent and accessible through text.
6. Filters and sorting produce correct display results without data mutation.
7. Task cards show every required field without changing permissions.
8. Success, empty, and error states are distinct and accurate.
9. No new dependency or unnecessary database field has been added.
10. Focused and full automated test suites pass.
11. Approved compile, lint, and formatting checks pass.
12. Manual interface, live AI, privacy, and regression checks pass.
13. README, specification, design, task plan, and manual checklist match the implemented behavior.

## 19. Suggested handoff prompt

Send this specification with the existing project files and use:

> Review the complete TaskHub project documentation and this enhancement specification. Identify the next logical incomplete task from Section 16. Before editing, state the task ID, connected requirement IDs, expected behavior, expected file changes, and required tests. Implement only that one task using the process in Section 17. Do not add dependencies or redesign the project. Stop and report inconsistencies instead of guessing.
