import streamlit as st
import os

TOKEN_FILE = ".login_token"

def show_login_form():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if validate_user(username, password):
            save_token(username)
            st.experimental_rerun()
        else:
            st.error("Invalid username or password. Contact developer: 9140588751 (WhatsApp)")

def validate_user(username, password):
    # Replace with your real KeyAuth check
    # For example:
    if username == "user1" and password == "1":
        return True
    return False

def save_token(username):
    with open(TOKEN_FILE, "w") as f:
        f.write(username)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def login_required():
    username = load_token()
    if username:
        return True
    else:
        show_login_form()
        return False
