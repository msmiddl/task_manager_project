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

    if not profiles:
        st.session_state.pop("current_user_id", None)
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
            st.session_state["current_user_id"] = selected_user_id
            selected_profile = profile_by_id[selected_user_id]
            st.write(f"Current user: {selected_profile['username']}")
except RuntimeError as error:
    st.session_state.pop("current_user_id", None)
    st.session_state.pop("current_user_selector", None)
    st.error(str(error))
