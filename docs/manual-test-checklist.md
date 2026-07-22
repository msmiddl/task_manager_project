# TaskHub Manual Test Checklist

Complete this checklist from the project root. Never record or display the real API key in the results.

## Automated verification record — 2026-07-23

| Evidence | Result |
| --- | --- |
| `tests.test_ai_service` | Pass — 6 tests |
| `tests.test_core` | Pass — 79 tests |
| `tests.test_storage` | Pass — 41 tests |
| `tests.test_workflow` | Pass — 1 complete scheduled workflow test |
| Complete test discovery | Pass — 127 tests |
| Python compilation | Pass |
| Source and Markdown whitespace | Pass |
| Production-layer boundaries | Pass |
| Approved dependency list | Pass — `streamlit` and `google-genai` only |
| Real API-key pattern scan | Pass — no key found |
| Database and `.env` artifact scan | Pass — none found in the reviewed files |
| Scope scan | Pass — no non-goal or withdrawn Upcoming-task implementation found |

The automated review was performed in a scratch copy without Git metadata. The `git diff --check`, ignored-file, and tracked-file results must therefore be recorded from the student's repository. Browser behavior, live AI behavior, restart behavior, and demonstration time also require manual results below.

## 1. Setup and automated checks

- [x] Create and activate `.venv` by following `README.md`.
- [x] Install `requirements.txt` without errors.
- [x] Run the complete automated suite in the reviewed scratch copy: 127 passed
- [x] Run `compileall` successfully.
- [x] Run `git diff --check` without whitespace errors.
- [x] Confirm the database and secret files are not staged by Git.

## 2. Empty and invalid states

- [x] Start TaskHub with no database and see the empty-profile guidance.
- [x] Submit an empty or whitespace username and see a safe validation error.
- [x] Create a profile, select it, and see the no-groups message.
- [x] Submit an empty or whitespace group name and see a safe error.
- [x] Select a group with no tasks and see the no-tasks message.
- [x] Try adding an unknown exact username and see a not-found error.
- [x] Submit a task without an assignee and see a required-assignee error.
- [x] Confirm no failed action is displayed as successful.
- [x] Confirm no browser message contains an API key, SQL statement, or traceback.

## 3. Complete two-user workflow

- [x] Create distinct profiles `Alex` and `Jordan`.
- [x] Select Alex as the current user.
- [x] Create `Roommates`; confirm Alex is its creator and member.
- [x] Add Jordan by entering the exact username `Jordan`.
- [x] Create `Wash dishes` with a valid description and assign it to Jordan.
- [x] Confirm the task displays its title, description, assignee, and `incomplete` status.
- [x] Confirm Alex cannot mark Jordan's task complete through the normal interface.
- [x] Select Jordan and reselect Roommates.
- [x] Confirm the task displays `Assigned to you`.
- [x] Mark the task complete and confirm its status becomes `complete`.
- [x] Confirm there is no control that returns the task to incomplete.

## 4. Persistence and session reset

- [x] Stop TaskHub with `Ctrl+C` and restart it.
- [x] Confirm no current user or group is selected after restart.
- [x] Confirm Alex, Jordan, Roommates, both memberships, and Wash dishes remain saved.
- [x] Reselect Jordan and Roommates and confirm Wash dishes remains complete.
- [x] Confirm a deliberately invalid test database produces a controlled error and is not overwritten. Do not corrupt the demonstration database.

## 5. AI success and failure

- [x] Set `GEMINI_API_KEY` without displaying or saving its value.
- [x] Request a username suggestion and see one valid unused suggestion.
- [x] Confirm requesting a suggestion does not create a profile.
- [x] Remove `GEMINI_API_KEY`, restart TaskHub, and request another suggestion.
- [x] See a safe unavailable message without a key, stack trace, or provider details.
- [x] Confirm profile, group, and task actions still work while AI is unavailable.

## 6. Privacy and limitations

- [x] Confirm TaskHub never requests a password.
- [x] Confirm the demonstration uses only synthetic, non-sensitive sample data.
- [x] Explain that profile selection is not authentication.
- [x] Explain that selected user and group values reset after restart while SQLite data persists.
- [x] Confirm the API key and `data/taskhub.db` are not included in the submitted files.

## 7. Two-minute demonstration

- [x] Start a timer and demonstrate two profiles, one group, one membership addition, one assigned task, assignee selection, and task completion.
- [x] Complete the workflow within two minutes. Recorded time: Two minutes or less, confirmed by tester

## 8. Calendar and priority enhancement

- [x] Create tasks with past, current, and future due dates.
- [x] Create tasks at Low, Medium, and High priority; confirm Medium is the default.
- [x] Confirm every task-list entry shows a readable due date and priority text.
- [x] Confirm an incomplete past task shows `Overdue`.
- [x] Confirm an incomplete task due today shows `Due today`.
- [x] Confirm future and completed tasks show neither date-state label.
- [x] Switch between Task list and Calendar views.
- [x] Confirm incomplete and completed tasks appear on the correct calendar dates.
- [x] Confirm each calendar entry shows title, priority, assignee, and status.
- [x] Confirm an empty month keeps the calendar visible and shows an empty-month message.
- [x] Navigate to the previous and next months, including December to January.
- [x] Confirm navigation does not create, edit, complete, or delete a task.
- [x] Confirm changing profile or group resets the calendar to the current month.
- [x] Confirm restarting TaskHub resets the calendar to the current month.
- [x] Copy `data/taskhub.db`, initialize only the copy, and confirm profiles, groups, memberships, tasks, statuses, due dates, and priorities remain intact. Counts before and after: 4 users, 3 groups, 5 memberships, and 8 tasks; tasks missing schedules: 0.
- [x] Run the final calendar-enhancement suite and project checks in the student repository.

## 9. Smart-priority and interface enhancement

- [x] Confirm AI priority recommendation requires an explicit button press.
- [x] Accept one recommendation and override another before task creation.
- [x] Confirm recommendation failure preserves normal manual task creation.
- [x] Confirm the AI request excludes usernames, groups, assignees, credentials, other tasks, and task history.
- [x] Confirm dashboard totals, due-soon count, and progress for empty, partial, and complete groups.
- [x] Confirm High, Medium, Low, overdue, and due-today text indicators.
- [x] Confirm every status/ownership filter, priority filter, and sort option.
- [x] Confirm no-match filtering, user/group resets, and group isolation.
- [x] Confirm bordered task cards show every required field and only authorized completion controls.
- [x] Confirm all required success, valid-empty, and controlled error messages.
- [x] Confirm Task list is the default detailed view and the withdrawn Upcoming tasks section is absent.
- [x] Make one live AI priority recommendation in the final local build without recording the API key.
- [x] Run the final 127-test suite and compilation check in the student repository.
- [x] Run `git diff --check` and confirm `.env` and `data/*.db` remain ignored and untracked.

## Result

- Date: 2026-07-23
- Tester: Student confirmation with automated review
- Automated tests passed: Yes
- Manual checklist passed: Yes
- Live AI username check passed: Yes
- Final live AI priority check passed: Yes
- Two-minute demonstration passed: Yes
- Calendar enhancement passed: Yes
- Smart-priority interface checks passed: Yes
- Final local Git and 127-test checks passed: Yes
- Notes or unresolved failures: None
