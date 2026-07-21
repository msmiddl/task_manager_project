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
            st.session_state["current_user_id"] = selected_user_id
            active_user_id = selected_user_id
            selected_profile = profile_by_id[selected_user_id]
            st.write(f"Current user: {selected_profile['username']}")

    st.subheader("Groups")

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

                if selected_group_id not in group_ids:
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
                    st.session_state["selected_group_id"] = (
                        chosen_group_id
                    )
                    chosen_group = group_by_id[chosen_group_id]
                    st.write(f"Selected group: {chosen_group['name']}")
        except (LookupError, RuntimeError) as error:
            st.session_state.pop("selected_group_id", None)
            st.session_state.pop("selected_group_selector", None)
            st.error(str(error))
except RuntimeError as error:
    st.session_state.pop("current_user_id", None)
    st.session_state.pop("current_user_selector", None)
    st.session_state.pop("selected_group_id", None)
    st.session_state.pop("selected_group_selector", None)
    st.error(str(error))
