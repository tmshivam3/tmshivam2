import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np
import requests
import time
import hashlib

# =================== KEYAUTH CONFIGURATION ===================
def keyauth_login(username, password):
    # Replace with your KeyAuth API details
    url = "https://keyauth.win/api/1.2/"
    ownerid = "jPmvngHsy3"  # Your OwnerID from KeyAuth
    app_name = "Skbindjnp9's Application"  # Your app name from KeyAuth
    secret = "6a0d4e8e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e"  # Your app secret from KeyAuth
    
    # Initialize session
    init = requests.post(url, data={
        "type": "init",
        "ver": "1.2",
        "name": app_name,
        "ownerid": ownerid
    })
    
    if init.json()["success"]:
        sessionid = init.json()["sessionid"]
        
        # Login
        login = requests.post(url, data={
            "type": "login",
            "username": username,
            "pass": password,
            "sessionid": sessionid,
            "name": app_name,
            "ownerid": ownerid
        })
        
        if login.json()["success"]:
            return True, login.json()["info"]["subscriptions"][0]["subscription"] if login.json()["info"]["subscriptions"] else None
        else:
            return False, login.json()["message"]
    else:
        return False, "Failed to initialize KeyAuth session"

# =================== LOGIN PAGE ===================
def login_page():
    st.set_page_config(page_title="Login | Instant Photo Generator", layout="centered")
    
    st.markdown("""
        <style>
            .main {
                background-color: #000000;
            }
            .stButton>button {
                background-color: #000000;
                color: #ffff00;
                border: 2px solid #ffff00;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-weight: bold;
            }
            .stTextInput>div>div>input {
                color: white !important;
                background-color: #000000 !important;
                border: 1px solid #ffff00 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background-color: #000000; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #ffff00;'>
            <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Instant Photo Generator</h1>
            <p style='text-align: center; color: white;'>Please login to access the tool</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                with st.spinner("Authenticating..."):
                    success, subscription = keyauth_login(username, password)
                    if success:
                        if subscription:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.subscription = subscription
                            st.experimental_rerun()  # Redirect to main app
                        else:
                            st.error("You don't have an active subscription. Please contact support at WhatsApp: 9140588751")
                    else:
                        st.error(f"Login failed: {subscription}")

# =================== MAIN APP ===================
def main_app():
    # Your existing photo generator code here
    # ... (keep all the existing code from your original file)
    pass

# =================== APP FLOW CONTROL ===================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    # Show the main app if logged in
    main_app()
else:
    # Show login page if not logged in
    login_page()
