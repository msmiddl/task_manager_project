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
except RuntimeError as error:
    st.error(str(error))