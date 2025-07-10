import streamlit as st
from keyauth import api
import os

# KeyAuth App Details
APP_NAME = "Skbindjnp9's Application"
OWNER_ID = "jPmvngHsy3"
APP_VERSION = "1.0"
HASH_TO_CHECK = ""

KeyAuthApp = api(
    name=APP_NAME,
    ownerid=OWNER_ID,
    version=APP_VERSION,
    hash_to_check=HASH_TO_CHECK
)

TOKEN_FILE = "auth_token.txt"

def save_token(auth_method, value):
    with open(TOKEN_FILE, "w") as f:
        f.write(f"{auth_method}:{value}")

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = f.read().strip()
            if ":" in data:
                return data.split(":", 1)
    return None, None

def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

def login_required():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Attempt auto-login with stored token
    if not st.session_state['authenticated']:
        auth_method, value = load_token()
        if auth_method and value:
            try:
                KeyAuthApp.init()
                if auth_method == "license":
                    KeyAuthApp.license(value)
                else:
                    username, password = value.split(":", 1)
                    KeyAuthApp.login(username, password)

                st.session_state['authenticated'] = True
                st.success("✅ Auto-login successful!")
                st.experimental_rerun()
            except:
                clear_token()  # Invalid/expired, remove

    # If still not authenticated, show login UI
    if not st.session_state['authenticated']:
        st.set_page_config(page_title="🔐 Login", layout="centered")
        st.title("🔒 Login Required to Access the Tool")

        tab1, tab2 = st.tabs(["Username & Password", "License Key"])

        with tab1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                try:
                    KeyAuthApp.init()
                    KeyAuthApp.login(username, password)
                    st.session_state['authenticated'] = True
                    save_token("login", f"{username}:{password}")
                    st.success(f"✅ Welcome {username}!")
                    st.experimental_rerun()
                except:
                    st.error("❌ Invalid username or password.")
                    st.info("💬 Contact WhatsApp: [9140588751](https://wa.me/919140588751)")

        with tab2:
            license = st.text_input("License Key", type="password")

            if st.button("Activate"):
                try:
                    KeyAuthApp.init()
                    KeyAuthApp.license(license)
                    st.session_state['authenticated'] = True
                    save_token("license", license)
                    st.success("✅ License activated successfully!")
                    st.experimental_rerun()
                except:
                    st.error("❌ Invalid license key.")
                    st.info("💬 Contact WhatsApp: [9140588751](https://wa.me/919140588751)")

    return st.session_state.get("authenticated", False)
