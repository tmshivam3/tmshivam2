import streamlit as st
import os
from keyauth import api

# ==================== CONFIG ====================
APP_NAME = "Skbindjnp9's Application"
OWNER_ID = "jPmvngHsy3"
APP_VERSION = "1.0"
HASH_TO_CHECK = "abc123"

AUTH_FILE = "auth_status.txt"  # Local file to "remember" login

# ==================== KEYAUTH ====================
KeyAuthApp = api(
    name=APP_NAME,
    ownerid=OWNER_ID,
    version=APP_VERSION,
    hash_to_check=HASH_TO_CHECK
)


# ==================== REMEMBER ME CHECK ====================
def is_remembered():
    return os.path.exists(AUTH_FILE)

def set_remembered():
    with open(AUTH_FILE, "w") as f:
        f.write("authenticated")

def clear_remembered():
    if os.path.exists(AUTH_FILE):
        os.remove(AUTH_FILE)


# ==================== LOGIN SCREEN ====================
def show_login_screen():
    st.set_page_config(page_title="🔐 Secure Login", layout="centered")
    st.title("🔒 Secure Login to Access Tool")

    tab1, tab2 = st.tabs(["🧑 ID & Password", "🔑 License Key"])

    with tab1:
        st.subheader("Login with ID & Password")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not username or not password:
                st.warning("⚠️ Please fill both fields.")
                st.stop()

            try:
                KeyAuthApp.init()
                KeyAuthApp.login(username, password)
                st.success(f"✅ Welcome {username}!")
                st.session_state['authenticated'] = True
                set_remembered()
                st.experimental_rerun()
            except Exception:
                st.error(f"❌ Invalid username or password.")
                with st.expander("Purchase Subscription"):
                    st.markdown(
                        """
                        🛒 To purchase access, contact:
                        - 📱 [WhatsApp 9140588751](https://wa.me/919140588751)
                        """
                    )
                st.stop()

    with tab2:
        st.subheader("Activate with License Key")
        license = st.text_input("License Key", type="password")

        if st.button("Activate"):
            if not license:
                st.warning("⚠️ Please enter your license key.")
                st.stop()

            try:
                KeyAuthApp.init()
                KeyAuthApp.license(license)
                st.success("✅ License activated successfully!")
                st.session_state['authenticated'] = True
                set_remembered()
                st.experimental_rerun()
            except Exception:
                st.error(f"❌ Invalid or expired license key.")
                with st.expander("Purchase Subscription"):
                    st.markdown(
                        """
                        🛒 To purchase a license, contact:
                        - 📱 [WhatsApp 9140588751](https://wa.me/919140588751)
                        """
                    )
                st.stop()


# ==================== MAIN TOOL ====================
def main_app():
    st.set_page_config(page_title="⚡ Instant Photo Generator", layout="wide")
    st.title("⚡ Welcome to Instant Photo Generator")
    st.success("✅ You are logged in!")

    if st.button("🔓 Logout"):
        clear_remembered()
        st.session_state['authenticated'] = False
        st.experimental_rerun()

    # 🎯 🎯 🎯  PASTE YOUR FULL 700+ LINE TOOL CODE HERE  🎯 🎯 🎯
    st.markdown("> 🛠️ Paste your full photo editing tool code below this line.")

    # Example Placeholder - REMOVE THESE LINES
    st.info("✨ This is a placeholder. Replace it with your actual Streamlit app code.")


# ==================== APP FLOW ====================
if 'authenticated' not in st.session_state:
    if is_remembered():
        st.session_state['authenticated'] = True
    else:
        st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    show_login_screen()
else:
    main_app()
