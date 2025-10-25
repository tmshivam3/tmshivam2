import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps, ImageChops
import os
import io
import random
from datetime import datetime, timedelta
import zipfile
import numpy as np
import textwrap
from typing import Tuple, List, Optional
import math
import colorsys
import traceback
from collections import Counter
#from streamlit.runtime.scriptrun_ctx import get_script_run_ctx
import json
import uuid
import hashlib
import requests
import gdown
import tempfile
import sqlite3
import pandas as pd
import os
import tempfile
import zipfile
import gdown
import streamlit as st
from utils import smart_crop
import pytz  # Add this import for timezone support

# 👇 Helper functions yaha paste karna hai
def list_subfolders(folder):
    """Return list of subfolders inside a folder"""
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]

def list_files(folder, extensions=None):
    """Return list of files inside a folder (filter by extension if given)"""
    if not os.path.exists(folder):
        return []
    files = []
    for f in os.listdir(folder):
        full_path = os.path.join(folder, f)
        if os.path.isfile(full_path):
            if extensions is None or any(f.lower().endswith(ext) for ext in extensions):
                files.append(full_path)
    return files


def list_subfolders(directory):
    """Return a list of subfolder names in the given directory"""
    return [name for name in os.listdir(directory) 
            if os.path.isdir(os.path.join(directory, name))]

def apply_emoji_stickers(img: Image.Image, emojis: List[str], num_stickers=5, occupied_boxes: Optional[List[Tuple[int, int, int, int]]] = None) -> Image.Image:
    if occupied_boxes is None:
        occupied_boxes = []
    # rest of the code

# Download and extract assets from Google Drive
@st.cache_resource
def get_assets_dir():
    local_assets = os.path.join(os.getcwd(), "assets")  # check local "assets" folder
    
    if os.path.exists(local_assets):
        st.info("Using local assets folder ✅")
        return local_assets

    # Agar local assets nahi hai to download kare
    tmpdir = tempfile.mkdtemp()
    file_id = "17i5_V45rTM0SqSmhbgPrl4PTcqJNvVhS"
    url = f"https://drive.google.com/uc?id={file_id}"
    zip_path = os.path.join(tmpdir, "assets.zip")

    try:
        st.info("assets Download Done ✅")
        gdown.download(url, zip_path, quiet=False)

        # Verify the file is a valid ZIP
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.testzip()  # Test ZIP integrity
                zip_ref.extractall(tmpdir)
        except zipfile.BadZipFile as e:
            raise ValueError(f"Invalid ZIP file: {str(e)}")
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)

        # Check for 'assets' folder or return tmpdir if structure differs
        assets_path = os.path.join(tmpdir, "assets")
        if os.path.exists(assets_path):
            return assets_path
        return tmpdir

    except Exception as e:
        st.error(f"Failed to download or extract assets: {str(e)}")
        st.error("Please ensure the Google Drive link is public and points to a valid ZIP file.")
        raise

ASSETS_DIR = get_assets_dir()

# ========== BEGIN AUTH / ADMIN BLOCK ==========
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
OVERLAP_SETTINGS_FILE = os.path.join(DATA_DIR, "overlap_settings.json")
TOOL_SETTINGS_FILE = os.path.join(DATA_DIR, "tool_settings.json")
DB_FILE = os.path.join(DATA_DIR, "usage_data.db")

# Initialize database for usage tracking
def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS image_usage
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  image_count INTEGER,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def log_image_usage(username, count):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO image_usage (username, image_count) VALUES (?, ?)", 
              (username, count))
    conn.commit()
    conn.close()

def get_usage_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM image_usage ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def export_settings():
    settings = {
        "users": _auth_load_users(),
        "app_settings": _auth_load_settings(),
        "overlap_settings": _load_overlap_settings(),
        "tool_settings": _load_tool_settings()
    }
    return json.dumps(settings, indent=2)

def import_settings(json_data):
    try:
        data = json.loads(json_data)
        _auth_save_users(data.get("users", {"users": {}}))
        _auth_save_settings(data.get("app_settings", {}))
        _save_overlap_settings(data.get("overlap_settings", {}))
        _save_tool_settings(data.get("tool_settings", {}))
        return True
    except:
        return False

def get_ip():
    try:
        # For Streamlit Cloud compatibility
        try:
            ctx = get_script_run_ctx()
            if ctx and hasattr(ctx, '_request_headers'):
                headers = ctx._request_headers
                ip = headers.get("X-Forwarded-For", "Unknown")
                if ip != "Unknown":
                    ip = ip.split(',')[0].strip()
                return ip
        except:
            pass
        
        # Fallback for local execution
        return "127.0.0.1"
    except Exception:
        return "Unknown"

def _auth_hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _auth_load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}

def _auth_save_users(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _auth_load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"notice":"", "active_tool":"V1.0", "visible_tools":["V1.0"], "primary_color":"#ffcc00", "login_enabled": False}  # Login disabled by default

def _auth_save_settings(s):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def _load_overlap_settings():
    try:
        with open(OVERLAP_SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_overlap_settings(settings):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OVERLAP_SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def _load_tool_settings():
    try:
        with open(TOOL_SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        # Default tool settings
        return {
            "text_style": {
                "white_only": True,
                "white_black_outline": True,
                "gradient": True,
                "neon": True,
                "rainbow": True,
                "country_flag": True,
                "3d": True,
                "white_color_outline": True,
                "pure_color_white_outline": True,
                "multicolor_gradient_outline": True,
                "metallic": True,
                "glowing": True
            },
            "overlay": {
                "1024": True,
                "2025": True,
                "pet": True
            },
            "filter": {
                "sepia": True,
                "black_white": True,
                "vintage": True,
                "vignette": True,
                "sketch": True,
                "cartoon": True,
                "anime": True
            },
            "advanced": {
                "emoji": True,
                "watermark": True,
                "quote": True
            }
        }

def _save_tool_settings(settings):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TOOL_SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def _auth_ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    users = _auth_load_users()
    if "admin" not in users.get("users", {}):
        default_pw = "admin123"
        users.setdefault("users", {})["admin"] = {
            "password_hash": _auth_hash(default_pw),
            "is_admin": True,
            "device_token": None,
            "last_login": None,
            "expires_at": None,
            "last_ip": None
        }
        _auth_save_users(users)
    settings = _auth_load_settings()
    _auth_save_settings(settings)
    
    # Ensure overlap settings file exists
    overlap_settings = _load_overlap_settings()
    _save_overlap_settings(overlap_settings)
    
    # Ensure tool settings file exists
    tool_settings = _load_tool_settings()
    _save_tool_settings(tool_settings)

_auth_ensure_files()
_users_db = _auth_load_users()
_settings = _auth_load_settings()
_overlap_settings = _load_overlap_settings()
_tool_settings = _load_tool_settings()

def _auth_logout_and_rerun():
    for k in ("_auth_user","_auth_device","_auth_login_time","_auth_show_admin"):
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

def _auth_check_session():
    username = st.session_state.get("_auth_user")
    if not username:
        return
    users = _auth_load_users()
    u = users.get("users", {}).get(username)
    if not u:
        st.warning("Your account was removed. Logging out.")
        _auth_logout_and_rerun()
    if u.get("expires_at"):
        try:
            exp = datetime.fromisoformat(u["expires_at"])
            if datetime.utcnow() > exp:
                st.warning("Session expired — please login again.")
                _auth_logout_and_rerun()
        except:
            pass
    token = st.session_state.get("_auth_device")
    current_ip = get_ip()
    if u.get("last_ip") and current_ip != u.get("last_ip"):
        st.warning("IP address mismatch. Logging out for security.")
        _auth_logout_and_rerun()
    if u.get("device_token") and token and u.get("device_token") != token:
        st.warning("You were logged in from another device. This session is logged out.")
        _auth_logout_and_rerun()

# ========== ADMIN PANEL AUTHENTICATION ==========
def admin_panel_auth():
    """Admin panel authentication function"""
    st.markdown("### 🔐 Admin Authentication Required")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        admin_username = st.text_input("Admin Username", key="admin_username")
        admin_password = st.text_input("Admin Password", type="password", key="admin_password")
    
    with col2:
        st.write("")  # Spacing
        if st.button("Login to Admin Panel", use_container_width=True):
            users_db = _auth_load_users()
            user_data = users_db.get("users", {}).get(admin_username)
            
            if user_data and user_data.get("password_hash") == _auth_hash(admin_password) and user_data.get("is_admin", False):
                st.session_state["_auth_admin_authenticated"] = True
                st.session_state["_auth_admin_user"] = admin_username
                st.success("Admin authentication successful!")
                st.rerun()
            else:
                st.error("Invalid admin credentials!")
    
    return False

# Check if login is enabled - DISABLED BY DEFAULT
if _settings.get("login_enabled", False):  # Changed to False by default
    if "_auth_user" not in st.session_state:
        st.markdown("<h2 style='color:#ffcc00'>🔐 Login First</h2>", unsafe_allow_html=True)
        st.info("For ID and Password, contact WhatsApp: 9140588751")
        left, right = st.columns([2,1])
        with left:
            login_id = st.text_input("Enter ID")
            login_pw = st.text_input("Password", type="password")
        with right:
            if st.button("Login"):
                db = _auth_load_users()
                user = db.get("users", {}).get(login_id)
                if not user or user.get("password_hash") != _auth_hash(login_pw or ""):
                    st.error("Invalid ID or Password. Contact dev: +91 9140588751")
                else:
                    token = str(uuid.uuid4())
                    now = datetime.utcnow()
                    current_ip = get_ip()
                    user["device_token"] = token
                    user["last_login"] = now.isoformat()
                    user["last_ip"] = current_ip
                    user["expires_at"] = (now + timedelta(days=7)).isoformat()
                    _auth_save_users(db)
                    st.session_state["_auth_user"] = login_id
                    st.session_state["_auth_device"] = token
                    st.session_state["_auth_login_time"] = now.isoformat()
                    st.success(f"Welcome {login_id} — logged in from IP {current_ip}!")
                    st.rerun()
        st.stop()

    _auth_check_session()
    CURRENT_USER = st.session_state.get("_auth_user")
    USERS_DB = _auth_load_users()
    CURRENT_RECORD = USERS_DB.get("users", {}).get(CURRENT_USER, {})
    IS_ADMIN = CURRENT_RECORD.get("is_admin", False)
else:
    # Bypass login if disabled - ALL USERS GET PRO FEATURES
    if "_auth_user" not in st.session_state:
        st.session_state["_auth_user"] = "guest"
        st.session_state["_auth_device"] = str(uuid.uuid4())
        st.session_state["_auth_login_time"] = datetime.utcnow().isoformat()
    CURRENT_USER = "guest"
    USERS_DB = _auth_load_users()
    CURRENT_RECORD = USERS_DB.get("users", {}).get(CURRENT_USER, {})
    # ALL USERS GET PRO FEATURES WHEN LOGIN IS DISABLED
    IS_ADMIN = False
    # Force all users to have Pro Member access when login is disabled
    CURRENT_RECORD["user_type"] = "Pro Member"

# Admin panel button - ALWAYS SHOW IN SIDEBAR AT TOP
if "_auth_show_admin" not in st.session_state:
    st.session_state["_auth_show_admin"] = False

# Always show admin panel button at top of sidebar
with st.sidebar:
    if st.button("🔧 Admin Panel", key="admin_panel_btn", use_container_width=True):
        st.session_state["_auth_show_admin"] = not st.session_state["_auth_show_admin"]

# Admin panel with authentication
if st.session_state.get("_auth_show_admin"):
    # Check if admin is already authenticated for this session
    if not st.session_state.get("_auth_admin_authenticated", False):
        if not admin_panel_auth():
            st.stop()
    
    # If authenticated, show admin panel
    st.markdown("## ⚙️ ADMIN PANEL")
    
    st.markdown("### User Management")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "User Accounts", "Access Control", "System Settings", "IP Management", 
        "Tools & Features", "Overlap Settings", "Tool Toggles", "Usage Statistics", 
        "Tool Visibility", "Theme Preview"
    ])
    
    with tab1:
        st.markdown("#### Create / Manage Users")
        c1,c2 = st.columns(2)
        with c1:
            new_id = st.text_input("New ID", key="__new_id")
            new_pw = st.text_input("New Password", type="password", key="__new_pw")
        with c2:
            new_admin = st.checkbox("Is Admin?", key="__new_admin")
            user_type = st.selectbox("User Type", ["Member", "Pro Member", "Admin"], key="__user_type")
            if st.button("Create User"):
                db = _auth_load_users()
                if new_id in db.get("users", {}):
                    st.error("User already exists.")
                else:
                    db.setdefault("users", {})[new_id] = {
                        "password_hash": _auth_hash(new_pw or "12345"),
                        "is_admin": bool(new_admin),
                        "user_type": user_type,
                        "device_token": None,
                        "last_login": None,
                        "last_ip": None,
                        "expires_at": None
                    }
                    _auth_save_users(db)
                    st.success(f"User {new_id} created.")
        
        st.markdown("#### Existing users")
        db = _auth_load_users()
        for uname, udata in list(db.get("users", {}).items()):
            cols = st.columns([3,1,1,1,1,1,1])
            exp = udata.get('expires_at', 'None')
            last_login = udata.get('last_login', 'None')
            last_ip = udata.get('last_ip', 'None')
            user_type = udata.get('user_type', 'Member')
            
            cols[0].write(f"**{uname}** ({user_type}) | Exp: {exp} | Last Login: {last_login} | IP: {last_ip}")
            
            if cols[1].button("Reset PW", key=f"reset_{uname}"):
                db["users"][uname]["password_hash"] = _auth_hash("admin123")
                _auth_save_users(db)
                st.success(f"{uname} password reset to admin123")
            
            if cols[2].button("Expire Now", key=f"expire_{uname}"):
                db["users"][uname]["expires_at"] = datetime.utcnow().isoformat()
                _auth_save_users(db)
                st.success(f"{uname} expired")
            
            if cols[3].button("Delete", key=f"del_{uname}"):
                del db["users"][uname]
                _auth_save_users(db)
                st.rerun()
            
            exp_days = cols[4].number_input("Expiry Days", min_value=0, value=7, key=f"exp_{uname}")
            if cols[5].button("Set Expiry", key=f"setexp_{uname}"):
                if exp_days > 0:
                    exp = (datetime.utcnow() + timedelta(days=exp_days)).isoformat()
                    db["users"][uname]["expires_at"] = exp
                else:
                    db["users"][uname]["expires_at"] = None
                _auth_save_users(db)
                st.success(f"Expiry set for {uname}")
            
            new_type = cols[6].selectbox("Type", ["Member", "Pro Member", "Admin"], 
                                        index=["Member", "Pro Member", "Admin"].index(user_type),
                                        key=f"type_{uname}")
            if new_type != user_type:
                db["users"][uname]["user_type"] = new_type
                _auth_save_users(db)
                st.success(f"{uname} type changed to {new_type}")
    
    with tab2:
        st.markdown("### Access Control")
        st.markdown("#### Tool Visibility Settings")
        
        all_tools = ["V1.0", "V2.0", "V3.0", "V4.0", "V5.0", "Premium Tools"]
        visible_tools = _settings.get("visible_tools", ["V1.0"])
        
        # Create compact checkboxes for tool visibility
        st.markdown("**Select which tools to display:**")
        cols = st.columns(3)
        tool_states = {}
        
        for i, tool in enumerate(all_tools):
            with cols[i % 3]:
                tool_states[tool] = st.checkbox(
                    tool, 
                    value=tool in visible_tools, 
                    key=f"tool_{tool}",
                    help=f"Show/Hide {tool} tool"
                )
        
        if st.button("Save Tool Visibility"):
            new_visible_tools = [tool for tool, visible in tool_states.items() if visible]
            _settings["visible_tools"] = new_visible_tools
            _auth_save_settings(_settings)
            st.success("Tool visibility settings saved!")
        
        st.markdown("#### User Type Restrictions")
        st.info("Pro Members can access all tools except Admin Panel. Members can only access basic tools.")
    
    with tab3:
        st.markdown("### System Settings")
        st.markdown("#### Noticeboard")
        new_notice = st.text_area("Global notice (shows on main page)", value=_settings.get("notice",""))
        
        primary_color = st.color_picker("Primary Color", value=_settings.get("primary_color", "#ffcc00"))
        
        # Login enable/disable toggle
        login_enabled = st.checkbox("Enable Login Page", value=_settings.get("login_enabled", False))
        
        if st.button("Save Settings"):
            _settings["notice"] = new_notice
            _settings["primary_color"] = primary_color
            _settings["login_enabled"] = login_enabled
            _auth_save_settings(_settings)
            st.success("Settings saved.")
        
        st.markdown("#### App Configuration")
        auto_logout = st.slider("Auto Logout (minutes of inactivity)", 5, 20, 10080)
        max_upload_size = st.slider("Max Upload Size (MB)", 5, 500, 200)
        
        if st.button("Save Configuration"):
            _settings["auto_logout"] = auto_logout
            _settings["max_upload_size"] = max_upload_size
            _auth_save_settings(_settings)
            st.success("Configuration saved!")
    
    with tab4:
        st.markdown("### IP Management")
        st.markdown("#### IP Whitelist/Blacklist")
        
        ip_list = _settings.get("ip_list", {"whitelist": [], "blacklist": []})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Whitelist")
            for ip in ip_list["whitelist"]:
                st.write(f"{ip} ❌", key=f"wl_{ip}")
            new_whitelist = st.text_input("Add to Whitelist")
            if st.button("Add IP to Whitelist"):
                if new_whitelist and new_whitelist not in ip_list["whitelist"]:
                    ip_list["whitelist"].append(new_whitelist)
                    _settings["ip_list"] = ip_list
                    _auth_save_settings(_settings)
                    st.success(f"Added {new_whitelist} to whitelist")
        
        with col2:
            st.markdown("##### Blacklist")
            for ip in ip_list["blacklist"]:
                st.write(f"{ip} ❌", key=f"bl_{ip}")
            new_blacklist = st.text_input("Add to Blacklist")
            if st.button("Add IP to Blacklist"):
                if new_blacklist and new_blacklist not in ip_list["blacklist"]:
                    ip_list["blacklist"].append(new_blacklist)
                    _settings["ip_list"] = ip_list
                    _auth_save_settings(_settings)
                    st.success(f"Added {new_blacklist} to blacklist")
        
        st.markdown("#### Current IP Sessions")
        db = _auth_load_users()
        for uname, udata in db.get("users", {}).items():
            if udata.get("last_ip"):
                st.write(f"{uname}: {udata.get('last_ip')} - {udata.get('last_login', 'Never')}")
    
    with tab5:
        st.markdown("### Tools & Features")
        st.markdown("#### Feature Toggles")
        
        features = _settings.get("features", {
            "watermark": True,
            "premium_filters": True,
            "batch_processing": True,
            "high_res_output": True
        })
        
        # Create compact checkboxes for features
        cols = st.columns(2)
        feature_states = {}
        
        feature_list = list(features.items())
        for i, (feature, enabled) in enumerate(feature_list):
            with cols[i % 2]:
                feature_states[feature] = st.checkbox(
                    f"{feature.replace('_', ' ').title()}", 
                    value=enabled, 
                    key=f"feature_{feature}",
                    help=f"Enable/disable {feature}"
                )
        
        if st.button("Save Feature Settings"):
            _settings["features"] = feature_states
            _auth_save_settings(_settings)
            st.success("Feature settings saved!")
        
        st.markdown("#### System Tools")
        if st.button("Clear All Cache"):
            st.cache_resource.clear()
            st.session_state.clear()
            st.success("Cache cleared!")
            st.rerun()
        
        # Export/Import Settings
        st.markdown("#### Export/Import Settings")
        export_data = export_settings()
        
        st.download_button(
            label="Export Settings",
            data=export_data,
            file_name="app_settings.json",
            mime="application/json"
        )
        
        imported_file = st.file_uploader("Import Settings", type=["json"])
        if imported_file is not None:
            if st.button("Import Settings"):
                if import_settings(imported_file.getvalue().decode()):
                    st.success("Settings imported successfully!")
                    st.rerun()
                else:
                    st.error("Failed to import settings. Invalid file format.")
    
    with tab6:
        st.markdown("### Overlap Settings")
        st.markdown("Configure overlap percentages for different themes")
        
        # Get all available years and themes
        overlay_years = list_subfolders(os.path.join(ASSETS_DIR, "overlays"))
        all_themes = {}
        
        for year in overlay_years:
            year_path = os.path.join(ASSETS_DIR, "overlays", year)
            themes = list_subfolders(year_path)
            if not themes:
                # If no subfolders, use the year folder itself as a theme
                all_themes[year] = [year]
            else:
                all_themes[year] = themes
        
        # Create a nested structure for overlap settings
        overlap_settings = _load_overlap_settings()
        
        for year, themes in all_themes.items():
            st.markdown(f"#### {year}")
            for theme in themes:
                key = f"{year}_{theme}"
                current_value = overlap_settings.get(key, 7)  # Default to 14
                new_value = st.slider(
                    f"{theme} overlap percentage", 
                    min_value=-15, 
                    max_value=50, 
                    value=current_value,
                    key=f"overlap_{key}"
                )
                overlap_settings[key] = new_value
                
        
        if st.button("Save Overlap Settings"):
            _save_overlap_settings(overlap_settings)
            st.success("Overlap settings saved!")
    
    with tab7:
        st.markdown("### Tool Toggles")
        st.markdown("Enable/disable individual tools and features")
        
        tool_settings = _load_tool_settings()
        
        st.markdown("#### Text Style Options")
        col1, col2 = st.columns(2)
        with col1:
            for style in ["white_only", "white_black_outline", "gradient", "neon", "white_color_outline", "pure_color_white_outline"]:
                tool_settings["text_style"][style] = st.checkbox(
                    style.replace("_", " ").title(),
                    value=tool_settings["text_style"].get(style, True),
                    key=f"text_style_{style}"
                )
        with col2:
            for style in ["rainbow", "country_flag", "3d", "multicolor_gradient_outline", "metallic", "glowing"]:
                tool_settings["text_style"][style] = st.checkbox(
                    style.replace("_", " ").title(),
                    value=tool_settings["text_style"].get(style, True),
                    key=f"text_style_{style}"
                )
        
        st.markdown("#### Overlay Options")
        col1, col2 = st.columns(2)
        with col1:
            for overlay in ["1024", "2025", "pet"]:
                tool_settings["overlay"][overlay] = st.checkbox(
                    f"{overlay} Overlay",
                    value=tool_settings["overlay"].get(overlay, True),
                    key=f"overlay_{overlay}"
                )
        
        st.markdown("#### Filter Options")
        col1, col2 = st.columns(2)
        with col1:
            for filt in ["sepia", "black_white", "vintage", "vignette"]:
                tool_settings["filter"][filt] = st.checkbox(
                    filt.replace("_", " ").title(),
                    value=tool_settings["filter"].get(filt, True),
                    key=f"filter_{filt}"
                )
        with col2:
            for filt in ["sketch", "cartoon", "anime"]:
                tool_settings["filter"][filt] = st.checkbox(
                    filt.replace("_", " ").title(),
                    value=tool_settings["filter"].get(filt, True),
                    key=f"filter_{filt}"
                )
        
        st.markdown("#### Advanced Options")
        col1, col2 = st.columns(2)
        with col1:
            for adv in ["emoji", "watermark", "quote"]:
                tool_settings["advanced"][adv] = st.checkbox(
                    adv.replace("_", " ").title(),
                    value=tool_settings["advanced"].get(adv, True),
                    key=f"advanced_{adv}"
                )
        
        if st.button("Save Tool Settings"):
            _save_tool_settings(tool_settings)
            st.success("Tool settings saved!")
    
    with tab8:
        st.markdown("### Usage Statistics")
        st.markdown("#### Image Generation by User")
        
        usage_data = get_usage_data()
        if not usage_data.empty:
            st.dataframe(usage_data)
            
            # Show summary statistics
            st.markdown("#### Summary")
            summary = usage_data.groupby("username")["image_count"].sum().reset_index()
            st.dataframe(summary)
            
            # Download usage data
            csv = usage_data.to_csv(index=False)
            st.download_button(
                label="Download Usage Data as CSV",
                data=csv,
                file_name="usage_data.csv",
                mime="text/csv"
            )
        else:
            st.info("No usage data available yet.")
    
    with tab9:
        st.markdown("### Tool Visibility Control")
        st.markdown("Turn tools on/off to show/hide them from the main interface")
        
        # Get current tool settings
        tool_settings = _load_tool_settings()
        
        # Create a compact form for tool visibility
        st.markdown("#### Main Tool Visibility")
        cols = st.columns(3)
        
        # Text style options
        with cols[0]:
            st.markdown("**Text Styles**")
            for style in tool_settings["text_style"]:
                tool_settings["text_style"][style] = st.checkbox(
                    style.replace("_", " ").title(),
                    value=tool_settings["text_style"][style],
                    key=f"vis_text_{style}"
                )
        
        # Overlay options
        with cols[1]:
            st.markdown("**Overlays**")
            for overlay in tool_settings["overlay"]:
                tool_settings["overlay"][overlay] = st.checkbox(
                    overlay,
                    value=tool_settings["overlay"][overlay],
                    key=f"vis_overlay_{overlay}"
                )
        
        # Filter options
        with cols[2]:
            st.markdown("**Filters**")
            for filt in tool_settings["filter"]:
                tool_settings["filter"][filt] = st.checkbox(
                    filt.replace("_", " ").title(),
                    value=tool_settings["filter"][filt],
                    key=f"vis_filter_{filt}"
                )
        
        # Advanced options
        st.markdown("**Advanced Features**")
        adv_cols = st.columns(3)
        for i, adv in enumerate(tool_settings["advanced"]):
            with adv_cols[i % 3]:
                tool_settings["advanced"][adv] = st.checkbox(
                    adv.replace("_", " ").title(),
                    value=tool_settings["advanced"][adv],
                    key=f"vis_advanced_{adv}"
                )
        
        if st.button("Save Tool Visibility Settings"):
            _save_tool_settings(tool_settings)
            st.success("Tool visibility settings saved!")
            st.rerun()
    
    with tab10:
        st.markdown("### Theme Preview")
        st.markdown("Preview theme settings and test with your own images")
        
        # Get all available years and themes
        overlay_years = list_subfolders(os.path.join(ASSETS_DIR, "overlays"))
        all_themes = {}
        
        for year in overlay_years:
            year_path = os.path.join(ASSETS_DIR, "overlays", year)
            themes = list_subfolders(year_path)
            if not themes:
                all_themes[year] = [year]
            else:
                all_themes[year] = themes
        
        # Create a compact form for theme selection
        col1, col2 = st.columns(2)
        
        with col1:
            selected_year = st.selectbox("Select Year", list(all_themes.keys()), index=0)
        
        with col2:
            if selected_year in all_themes:
                selected_theme = st.selectbox("Select Theme", all_themes[selected_year], index=0)
        
        # Add greeting type for preview
        preview_greeting = st.selectbox("Preview Greeting Type", ["Good Morning", "Good Night"])
        preview_show_wish = st.checkbox("Show Wish in Preview", value=True)
        preview_png_size = st.slider("PNG Size in Preview", 0.01, 0.75, 0.18)
        
        # Display theme preview
        if selected_year and selected_theme:
            theme_path = os.path.join(ASSETS_DIR, "overlays", selected_year, selected_theme)
            
            if os.path.exists(theme_path):
                st.markdown(f"### Preview for {selected_year} - {selected_theme}")
                
                # Display individual theme files
                theme_files = list_files(theme_path, [".png", ".jpg", ".jpeg"])
                
                if theme_files:
                    cols = st.columns(min(3, len(theme_files)))
                    for i, file in enumerate(sorted(theme_files)):
                        with cols[i % 3]:
                            try:
                                img = Image.open(file)
                                st.image(img, caption=os.path.basename(file), use_container_width=True)
                            except Exception as e:
                                st.error(f"Error loading {os.path.basename(file)}: {str(e)}")
                else:
                    st.warning("No image files found in this theme folder.")
                
                # Test with custom image
                st.markdown("### Test with Your Image")
                test_image = st.file_uploader("Upload test image (or leave blank for dummy)", type=["jpg", "jpeg", "png"], key="theme_test")
                
                try:
                    if test_image:
                        img = Image.open(test_image)
                        img = smart_crop(img, 3/4).convert("RGBA")
                    else:
                        # Dummy image
                        img = Image.new("RGBA", (750, 1000), (200, 200, 200, 255))
                    
                    # Get overlap
                    overlap_key = f"{selected_year}_{selected_theme}"
                    overlap_percent = _load_overlap_settings().get(overlap_key, 14)
                    
                    # Load PNGs based on greeting
                    png_files = []
                    if preview_greeting == "Good Morning":
                        png_files = ["1.png", "2.png"]
                        if preview_show_wish:
                            png_files.append("4.png")
                    elif preview_greeting == "Good Night":
                        png_files = ["1.png", "3.png"]
                        if preview_show_wish:
                            png_files.append("5.png")
                    
                    pngs = []
                    for f in png_files:
                        path = os.path.join(theme_path, f)
                        if os.path.exists(path):
                            png_img = Image.open(path).convert("RGBA")
                            png_img._filename = f
                            pngs.append(png_img)
                    
                    if pngs:
                        # Layering
                        main_pngs = [p for p in pngs if p._filename in ["1.png", "2.png", "3.png"]]
                        wish_pngs = [p for p in pngs if p._filename in ["4.png", "5.png"]]
                        
                        main_pngs.sort(key=lambda x: 0 if x._filename == "1.png" else 1)
                        
                        pngs = main_pngs + wish_pngs
                        
                        # Gaps
                        main_gap = -int(min([p.height for p in main_pngs]) * overlap_percent / 100) if len(main_pngs) >= 2 else 0
                        wish_gap = 10
                        
                        gaps = [main_gap] * (len(pngs) - 1)
                        if preview_show_wish and len(pngs) > len(main_pngs):
                            gaps[-1] = wish_gap
                        
                        total_h = sum(p.height for p in pngs) + sum(gaps)
                        max_w = max(p.width for p in pngs)
                        
                        scale = min(preview_png_size, min((img.width * 0.9) / max_w, (img.height * 0.9) / total_h))
                        pngs = [p.resize((int(p.width * scale), int(p.height * scale)), Image.LANCZOS) for p in pngs]
                        
                        total_h = sum(p.height for p in pngs) + sum(gaps)
                        max_w = max(p.width for p in pngs)
                        
                        start_y = (img.height - total_h) // 2
                        start_x = (img.width - max_w) // 2
                        
                        current_y = start_y
                        for i, p in enumerate(pngs):
                            x = start_x + (max_w - p.width) // 2
                            x = max(0, min(x, img.width - p.width))
                            y = max(0, min(current_y, img.height - p.height))
                            img.paste(p, (x, y), p)
                            if i < len(pngs) - 1:
                                current_y += p.height + gaps[i]
                        
                        st.image(img, caption="Full Theme Preview with Overlap", use_container_width=True)
                        
                        new_overlap = st.slider(
                            "Adjust Overlap Percentage", 
                            min_value=-15, 
                            max_value=50, 
                            value=overlap_percent,
                            key=f"preview_overlap_{overlap_key}"
                        )
                        
                        if st.button("Save Overlap Setting"):
                            overlap_settings = _load_overlap_settings()
                            overlap_settings[overlap_key] = new_overlap
                            _save_overlap_settings(overlap_settings)
                            st.success("Overlap setting saved!")
                    else:
                        st.warning("Missing PNG files for selected greeting.")
                except Exception as e:
                    st.error(f"Error in preview: {str(e)}")
    
    st.markdown("---")
    st.write("Contact developer: +91 9140588751")
    
    # Add logout button for admin panel
    if st.button("Logout from Admin Panel"):
        st.session_state["_auth_admin_authenticated"] = False
        st.session_state["_auth_admin_user"] = None
        st.session_state["_auth_show_admin"] = False
        st.success("Logged out from Admin Panel!")
        st.rerun()
    
    st.stop()

if _settings.get("notice"):
    st.info(_settings.get("notice"))
# ========== END AUTH / ADMIN BLOCK ==========

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ 100+ EDIT IN 1 CLICK", layout="wide")

# Custom CSS with dynamic primary color
primary_color = _settings.get("primary_color", "#ffcc00")
st.markdown(f"""
    <style>
    .main {{
        background-color: #0a0a0a;
        color: #ffffff;
    }}
    .header-container {{
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 2px solid {primary_color};
        box-shadow: 0 0 20px rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.5);
    }}
    .stButton>button {{
        background: linear-gradient(135deg, {primary_color} 0%, #ff9900 100%);
        color: #000000;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 50px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    .stButton>button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.5);
    }}
    .stSlider>div>div>div>div {{
        background-color: {primary_color};
    }}
    .stImage>img {{
        border: 2px solid {primary_color};
        border-radius: 8px;
        box-shadow: 0 0 15px rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.3);
    }}
    .feature-card {{
        border: 1px solid {primary_color};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        color: #ffffff;
        box-shadow: 0 0 15px rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.2);
    }}
    .section-title {{
        color: {primary_color};
        border-bottom: 2px solid {primary_color};
        padding-bottom: 8px;
        margin-top: 25px;
        font-size: 1.4rem;
    }}
    .quote-display {{
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        border-left: 4px solid {primary_color};
    }}
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {primary_color}, #ff9900);
    }}
    </style>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder: str, exts: List[str]) -> List[str]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext.lower()) for ext in exts)]

def list_subfolders(folder: str) -> List[str]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

def get_text_size(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    if text is None:
        return 0, 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_font(font_folder=os.path.join(ASSETS_DIR, "fonts")) -> ImageFont.FreeTypeFont:
    try:
        fonts = list_files(font_folder, [".ttf", ".otf"])
        if not fonts:
            return ImageFont.truetype("arial.ttf", 80)
        for _ in range(3):
            try:
                font_path = os.path.join(font_folder, random.choice(fonts))
                return ImageFont.truetype(font_path, 80)
            except:
                continue
        return ImageFont.truetype("arial.ttf", 80)
    except:
        return ImageFont.load_default()

def get_random_wish(greeting_type: str) -> str:
    wishes = {
        "Good Morning": [
            "Have a nice day!",
            "Have a great day!"
        ],
        "Good Afternoon": [
            "Have a nice day!",
            "Have a great day!"
        ],
        "Good Evening": [
            "Have a nice day!",
            "Have a great day!"
        ],
        "Good Night": [
            "Sweet dreams!",
            "Sweet dreams!"
        ],
        "Happy Birthday": [
            "Happy Birthday!",
            "Wishing you a fantastic birthday!"
        ],
        "Merry Christmas": [
            "Merry Christmas!",
            "Happy Holidays!"
        ],
        "Custom Greeting": [
            "Have a nice day!",
            "Have a great day!"
        ]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_quote() -> str:
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Stay hungry, stay foolish. - Steve Jobs",
        "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
        "Success is not final, failure is not fatal. - Winston Churchill",
        "The best way to predict the future is to create it. - Peter Drucker",
        "Believe you can and you're halfway there. - Theodore Roosevelt",
        "Life is what happens when you're busy making other plans. - John Lennon",
        "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
        "Do what you can, with what you have, where you are. - Theodore Roosevelt",
        "Strive not to be a success, but rather to be of value. - Albert Einstein"
    ]
    return random.choice(quotes)

def get_random_color() -> Tuple[int, int, int]:
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def get_vibrant_color() -> Tuple[int, int, int]:
    hue = random.random()
    r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, 0.9, 0.9)]
    return (r, g, b)

PURE_COLORS = [
    (255, 0, 0), (255, 255, 0), (0, 255, 0),
    (0, 0, 255), (255, 0, 255), (0, 255, 255)
]

def get_gradient_colors(dominant_color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
    if random.random() < 0.8:
        return [(255, 255, 255), dominant_color]
    return [(255, 255, 255), random.choice(PURE_COLORS)]

def get_multi_gradient_colors() -> List[Tuple[int, int, int]]:
    num_colors = random.randint(2, 7)
    return [get_vibrant_color() for _ in range(num_colors)]

def create_gradient_mask(width: int, height: int, colors: List[Tuple[int, int, int]], direction: str = 'horizontal') -> Image.Image:
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    if direction == 'vertical':
        # For vertical gradient
        num_segments = len(colors) - 1
        segment_height = height // num_segments
        for seg in range(num_segments):
            start_color = colors[seg]
            end_color = colors[seg + 1]
            start_y = seg * segment_height
            end_y = start_y + segment_height
            for y in range(start_y, min(end_y, height)):
                ratio = (y - start_y) / segment_height
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        num_segments = len(colors) - 1
        segment_width = width // num_segments
        for seg in range(num_segments):
            start_color = colors[seg]
            end_color = colors[seg + 1]
            start_x = seg * segment_width
            end_x = start_x + segment_width
            for x in range(start_x, min(end_x, width)):
                ratio = (x - start_x) / segment_width
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
    
    return gradient

def format_date(date_format: str = "%d %B %Y", show_day: bool = False) -> str:
    today = datetime.now()
    formatted_date = today.strftime(date_format)
    
    if show_day:
        day_name = today.strftime("%A")
        formatted_date += f" ({day_name})"
    
    return formatted_date

def apply_overlay(image: Image.Image, overlay_path: str, size: float = 0.5, position: Tuple[int, int] = None) -> Image.Image:
    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        new_size = (int(image.width * size), int(image.height * size))
        overlay = overlay.resize(new_size, Image.LANCZOS)
        
        if position is None:
            max_x = max(20, image.width - overlay.width - 20)
            max_y = max(20, image.height - overlay.height - 20)
            x = random.randint(20, max_x) if max_x > 20 else 20
            y = random.randint(20, max_y) if max_y > 20 else 20
        else:
            x, y = position
        
        image.paste(overlay, (x, y), overlay)
    except Exception as e:
        st.error(f"Error applying overlay: {str(e)}")
    return image

# ========== UPDATED FILENAME GENERATION WITH TIMESTAMP FEATURE ==========
def generate_filename(base_name="Picsart", time_option="current", custom_time=None) -> str:
    """
    Generate filename with timestamp options
    
    Args:
        base_name: Base name for the file
        time_option: "current", "past", "future", or "custom"
        custom_time: Custom datetime object (for custom option)
    """
    try:
        # Try to get device timezone, fallback to Kolkata/IST
        try:
            device_tz = pytz.timezone('Asia/Kolkata')  # Default to IST
            # You can add logic here to detect device timezone if needed
        except:
            device_tz = pytz.timezone('Asia/Kolkata')  # Fallback to IST
        
        now = datetime.now(device_tz)
        
        if time_option == "past":
            target_time = now - timedelta(minutes=10)
        elif time_option == "future":
            target_time = now + timedelta(minutes=10)
        elif time_option == "custom" and custom_time:
            target_time = custom_time
        else:  # current
            target_time = now
        
        # Format: Picsart_25-01-15_14-30-45.jpg
        timestamp = target_time.strftime('%y-%m-%d_%H-%M-%S')
        return f"{base_name}_{timestamp}.jpg"
    
    except Exception as e:
        # Fallback to original method if any error
        future_minutes = random.randint(1, 10)
        now = datetime.now()
        future_time = now + timedelta(minutes=future_minutes)
        return f"{base_name}_{future_time.strftime('%y-%m-%d_%H-%M-%S')}.jpg"

def get_watermark_position(img: Image.Image, watermark: Image.Image, occupied_boxes: List[Tuple[int, int, int, int]], padding: int = 10) -> Tuple[int, int]:
    ew, eh = watermark.size
    iw, ih = img.size
    possible_positions = [
        (20, ih - eh - 20),
        (iw - ew - 20, ih - eh - 20),
        (20, 20),
        (iw - ew - 20, 20),
        ((iw - ew) // 2, ih - eh - 20)
    ]
    for pos in possible_positions:
        new_box = (pos[0], pos[1], ew, eh)
        if not any_overlap(new_box, occupied_boxes, padding):
            return pos
    # Fallback with more tries
    return find_non_overlapping_position((iw, ih), (ew, eh), occupied_boxes, None, 100, padding)

def enhance_image_quality(img: Image.Image, brightness=1.0, contrast=1.0, sharpness=1.0, saturation=1.0) -> Image.Image:
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)
    img = ImageEnhance.Color(img).enhance(saturation)
    
    return img

def upscale_text_elements(img: Image.Image, scale_factor: int = 4) -> Image.Image:
    if scale_factor > 1:
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.LANCZOS)
    return img

def apply_vignette(img: Image.Image, intensity: float = 0.8) -> Image.Image:
    width, height = img.size
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    mask = 1 - np.clip(R * intensity, 0, 1)
    mask = (mask * 255).astype(np.uint8)
    mask_img = Image.fromarray(mask).convert('L')
    vignette = Image.new('RGB', (width, height), (0, 0, 0))
    img.paste(vignette, (0, 0), mask_img)
    return img

def apply_sepia(img: Image.Image) -> Image.Image:
    arr = np.array(img)
    sepia_filter = np.array([
        [.393, .769, .189],
        [.349, .686, .168],
        [.272, .534, .131]
    ])
    arr = arr @ sepia_filter.T
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype('uint8'))

def apply_black_white(img: Image.Image) -> Image.Image:
    return img.convert('L').convert('RGB')

def apply_vintage(img: Image.Image) -> Image.Image:
    img = apply_sepia(img)
    noise = np.random.normal(0, 25, img.size[::-1] + (3,)).astype(np.uint8)
    noise_img = Image.fromarray(noise)
    img = ImageChops.add(img, noise_img, scale=2.0)
    img = apply_vignette(img, 0.5)
    return img

def apply_sketch_effect(img: Image.Image) -> Image.Image:
    img_gray = img.convert('L')
    img_invert = ImageOps.invert(img_gray)
    img_blur = img_invert.filter(ImageFilter.GaussianBlur(radius=3))
    return ImageOps.invert(img_blur)

def apply_cartoon_effect(img: Image.Image) -> Image.Image:
    reduced = img.quantize(colors=8, method=1)
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    cartoon = reduced.convert('RGB')
    cartoon.paste((0, 0, 0), (0, 0), edges)
    return cartoon

def apply_anime_effect(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Color(img).enhance(1.5)
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    result = img.copy()
    result.paste((0, 0, 0), (0, 0), edges)
    return result

def apply_emoji_stickers(img: Image.Image, emojis: List[str], occupied_boxes: List[Tuple[int, int, int, int]], num_stickers=5, padding: int = 10) -> Image.Image:
    if not emojis:
        return img
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 40)
    es = 40  # emoji size approx
    for _ in range(num_stickers):
        pos = find_non_overlapping_position(img.size, (es, es), occupied_boxes, None, 100, padding)
        emoji = random.choice(emojis)
        draw.text(pos, emoji, font=font, fill=(255, 255, 0))
        occupied_boxes.append((pos[0], pos[1], es, es))
    return img

def get_dominant_color(img: Image.Image) -> Tuple[int, int, int]:
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img_small = img.resize((100, 100))
    colors = Counter(img_small.getdata())
    dominant = colors.most_common(1)[0][0]
    if len(dominant) > 3:
        dominant = dominant[:3]
    h, l, s = colorsys.rgb_to_hls(dominant[0] / 255, dominant[1] / 255, dominant[2] / 255)
    if l < 0.5:
        l = 0.7
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def find_text_position(img: Image.Image, required_width: int, required_height: int, prefer_top: bool = True) -> Tuple[int, int]:
    arr = np.array(img.convert('L'))
    step = 20
    min_var = float('inf')
    best_pos = (20, 20 if prefer_top else img.height - required_height - 20)
    start_y = 0 if prefer_top else img.height // 2
    for y in range(start_y, img.height - required_height, step):
        for x in range(0, img.width - required_width, step):
            region = arr[y:y + required_height, x:x + required_width]
            var = np.var(region)
            if var < min_var:
                min_var = var
                best_pos = (x, y)
    return best_pos

def get_random_horizontal_position(img_width: int, text_width: int) -> int:
    positions = [
        20,
        (img_width - text_width) // 2,
        img_width - text_width - 20
    ]
    return random.choice(positions)

def apply_text_effect(draw: ImageDraw.Draw, position: Tuple[int, int], text: str, font: ImageFont.FreeTypeFont, 
                      effect_settings: dict, base_img: Image.Image) -> dict:
    x, y = position
    effect_type = effect_settings['type']
    
    if text is None or text.strip() == "":
        return effect_settings
    
    text_width, text_height = get_text_size(draw, text, font)
    
    if effect_type == 'random':
        available_effects = [
            'white_only', 'white_black_outline_shadow', 'gradient', 
            'neon', 'rainbow', 'country_flag', '3d',
            'white_color_outline_shadow', 'pure_color_white_outline',
            'multicolor_gradient_outline', 'metallic', 'glowing'
        ]
        effect_type = random.choice(available_effects)
        effect_settings['type'] = effect_type
    
    shadow_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    outline_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    fill_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    
    shadow_draw = ImageDraw.Draw(shadow_layer)
    outline_draw = ImageDraw.Draw(outline_layer)
    fill_draw = ImageDraw.Draw(fill_layer)
    
    shadow_offset = (2, 2)
    shadow_draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 40))
    
    pure_colors = [
        (255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0),
        (0, 0, 255), (75, 0, 130), (238, 130, 238), (255, 192, 203)
    ]
    
    outline_range = 1 if effect_type == 'neon' else 2
    
    if effect_type == 'white_color_outline_shadow':
        outline_color = random.choice(pure_colors)
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                if ox != 0 or oy != 0:
                    outline_draw.text((x + ox, y + oy), text, font=font, fill=outline_color)
        fill_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    elif effect_type == 'pure_color_white_outline':
        text_color = random.choice(pure_colors)
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                if ox != 0 or oy != 0:
                    outline_draw.text((x + ox, y + oy), text, font=font, fill=(255, 255, 255, 255))
        fill_draw.text((x, y), text, font=font, fill=text_color)
    
    elif effect_type == 'multicolor_gradient_outline':
        colors = [random.choice(pure_colors) for _ in range(random.randint(2, 4))]
        gradient = create_gradient_mask(text_width, text_height, colors)
        mask = Image.new("L", (text_width, text_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((0, 0), text, font=font, fill=255)
        gradient_text = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
        gradient_text.paste(gradient, (0, 0), mask)
        
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                if ox != 0 or oy != 0:
                    outline_draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 255))
        
        fill_layer.paste(gradient_text, (x, y), gradient_text)
    
    elif effect_type == 'metallic':
        metallic_colors = [(192, 192, 192), (169, 169, 169), (211, 211, 211), (105, 105, 105)]
        base_color = random.choice(metallic_colors)
        highlight_color = (255, 255, 255, 180)
        
        fill_draw.text((x, y), text, font=font, fill=base_color)
        
        fill_draw.text((x-1, y-1), text, font=font, fill=highlight_color)
    
    elif effect_type == 'glowing':
        glow_color = random.choice(pure_colors)
        glow_size = 15
        for i in range(glow_size, 0, -2):
            alpha = int(100 * (i / glow_size))
            for ox in range(-i, i + 1, 2):
                for oy in range(-i, i + 1, 2):
                    if ox != 0 or oy != 0:
                        fill_draw.text((x + ox, y + oy), text, font=font, fill=(*glow_color, alpha))
        fill_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    else:
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                if ox != 0 or oy != 0:
                    outline_draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 255))
        
        mask = Image.new("L", (text_width, text_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((0, 0), text, font=font, fill=255)
        
        if effect_type in ['gradient', 'rainbow']:
            colors = effect_settings['colors']
            gradient = create_gradient_mask(text_width, text_height, colors)
            gradient_text = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
            gradient_text.paste(gradient, (0, 0), mask)
            fill_layer.paste(gradient_text, (x, y), gradient_text)
        
        elif effect_type == 'neon':
            glow_color = get_vibrant_color()
            glow_size = 10
            for i in range(glow_size, 0, -1):
                alpha = int(80 * (i / glow_size))
                for ox in range(-i, i + 1):
                    for oy in range(-i, i + 1):
                        if ox != 0 or oy != 0:
                            fill_draw.text((x + ox, y + oy), text, font=font, fill=(*glow_color, alpha))
            fill_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        elif effect_type == 'country_flag':
            flags = list_files(os.path.join(ASSETS_DIR, "flags"), [".png", ".jpg"])
            if flags:
                flag_path = os.path.join(ASSETS_DIR, "flags", random.choice(flags))
                flag_img = Image.open(flag_path).convert("RGB").resize((text_width, text_height), Image.LANCZOS)
                flag_text = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
                flag_text.paste(flag_img, (0, 0), mask)
                fill_layer.paste(flag_text, (x, y), flag_text)
            else:
                fill_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        elif effect_type == '3d':
            depth = 5
            shadow_color = (100, 100, 100, 255)
            for i in range(depth):
                fill_draw.text((x + i, y + i), text, font=font, fill=shadow_color)
            fill_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        else:
            fill_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    base_img_rgba = base_img.convert('RGBA') if base_img.mode != 'RGBA' else base_img
    base_img_rgba = Image.alpha_composite(base_img_rgba, shadow_layer)
    base_img_rgba = Image.alpha_composite(base_img_rgba, outline_layer)
    base_img_rgba = Image.alpha_composite(base_img_rgba, fill_layer)
    
    base_img.paste(base_img_rgba, (0, 0))
    
    return effect_settings

def get_pet_position(img: Image.Image, pet_img: Image.Image, occupied_boxes: List[Tuple[int, int, int, int]], padding: int = 10) -> Tuple[int, int]:
    ew, eh = pet_img.size
    iw, ih = img.size
    possible_positions = [
        (20, ih - eh - 20),
        (iw - ew - 20, ih - eh - 20),
        ((iw - ew) // 2, ih - eh - 20)
    ]
    for pos in possible_positions:
        new_box = (pos[0], pos[1], ew, eh)
        if not any_overlap(new_box, occupied_boxes, padding):
            return pos
    # Fallback
    return find_non_overlapping_position((iw, ih), (ew, eh), occupied_boxes, None, 100, padding)

def is_overlap(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> bool:
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return max(x1, x2) < min(x1 + w1, x2 + w2) and max(y1, y2) < min(y1 + h1, y2 + h2)

def any_overlap(new_box: Tuple[int, int, int, int], occupied: List[Tuple[int, int, int, int]], padding: int = 0) -> bool:
    inflated_new = (new_box[0] - padding, new_box[1] - padding, new_box[2] + 2 * padding, new_box[3] + 2 * padding)
    for box in occupied:
        inflated_box = (box[0] - padding, box[1] - padding, box[2] + 2 * padding, box[3] + 2 * padding)
        if is_overlap(inflated_new, inflated_box):
            return True
    return False

def find_non_overlapping_position(img_size: Tuple[int, int], elem_size: Tuple[int, int], occupied: List[Tuple[int, int, int, int]], 
                                  preferred_pos: Optional[Tuple[int, int]] = None, tries: int = 100, padding: int = 10) -> Tuple[int, int]:
    iw, ih = img_size
    ew, eh = elem_size
    if preferred_pos:
        x, y = preferred_pos
        x = max(0, min(x, iw - ew))
        y = max(0, min(y, ih - eh))
        if not any_overlap((x, y, ew, eh), occupied, padding):
            return x, y
    for _ in range(tries):
        x = random.randint(0, iw - ew)
        y = random.randint(0, ih - eh)
        if not any_overlap((x, y, ew, eh), occupied, padding):
            return x, y
    # Fallback to candidate positions
    candidates = [
        (0, 0),
        (iw - ew, 0),
        (0, ih - eh),
        (iw - ew, ih - eh),
        ((iw - ew) // 2, (ih - eh) // 2)
    ]
    for cx, cy in candidates:
        if not any_overlap((cx, cy, ew, eh), occupied, padding):
            return cx, cy
    # Ultimate fallback
    return (iw - ew, ih - eh)

def get_overlap_percentage(year, theme):
    overlap_settings = _load_overlap_settings()
    key = f"{year}_{theme}"
    return overlap_settings.get(key, 14)

def generate_background(background_type: str) -> Image.Image:
    width, height = 750, 1000  # 3:4 ratio
    if background_type == "Random Color":
        if random.random() < 0.4:
            color = (255, 255, 255)
            return Image.new("RGB", (width, height), color)
        else:
            solid_colors = [
                (255, 0, 0),  # red
                (255, 192, 203),  # pink
                (199, 21, 133),  # dark pink
                (255, 182, 193),  # light pink
            ]
            gradient_options = [
                [(255, 192, 203), (255, 255, 255)],  # pink white
                [(255, 255, 0), (255, 0, 0)],  # yellow red
                get_multi_gradient_colors(),  # rainbow
            ]
            if random.random() < 0.5:
                color = random.choice(solid_colors)
                return Image.new("RGB", (width, height), color)
            else:
                colors = random.choice(gradient_options)
                return create_gradient_mask(width, height, colors, random.choice(['horizontal', 'vertical']))
    elif background_type == "Pre-made Image":
        bg_folder = os.path.join(ASSETS_DIR, "backgrounds")
        bg_files = list_files(bg_folder, [".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG"])
        if bg_files:
            path = random.choice(bg_files)
            full_path = os.path.join(bg_folder, path)
            bg = Image.open(full_path).convert("RGB")
            return smart_crop(bg, 3/4).resize((width, height), Image.LANCZOS)
        else:
            return Image.new("RGB", (width, height), (255, 255, 255))
    return Image.new("RGB", (width, height), (255, 255, 255))

def create_variant(original_img: Optional[Image.Image], settings: dict) -> Optional[Image.Image]:
    try:
        img = original_img
        if img is None:
            img = generate_background(settings['background_type'])
        img = img.convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        font = get_random_font(settings.get('font_folder', os.path.join(ASSETS_DIR, "fonts")))
        if font is None:
            return None
        
        dominant_color = get_dominant_color(img)
        
        effect_settings = {
            'type': settings.get('text_effect', 'gradient'),
            'outline_size': 2,
            'colors': get_gradient_colors(dominant_color) if settings.get('text_effect', 'gradient') == 'gradient' else get_multi_gradient_colors()
        }
        
        style_mode = settings.get('style_mode', 'Text')
        
        overlap_percent = settings.get('overlap_percent', 14)
        
        occupied_boxes = []
        
        min_distance = 20
        padding = min_distance // 2
        
        if style_mode == 'PNG Overlay' and settings['greeting_type'] in ["Good Morning", "Good Night"]:
            years = list_subfolders(os.path.join(ASSETS_DIR, "overlays"))
            if not years:
                st.warning("No overlay years found.")
                return img.convert("RGB")
            
            overlay_year = settings.get('overlay_year', "2025")
            if overlay_year == "ALL":
                selected_years = years
            else:
                selected_years = [overlay_year]
                if overlay_year not in years:
                    st.warning("Selected year not found.")
                    return img.convert("RGB")
            
            theme_paths = []
            for y in selected_years:
                year_path = os.path.join(ASSETS_DIR, "overlays", y)
                sub_themes = list_subfolders(year_path)
                if not sub_themes:
                    if list_files(year_path, [".png"]):
                        theme_paths.append((y, year_path))
                else:
                    for t in sub_themes:
                        theme_paths.append((t, os.path.join(year_path, t)))
            
            if not theme_paths:
                st.warning("No overlay themes found.")
                return img.convert("RGB")
            
            theme_name, base_path = random.choice(theme_paths)
            
            overlap_percent = get_overlap_percentage(overlay_year, theme_name)
            
            png_files = []
            if settings['greeting_type'] == "Good Morning":
                png_files = ["1.png", "2.png"]
                if settings['show_wish']:
                    png_files.append("4.png")
            elif settings['greeting_type'] == "Good Night":
                png_files = ["1.png", "3.png"]
                if settings['show_wish']:
                    png_files.append("5.png")
            
            pngs = []
            for f in png_files:
                path = os.path.join(base_path, f)
                if os.path.exists(path):
                    png_img = Image.open(path).convert("RGBA")
                    png_img._filename = os.path.basename(path)
                    pngs.append(png_img)
            
            if pngs:
                main_pngs = [p for p in pngs if p._filename in ["1.png", "2.png", "3.png"]]
                wish_pngs = [p for p in pngs if p._filename in ["4.png", "5.png"]]
                
                main_pngs.sort(key=lambda x: 0 if x._filename == "1.png" else 1)
                
                pngs = main_pngs + wish_pngs
                
                main_gap = -int(min([p.height for p in main_pngs]) * overlap_percent / 100) if len(main_pngs) >= 2 else 0
                wish_gap = min_distance
                
                gaps = [main_gap] * (len(pngs) - 1)
                if settings['show_wish'] and len(wish_pngs) > 0:
                    gaps[-1] = wish_gap
                
                total_h = sum(p.height for p in pngs) + sum(gaps)
                max_w = max(p.width for p in pngs)
                
                png_size = settings.get('png_size', 0.5)
                scale = min(png_size, min((img.width * 0.9) / max_w, (img.height * 0.9) / total_h))
                pngs = [p.resize((int(p.width * scale), int(p.height * scale)), Image.LANCZOS) for p in pngs]
                
                total_h = sum(p.height for p in pngs) + sum(gaps)
                max_w = max(p.width for p in pngs)
                
                main_position = random.choice(["top", "bottom"])
                if main_position == "top":
                    start_y = random.randint(20, img.height // 4)
                else:
                    start_y = img.height - total_h - random.randint(20, img.height // 4)
                
                if settings.get('custom_position', False):
                    start_x = settings.get('text_x', 100)
                    start_y = settings.get('text_y', 100)
                else:
                    start_x = get_random_horizontal_position(img.width, max_w)
                
                start_x = max(0, min(start_x, img.width - max_w))
                start_y = max(0, min(start_y, img.height - total_h))
                
                # Find non-overlapping position for the group
                start_x, start_y = find_non_overlapping_position(img.size, (max_w, total_h), occupied_boxes, (start_x, start_y), 100, padding)
                
                current_y = start_y
                group_boxes = []
                for i, p in enumerate(pngs):
                    offset = random.randint(-20, 20)
                    x = start_x + (max_w - p.width) // 2 + offset
                    x = max(0, min(x, img.width - p.width))
                    y = max(0, min(current_y, img.height - p.height))
                    img.paste(p, (x, y), p)
                    group_boxes.append((x, y, p.width, p.height))
                    if i < len(pngs) - 1:
                        current_y += p.height + gaps[i]
                
                # Add group bounding box
                gx = min(b[0] for b in group_boxes)
                gy = min(b[1] for b in group_boxes)
                gw = max(b[0] + b[2] for b in group_boxes) - gx
                gh = max(b[1] + b[3] for b in group_boxes) - gy
                occupied_boxes.append((gx, gy, gw, gh))
                
                main_end_y = current_y
            else:
                st.warning("Missing PNG files for selected theme.")
        else:
            if settings['show_text']:
                font_size = settings['main_size']
                font_main = font.font_variant(size=font_size)
                main_texts = settings['greeting_type'].split()
                if not main_texts:
                    main_texts = ["ULTRA", "PRO"]
                
                line_heights = []
                line_widths = []
                for t in main_texts:
                    w, h = get_text_size(draw, t, font_main)
                    line_widths.append(w)
                    line_heights.append(h)
                
                main_gap = -int(min(line_heights) * overlap_percent / 100) if len(line_heights) > 1 else 0
                total_h = sum(line_heights) + (len(main_texts) - 1) * main_gap
                max_w = max(line_widths)
                
                while max(line_widths) > img.width * 0.8 and font_size > 10:
                    font_size -= 5
                    font_main = font.font_variant(size=font_size)
                    line_widths = []
                    line_heights = []
                    for t in main_texts:
                        w, h = get_text_size(draw, t, font_main)
                        line_widths.append(w)
                        line_heights.append(h)
                    total_h = sum(line_heights) + (len(main_texts) - 1) * main_gap
                    max_w = max(line_widths)
                
                main_position = random.choice(["top", "bottom"])
                if main_position == "top":
                    text_y = random.randint(20, img.height // 4)
                else:
                    text_y = img.height - total_h - random.randint(20, img.height // 4)
                
                if settings.get('custom_position', False):
                    text_x = settings.get('text_x', 100)
                    text_y = settings.get('text_y', 100)
                else:
                    text_x = get_random_horizontal_position(img.width, max_w)
                
                text_x = max(0, min(text_x, img.width - max_w))
                text_y = max(0, min(text_y, img.height - total_h))
                
                # Find non-overlapping position for the group
                text_x, text_y = find_non_overlapping_position(img.size, (max_w, total_h), occupied_boxes, (text_x, text_y), 100, padding)
                
                current_y = text_y
                group_boxes = []
                for i, t in enumerate(main_texts):
                    offset = random.randint(-30, 50)
                    line_x = text_x + (max_w - line_widths[i]) // 2 + offset
                    line_x = max(0, min(line_x, img.width - line_widths[i]))
                    y_pos = max(0, min(current_y, img.height - line_heights[i]))
                    apply_text_effect(draw, (line_x, y_pos), t, font_main, effect_settings, img)
                    group_boxes.append((line_x, y_pos, line_widths[i], line_heights[i]))
                    if i < len(main_texts) - 1:
                        current_y += line_heights[i] + main_gap
                
                gx = min(b[0] for b in group_boxes)
                gy = min(b[1] for b in group_boxes)
                gw = max(b[0] + b[2] for b in group_boxes) - gx
                gh = max(b[1] + b[3] for b in group_boxes) - gy
                occupied_boxes.append((gx, gy, gw, gh))
                
                main_end_y = gy + gh
            
            if settings['show_wish']:
                font_size = settings['wish_size']
                font_wish = font.font_variant(size=font_size)
                wish_text = settings.get('custom_wish', None)
                if wish_text is None or wish_text.strip() == "":
                    wish_text = get_random_wish(settings['greeting_type'])
                
                avg_char_width = get_text_size(draw, "A", font_wish)[0]
                wrap_width = int((img.width * 0.8) / avg_char_width)
                lines = textwrap.wrap(wish_text, width=wrap_width)
                
                while len(lines) > 3 and font_size > 10:
                    font_size -= 5
                    font_wish = font.font_variant(size=font_size)
                    avg_char_width = get_text_size(draw, "A", font_wish)[0]
                    wrap_width = int((img.width * 0.8) / avg_char_width)
                    lines = textwrap.wrap(wish_text, width=wrap_width)
                
                line_heights = []
                line_widths = []
                for line in lines:
                    w, h = get_text_size(draw, line, font_wish)
                    line_widths.append(w)
                    line_heights.append(h)
                
                wish_gap = min_distance
                total_h = sum(line_heights) + (len(lines) - 1) * wish_gap
                max_w = max(line_widths)
                
                wish_position = random.choice(["mid", "bottom"])
                if wish_position == "mid":
                    wish_y = img.height // 2 - total_h // 2 + random.randint(-50, 50)
                else:
                    wish_y = img.height - total_h - random.randint(20, 100)
                
                if settings.get('custom_position', False):
                    wish_x = settings.get('text_x', 100)
                else:
                    wish_x = get_random_horizontal_position(img.width, max_w)
                
                if settings['show_text']:
                    wish_y = max(wish_y, main_end_y + min_distance)
                
                wish_x = max(0, min(wish_x, img.width - max_w))
                wish_y = max(0, min(wish_y, img.height - total_h))
                
                # Find non-overlapping position
                wish_x, wish_y = find_non_overlapping_position(img.size, (max_w, total_h), occupied_boxes, (wish_x, wish_y), 100, padding)
                
                current_y = wish_y
                group_boxes = []
                for i, line in enumerate(lines):
                    offset = random.randint(-20, 20)
                    line_x = wish_x + (max_w - line_widths[i]) // 2 + offset
                    line_x = max(0, min(line_x, img.width - line_widths[i]))
                    y_pos = max(0, min(current_y, img.height - line_heights[i]))
                    apply_text_effect(draw, (line_x, y_pos), line, font_wish, effect_settings, img)
                    group_boxes.append((line_x, y_pos, line_widths[i], line_heights[i]))
                    if i < len(lines) - 1:
                        current_y += line_heights[i] + wish_gap
                
                gx = min(b[0] for b in group_boxes)
                gy = min(b[1] for b in group_boxes)
                gw = max(b[0] + b[2] for b in group_boxes) - gx
                gh = max(b[1] + b[3] for b in group_boxes) - gy
                occupied_boxes.append((gx, gy, gw, gh))
        
        if settings['show_date']:
            font_date = font.font_variant(size=settings['date_size'])
            
            if settings['date_format'] == "8 July 2025":
                date_text = format_date("%d %B %Y", settings['show_day'])
            elif settings['date_format'] == "28 January 2025":
                date_text = format_date("%d %B %Y", settings['show_day'])
            elif settings['date_format'] == "07/08/2025":
                date_text = format_date("%m/%d/%Y", settings['show_day'])
            else:
                date_text = format_date("%Y-%m-%d", settings['show_day'])
                
            date_width, date_height = get_text_size(draw, date_text, font_date)
            
            date_x = get_random_horizontal_position(img.width, date_width)
            date_y = img.height - date_height - 20
            
            preferred = (date_x, date_y)
            date_x, date_y = find_non_overlapping_position(img.size, (date_width, date_height), occupied_boxes, preferred, 100, padding)
            
            apply_text_effect(draw, (date_x, date_y), date_text, font_date, effect_settings, img)
            occupied_boxes.append((date_x, date_y, date_width, date_height))
        
        if settings['show_quote']:
            font_quote = font.font_variant(size=settings['quote_size'])
            quote_text = settings['quote_text']
            
            lines = [line.strip() for line in quote_text.split('\n') if line.strip()]
            
            line_heights = []
            line_widths = []
            for line in lines:
                w, h = get_text_size(draw, line, font_quote)
                line_widths.append(w)
                line_heights.append(h)
            
            quote_gap = min_distance
            total_h = sum(line_heights) + (len(lines) - 1) * quote_gap
            max_w = max(line_widths)
            
            quote_x = (img.width - max_w) // 2
            quote_y = (img.height - total_h) // 2
            
            quote_x, quote_y = find_non_overlapping_position(img.size, (max_w, total_h), occupied_boxes, (quote_x, quote_y), 100, padding)
            
            current_y = quote_y
            group_boxes = []
            for i, line in enumerate(lines):
                line_x = quote_x + (max_w - line_widths[i]) // 2
                line_x = max(0, min(line_x, img.width - line_widths[i]))
                y_pos = max(0, min(current_y, img.height - line_heights[i]))
                apply_text_effect(draw, (line_x, y_pos), line, font_quote, effect_settings, img)
                group_boxes.append((line_x, y_pos, line_widths[i], line_heights[i]))
                if i < len(lines) - 1:
                    current_y += line_heights[i] + quote_gap
            
            gx = min(b[0] for b in group_boxes)
            gy = min(b[1] for b in group_boxes)
            gw = max(b[0] + b[2] for b in group_boxes) - gx
            gh = max(b[1] + b[3] for b in group_boxes) - gy
            occupied_boxes.append((gx, gy, gw, gh))
        
        if settings['use_watermark'] and settings['watermark_image']:
            watermark = settings['watermark_image'].copy()
            
            if settings['watermark_opacity'] < 1.0:
                alpha = watermark.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(settings['watermark_opacity'])
                watermark.putalpha(alpha)
            
            watermark.thumbnail((img.width//4, img.height//4))
            pos = get_watermark_position(img, watermark, occupied_boxes, padding)
            pos = (max(0, min(pos[0], img.width - watermark.width)), 
                   max(0, min(pos[1], img.height - watermark.height)))
            
            img.paste(watermark, pos, watermark)
            occupied_boxes.append((pos[0], pos[1], watermark.width, watermark.height))
        
        # ALL USERS GET PRO FEATURES WHEN LOGIN IS DISABLED
        if settings['use_coffee_pet'] and settings['pet_choice']:
            pet_files = list_files(os.path.join(ASSETS_DIR, "pets"), [".png", ".jpg", ".jpeg"])
            if settings['pet_choice'] == "Random":
                selected_pet = random.choice(pet_files) if pet_files else None
            else:
                selected_pet = settings['pet_choice']
            if selected_pet:
                pet_path = os.path.join(ASSETS_DIR, "pets", selected_pet)
                if os.path.exists(pet_path):
                    pet_img = Image.open(pet_path).convert("RGBA")
                    pet_img = pet_img.resize(
                        (int(img.width * settings['pet_size']), 
                         int((img.width * settings['pet_size']) * (pet_img.height / pet_img.width))),
                        Image.LANCZOS
                    )
                    pet_pos = get_pet_position(img, pet_img, occupied_boxes, padding)
                    pet_pos = (max(0, min(pet_pos[0], img.width - pet_img.width)), 
                               max(0, min(pet_pos[1], img.height - pet_img.height)))
                    
                    img.paste(pet_img, pet_pos, pet_img)
                    occupied_boxes.append((pet_pos[0], pet_pos[1], pet_img.width, pet_img.height))
        
        if settings.get('apply_emoji', False) and settings.get('emojis'):
            img = apply_emoji_stickers(img, settings['emojis'], occupied_boxes, settings.get('num_emojis', 5), padding)
        
        img = enhance_image_quality(
            img,
            settings.get('brightness', 1.0),
            settings.get('contrast', 1.0),
            settings.get('sharpness', 1.2),
            settings.get('saturation', 1.1)
        )
        
        if settings.get('apply_sepia', False):
            img = apply_sepia(img)
        
        if settings.get('apply_bw', False):
            img = apply_black_white(img)
        
        if settings.get('apply_vintage', False):
            img = apply_vintage(img)
        
        if settings.get('apply_vignette', False):
            img = apply_vignette(img, settings.get('vignette_intensity', 0.8))
        
        if settings.get('apply_sketch', False):
            img = apply_sketch_effect(img)
        
        if settings.get('apply_cartoon', False):
            img = apply_cartoon_effect(img)
        
        if settings.get('apply_anime', False):
            img = apply_anime_effect(img)
        
        img = upscale_text_elements(img, scale_factor=settings.get('upscale_factor', 4))
        
        return img.convert("RGB")
    
    except Exception as e:
        st.error(f"Error creating variant: {str(e)}")
        st.error(traceback.format_exc())
        return None

# =================== MAIN APP ===================
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'watermark_groups' not in st.session_state:
    st.session_state.watermark_groups = {}

st.markdown("""
    <div class='header-container'>
        <h1 style='text-align: center; color: #ffcc00; margin: 0;'>
            ⚡ 100+ EDIT IN 1 CLICK
        </h1>
        <p style='text-align: center; color: #ffffff;'>Professional Image Processing Tool</p>
    </div>
""", unsafe_allow_html=True)

# ALL USERS GET PRO FEATURES WHEN LOGIN IS DISABLED
user_type = "Pro Member"  # Force all users to have Pro features
visible_tools = _settings.get("visible_tools", ["V1.0"])

if user_type == "Member":
    available_tools = ["V1.0"]
elif user_type == "Pro Member":
    available_tools = [t for t in visible_tools if t != "Admin Panel"]
else:
    available_tools = visible_tools

# Show status message
st.success("⭐ Welcome! You have full access to all Pro features including Coffee & Pet PNG overlays and Emoji Stickers!")

with st.sidebar:
    st.markdown("### ⚙️ SETTINGS")
    
    background_type = st.selectbox("Background Type", ["Uploaded Image", "Random Color", "Pre-made Image"])

if background_type == "Uploaded Image":
    uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_images and 'cropped_images' not in st.session_state:
        st.session_state.cropped_images = []
        for uploaded_file in uploaded_images:
            try:
                img = Image.open(uploaded_file)
                cropped_img = smart_crop(img, 3/4)
                st.session_state.cropped_images.append((uploaded_file.name, cropped_img))
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    if 'cropped_images' in st.session_state and st.session_state.cropped_images:
        st.info(f"✅ {len(st.session_state.cropped_images)} images cropped to 3:4 ratio")
        with st.expander("Preview Cropped Images"):
            cols = st.columns(3)
            for i, (name, img) in enumerate(st.session_state.cropped_images):
                with cols[i % 3]:
                    st.image(img, caption=name, use_container_width=True)
else:
    num_images = st.sidebar.number_input("Number of Images to Generate", min_value=1, max_value=100, value=10)

with st.sidebar:
    greeting_type = st.selectbox("Greeting Type", 
                                 ["Good Morning", "Good Afternoon", "Good Evening", "Good Night", 
                                  "Happy Birthday", "Merry Christmas", "Custom Greeting"])
    if greeting_type == "Custom Greeting":
        custom_greeting = st.text_input("Enter Custom Greeting", "Awesome Day!")
    else:
        custom_greeting = None
    
    generate_variants = st.checkbox("Generate Multiple Variants", value=False)
    if generate_variants:
        num_variants = st.slider("Variants per Image", 1, 5, 3)
    
    style_mode = st.selectbox("Style Mode", ["Text", "PNG Overlay"], index=0)
    
    overlay_years = list_subfolders(os.path.join(ASSETS_DIR, "overlays"))
    if not overlay_years:
        overlay_years = ["2024", "2025"]
    
    overlay_year_options = ["ALL"] + overlay_years
    
    if style_mode == 'PNG Overlay':
        overlay_year = st.selectbox("Overlay Year", overlay_year_options, index=1)
        png_size = st.slider("PNG Overlay Size", 0.01, 0.75, 0.18)
    
    tool_settings = _load_tool_settings()
    available_text_effects = []
    
    if tool_settings["text_style"]["white_only"]:
        available_text_effects.append("White Only")
    if tool_settings["text_style"]["white_black_outline"]:
        available_text_effects.append("White + Black Outline + Shadow")
    if tool_settings["text_style"]["gradient"]:
        available_text_effects.append("Gradient")
    if tool_settings["text_style"]["neon"]:
        available_text_effects.append("NEON")
    if tool_settings["text_style"]["rainbow"]:
        available_text_effects.append("Rainbow")
    if tool_settings["text_style"]["country_flag"]:
        available_text_effects.append("Country Flag")
    if tool_settings["text_style"]["3d"]:
        available_text_effects.append("3D")
    
    available_text_effects.append("RANDOM")
    
    text_effect = st.selectbox(
        "Text Style",
        available_text_effects,
        index=len(available_text_effects) - 1
    )
    
    text_position = st.radio("Main Text Position", ["Top Center", "Bottom Center", "Random"], index=1)
    text_position = text_position.lower().replace(" ", "_")
    
    st.markdown("### 🎨 MANUAL TEXT POSITIONING")
    custom_position = st.checkbox("Enable Manual Positioning", value=False)
    if custom_position:
        text_x = st.slider("Text X Position", 0, 1000, 100)
        text_y = st.slider("Text Y Position", 0, 1000, 100)
    
    show_text = st.checkbox("Show Greeting", value=True)
    if show_text:
        main_size = st.slider("Main Text Size", 10, 200, 90)
    
    show_wish = st.checkbox("Show Wish", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 200, 60)
        custom_wish = st.checkbox("Custom Wish", value=False)
        if custom_wish:
            wish_text = st.text_area("Enter Custom Wish", "Have a wonderful day!")
        else:
            wish_text = None
    
    st.markdown("### Overlap Settings")
    overlap_percent = st.slider("Main Text Overlap (%)", -15, 50, 14)
    
    show_date = st.checkbox("Show Date", value=False)
    if show_date:
        date_size = st.slider("Date Text Size", 10, 200, 30)
        date_format = st.selectbox("Date Format", 
                                   ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                   index=0)
        show_day = st.checkbox("Show Day", value=False)
    
    show_quote = st.checkbox("Add Quote", value=False) if tool_settings["advanced"]["quote"] else False
    if show_quote:
        quote_size = st.slider("Quote Text Size", 10, 100, 40)
        st.markdown("### ✨ QUOTE DATABASE")
        st.markdown("<div class='quote-display'>" + get_random_quote() + "</div>", unsafe_allow_html=True)
        if st.button("Refresh Quote"):
            st.rerun()
    
    use_watermark = st.checkbox("Add Watermark", value=True) if tool_settings["advanced"]["watermark"] else False
    watermark_images = []
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            watermark_files = list_files(os.path.join(ASSETS_DIR, "logos"), [".png", ".jpg", ".jpeg"])
            if watermark_files:
                default_wm = ["Good Vibes.png"]
                default = [f for f in default_wm if f in watermark_files]
                if not default and len(watermark_files) >= 3:
                    default = watermark_files[:3]
                selected_watermarks = st.multiselect("Select Watermark(s)", watermark_files, default=default)
                for watermark_file in selected_watermarks:
                    watermark_path = os.path.join(ASSETS_DIR, "logos", watermark_file)
                    if os.path.exists(watermark_path):
                        watermark_images.append(Image.open(watermark_path).convert("RGBA"))
        else:
            uploaded_watermark = st.file_uploader("Upload Watermark", type=["png"], accept_multiple_files=True)
            if uploaded_watermark:
                for watermark in uploaded_watermark:
                    watermark_images.append(Image.open(watermark).convert("RGBA"))
        
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 1.0)
    
    st.markdown("---")
    
    # ALL USERS GET PRO FEATURES - NO RESTRICTIONS
    st.markdown("###☕🐾 PRO OVERLAYS")
    use_coffee_pet = st.checkbox("Enable Coffee & Pet PNG", value=True) if tool_settings["overlay"]["pet"] else False
    if use_coffee_pet:
        pet_size = st.slider("PNG Size", 0.1, 1.0, 0.3)
        pet_files = list_files(os.path.join(ASSETS_DIR, "pets"), [".png", ".jpg", ".jpeg"])
        if pet_files:
            pet_choice = st.selectbox("Select Pet PNG", ["Random"] + pet_files)
        else:
            pet_choice = None
            st.warning("No pet PNGs found in assets/pets")
    else:
        pet_choice = None
            
    st.markdown("### 😊 EMOJI STICKERS")
    apply_emoji = st.checkbox("Add Emoji Stickers", value=False) if tool_settings["advanced"]["emoji"] else False
    if apply_emoji:
        emojis = st.multiselect("Select Emojis", ["😊", "👍", "❤️", "🌟", "🎉", "🔥", "🌈", "✨", "💯"], default=["😊", "❤️", "🌟"])
        num_emojis = st.slider("Number of Emojis", 1, 10, 5)
    else:
        emojis = []
        num_emojis = 5
    
    st.markdown("### ⚡ BULK PROCESSING")
    bulk_quality = st.selectbox("Output Quality", ["High (90%)", "Medium (80%)", "Low (70%)"], index=0)
    
    # ALL USERS GET ADVANCED FEATURES
    with st.expander("🔥 Advanced Features"):
        st.markdown("### Image Adjustments")
        brightness = st.slider("Brightness", 0.5, 1.5, 1.0)
        contrast = st.slider("Contrast", 0.5, 1.5, 1.0)
        sharpness = st.slider("Sharpness", 0.5, 2.0, 1.2)
        saturation = st.slider("Saturation", 0.5, 2.0, 1.1)
        
        st.markdown("### Filters")
        apply_sepia = st.checkbox("Apply Sepia Filter", value=False) if tool_settings["filter"]["sepia"] else False
        apply_bw = st.checkbox("Apply Black & White Filter", value=False) if tool_settings["filter"]["black_white"] else False
        apply_vintage = st.checkbox("Apply Vintage Filter", value=False) if tool_settings["filter"]["vintage"] else False
        apply_vignette = st.checkbox("Apply Vignette Effect", value=False) if tool_settings["filter"]["vignette"] else False
        if apply_vignette:
            vignette_intensity = st.slider("Vignette Intensity", 0.1, 1.0, 0.8)
        apply_sketch = st.checkbox("Apply Sketch Effect", value=False) if tool_settings["filter"]["sketch"] else False
        apply_cartoon = st.checkbox("Apply Cartoon Effect", value=False) if tool_settings["filter"]["cartoon"] else False
        apply_anime = st.checkbox("Apply Anime Effect", value=False) if tool_settings["filter"]["anime"] else False
        
        st.markdown("### Text Customizations")
        font_folder = st.text_input("Font Folder Path", os.path.join(ASSETS_DIR, "fonts"))
        upscale_factor = st.slider("Text Upscale Factor", 1, 8, 4)
        
        st.markdown("### Additional Overlays")
        use_frame = st.checkbox("Add Frame Overlay", value=False)
        if use_frame:
            frame_files = list_files(os.path.join(ASSETS_DIR, "frames"), [".png", ".jpg"])
            if frame_files:
                frame_choice = st.selectbox("Select Frame", frame_files)
                frame_path = os.path.join(ASSETS_DIR, "frames", frame_choice)
                frame_size = st.slider("Frame Size", 0.1, 1.0, 1.0)
        
        st.markdown("### 📅 FILENAME TIMESTAMP SETTINGS")
        time_option = st.selectbox(
            "Timestamp for Filename",
            ["Current Time", "Past (10 mins ago)", "Future (10 mins later)", "Custom Time"],
            index=0
        )
        
        custom_time = None
        if time_option == "Custom Time":
            custom_date = st.date_input("Select Date")
            custom_time_input = st.time_input("Select Time")
            custom_time = datetime.combine(custom_date, custom_time_input)
            # Convert to timezone aware
            try:
                custom_time = pytz.timezone('Asia/Kolkata').localize(custom_time)
            except:
                pass
        
        st.markdown("### Export Options")
        export_format = st.selectbox("Export Format", ["JPEG", "PNG"], index=0)
        compression_level = st.slider("Compression Level (for JPEG)", 50, 100, 95)

# Map time options for filename generation
time_option_map = {
    "Current Time": "current",
    "Past (10 mins ago)": "past", 
    "Future (10 mins later)": "future",
    "Custom Time": "custom"
}

if st.button("✨ GENERATE", key="generate", use_container_width=True):
    images = []
    if background_type == "Uploaded Image":
        if 'cropped_images' in st.session_state and st.session_state.cropped_images:
            images = st.session_state.cropped_images
        else:
            st.warning("Please upload images for Uploaded Image mode.")
            st.stop()
    else:
        if 'num_images' in locals():
            images = [("bg_{}.jpg".format(i+1), None) for i in range(num_images)]
        else:
            st.warning("Please set number of images.")
            st.stop()
    
    with st.spinner("Processing images with ULTRA PRO quality..."):
        processed_images = []
        variant_images = []
        progress_bar = st.progress(0)
        total_images = len(images) * (num_variants if generate_variants else 1)
        
        effect_mapping = {
            "White Only": "white_only",
            "White + Black Outline + Shadow": "white_black_outline_shadow",
            "Gradient": "gradient",
            "NEON": "neon",
            "Rainbow": "rainbow",
            "RANDOM": "random",
            "Country Flag": "country_flag",
            "3D": "3d"
        }
        selected_effect = effect_mapping.get(text_effect, "random")
        
        watermark_groups = {}
        if watermark_images:
            if len(watermark_images) > 1:
                group_size = len(images) // len(watermark_images)
                for i, watermark in enumerate(watermark_images):
                    start_idx = i * group_size
                    end_idx = (i + 1) * group_size if i < len(watermark_images) - 1 else len(images)
                    watermark_groups[f"Group {i+1}"] = {
                        'watermark': watermark,
                        'images': images[start_idx:end_idx]
                    }
            else:
                watermark_groups["All Images"] = {
                    'watermark': watermark_images[0],
                    'images': images
                }
        else:
            watermark_groups["All Images"] = {
                'watermark': None,
                'images': images
            }
        
        st.session_state.watermark_groups = watermark_groups
        
        prog_idx = 0
        for group_name, group_data in watermark_groups.items():
            watermark = group_data['watermark']
            group_images = group_data['images']
            
            for filename, img in group_images:
                if generate_variants:
                    for v in range(num_variants):
                        settings = {
                            'greeting_type': custom_greeting if greeting_type == "Custom Greeting" else greeting_type,
                            'show_text': show_text,
                            'main_size': main_size if show_text else 90,
                            'text_position': text_position,
                            'show_wish': show_wish,
                            'wish_size': wish_size if show_wish else 60,
                            'custom_wish': wish_text,
                            'show_date': show_date,
                            'show_day': show_day if show_date else False,
                            'date_size': date_size if show_date else 30,
                            'date_format': date_format if show_date else "8 July 2025",
                            'show_quote': show_quote,
                            'quote_text': get_random_quote() if show_quote else "",
                            'quote_size': quote_size if show_quote else 40,
                            'use_watermark': use_watermark,
                            'watermark_image': watermark,
                            'watermark_opacity': watermark_opacity if use_watermark else 1.0,
                            'use_coffee_pet': use_coffee_pet,
                            'pet_size': pet_size if use_coffee_pet else 0.3,
                            'pet_choice': pet_choice,
                            'text_effect': selected_effect,
                            'custom_position': custom_position,
                            'text_x': text_x if custom_position else 100,
                            'text_y': text_y if custom_position else 100,
                            'apply_emoji': apply_emoji,
                            'emojis': emojis,
                            'num_emojis': num_emojis,
                            'style_mode': style_mode,
                            'overlap_percent': overlap_percent,
                            'overlay_year': overlay_year if style_mode == 'PNG Overlay' else "2025",
                            'png_size': png_size if style_mode == 'PNG Overlay' else 0.5,
                            'brightness': brightness,
                            'contrast': contrast,
                            'sharpness': sharpness,
                            'saturation': saturation,
                            'apply_sepia': apply_sepia,
                            'apply_bw': apply_bw,
                            'apply_vintage': apply_vintage,
                            'apply_vignette': apply_vignette,
                            'vignette_intensity': vignette_intensity if apply_vignette else 0.8,
                            'apply_sketch': apply_sketch,
                            'apply_cartoon': apply_cartoon,
                            'apply_anime': apply_anime,
                            'font_folder': font_folder,
                            'upscale_factor': upscale_factor,
                            'background_type': background_type
                        }
                        variant = create_variant(img, settings)
                        if variant is not None:
                            # Use new filename generation with timestamp options
                            filename = generate_filename(
                                base_name="Picsart",
                                time_option=time_option_map.get(time_option, "current"),
                                custom_time=custom_time
                            )
                            variant_images.append((filename, variant))
                        prog_idx += 1
                        progress_bar.progress(min(prog_idx / total_images, 1.0))
                else:
                    settings = {
                        'greeting_type': custom_greeting if greeting_type == "Custom Greeting" else greeting_type,
                        'show_text': show_text,
                        'main_size': main_size if show_text else 90,
                        'text_position': text_position,
                        'show_wish': show_wish,
                        'wish_size': wish_size if show_wish else 60,
                        'custom_wish': wish_text,
                        'show_date': show_date,
                        'show_day': show_day if show_date else False,
                        'date_size': date_size if show_date else 30,
                        'date_format': date_format if show_date else "8 July 2025",
                        'show_quote': show_quote,
                        'quote_text': get_random_quote() if show_quote else "",
                        'quote_size': quote_size if show_quote else 40,
                        'use_watermark': use_watermark,
                        'watermark_image': watermark,
                        'watermark_opacity': watermark_opacity if use_watermark else 1.0,
                        'use_coffee_pet': use_coffee_pet,
                        'pet_size': pet_size if use_coffee_pet else 0.3,
                        'pet_choice': pet_choice,
                        'text_effect': selected_effect,
                        'custom_position': custom_position,
                        'text_x': text_x if custom_position else 100,
                        'text_y': text_y if custom_position else 100,
                        'apply_emoji': apply_emoji,
                        'emojis': emojis,
                        'num_emojis': num_emojis,
                        'style_mode': style_mode,
                        'overlap_percent': overlap_percent,
                        'overlay_year': overlay_year if style_mode == 'PNG Overlay' else "2025",
                        'png_size': png_size if style_mode == 'PNG Overlay' else 0.5,
                        'brightness': brightness,
                        'contrast': contrast,
                        'sharpness': sharpness,
                        'saturation': saturation,
                        'apply_sepia': apply_sepia,
                        'apply_bw': apply_bw,
                        'apply_vintage': apply_vintage,
                        'apply_vignette': apply_vignette,
                        'vignette_intensity': vignette_intensity if apply_vignette else 0.8,
                        'apply_sketch': apply_sketch,
                        'apply_cartoon': apply_cartoon,
                        'apply_anime': apply_anime,
                        'font_folder': font_folder,
                        'upscale_factor': upscale_factor,
                        'background_type': background_type
                    }
                    processed_img = create_variant(img, settings)
                    if processed_img is not None:
                        # Use new filename generation with timestamp options
                        filename = generate_filename(
                            base_name="Picsart", 
                            time_option=time_option_map.get(time_option, "current"),
                            custom_time=custom_time
                        )
                        processed_images.append((filename, processed_img))
                    prog_idx += 1
                    progress_bar.progress(min(prog_idx / total_images, 1.0))
        
        st.session_state.generated_images = processed_images + variant_images
        
        if st.session_state.generated_images:
            log_image_usage(CURRENT_USER, len(st.session_state.generated_images))
            st.success(f"✅ Successfully processed {len(st.session_state.generated_images)} images with ULTRA PRO quality!")
        else:
            st.warning("No images were processed.")

if st.session_state.generated_images:
    if len(st.session_state.watermark_groups) > 1:
        for group_name, group_data in st.session_state.watermark_groups.items():
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for filename, img in st.session_state.generated_images:
                    try:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img_bytes = io.BytesIO()
                        quality = 90 if bulk_quality == "High (90%)" else 80 if bulk_quality == "Medium (80%)" else 70
                        img.save(img_bytes, format='JPEG', quality=quality)
                        zip_file.writestr(filename, img_bytes.getvalue())
                    except Exception as e:
                        st.error(f"Error adding {filename} to zip: {str(e)}")
                        continue
            
            st.download_button(
                label=f"⬇️ Download {group_name} Photos",
                data=zip_buffer.getvalue(),
                file_name=f"{group_name.replace(' ', '_').lower()}_photos.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, img in st.session_state.generated_images:
            try:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_bytes = io.BytesIO()
                quality = 90 if bulk_quality == "High (90%)" else 80 if bulk_quality == "Medium (80%)" else 70
                img.save(img_bytes, format='JPEG', quality=quality)
                zip_file.writestr(filename, img_bytes.getvalue())
            except Exception as e:
                st.error(f"Error adding {filename} to zip: {str(e)}")
                continue
    
    st.download_button(
        label="⬇️ Download All Photos ",
        data=zip_buffer.getvalue(),
        file_name="ultra_pro_photos.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    st.markdown("""
        <div class='image-preview-container'>
            <h2 style='text-align: center; color: #ffcc00; margin: 0;'>😇  RESULTS</h2>
        </div>
    """, unsafe_allow_html=True)
    
    cols_per_row = 3
    rows = math.ceil(len(st.session_state.generated_images) / cols_per_row)
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col in range(cols_per_row):
            idx = row * cols_per_row + col
            if idx < len(st.session_state.generated_images):
                filename, img = st.session_state.generated_images[idx]
                with cols[col]:
                    try:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='JPEG', quality=95)
                        img_bytes.seek(0)
                        st.image(img_bytes, use_container_width=True)
                        st.caption(filename)
                        
                        st.download_button(
                            label="⬇️ Download",
                            data=img_bytes.getvalue(),
                            file_name=filename,
                            mime="image/jpeg",
                            key=f"download_{idx}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error displaying {filename}: {str(e)}")
