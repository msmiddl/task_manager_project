# Project Specification

## 1. Project overview

TaskHub is a local group-task application. It allows people to create local user profiles, organize profiles into groups, create assigned tasks, view group work, and record task completion. It also offers an AI-generated username suggestion that a person may choose whether to request. Implementing this suggestion feature is required for the MVP, but using it is optional. The core application must remain usable when the AI service is unavailable.

This specification defines the approved capstone scope without password authentication, formal invitations, real-time synchronization, or cloud deployment.

## 2. Problem statement

Small groups often coordinate responsibilities through verbal reminders, shared notes, or no organized system. These approaches make it difficult to determine which tasks remain incomplete, who is responsible for each task, and whether assigned work has been completed.

TaskHub provides one local record of group members, task assignments, and completion status.

## 3. Target user

The target user is a member of a small group that shares responsibilities, such as roommates, classmates, family members, or coworkers. No technical knowledge is assumed.

The MVP has one user type. A group creator may create a group and add existing user profiles to it, but is not a separate user type with a wider permission system.

### 3.1 Terms

- **Person:** The human operating the local application.
- **User profile:** A stored identity represented by a unique username.
- **Current user:** The user profile selected for the active session. Selecting a profile identifies the acting profile but does not authenticate the person.
- **Group member:** A user profile that has been added to a group.
- **Group creator:** The user profile that created a group. The creator is automatically a group member and is the only member who may add other existing profiles to that group.
- **Assignee:** The group member responsible for a task.
- **Core application:** User-profile, group, membership, task, viewing, completion, and persistence functions. The AI username suggestion is not a core function.

## 4. Project goals

The MVP will allow a person to:

- Create distinct local user profiles and select one as the current user through a separate action.
- View the groups belonging to the current user.
- Create a group and add existing user profiles to it by exact username.
- Create an incomplete task with one required assignee from the task's group.
- View all tasks for a selected group and identify tasks assigned to the current user.
- Allow only the selected assignee profile to mark its task complete.
- Retain user, group, membership, and task data after the application closes.
- Request an example username from an AI service without exposing private credentials.
- Receive observable error messages when an operation cannot be completed.

The capstone should demonstrate Python fundamentals, data handling, functions, error handling, and basic automated testing.

## 5. MVP scope

The MVP includes:

1. Creation of local user profiles with unique usernames.
2. Selection of a current user without password authentication.
3. Display of groups belonging to the current user.
4. Creation of multiple groups with names of 2 to 25 characters and no exact duplicates.
5. Addition of an existing user profile to a group by exact username by the group creator.
6. Creation of group tasks with a required title, required description, and required assignee.
7. Assignment of each new task to one existing member of the task's group during task creation.
8. Creation of every new task with an incomplete status.
9. A group task view showing title, description, assignee, and status and labeling tasks assigned to the current user.
10. One-way completion of an assigned task only by its assignee.
11. Persistence of all core application data after the application closes.
12. An isolated AI feature that suggests an unused, valid example username and fails without preventing use of the core application.
13. Automated tests for validation and business rules and a manual demonstration checklist for the interface and live AI request.
14. One simple local user interface. A CLI may be used during development, but a second complete interface is not an MVP deliverable.

## 6. Non-goals

The following are excluded from the MVP:

- Password authentication or password storage.
- AI-generated password examples.
- Formal invitations that users accept or reject.
- Viewing a list of users available to add to a group.
- Creating unassigned tasks.
- Assigning or reassigning a task after its creation.
- Editing or deleting tasks.
- Returning a completed task to incomplete.
- Real-time synchronization between users or devices.
- Cloud deployment or remote access.
- Notifications.
- Due dates and priority levels.
- Recurring tasks.
- Calendar integration.
- AI task assignment.
- Member preferences and workload calculations.
- Different permission models for roommate, family, or business groups.
- Automatic detection of personal or sensitive information in user-entered text.
- Duplicate-click protection beyond normal validation and business rules.
- A second complete interface.
- A polished production interface.

## 7. User workflows

### 7.1 Create and select a user

1. A person enters a username.
2. The application validates the username.
3. If valid and unique, the application creates the user profile.
4. In a separate action, a person selects an existing user profile.
5. The selected profile becomes the current user for later group and task actions.

### 7.2 Create and select a group

1. The current user views the groups to which they belong.
2. The current user may create a group with a valid, nonduplicate name.
3. The current user becomes the group's creator and first member.
4. The current user selects one of their groups for group-specific actions.

### 7.3 Add a group member

1. A second user profile is created or already exists.
2. The group creator enters that profile's exact username.
3. The application adds that profile if it exists and is not already a member.

### 7.4 Create and assign a task

1. A group member selects one of their groups.
2. The member enters a task title and description.
3. The member selects one assignee from that group's members.
4. The application creates the task with an incomplete status.

### 7.5 View and complete a task

1. The current user selects one of their groups.
2. The application displays all tasks in that group.
3. Each task displays its title, description, assignee, and status.
4. Tasks assigned to the current user display an `Assigned to you` label.
5. The current user selects one of their assigned incomplete tasks and marks it complete.
6. The application displays the complete status.

### 7.6 Request a username suggestion

1. A person requests a username suggestion.
2. The application requests an example from the AI service without sending a password.
3. The application validates that the suggestion follows the username rules and is unused.
4. The application displays a valid suggestion or an availability error.
5. The person may separately enter the suggestion through the normal profile-creation workflow.
6. Failure of this workflow does not block core application workflows.

## 8. Functional requirements

### REQ-01 - Create a local user profile

**User value:** Distinct profiles allow tasks to be assigned to different group members.

**Description:** The application shall create a local user profile when a person submits a username that is between 2 and 30 characters, is not entirely whitespace, and is not an exact duplicate of an existing username. Capitalization and spaces are significant: usernames that differ by capitalization or spacing are different usernames. Creating a profile does not automatically select it as the current user.

**Preconditions:** None.

**Expected result:** One valid profile is created and retained without changing the current-user selection.

**Acceptance criteria:**

- **Normal case - Given** no profile has the exact username `Alex`, **when** a person submits `Alex`, **then** one profile named `Alex` is created and the current user is unchanged.
- **Exact-match case - Given** `Alex` exists, **when** a person submits `alex`, **then** a separate profile named `alex` is created because capitalization differs.
- **Invalid-input case - Given** `Alex` exists, **when** a person submits the exact username `Alex`, **then** no profile is created and a duplicate-username error is displayed.
- **Invalid-input case - Given** profile creation is available, **when** a person submits fewer than 2 or more than 30 characters, **then** no profile is created and a length error is displayed.
- **Invalid-input case - Given** profile creation is available, **when** a person submits an empty or entirely whitespace username, **then** no profile is created and a required-username error is displayed.
- **Error case - Given** profile data cannot be saved, **when** a valid username is submitted, **then** creation failure is reported and the profile is not presented as created.

### REQ-02 - Select the current user

**User value:** A person must select the profile whose memberships and assignments will be used during the session.

**Description:** The application shall allow a person to select one existing profile as the current user. Selection is not password authentication and does not prove the person's identity.

**Preconditions:** At least one user profile exists.

**Expected result:** The selected existing profile becomes the current user.

**Acceptance criteria:**

- **Normal case - Given** profiles `Alex` and `Jordan` exist, **when** a person selects `Jordan`, **then** Jordan becomes the current user.
- **Invalid-input case - Given** no profile named `Unknown` exists, **when** a person attempts to select `Unknown`, **then** the current user is unchanged and a user-not-found error is displayed.
- **Empty-data case - Given** no profiles exist, **when** a person attempts to select a current user, **then** the application states that a profile must be created first.
- **Error case - Given** user profiles cannot be loaded, **when** selection is requested, **then** no selection is made and a load error is displayed.

### REQ-03 - Display and create groups

**User value:** The current user needs to see their groups and create a space for shared tasks.

**Description:** The application shall display the groups to which the current user belongs. It shall allow the current user to create a group with a name of 2 to 25 characters that is not entirely whitespace and does not exactly duplicate an existing group name. Capitalization and spaces are significant. The creator becomes the group's first member.

**Preconditions:** A current user is selected.

**Expected result:** The current user can see their groups, and a valid new group is retained with the current user as creator and member.

**Acceptance criteria:**

- **Normal display case - Given** Alex belongs to `Roommates` and `Class Project`, **when** Alex views their groups, **then** both names are displayed.
- **Normal creation case - Given** no group named `Roommates` exists and Alex is current, **when** Alex creates `Roommates`, **then** it is retained and Alex is its creator and a member.
- **Exact-match case - Given** a group named `Roommates` exists, **when** a current user submits `roommates`, **then** a separate group is created because capitalization differs.
- **Invalid-input case - Given** a group named `Roommates` exists, **when** a current user submits the exact name `Roommates`, **then** no group is created and a duplicate-name error is displayed.
- **Invalid-input case - Given** a current user is selected, **when** a group name has fewer than 2 or more than 25 characters, **then** no group is created and a length error is displayed.
- **Invalid-input case - Given** a current user is selected, **when** a blank or entirely whitespace group name is submitted, **then** no group is created and a required-name error is displayed.
- **Empty-data case - Given** the current user belongs to no groups, **when** their groups are displayed, **then** a no-groups message is displayed.
- **Error case - Given** group data cannot be saved, **when** a valid group is submitted, **then** creation failure is reported and the group is not presented as created.

### REQ-04 - Add an existing user to a group

**User value:** A group creator needs to include other profiles so tasks can be assigned to them.

**Description:** The application shall allow a group creator to add one existing user profile to that group by entering its exact username. It shall reject nonexistent usernames, all duplicate memberships including the creator, and attempts made by a current user who is not the group creator. It shall not display a list of profiles available to add.

**Preconditions:** A current user is selected, the group exists, and the current user is the group's creator.

**Expected result:** The existing profile becomes a member of the group exactly once.

**Acceptance criteria:**

- **Normal case - Given** Alex created `Roommates`, `Jordan` exists, and Jordan is not a member, **when** Alex enters the exact username `Jordan`, **then** Jordan appears once in the group's member list.
- **Exact-match case - Given** `Jordan` exists but `jordan` does not, **when** the creator enters `jordan`, **then** membership is unchanged and a user-not-found error is displayed.
- **Invalid-input case - Given** no profile has the submitted exact username, **when** the creator attempts to add it, **then** membership is unchanged and a user-not-found error is displayed.
- **Duplicate case - Given** a profile, including the creator, already belongs to the group, **when** the creator attempts to add that exact username, **then** no duplicate membership is created and an already-a-member message is displayed.
- **Permission case - Given** Jordan is a member but not the creator, **when** Jordan attempts to add another profile, **then** membership is unchanged and a permission error is displayed.
- **Error case - Given** membership data cannot be saved, **when** a valid existing profile is submitted, **then** failure is reported and the profile is not presented as added.

### REQ-05 - Create an assigned task

**User value:** A group member needs to record a responsibility and identify who must complete it.

**Description:** The application shall allow a group member to create a task in the selected group with a title of 1 to 20 total characters that is not entirely whitespace, a description of 1 to 100 total characters that is not entirely whitespace, and exactly one assignee who is already a group member. Internal spaces are valid and count toward the character limit. Every new task begins incomplete. A task cannot be created unassigned, assigned later, reassigned, edited, or deleted in the MVP.

**Preconditions:** A current user and one of that user's groups are selected.

**Expected result:** One valid incomplete task is created in the selected group for the selected assignee.

**Acceptance criteria:**

- **Normal case - Given** Alex and Jordan belong to `Roommates`, **when** Alex creates `Wash dishes` with a valid description and assigns it to Jordan, **then** one incomplete task is created for Jordan in `Roommates`.
- **Invalid-input case - Given** task creation is available, **when** a member submits a blank or entirely whitespace title or description, **then** no task is created and the missing field is identified.
- **Invalid-input case - Given** task creation is available, **when** the title exceeds 20 characters or the description exceeds 100 characters, **then** no task is created and the invalid field is identified.
- **Invalid-input case - Given** no assignee is selected, **when** a member submits otherwise valid task information, **then** no task is created and a required-assignee error is displayed.
- **Invalid-input case - Given** Taylor is not a member of `Roommates`, **when** a member attempts to assign a Roommates task to Taylor, **then** no task is created and an invalid-assignee error is displayed.
- **One-member case - Given** Alex is the only member of a group, **when** Alex submits a valid task assigned to Alex, **then** one incomplete task is created.
- **Error case - Given** task data cannot be saved, **when** valid task data is submitted, **then** creation failure is reported and the task is not presented as created.

### REQ-06 - Display group tasks and current-user assignments

**User value:** Members need to see the group's tasks and recognize their own responsibilities.

**Description:** The application shall display all tasks for a group selected from the current user's group list. Every displayed task shall show its title, description, assignee, and incomplete or complete status. A task assigned to the current user shall also display the label `Assigned to you`.

**Preconditions:** A current user and one of that user's groups are selected.

**Expected result:** Only tasks belonging to the selected group are displayed with the four required fields and the assignment label where applicable.

**Acceptance criteria:**

- **Normal case - Given** a selected group has tasks assigned to Alex and Jordan, **when** Alex views the group, **then** all group tasks show title, description, assignee, and status, and only Alex's tasks show `Assigned to you`.
- **Access case - Given** a group does not appear in Alex's group list because Alex is not a member, **when** Alex views available groups, **then** that group cannot be selected through the normal workflow and its tasks are not displayed.
- **Empty-data case - Given** the selected group has no tasks, **when** a member opens its task view, **then** a no-tasks message is displayed rather than an error.
- **Error case - Given** task data cannot be loaded, **when** a member opens the task view, **then** no task list is displayed and one task-load error is shown.

### REQ-07 - Mark an assigned task complete

**User value:** The group needs an accurate record of completed work updated by the responsible profile.

**Description:** The application shall allow the current user to change one of their assigned incomplete tasks to complete. A profile that is not the assignee shall not be allowed to complete the task. Completion is one-way: a completed task cannot return to incomplete.

**Preconditions:** A current user is selected and the task exists in one of that user's groups.

**Expected result:** An authorized incomplete task immediately changes to complete for the active session.

**Acceptance criteria:**

- **Normal case - Given** `Wash dishes` is incomplete and assigned to Jordan, **when** Jordan is the current user and marks it complete, **then** its displayed status becomes complete.
- **Invalid-input case - Given** no task matches the selected task identifier, **when** completion is attempted, **then** no task changes and a task-not-found error is displayed.
- **Permission case - Given** the task is assigned to Jordan, **when** Alex is the current user and attempts completion, **then** its status remains incomplete and a permission error is displayed.
- **Already-complete case - Given** a task is already complete, **when** its assignee attempts to mark it complete again, **then** its status remains complete and an already-complete informational message is displayed.
- **Empty-data case - Given** the current user has no assigned incomplete tasks, **when** completion options are displayed, **then** a no-assigned-incomplete-tasks message is displayed.
- **Error case - Given** the completion change cannot be saved, **when** the assignee attempts completion, **then** failure is reported and the task is not displayed as successfully updated.

### REQ-08 - Retain application data

**User value:** Users need their groups and tasks to remain available between sessions.

**Description:** The application shall retain valid profiles, groups, memberships, tasks, assignees, and statuses after it closes and reopens.

**Preconditions:** None for startup. Successfully created data is required for the corresponding persistence cases.

**Expected result:** Saved data and relationships are available with the same values in a later session.

**Acceptance criteria:**

- **Profile persistence - Given** valid profiles were saved, **when** the application closes and reopens, **then** the same profiles are available.
- **Group persistence - Given** a group and memberships were saved, **when** the application closes and reopens, **then** the group has the same creator and members.
- **Task persistence - Given** assigned tasks were saved, **when** the application closes and reopens, **then** each task has the same group, title, description, assignee, and status.
- **Completion persistence - Given** a task was marked complete and saved, **when** the application closes and reopens, **then** it remains complete.
- **Empty-data case - Given** no saved data exists, **when** the application starts, **then** empty user and group collections are presented and the person is prompted to create a profile; this is not reported as a failure.
- **Unreadable-data case - Given** saved data exists but cannot be read or is corrupted, **when** the application starts, **then** a saved-data-unavailable error is displayed and the condition is not silently presented as an empty new application.

### REQ-09 - Suggest an example username using AI

**User value:** A person who is unsure what username to choose can request an example.

**Description:** The application shall allow a person to request one AI-generated example username. Before display as a usable example, it must meet the same rules as a submitted username and must not duplicate an existing username. It shall not automatically create or change a profile. API request privacy is a documented manual verification rather than a required automated network-payload test.

**Preconditions:** A live success demonstration requires configured AI access and internet service. These are not preconditions for any core function.

**Expected result:** One valid unused suggestion is displayed, or an availability error is displayed without interrupting the core application.

**Acceptance criteria:**

- **Normal live case - Given** the AI service is configured and available, **when** a person requests a suggestion, **then** one valid unused suggestion is displayed and no profile is created automatically.
- **Invalid-result case - Given** the service returns a blank, invalid-length, whitespace-only, or duplicate username, **when** the response is validated, **then** it is not displayed as a usable suggestion and a suggestion-unavailable message is displayed.
- **Error case - Given** internet access, configuration, or the AI service is unavailable, **when** a person requests a suggestion, **then** an AI-unavailable message is displayed and core functions remain available.
- **Privacy case - Given** a live suggestion is requested, **when** the manual privacy check is performed, **then** the request contains no password because the MVP does not collect passwords.

## 9. Data requirements

### 9.1 Required data

The application requires data representing users, groups, group memberships, tasks, and the current-user selection for the active session.

### 9.2 Data fields and validation

| Data item | Field | Data type | Required | Validation rule |
| --- | --- | --- | --- | --- |
| User | Unique identifier | Identifier | Yes | Must identify exactly one user. |
| User | Username | Text | Yes | Must contain 2-30 characters, must not be entirely whitespace, and must be an exact unique value. Capitalization and spaces are significant. |
| Group | Unique identifier | Identifier | Yes | Must identify exactly one group. |
| Group | Group name | Text | Yes | Must contain 2-25 characters, must not be entirely whitespace, and must be an exact unique value. Capitalization and spaces are significant. |
| Group | Creator | User reference | Yes | Must reference an existing user who is also a group member. |
| Membership | Group | Group reference | Yes | Must reference an existing group. |
| Membership | User | User reference | Yes | Must reference an existing user. |
| Membership | User-group pair | Relationship | Yes | The same user may appear no more than once in the same group. |
| Task | Unique identifier | Identifier | Yes | Must identify exactly one task. |
| Task | Group | Group reference | Yes | Must reference an existing group. |
| Task | Title | Text | Yes | Must contain 1-20 characters and must not be entirely whitespace. |
| Task | Description | Text | Yes | Must contain 1-100 characters and must not be entirely whitespace. |
| Task | Assignee | User reference | Yes | Must reference one existing member of the task's group. |
| Task | Status | Defined value | Yes | Must be `incomplete` or `complete`; every new task begins `incomplete`, and the change to `complete` is one-way. |
| Session | Current user | User reference | Yes for user-specific actions | Must reference an existing profile. It does not prove the person's identity. |

No character restrictions beyond length and non-whitespace requirements have been approved for usernames, group names, task titles, or task descriptions.

An AI username suggestion is temporary display data. It becomes user data only if a person separately submits it through normal profile creation.

## 10. Error-handling requirements

- Invalid input shall not create or change data.
- An error message shall identify the failed action and its known reason.
- An empty valid result shall be distinguished from a data-loading failure.
- A failed save or update shall not be reported or displayed as successful.
- A failed AI suggestion shall not prevent access to any core function.
- An unexpected error shall produce an observable error message rather than silently ending the application.
- An error message shall not expose an API key or other internal diagnostic secret.
- Duplicate-click protection is not required. Duplicate usernames, group names, and memberships are prevented by their stated business rules; identical task content is otherwise permitted as separate tasks.

## 11. Privacy and security considerations

- The MVP does not authenticate identities. Selecting a current user does not prove that the person operating the application is that user.
- Permission checks apply to the selected current profile, not to a verified human identity.
- The MVP shall not request, store, display, or transmit user passwords.
- An AI username request shall contain no password.
- API keys shall not be displayed to users or included in submitted project data, screenshots, demonstrations, or error messages.
- Users shall be told not to enter personal, private, or sensitive information in usernames, group names, task titles, or task descriptions.
- The application does not automatically detect sensitive information.
- A group's task data shall be available through the normal workflow only when the selected current user belongs to that group.
- This local capstone is not suitable for sensitive data or untrusted users.

## 12. Assumptions

- Multiple people may be represented by local profiles in one local application.
- A person may select any existing local profile.
- Each group has one recorded creator.
- Only the group creator adds existing profiles to that group.
- Any group member may create a task in the group.
- Every task is assigned during creation to one group member.
- Only the selected assignee profile may mark its task complete.
- Users manually enter all core data.
- The AI service is used only for optional username suggestions.
- Core functions remain usable without internet access.

## 13. Constraints

- The project is intended for a beginner Python student.
- Development time is approximately two hours per day through July 24, 2026.
- The application must run locally.
- It must demonstrate Python fundamentals, data handling, functions, error handling, and basic testing.
- Core application data must remain available after the application closes.
- Internet access and configured Google API access may be required only for the AI username suggestion.
- One simple local interface is the MVP deliverable.
- No specific library, database product, interface framework, or architecture is selected by this specification.

## 14. Definition of Done

The MVP is done when:

1. Automated tests pass for username validation and uniqueness, group-name validation and uniqueness, membership rules, task validation, assignee eligibility, completion permission, one-way completion, and persistence of core data.
2. Automated tests verify controlled handling of invalid AI results and unavailable AI service behavior without requiring a live service.
3. The manual checklist verifies interface behavior, empty-data messages, displayed task fields, the `Assigned to you` label, and a live AI username request.
4. Two distinct local profiles can be created and selected separately.
5. The first profile can create a group and add the second existing profile by exact username.
6. A group member can create one incomplete task assigned to the second profile.
7. The second profile can be selected and its assignment displays the `Assigned to you` label.
8. The second profile can mark its assigned task complete, while a nonassignee profile cannot.
9. The completed task cannot be returned to incomplete.
10. Profiles, groups, memberships, assignments, and statuses remain available after closing and reopening the application.
11. Missing saved data is handled as an empty application, while unreadable or corrupted data produces an error.
12. The AI feature displays a valid unused username when available and a controlled error when unavailable.
13. AI failure does not prevent the complete group-task demonstration.
14. A manual two-minute demonstration shows two profiles, one group, one assigned task, and completion by the assignee.
15. The documentation states the absence of authentication and the approved validation rules.

## 15. Future possibilities

The following are not part of the MVP or its Definition of Done:

- Password authentication and secure password verification.
- Formal group invitations with accept and reject actions.
- Group-specific member preferences.
- Current-workload tracking.
- AI-generated task-assignment recommendations.
- Configurable group-owner and member permissions.
- Task editing, deletion, assignment after creation, and reassignment.
- Returning completed tasks to incomplete.
- Task priorities and due dates.
- Recurring tasks.
- Notifications.
- Calendar integration.
- Real-time synchronization between devices.
- Cloud deployment.
- A more polished interface.

Before any future feature is started, the MVP should meet its Definition of Done and pass its core tests.
