from pathlib import Path

import streamlit as st

from taskhub import core, storage


DATABASE_PATH = Path("data/taskhub.db")

st.title("TaskHub")

try:
    storage.initialize_storage(DATABASE_PATH)

    username = st.text_input("Username")

    if st.button("Create profile"):
        try:
            profile = core.create_profile(DATABASE_PATH, username)
            st.success(f"Created profile: {profile['username']}")
        except ValueError as error:
            st.error(str(error))
        except RuntimeError as error:
            st.error(str(error))

    st.subheader("Saved profiles")
    profiles = storage.list_users(DATABASE_PATH)

    if profiles:
        for saved_profile in profiles:
            st.write(saved_profile["username"])
    else:
        st.info("No profiles have been created yet.")

    st.subheader("Current user")
    active_user_id = None

    if not profiles:
        st.session_state.pop("current_user_id", None)
        st.session_state.pop("selected_group_id", None)
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
            st.session_state["current_user_id"] = selected_user_id
            active_user_id = selected_user_id
            selected_profile = profile_by_id[selected_user_id]
            st.write(f"Current user: {selected_profile['username']}")

    st.subheader("Groups")
    active_group = None

    if active_user_id is None:
        st.session_state.pop("selected_group_id", None)
        st.info("Select a current user to view or create groups.")
    else:
        group_name = st.text_input("Group name")

        if st.button("Create group"):
            try:
                created_group = core.create_group(
                    DATABASE_PATH,
                    group_name,
                    active_user_id,
                )
                st.success(f"Created group: {created_group['name']}")
            except (ValueError, LookupError, RuntimeError) as error:
                st.error(str(error))

        try:
            groups = core.list_user_groups(
                DATABASE_PATH,
                active_user_id,
            )

            if not groups:
                st.session_state.pop("selected_group_id", None)
                st.info("The current user does not belong to any groups.")
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
                    st.session_state["selected_group_id"] = (
                        chosen_group_id
                    )
                    chosen_group = group_by_id[chosen_group_id]
                    active_group = chosen_group
                    st.write(f"Selected group: {chosen_group['name']}")
        except (LookupError, RuntimeError) as error:
            st.session_state.pop("selected_group_id", None)
            st.session_state.pop("selected_group_selector", None)
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
                        f"Added group member: {added_member['username']}"
                    )

            group_members = storage.list_group_members(
                DATABASE_PATH,
                int(active_group["group_id"]),
            )

            for member in group_members:
                st.write(member["username"])
        except (
            ValueError,
            LookupError,
            PermissionError,
            RuntimeError,
        ) as error:
            st.error(str(error))

    st.subheader("Create task")

    if active_group is None:
        st.info("Select a group before creating a task.")
    elif not group_members:
        st.info("The selected group has no available assignees.")
    else:
        task_title = st.text_input("Task title", key="task_title")
        task_description = st.text_area(
            "Task description",
            key="task_description",
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

        if st.button("Create task"):
            try:
                created_task = core.create_assigned_task(
                    DATABASE_PATH,
                    int(active_group["group_id"]),
                    int(active_user_id),
                    task_title,
                    task_description,
                    selected_assignee_id,
                )
                st.success(
                    f"Created incomplete task: {created_task['title']}"
                )
            except (
                ValueError,
                LookupError,
                PermissionError,
                RuntimeError,
            ) as error:
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
    st.error(str(error))
