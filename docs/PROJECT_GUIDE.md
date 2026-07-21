# Project Guide

## Project purpose

TaskHub is a beginner Python capstone for organizing assigned tasks within small groups. It runs locally with a Streamlit interface, stores data in SQLite, and includes an isolated AI username-suggestion feature.

## Source of truth

Application behavior is defined in [docs/specification.md](docs/specification.md). If code, tasks, or other documents disagree with the specification, stop and resolve the disagreement before coding.

- [docs/specification.md](docs/specification.md) — approved behavior and acceptance criteria
- [docs/design.md](docs/design.md) — approved technical design
- [docs/tasks.md](docs/tasks.md) — ordered implementation tasks

## Project structure

```text
app.py                     Streamlit interface
taskhub/core.py            Validation and business rules
taskhub/storage.py         SQLite access
taskhub/ai_service.py      Google AI request
tests/                     Automated tests
data/                      Local database location
docs/                      Specification, design, and task plan
```

Do not move business rules or SQL into `app.py`.

## Setup commands

From the project root in Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

Set the Google API key only in the local environment. Never place it in Python source, committed files, or SQLite data.

## Run command

```powershell
py -m streamlit run app.py
```

## Test command

Run the complete automated suite:

```powershell
py -m unittest discover -s tests -v
```

Run one test file while developing a behavior:

```powershell
py -m unittest tests.test_core -v
```

Replace `test_core` with the relevant test module.

## Formatting and linting commands

No automatic formatter or external linter is approved. Do not add one without justification and approval.

Use these dependency-free checks:

```powershell
py -m compileall app.py taskhub tests
git diff --check
```

`compileall` checks Python syntax. `git diff --check` finds whitespace errors. Neither replaces the automated tests.

## Development workflow

1. Read the three project documents.
2. Choose the next incomplete task from [docs/tasks.md](docs/tasks.md).
3. Note its task ID, requirement IDs, dependencies, files, and completion criteria.
4. Confirm all dependency tasks are complete.
5. Implement only that task’s behavior.
6. Add or update the corresponding tests in the same session.
7. Run the focused test module.
8. Run the full test suite before marking the task complete.
9. Perform the task’s manual verification when required.
10. Record blockers or failed checks honestly.

## Coding rules

- Work on one task at a time.
- Do not add unapproved features or implement non-goals.
- Do not add a dependency without explaining why the standard library and current dependencies are insufficient.
- Keep Streamlit input and display code in `app.py`.
- Keep validation and business rules in `taskhub/core.py`.
- Keep SQL and database access in `taskhub/storage.py`.
- Keep the external AI request in `taskhub/ai_service.py`.
- Validate data before processing or storing it.
- Add or update tests whenever behavior changes.
- Use temporary or synthetic test data, never real private data.
- Never store API keys in the repository or database.
- Keep functions small, focused, and clearly named.
- Prefer readable code over clever code.
- Use approved standard Python errors and safe user messages.
- Do not display API keys, SQL, or stack traces in the interface.
- Update documentation when approved behavior or design changes.
- Do not repair or overwrite a corrupted database automatically.

## AI assistant rules

Before changing code, the assistant must:

- Read this guide and the three linked project documents.
- Identify the exact task ID being implemented.
- Connect the proposed changes to the task’s requirement IDs.
- State any assumptions and ask before changing approved behavior.
- Confirm the task’s dependencies are complete.

While working, the assistant must:

- Avoid unrelated edits and unnecessary refactoring.
- Preserve the approved four-file separation.
- Explain new Python, SQL, Streamlit, and testing concepts at a beginner level.
- Add tests with the behavior instead of postponing them.
- Use sample data and protect secrets.

Before finishing, the assistant must:

- Run or provide the task’s focused verification command.
- Run the full test command when the project can support it.
- Report exactly which checks were executed and their results.
- Report checks it could not run and explain why.
- Never claim that a check passed unless it was actually executed.
- Summarize changed files, supported requirement IDs, and remaining blockers.

## Definition of Done

A task is done only when its completion criteria in [docs/tasks.md](docs/tasks.md) are met, its required tests pass, and its manual check is complete when applicable.

The project is done only when:

- REQ-01 through REQ-09 have passing evidence.
- The complete automated test suite passes.
- The manual checklist passes, including one live AI check.
- The two-user demonstration completes within two minutes.
- Saved data survives restart while current-user and group selections reset.
- No API key or local database is committed.
- The Definition of Done in [docs/specification.md](docs/specification.md) is satisfied.
