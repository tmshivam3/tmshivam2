import streamlit as st

def login_required():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Login Page")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "user1" and password == "1":
                st.session_state.logged_in = True
                st.success("Login Successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials. Try again.")
        st.stop()
