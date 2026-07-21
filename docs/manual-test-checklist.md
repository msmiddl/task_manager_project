# TaskHub Manual Test Checklist

Complete this checklist from the project root. Never record or display the real API key in the results.

## Automated verification record — 2026-07-21

| Evidence | Result |
| --- | --- |
| `tests.test_ai_service` | Pass — 3 tests |
| `tests.test_core` | Pass — 41 tests |
| `tests.test_storage` | Pass — 36 tests |
| `tests.test_workflow` | Pass — 1 complete workflow test |
| Complete test discovery | Pass — 81 tests |
| Python compilation | Pass |
| Source and Markdown whitespace | Pass |
| Production-layer boundaries | Pass |
| Approved dependency list | Pass — `streamlit` and `google-genai` only |
| Real API-key pattern scan | Pass — no key found |
| Database and `.env` artifact scan | Pass — none found in the reviewed files |
| Future-feature implementation scan | Pass — no non-goal implementation found |

The automated review was performed in a scratch copy without Git metadata. The `git diff --check`, ignored-file, and tracked-file results must therefore be recorded from the student's repository. Browser behavior, live AI behavior, restart behavior, and demonstration time also require manual results below.

## 1. Setup and automated checks

- [ ] Create and activate `.venv` by following `README.md`.
- [ ] Install `requirements.txt` without errors.
- [ ] Run the complete automated suite and record the result: __________
- [ ] Run `compileall` successfully.
- [ ] Run `git diff --check` without whitespace errors.
- [ ] Confirm the database and secret files are not staged by Git.

## 2. Empty and invalid states

- [ ] Start TaskHub with no database and see the empty-profile guidance.
- [ ] Submit an empty or whitespace username and see a safe validation error.
- [ ] Create a profile, select it, and see the no-groups message.
- [ ] Submit an empty or whitespace group name and see a safe error.
- [ ] Select a group with no tasks and see the no-tasks message.
- [ ] Try adding an unknown exact username and see a not-found error.
- [ ] Submit a task without an assignee and see a required-assignee error.
- [ ] Confirm no failed action is displayed as successful.
- [ ] Confirm no browser message contains an API key, SQL statement, or traceback.

## 3. Complete two-user workflow

- [ ] Create distinct profiles `Alex` and `Jordan`.
- [ ] Select Alex as the current user.
- [ ] Create `Roommates`; confirm Alex is its creator and member.
- [ ] Add Jordan by entering the exact username `Jordan`.
- [ ] Create `Wash dishes` with a valid description and assign it to Jordan.
- [ ] Confirm the task displays its title, description, assignee, and `incomplete` status.
- [ ] Confirm Alex cannot mark Jordan's task complete through the normal interface.
- [ ] Select Jordan and reselect Roommates.
- [ ] Confirm the task displays `Assigned to you`.
- [ ] Mark the task complete and confirm its status becomes `complete`.
- [ ] Confirm there is no control that returns the task to incomplete.

## 4. Persistence and session reset

- [ ] Stop TaskHub with `Ctrl+C` and restart it.
- [ ] Confirm no current user or group is selected after restart.
- [ ] Confirm Alex, Jordan, Roommates, both memberships, and Wash dishes remain saved.
- [ ] Reselect Jordan and Roommates and confirm Wash dishes remains complete.
- [ ] Confirm a deliberately invalid test database produces a controlled error and is not overwritten. Do not corrupt the demonstration database.

## 5. AI success and failure

- [ ] Set `GEMINI_API_KEY` without displaying or saving its value.
- [ ] Request a username suggestion and see one valid unused suggestion.
- [ ] Confirm requesting a suggestion does not create a profile.
- [ ] Remove `GEMINI_API_KEY`, restart TaskHub, and request another suggestion.
- [ ] See a safe unavailable message without a key, stack trace, or provider details.
- [ ] Confirm profile, group, and task actions still work while AI is unavailable.

## 6. Privacy and limitations

- [ ] Confirm TaskHub never requests a password.
- [ ] Confirm the demonstration uses only synthetic, non-sensitive sample data.
- [ ] Explain that profile selection is not authentication.
- [ ] Explain that selected user and group values reset after restart while SQLite data persists.
- [ ] Confirm the API key and `data/taskhub.db` are not included in the submitted files.

## 7. Two-minute demonstration

- [ ] Start a timer and demonstrate two profiles, one group, one membership addition, one assigned task, assignee selection, and task completion.
- [ ] Complete the workflow within two minutes. Recorded time: __________

## Result

- Date: __________
- Tester: __________
- Automated tests passed: Yes / No
- Manual checklist passed: Yes / No
- Live AI check passed: Yes / No
- Two-minute demonstration passed: Yes / No
- Notes or unresolved failures: ________________________________________
