# TaskHub On-Demand Creation UI Specification

## 1. Purpose

TaskHub shall keep routine selection, dashboard, task-list, and calendar
actions immediately visible while hiding less-frequent creation forms until a
person asks to use them. This reduces page length without changing validation,
permissions, AI behavior, or saved data.

## 2. Scope

This enhancement changes only Streamlit presentation. It adds no dependency,
database field, business rule, or permission. Existing core, storage, and AI
functions remain the source of truth.

## 3. Requirements

### REQ-ODUI-01 — Keep the routine interface compact

- Profile, group, and task creation fields are hidden on initial display.
- Current-user selection, group selection, group members, dashboard, Task
  list, filters, task cards, and Calendar remain available as before.
- Task list remains the default detailed view.

### REQ-ODUI-02 — Reveal profile creation on demand

- One `Create profile` popover button reveals username entry, the optional AI
  username suggestion action, and `Save profile`.
- Valid and invalid profile behavior remains unchanged.
- When no profiles exist, guidance points to `Create profile`.

### REQ-ODUI-03 — Reveal group creation on demand

- After a current user is selected, one `Create group` popover button reveals
  group-name entry and `Save group`.
- Valid and invalid group behavior remains unchanged.
- When the current user has no groups, guidance points to `Create group`.

### REQ-ODUI-04 — Reveal task creation on demand

- After a group with an available assignee is selected, one collapsed `Create
  task` expander reveals title, description, assignee, due date, optional AI
  priority recommendation, manual priority, and `Save task`.
- Validation, recommendation privacy, assignment permission, and persistence
  behavior remain unchanged.
- Changing user or group continues to clear temporary task-form state.

## 4. Verification

Automated regression tests and compilation must pass. Manual checks must
confirm that all three forms begin hidden, open from the correct button, keep
their existing validation and success behavior, and do not hide routine
actions or change saved data.

## 5. Implementation task

### ODUI-T01 — Add on-demand creation controls

- **Requirement IDs:** REQ-ODUI-01 through REQ-ODUI-04
- **Files:** `app.py`, user and project documentation
- **Completion criteria:** The page begins compact, each creation workflow is
  accessible from one labeled disclosure control, existing behavior remains intact, all
  checks pass, and the manual checklist is confirmed.
