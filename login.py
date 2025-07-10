# login.py
import streamlit as st
from keyauth import api

# KeyAuth App Details (use your correct credentials)
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

def login_required():
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
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
                    st.success("✅ License activated successfully!")
                    st.experimental_rerun()
                except:
                    st.error("❌ Invalid license key.")
                    st.info("💬 Contact WhatsApp: [9140588751](https://wa.me/919140588751)")

    return st.session_state.get("authenticated", False)
