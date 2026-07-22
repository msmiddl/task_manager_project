import calendar
from datetime import date
from pathlib import Path

import streamlit as st

from taskhub import ai_service, core, storage


DATABASE_PATH = Path("data/taskhub.db")
USER_FACING_ERRORS = (
    ValueError,
    LookupError,
    PermissionError,
    RuntimeError,
)


def clear_priority_recommendation() -> None:
    """Remove only temporary AI recommendation data."""
    st.session_state.pop("ai_priority_recommendation", None)
    st.session_state.pop("ai_priority_input_snapshot", None)


def clear_task_display_settings() -> None:
    """Reset temporary task-list filter and sort selections."""
    st.session_state.pop("task_status_filter", None)
    st.session_state.pop("task_priority_filter", None)
    st.session_state.pop("task_sort", None)


def render_task_card(
    task: dict[str, int | str | bool],
    active_user_id: int,
) -> None:
    """Render one task-list card while preserving completion rules."""
    due_date = date.fromisoformat(str(task["due_date"]))
    readable_due_date = (
        f"{due_date.strftime('%B')} {due_date.day}, {due_date.year}"
    )
    priority_display = core.format_priority_display(
        str(task["priority"])
    )

    with st.container(border=True):
        st.write(f"**Title:** {task['title']}")
        st.write(f"**Description:** {task['description']}")
        st.write(f"**Assignee:** {task['assignee_username']}")
        st.write(f"**Due date:** {readable_due_date}")
        st.write(f"**Priority:** {priority_display}")
        st.write(f"**Status:** {task['status']}")

        if task["assigned_to_current_user"]:
            st.write("Assigned to you")
        if task["overdue_warning"]:
            st.write(task["overdue_warning"])
        elif task["date_state"]:
            st.write(task["date_state"])

        if (
            task["assigned_to_current_user"]
            and task["status"] == "incomplete"
        ):
            if st.button(
                "Mark complete",
                key=f"complete_task_{task['task_id']}",
            ):
                try:
                    message = core.complete_assigned_task(
                        DATABASE_PATH,
                        int(task["task_id"]),
                        active_user_id,
                    )
                    st.session_state["task_completion_message"] = message
                    st.rerun()
                except USER_FACING_ERRORS as error:
                    st.error(str(error))


st.title("TaskHub")

try:
    storage.initialize_storage(DATABASE_PATH)
    profiles = storage.list_users(DATABASE_PATH)

    with st.popover("Create profile"):
        username = st.text_input("Username")

        if st.button("Save profile"):
            try:
                profile = core.create_profile(DATABASE_PATH, username)
                st.success(f"Profile created: {profile['username']}")
            except USER_FACING_ERRORS as error:
                st.error(str(error))

        if st.button("Suggest a username"):
            try:
                raw_suggestion = ai_service.request_username_suggestion()
                suggestion = core.validate_ai_username_suggestion(
                    raw_suggestion,
                    [profile["username"] for profile in profiles],
                )
                st.success(f"Suggested username: {suggestion}")
            except USER_FACING_ERRORS as error:
                st.error(str(error))

    profiles = storage.list_users(DATABASE_PATH)

    if not profiles:
        st.info("No profiles yet. Use Create profile to add one.")

    st.subheader("Current user")
    active_user_id = None

    if not profiles:
        st.session_state.pop("current_user_id", None)
        st.session_state.pop("selected_group_id", None)
        clear_priority_recommendation()
        clear_task_display_settings()
        st.info("Create a profile before selecting a current user.")
    else:
        profile_by_id = {
            profile["user_id"]: profile for profile in profiles
        }
        profile_ids = list(profile_by_id)
        current_user_id = st.session_state.get("current_user_id")

        if current_user_id is not None:
            current_profile = storage.get_user_by_id(
                DATABASE_PATH,
                current_user_id,
            )
            if current_profile is None:
                st.session_state.pop("current_user_id", None)
                st.session_state.pop("current_user_selector", None)
                current_user_id = None
                clear_task_display_settings()
                st.error("The selected user could not be found.")

        selected_index = None
        if current_user_id in profile_ids:
            selected_index = profile_ids.index(current_user_id)

        selected_user_id = st.selectbox(
            "Select a profile",
            options=profile_ids,
            index=selected_index,
            format_func=lambda user_id: profile_by_id[user_id]["username"],
            placeholder="Choose a profile",
            key="current_user_selector",
        )

        if selected_user_id is not None:
            if selected_user_id != current_user_id:
                st.session_state.pop("selected_group_id", None)
                st.session_state.pop("selected_group_selector", None)
                st.session_state.pop("member_username", None)
                st.session_state.pop("task_title", None)
                st.session_state.pop("task_description", None)
                st.session_state.pop("task_assignee_selector", None)
                st.session_state.pop("task_due_date", None)
                st.session_state.pop("task_priority", None)
                st.session_state.pop("task_view", None)
                st.session_state.pop("calendar_year", None)
                st.session_state.pop("calendar_month", None)
                clear_priority_recommendation()
                clear_task_display_settings()
            st.session_state["current_user_id"] = selected_user_id
            active_user_id = selected_user_id
            selected_profile = profile_by_id[selected_user_id]
            st.write(f"Current user: {selected_profile['username']}")

    st.subheader("Groups")
    active_group = None

    if active_user_id is None:
        st.session_state.pop("selected_group_id", None)
        clear_task_display_settings()
        st.info("Select a current user to view or create groups.")
    else:
        with st.popover("Create group"):
            group_name = st.text_input("Group name")

            if st.button("Save group"):
                try:
                    created_group = core.create_group(
                        DATABASE_PATH,
                        group_name,
                        active_user_id,
                    )
                    st.success(
                        f"Group created: {created_group['name']}"
                    )
                except USER_FACING_ERRORS as error:
                    st.error(str(error))

        try:
            groups = core.list_user_groups(
                DATABASE_PATH,
                active_user_id,
            )

            if not groups:
                st.session_state.pop("selected_group_id", None)
                clear_task_display_settings()
                st.info(
                    "No groups for the current user. Use Create group "
                    "to add one."
                )
            else:
                group_by_id = {
                    group["group_id"]: group for group in groups
                }
                group_ids = list(group_by_id)
                selected_group_id = st.session_state.get(
                    "selected_group_id"
                )

                if (
                    selected_group_id is not None
                    and selected_group_id not in group_ids
                ):
                    st.session_state.pop("selected_group_id", None)
                    st.session_state.pop("selected_group_selector", None)
                    clear_task_display_settings()
                    selected_group_id = None

                selected_group_index = None
                if selected_group_id in group_ids:
                    selected_group_index = group_ids.index(
                        selected_group_id
                    )

                chosen_group_id = st.selectbox(
                    "Select a group",
                    options=group_ids,
                    index=selected_group_index,
                    format_func=lambda group_id: group_by_id[group_id][
                        "name"
                    ],
                    placeholder="Choose a group",
                    key="selected_group_selector",
                )

                if chosen_group_id is not None:
                    if chosen_group_id != selected_group_id:
                        st.session_state.pop("member_username", None)
                        st.session_state.pop("task_title", None)
                        st.session_state.pop("task_description", None)
                        st.session_state.pop(
                            "task_assignee_selector",
                            None,
                        )
                        st.session_state.pop("task_due_date", None)
                        st.session_state.pop("task_priority", None)
                        st.session_state.pop("task_view", None)
                        st.session_state.pop("calendar_year", None)
                        st.session_state.pop("calendar_month", None)
                        clear_priority_recommendation()
                        clear_task_display_settings()
                    st.session_state["selected_group_id"] = (
                        chosen_group_id
                    )
                    chosen_group = group_by_id[chosen_group_id]
                    active_group = chosen_group
                    st.write(f"Selected group: {chosen_group['name']}")
        except USER_FACING_ERRORS as error:
            st.session_state.pop("selected_group_id", None)
            st.session_state.pop("selected_group_selector", None)
            clear_task_display_settings()
            st.error(str(error))

    st.subheader("Group members")
    group_members = []

    if active_group is None:
        st.info("Select a group to view its members.")
    else:
        try:
            if active_group["creator_id"] == active_user_id:
                member_username = st.text_input(
                    "Exact username to add",
                    key="member_username",
                )

                if st.button("Add group member"):
                    added_member = core.add_group_member_by_username(
                        DATABASE_PATH,
                        int(active_group["group_id"]),
                        int(active_user_id),
                        member_username,
                    )
                    st.success(
                        f"Member added: {added_member['username']}"
                    )

            group_members = storage.list_group_members(
                DATABASE_PATH,
                int(active_group["group_id"]),
            )

            if group_members:
                for member in group_members:
                    st.write(member["username"])
            else:
                st.info("The selected group has no members.")
        except USER_FACING_ERRORS as error:
            st.error(str(error))


    if active_group is None:
        st.info("Select a group before creating a task.")
    elif not group_members:
        st.info("The selected group has no available assignees.")
    else:
        with st.expander("Create task"):
            task_title = st.text_input(
                "Task title",
                key="task_title",
                on_change=clear_priority_recommendation,
            )
            task_description = st.text_area(
                "Task description",
                key="task_description",
                on_change=clear_priority_recommendation,
            )
            member_by_id = {
                member["user_id"]: member for member in group_members
            }
            assignee_ids = list(member_by_id)
            selected_assignee_id = st.selectbox(
                "Assignee",
                options=assignee_ids,
                index=None,
                format_func=lambda user_id: member_by_id[user_id]["username"],
                placeholder="Choose an assignee",
                key="task_assignee_selector",
            )
            selected_due_date = st.date_input(
                "Due date",
                value=None,
                key="task_due_date",
                on_change=clear_priority_recommendation,
            )

            recommendation_snapshot = {
                "title": task_title,
                "description": task_description,
                "due_date": (
                    selected_due_date.isoformat()
                    if selected_due_date is not None
                    else None
                ),
            }
            saved_snapshot = st.session_state.get(
                "ai_priority_input_snapshot"
            )
            if (
                saved_snapshot is not None
                and saved_snapshot != recommendation_snapshot
            ):
                clear_priority_recommendation()

            if st.button("Suggest priority with AI"):
                clear_priority_recommendation()
                try:
                    request_fields = (
                        core.prepare_priority_recommendation_request(
                            task_title,
                            task_description,
                            recommendation_snapshot["due_date"],
                            date.today(),
                        )
                    )
                    raw_recommendation = (
                        ai_service.request_priority_recommendation(
                            **request_fields
                        )
                    )
                    recommendation = (
                        core.validate_ai_priority_recommendation(
                            raw_recommendation,
                            request_fields["baseline_priority"],
                        )
                    )
                    st.session_state["ai_priority_recommendation"] = (
                        recommendation
                    )
                    st.session_state["ai_priority_input_snapshot"] = (
                        recommendation_snapshot
                    )
                    st.session_state["task_priority"] = recommendation[
                        "priority"
                    ].capitalize()
                except USER_FACING_ERRORS as error:
                    st.error(str(error))

            selected_priority = st.selectbox(
                "Priority",
                options=("Low", "Medium", "High"),
                index=1,
                key="task_priority",
            )
            recommendation = st.session_state.get(
                "ai_priority_recommendation"
            )
            if recommendation is not None:
                st.info(
                    "AI recommendation: "
                    f"{str(recommendation['priority']).capitalize()} — "
                    f"{recommendation['reason']}"
                )

            if st.button("Save task"):
                try:
                    created_task = core.create_assigned_task(
                        DATABASE_PATH,
                        int(active_group["group_id"]),
                        int(active_user_id),
                        task_title,
                        task_description,
                        selected_assignee_id,
                        (
                            selected_due_date.isoformat()
                            if selected_due_date is not None
                            else None
                        ),
                        selected_priority.lower(),
                    )
                    st.success(f"Task created: {created_task['title']}")
                except USER_FACING_ERRORS as error:
                    st.error(str(error))

    st.subheader("Group tasks and calendar")

    if active_group is None:
        st.info("Select a group to view its tasks.")
    else:
        try:
            reference_date = date.today()
            group_tasks = core.get_group_tasks(
                DATABASE_PATH,
                int(active_group["group_id"]),
                int(active_user_id),
                reference_date,
            )
            task_metrics = core.calculate_group_task_metrics(
                group_tasks,
                reference_date,
            )
            completion_progress = core.calculate_completion_progress(
                group_tasks
            )

            st.subheader("Group dashboard")
            metric_columns = st.columns(4)
            metric_columns[0].metric("Total", task_metrics["total"])
            metric_columns[1].metric(
                "Incomplete",
                task_metrics["incomplete"],
            )
            metric_columns[2].metric(
                "Complete",
                task_metrics["complete"],
            )
            metric_columns[3].metric(
                "Due soon",
                task_metrics["due_soon"],
            )
            st.write(
                f"{completion_progress['completed']} of "
                f"{completion_progress['total']} tasks complete"
            )
            st.progress(float(completion_progress["ratio"]))

            completion_message = st.session_state.pop(
                "task_completion_message",
                None,
            )
            if completion_message == "Task marked complete.":
                st.success(completion_message)
            elif completion_message is not None:
                st.info(completion_message)

            task_view = st.radio(
                "View",
                options=("Task list", "Calendar"),
                index=0,
                horizontal=True,
                key="task_view",
            )

            if task_view == "Task list":
                filter_columns = st.columns(3)
                with filter_columns[0]:
                    status_filter = st.selectbox(
                        "Filter by status or assignment",
                        options=(
                            "All tasks",
                            "Assigned to me",
                            "Incomplete",
                            "Complete",
                        ),
                        key="task_status_filter",
                    )
                with filter_columns[1]:
                    priority_filter = st.selectbox(
                        "Filter by priority",
                        options=(
                            "All priorities",
                            "High",
                            "Medium",
                            "Low",
                        ),
                        key="task_priority_filter",
                    )
                with filter_columns[2]:
                    sort_by = st.selectbox(
                        "Sort tasks by",
                        options=(
                            "Due date",
                            "Priority",
                            "Assignee",
                            "Status",
                        ),
                        key="task_sort",
                    )

                filtered_tasks = core.filter_tasks(
                    group_tasks,
                    status_filter,
                    priority_filter,
                )
                displayed_tasks = core.sort_tasks(
                    filtered_tasks,
                    sort_by,
                )

                if not group_tasks:
                    st.info(
                        "No tasks in the selected group. Use Create task "
                        "above to add one."
                    )
                elif not displayed_tasks:
                    st.info(
                        "No tasks match the selected filters. Change the "
                        "filters to see other tasks."
                    )
                else:
                    assigned_incomplete_tasks = [
                        task
                        for task in group_tasks
                        if task["assigned_to_current_user"]
                        and task["status"] == "incomplete"
                    ]
                    if not assigned_incomplete_tasks:
                        st.info(
                            "No assigned incomplete tasks available for "
                            "completion."
                        )

                    for task in displayed_tasks:
                        render_task_card(task, int(active_user_id))
            else:
                if "calendar_year" not in st.session_state:
                    st.session_state["calendar_year"] = (
                        reference_date.year
                    )
                if "calendar_month" not in st.session_state:
                    st.session_state["calendar_month"] = (
                        reference_date.month
                    )

                calendar_year = int(st.session_state["calendar_year"])
                calendar_month = int(st.session_state["calendar_month"])

                previous_column, heading_column, next_column = st.columns(
                    [1, 2, 1]
                )
                with previous_column:
                    if st.button("Previous month"):
                        if calendar_month == 1:
                            st.session_state["calendar_year"] = (
                                calendar_year - 1
                            )
                            st.session_state["calendar_month"] = 12
                        else:
                            st.session_state["calendar_month"] = (
                                calendar_month - 1
                            )
                        st.rerun()
                with heading_column:
                    st.subheader(
                        f"{calendar.month_name[calendar_month]} "
                        f"{calendar_year}"
                    )
                with next_column:
                    if st.button("Next month"):
                        if calendar_month == 12:
                            st.session_state["calendar_year"] = (
                                calendar_year + 1
                            )
                            st.session_state["calendar_month"] = 1
                        else:
                            st.session_state["calendar_month"] = (
                                calendar_month + 1
                            )
                        st.rerun()

                calendar_tasks = core.get_group_tasks_for_month(
                    DATABASE_PATH,
                    int(active_group["group_id"]),
                    int(active_user_id),
                    calendar_year,
                    calendar_month,
                    reference_date,
                )
                tasks_by_day = {}
                for task in calendar_tasks:
                    task_due_date = date.fromisoformat(
                        str(task["due_date"])
                    )
                    tasks_by_day.setdefault(task_due_date.day, []).append(
                        task
                    )

                weekday_columns = st.columns(7)
                for column, weekday_name in zip(
                    weekday_columns,
                    calendar.day_abbr,
                ):
                    column.write(f"**{weekday_name}**")

                for week in calendar.monthcalendar(
                    calendar_year,
                    calendar_month,
                ):
                    day_columns = st.columns(7)
                    for column, day_number in zip(day_columns, week):
                        with column:
                            if day_number == 0:
                                st.write("")
                                continue

                            st.write(f"**{day_number}**")
                            for task in tasks_by_day.get(day_number, []):
                                st.write(f"Title: {task['title']}")
                                priority_display = (
                                    core.format_priority_display(
                                        str(task["priority"])
                                    )
                                )
                                st.write(
                                    f"Priority: {priority_display}"
                                )
                                if task["overdue_warning"]:
                                    st.write(task["overdue_warning"])
                                st.write(
                                    f"Assignee: "
                                    f"{task['assignee_username']}"
                                )
                                st.write(f"Status: {task['status']}")
                                st.divider()

                if not calendar_tasks:
                    st.info("There are no tasks due in this month.")
        except USER_FACING_ERRORS as error:
            st.error(str(error))
except RuntimeError as error:
    st.session_state.pop("current_user_id", None)
    st.session_state.pop("current_user_selector", None)
    st.session_state.pop("selected_group_id", None)
    st.session_state.pop("selected_group_selector", None)
    st.session_state.pop("member_username", None)
    st.session_state.pop("task_title", None)
    st.session_state.pop("task_description", None)
    st.session_state.pop("task_assignee_selector", None)
    st.session_state.pop("task_due_date", None)
    st.session_state.pop("task_priority", None)
    st.session_state.pop("task_view", None)
    st.session_state.pop("calendar_year", None)
    st.session_state.pop("calendar_month", None)
    clear_priority_recommendation()
    clear_task_display_settings()
    st.error(str(error))
