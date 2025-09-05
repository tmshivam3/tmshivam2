import os
import zipfile
import shutil
import streamlit as st
import subprocess
import sys

# Make sure gdown is installed
try:
    import gdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])
    import gdown

ASSETS_DIR = "assets"
ZIP_FILE = "assets.zip"

# ✅ Tumhara Google Drive file ID
FILE_ID = "18qGAPUO3aCFKx7tfDxD2kOPzFXLUo66U"
ZIP_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

# ✅ Agar assets folder nahi hai to download + extract karo
if not os.path.exists(ASSETS_DIR):
    st.info("Downloading assets from Google Drive... ⏳")
    gdown.download(ZIP_URL, ZIP_FILE, quiet=False)

    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall("temp_assets_extract")

    top_level = os.listdir("temp_assets_extract")

    # Case 1: Agar andar ek hi "assets" folder hai
    if len(top_level) == 1 and top_level[0].lower() == "assets":
        inner_path = os.path.join("temp_assets_extract", top_level[0])
        shutil.move(inner_path, ASSETS_DIR)

    # Case 2: Agar ek hi folder ho (sab content usme hai)
    elif len(top_level) == 1 and os.path.isdir(os.path.join("temp_assets_extract", top_level[0])):
        inner_path = os.path.join("temp_assets_extract", top_level[0])
        os.makedirs(ASSETS_DIR, exist_ok=True)
        for item in os.listdir(inner_path):
            shutil.move(os.path.join(inner_path, item), ASSETS_DIR)

    # Case 3: Mixed files/folders directly andar
    else:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        for item in top_level:
            shutil.move(os.path.join("temp_assets_extract", item), ASSETS_DIR)

# ❌ HuggingFace wala purana code hata diya hai
"""
from huggingface_hub import snapshot_download

ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    try:
        snapshot_download(repo_id="tmshivam/tool", repo_type="dataset", local_dir=ASSETS_DIR)
    except Exception as e:
        st.error(f"Failed to download assets: {str(e)}")
"""

# =======================
# Yahan se tumhara asli tool ka code jaisa tha waisa hi paste hai
# (auth system, overlays, greetings, hue tool, etc.)
# =======================

# Example start (tumhara original code neeche continue karega)
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps, ImageChops
import io, random, traceback, math, colorsys, json, uuid, hashlib
import numpy as np
import textwrap
from datetime import datetime, timedelta
from typing import Tuple, List, Optional
from collections import Counter
from streamlit.runtime.scriptrunner import get_script_run_ctx

# 🔽🔽🔽
# Ab tumhara pura original code yahan se aage continue karega
# (auth block, utils, main app, tools, etc.)
# 🔼🔼🔼


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
from streamlit.runtime.scriptrunner import get_script_run_ctx
import json, uuid, hashlib
from huggingface_hub import snapshot_download

# Download assets from Hugging Face dataset if not present
ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    try:
        snapshot_download(repo_id="tmshivam/tool", repo_type="dataset", local_dir=ASSETS_DIR)
    except Exception as e:
        st.error(f"Failed to download assets: {str(e)}")

# =================== CONFIG ===================

# ========== BEGIN AUTH / ADMIN BLOCK (PASTE ABOVE "MAIN APP" MARK) ==========
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def get_ip():
    """
    Get the client's IP address from request headers.
    Handles proxies by taking the first IP in X-Forwarded-For.
    """
    try:
        ctx = get_script_run_ctx()
        if ctx:
            headers = ctx._request_headers if hasattr(ctx, '_request_headers') else {}
            ip = headers.get("X-Forwarded-For", "Unknown")
            if ip != "Unknown":
                ip = ip.split(',')[0].strip()
            return ip
    except Exception as e:
        return "Unknown"

def _auth_hash(pw: str) -> str:
    """
    Hash the password using SHA256 for secure storage.
    """
    return hashlib.sha256(pw.encode()).hexdigest()

def _auth_load_users():
    """
    Load users data from JSON file.
    """
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}

def _auth_save_users(data):
    """
    Save users data to JSON file.
    """
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _auth_load_settings():
    """
    Load settings from JSON file.
    """
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"notice":"", "active_tool":"V1.0", "visible_tools":["V1.0"], "primary_color":"#ffcc00", 
                "login_required": True, "hue_enabled_pngs": {}, "tool_visibility": {}}

def _auth_save_settings(s):
    """
    Save settings to JSON file.
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def _auth_ensure_files():
    """
    Ensure data directories and default files exist, create admin if not present.
    """
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

_auth_ensure_files()
_users_db = _auth_load_users()
_settings = _auth_load_settings()

def _auth_logout_and_rerun():
    """
    Logout the user by clearing session state and rerunning the app.
    """
    for k in ("_auth_user","_auth_device","_auth_login_time","_auth_show_admin"):
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

def _auth_check_session():
    """
    Check if the current session is valid, including expiry and IP match.
    """
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

# Check if login is required
settings = _auth_load_settings()
login_required = settings.get("login_required", True)

if login_required and "_auth_user" not in st.session_state:
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

if "_auth_user" in st.session_state:
    _auth_check_session()
    CURRENT_USER = st.session_state.get("_auth_user")
    USERS_DB = _auth_load_users()
    CURRENT_RECORD = USERS_DB.get("users", {}).get(CURRENT_USER, {})
    IS_ADMIN = CURRENT_RECORD.get("is_admin", False)

    if IS_ADMIN:
        if "_auth_show_admin" not in st.session_state:
            st.session_state["_auth_show_admin"] = False
        if st.sidebar.button("🔧 Open Admin Panel"):
            st.session_state["_auth_show_admin"] = not st.session_state["_auth_show_admin"]

    if st.session_state.get("_auth_show_admin"):
        st.markdown("## ⚙️ ADMIN PANEL")
        
        # Enhanced admin features
        st.markdown("### User Management")
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["User Accounts", "Access Control", "System Settings", "IP Management", "Tools & Features", "PNG Hue Settings", "Tool Visibility"])
        
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
                
                # User type change
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
            
            all_tools = ["V1.0", "V2.0", "V3.0", "V4.0", "V5.0", "Premium Tools", "Hue Color Tool"]
            visible_tools = _settings.get("visible_tools", ["V1.0"])
            
            for tool in all_tools:
                is_visible = st.checkbox(f"Show {tool}", value=tool in visible_tools, key=f"tool_{tool}")
                if is_visible and tool not in visible_tools:
                    visible_tools.append(tool)
                elif not is_visible and tool in visible_tools:
                    visible_tools.remove(tool)
            
            if st.button("Save Tool Visibility"):
                _settings["visible_tools"] = visible_tools
                _auth_save_settings(_settings)
                st.success("Tool visibility settings saved!")
            
            st.markdown("#### User Type Restrictions")
            st.info("Pro Members can access all tools except Admin Panel. Members can only access basic tools.")
        
        with tab3:
            st.markdown("### System Settings")
            st.markdown("#### Noticeboard")
            new_notice = st.text_area("Global notice (shows on main page)", value=_settings.get("notice",""))
            
            primary_color = st.color_picker("Primary Color", value=_settings.get("primary_color", "#ffcc00"))
            
            # Login page toggle
            login_required = st.checkbox("Require Login", value=_settings.get("login_required", True))
            
            if st.button("Save Settings"):
                _settings["notice"] = new_notice
                _settings["primary_color"] = primary_color
                _settings["login_required"] = login_required
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
            
            for feature, enabled in features.items():
                features[feature] = st.checkbox(f"Enable {feature.replace('_', ' ').title()}", 
                                               value=enabled, key=f"feature_{feature}")
            
            if st.button("Save Feature Settings"):
                _settings["features"] = features
                _auth_save_settings(_settings)
                st.success("Feature settings saved!")
            
            st.markdown("#### System Tools")
            if st.button("Clear All Cache"):
                st.session_state.clear()
                st.success("Cache cleared!")
            
            if st.button("Export User Data"):
                # Create export functionality
                st.success("User data exported!")
            
            if st.button("Import User Data"):
                # Create import functionality
                st.success("User data imported!")
        
        with tab6:
            st.markdown("### PNG Hue Color Settings")
            st.info("Select which PNGs should have hue color change enabled")
            
            # Get all available PNG folders
            hue_enabled_pngs = _settings.get("hue_enabled_pngs", {})
            
            # Find all overlay folders
            overlay_base = "assets/overlays"
            if os.path.exists(overlay_base):
                years = os.listdir(overlay_base)
                for year in years:
                    year_path = os.path.join(overlay_base, year)
                    if os.path.isdir(year_path):
                        themes = os.listdir(year_path)
                        for theme in themes:
                            theme_path = os.path.join(year_path, theme)
                            if os.path.isdir(theme_path):
                                png_key = f"{year}/{theme}"
                                current_value = hue_enabled_pngs.get(png_key, False)
                                
                                # Check if this theme has PNG files
                                png_files = [f for f in os.listdir(theme_path) if f.lower().endswith('.png')]
                                if png_files:
                                    enabled = st.checkbox(f"{png_key}", value=current_value, key=f"hue_{png_key}")
                                    hue_enabled_pngs[png_key] = enabled
            
            if st.button("Save Hue Settings"):
                _settings["hue_enabled_pngs"] = hue_enabled_pngs
                _auth_save_settings(_settings)
                st.success("Hue settings saved!")
        
        with tab7:
            st.markdown("### Tool Visibility Settings")
            st.info("Control which tools are visible to users")
            
            # Get current tool visibility settings
            tool_visibility = _settings.get("tool_visibility", {})
            
            # Define all available tools
            all_tools = {
                "upload_images": "Image Upload",
                "greeting_type": "Greeting Type Selection",
                "generate_variants": "Generate Multiple Variants",
                "style_mode": "Style Mode Selection",
                "text_effect": "Text Style Selection",
                "text_position": "Text Position Selection",
                "custom_position": "Manual Positioning",
                "show_text": "Show Greeting Text",
                "show_wish": "Show Wish Text",
                "overlap_percent": "Overlap Settings",
                "show_date": "Show Date",
                "show_quote": "Add Quote",
                "use_watermark": "Add Watermark",
                "use_coffee_pet": "Coffee & Pet PNG",
                "apply_emoji": "Emoji Stickers",
                "bulk_quality": "Bulk Processing",
                "advanced_features": "Advanced Features",
                "hue_tool": "Hue Color Tool"
            }
            
            for tool_key, tool_name in all_tools.items():
                current_value = tool_visibility.get(tool_key, True)
                tool_visibility[tool_key] = st.checkbox(f"Show {tool_name}", value=current_value, key=f"vis_{tool_key}")
            
            if st.button("Save Tool Visibility Settings"):
                _settings["tool_visibility"] = tool_visibility
                _auth_save_settings(_settings)
                st.success("Tool visibility settings saved!")
        
        st.markdown("---")
        st.write("Contact developer: +91 9140588751")
        st.stop()

    if _settings.get("notice"):
        st.info(_settings.get("notice"))
# ========== END AUTH / ADMIN BLOCK ==========

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
    """
    List files in a folder with specific extensions.
    """
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    files = os.listdir(folder)
    return [f for f in files 
            if any(f.lower().endswith(ext.lower()) for ext in exts)]

def list_subfolders(folder: str) -> List[str]:
    """
    List subfolders in a folder.
    """
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

def smart_crop(img: Image.Image, target_ratio: float = 3/4) -> Image.Image:
    """
    Smart crop image to target aspect ratio, centering the crop.
    """
    w, h = img.size
    if w/h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_text_size(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """
    Get the size of text with given font.
    """
    if text is None:
        return 0, 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_font(font_folder="assets/fonts") -> ImageFont.FreeTypeFont:
    """
    Get a random font from the fonts folder, fallback to default.
    """
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
    """
    Get a random wish message based on greeting type.
    Expanded list for more variety.
    """
    wishes = {
        "Good Morning": [
            "Rise and shine! A new day is a new opportunity!",
            "Good morning! Make today amazing!",
            # ... (rest of the wishes remain the same)
        ],
        # ... (other greeting types remain the same)
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_quote() -> str:
    """
    Get a random inspirational quote from an expanded list.
    """
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        # ... (rest of the quotes remain the same)
    ]
    return random.choice(quotes)

def get_random_color() -> Tuple[int, int, int]:
    """
    Generate a random RGB color with medium brightness.
    """
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def get_vibrant_color() -> Tuple[int, int, int]:
    """
    Generate a vibrant RGB color using HSV.
    """
    hue = random.random()
    r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, 0.9, 0.9)]
    return (r, g, b)

PURE_COLORS = [
    (255, 0, 0),  # Red
    (255, 255, 0),  # Yellow
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]

def get_gradient_colors(dominant_color: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
    """
    Get gradient colors based on dominant color or pure colors.
    """
    if random.random() < 0.8:
        return [(255, 255, 255), dominant_color]
    else:
        return [(255, 255, 255), random.choice(PURE_COLORS)]

def get_multi_gradient_colors() -> List[Tuple[int, int, int]]:
    """
    Get multiple vibrant colors for rainbow gradient.
    """
    num_colors = random.randint(2, 7)
    colors = []
    for _ in range(num_colors):
        colors.append(get_vibrant_color())
    return colors

def create_gradient_mask(width: int, height: int, colors: List[Tuple[int, int, int]], direction: str = 'horizontal') -> Image.Image:
    """
    Create a gradient mask image with given colors.
    """
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    if len(colors) == 2:
        start_color, end_color = colors
        for x in range(width):
            ratio = x / width
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            color = (r, g, b)
            draw.line([(x, 0), (x, height)], fill=color)
        if random.choice([True, False]):
            gradient = gradient.transpose(Image.FLIP_LEFT_RIGHT)
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
    """
    Format current date with optional day name.
    """
    today = datetime.now()
    formatted_date = today.strftime(date_format)
    
    if show_day:
        if today.hour >= 19:
            next_day = today + timedelta(days=1)
            day_name = next_day.strftime("%A")
            formatted_date += f" (Advance {day_name})"
        else:
            day_name = today.strftime("%A")
            formatted_date += f" ({day_name})"
    
    return formatted_date

def apply_overlay(image: Image.Image, overlay_path: str, size: float = 0.5, position: Tuple[int, int] = None) -> Image.Image:
    """
    Apply an overlay image with resizing and random or specified position.
    """
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

def generate_filename(base_name="Picsart") -> str:
    """
    Generate a filename with future timestamp for uniqueness.
    """
    future_minutes = random.randint(1, 10)
    now = datetime.now()
    future_time = now + timedelta(minutes=future_minutes)
    return f"{base_name}_{future_time.strftime('%y-%m-%d_%H-%M-%S')}.jpg"

def get_watermark_position(img: Image.Image, watermark: Image.Image, avoid_positions: List[Tuple[int, int, int, int]] = None) -> Tuple[int, int]:
    """
    Get a position for watermark, avoiding overlaps if provided.
    """
    possible_positions = [20, img.width - watermark.width - 20]
    x = random.choice(possible_positions)
    y = img.height - watermark.height - 20
    if avoid_positions:
        for ax, ay, aw, ah in avoid_positions:
            if abs(x - ax) < aw or abs(y - ay) < ah:
                x = possible_positions[1 - possible_positions.index(x)]  # switch side
    return (x, y)

def enhance_image_quality(img: Image.Image, brightness=1.0, contrast=1.0, sharpness=1.0, saturation=1.0) -> Image.Image:
    """
    Enhance image quality with adjustable parameters.
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)
    
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness)
    
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation)
    
    return img

def upscale_text_elements(img: Image.Image, scale_factor: int = 4) -> Image.Image:
    """
    Upscale image for better text rendering.
    """
    if scale_factor > 1:
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.LANCZOS)
    return img

def apply_vignette(img: Image.Image, intensity: float = 0.8) -> Image.Image:
    """
    Apply vignette effect to image.
    """
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
    """
    Apply sepia filter to image.
    """
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
    """
    Convert image to black and white.
    """
    return img.convert('L').convert('RGB')

def apply_vintage(img: Image.Image) -> Image.Image:
    """
    Apply vintage effect: sepia + noise + vignette.
    """
    img = apply_sepia(img)
    noise = np.random.normal(0, 25, img.size[::-1] + (3,)).astype(np.uint8)
    noise_img = Image.fromarray(noise)
    img = ImageChops.add(img, noise_img, scale=2.0)
    img = apply_vignette(img, 0.5)
    return img

def apply_sketch_effect(img: Image.Image) -> Image.Image:
    """
    Apply sketch effect to image.
    """
    img_gray = img.convert('L')
    img_invert = ImageOps.invert(img_gray)
    img_blur = img_invert.filter(ImageFilter.GaussianBlur(radius=3))
    return ImageOps.invert(img_blur)

def apply_cartoon_effect(img: Image.Image) -> Image.Image:
    """
    Apply cartoon effect to image.
    """
    reduced = img.quantize(colors=8, method=1)
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    cartoon = reduced.convert('RGB')
    cartoon.paste((0, 0, 0), (0, 0), edges)
    return cartoon

def apply_anime_effect(img: Image.Image) -> Image.Image:
    """
    Apply anime-style effect to image.
    """
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.5)
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    result = img.copy()
    result.paste((0, 0, 0), (0, 0), edges)
    return result

def apply_emoji_stickers(img: Image.Image, emojis: List[str], num_stickers=5) -> Image.Image:
    """
    Add random emoji stickers to image.
    """
    if not emojis:
        return img
        
    draw = ImageDraw.Draw(img)
    for _ in range(num_stickers):
        x = random.randint(20, img.width-40)
        y = random.randint(20, img.height-40)
        emoji = random.choice(emojis)
        font = ImageFont.truetype("arial.ttf", 40)
        draw.text((x, y), emoji, font=font, fill=(255, 255, 0))
    return img

def get_dominant_color(img: Image.Image) -> Tuple[int, int, int]:
    """
    Get dominant color from resized image, adjust lightness.
    FIXED: Handle RGBA images by converting to RGB first
    """
    # Convert to RGB if image has alpha channel
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    img_small = img.resize((100, 100))
    colors = Counter(img_small.getdata())
    dominant = colors.most_common(1)[0][0]
    
    # Ensure we only have 3 values (RGB)
    if len(dominant) > 3:
        dominant = dominant[:3]
    
    h, l, s = colorsys.rgb_to_hls(dominant[0] / 255, dominant[1] / 255, dominant[2] / 255)
    if l < 0.5:
        l = 0.7
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def find_text_position(img: Image.Image, required_width: int, required_height: int, prefer_top: bool = True) -> Tuple[int, int]:
    """
    Find optimal position for text based on image variance (low variance areas).
    """
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
    """
    Get random horizontal position: left, mid, right.
    """
    positions = [
        20,  # left
        (img_width - text_width) // 2,  # mid
        img_width - text_width - 20  # right
    ]
    return random.choice(positions)

def apply_text_effect(draw: ImageDraw.Draw, position: Tuple[int, int], text: str, font: ImageFont.FreeTypeFont, 
                      effect_settings: dict, base_img: Image.Image) -> dict:
    """
    Apply advanced text effects using separate layers for better control.
    """
    x, y = position
    effect_type = effect_settings['type']
    
    if text is None or text.strip() == "":
        return effect_settings
    
    text_width, text_height = get_text_size(draw, text, font)
    
    # Handle RANDOM effect type
    if effect_type == 'random':
        available_effects = [
            'white_only', 'white_black_outline_shadow', 'gradient', 
            'neon', 'rainbow', 'country_flag', '3d'
        ]
        effect_type = random.choice(available_effects)
        effect_settings['type'] = effect_type
    
    # Create separate transparent layers for shadow, outline, and fill
    shadow_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    outline_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    fill_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    
    shadow_draw = ImageDraw.Draw(shadow_layer)
    outline_draw = ImageDraw.Draw(outline_layer)
    fill_draw = ImageDraw.Draw(fill_layer)
    
    # Draw shadow
    shadow_offset = (2, 2)
    shadow_draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 40))
    
    # Draw outline
    outline_range = 1 if effect_type == 'neon' else 2
    for ox in range(-outline_range, outline_range + 1):
        for oy in range(-outline_range, outline_range + 1):
            if ox != 0 or oy != 0:
                outline_draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 255))
    
    # Create mask for fill
    mask = Image.new("L", (text_width, text_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((0, 0), text, font=font, fill=255)
    
    # Apply fill
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
        flags = list_files("assets/flags", [".png", ".jpg"])
        if flags:
            flag_path = os.path.join("assets/flags", random.choice(flags))
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
    
    # Composite layers
    base_img_rgba = base_img.convert('RGBA') if base_img.mode != 'RGBA' else base_img
    base_img_rgba = Image.alpha_composite(base_img_rgba, shadow_layer)
    base_img_rgba = Image.alpha_composite(base_img_rgba, outline_layer)
    base_img_rgba = Image.alpha_composite(base_img_rgba, fill_layer)
    
    base_img.paste(base_img_rgba, (0, 0))
    
    return effect_settings

def get_pet_position(img: Image.Image, pet_img: Image.Image) -> Tuple[int, int]:
    """
    Get random position for pet PNG at bottom: 40% left, 40% right, 20% mid.
    """
    prob = random.random()
    if prob < 0.4:
        x = 20  # left
    elif prob < 0.8:
        x = img.width - pet_img.width - 20  # right
    else:
        x = (img.width - pet_img.width) // 2  # mid
    y = img.height - pet_img.height - 20
    return x, y

def change_png_hue(png_image: Image.Image, hue_shift: float) -> Image.Image:
    """
    Change the hue of a PNG image while preserving transparency.
    """
    if png_image.mode != 'RGBA':
        png_image = png_image.convert('RGBA')
    
    # Convert to HSV color space
    data = np.array(png_image)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    
    # Convert RGB to HSV
    hsv = np.zeros_like(data[:,:,:3])
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if a[i, j] > 0:  # Only process non-transparent pixels
                r_norm = r[i, j] / 255.0
                g_norm = g[i, j] / 255.0
                b_norm = b[i, j] / 255.0
                h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
                h = (h + hue_shift) % 1.0  # Apply hue shift
                r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)
                hsv[i, j] = [int(r_new * 255), int(g_new * 255), int(b_new * 255)]
            else:
                hsv[i, j] = [0, 0, 0]  # Keep transparent pixels as is
    
    # Combine the new RGB with original alpha channel
    result = np.dstack((hsv, a))
    return Image.fromarray(result, 'RGBA')

def create_variant(original_img: Image.Image, settings: dict) -> Optional[Image.Image]:
    """
    Create a variant of the image with all applied settings, ensuring no overlaps except main.
    """
    try:
        img = original_img.copy()
        draw = ImageDraw.Draw(img)
        
        font = get_random_font(settings.get('font_folder', "assets/fonts"))
        if font is None:
            return None
        
        dominant_color = get_dominant_color(img)
        
        effect_settings = {
            'type': settings.get('text_effect', 'gradient'),
            'outline_size': 2,
            'colors': get_gradient_colors(dominant_color) if settings.get('text_effect', 'gradient') == 'gradient' else get_multi_gradient_colors()
        }
        
        style_mode = settings.get('style_mode', 'Text')
        overlap_percent = settings.get('overlap_percent', 30)
        
        # Track positions to avoid overlaps
        occupied_boxes = []  # list of (x, y, w, h)
        
        if style_mode == 'PNG Overlay' and settings['greeting_type'] in ["Good Morning", "Good Night"]:
            years = list_subfolders("assets/overlays")
            if not years:
                st.warning("No overlay years found.")
                return img
            if settings['overlay_year'] == "ALL":
                selected_years = years
            else:
                selected_years = [settings['overlay_year']]
                if settings['overlay_year'] not in years:
                    st.warning("Selected year not found.")
                    return img
            
            theme_paths = []
            for y in selected_years:
                year_path = os.path.join("assets/overlays", y)
                sub_themes = list_subfolders(year_path)
                if not sub_themes:
                    if list_files(year_path, [".png"]):
                        theme_paths.append(year_path)
                else:
                    for t in sub_themes:
                        theme_paths.append(os.path.join(year_path, t))
            
            if not theme_paths:
                st.warning("No overlay themes found.")
                return img
            
            base_path = random.choice(theme_paths)
            
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
                    
                    # Apply hue change if enabled for this PNG
                    theme_key = f"{os.path.basename(os.path.dirname(base_path))}/{os.path.basename(base_path)}"
                    hue_enabled_pngs = _settings.get("hue_enabled_pngs", {})
                    
                    if theme_key in hue_enabled_pngs and hue_enabled_pngs[theme_key]:
                        if 'hue_shift' in settings and settings['hue_shift'] != 0:
                            # Apply random hue shift if set to random
                            if settings['hue_shift'] == 'random':
                                hue_shift = random.random()
                            else:
                                hue_shift = settings['hue_shift']
                            png_img = change_png_hue(png_img, hue_shift)
                    
                    pngs.append(png_img)
            
            if pngs:
                main_gap = -int(min(pngs[0].height, pngs[1].height) * overlap_percent / 100) if len(pngs) >= 2 else 0
                wish_gap = 10
                
                gaps = [main_gap] * (len(pngs) - 1)
                if settings['show_wish']:
                    gaps[-1] = wish_gap
                
                total_h = sum(p.height for p in pngs)
                for g in gaps:
                    total_h += g
                max_w = max(p.width for p in pngs)
                
                png_size = settings.get('png_size', 0.5)
                scale = min(png_size, min((img.width * 0.9) / max_w, (img.height * 0.9) / total_h))
                pngs = [p.resize((int(p.width * scale), int(p.height * scale)), Image.LANCZOS) for p in pngs]
                
                total_h = sum(p.height for p in pngs)
                for g in gaps:
                    total_h += g
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
                
                current_y = start_y
                for i, p in enumerate(pngs):
                    offset = random.randint(-20, 20)
                    x = start_x + (max_w - p.width) // 2 + offset
                    img.paste(p, (x, current_y), p)
                    occupied_boxes.append((x, current_y, p.width, p.height))
                    if i < len(pngs) - 1:
                        current_y += p.height + gaps[i]
                
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
                
                current_y = text_y
                for i, t in enumerate(main_texts):
                    offset = random.randint(-30, 50)
                    line_x = text_x + (max_w - line_widths[i]) // 2 + offset
                    apply_text_effect(draw, (line_x, current_y), t, font_main, effect_settings, img)
                    occupied_boxes.append((line_x, current_y, line_widths[i], line_heights[i]))
                    if i < len(main_texts) - 1:
                        current_y += line_heights[i] + main_gap
                
                main_end_y = current_y
            
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
                
                wish_gap = 5
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
                
                # Avoid overlap with main
                if settings['show_text']:
                    if wish_y < main_end_y + 20:
                        wish_y = main_end_y + 20
                    if wish_y + total_h > img.height - 20:
                        wish_y = img.height - total_h - 20
                
                current_y = wish_y
                for i, line in enumerate(lines):
                    offset = random.randint(-20, 20)
                    line_x = wish_x + (max_w - line_widths[i]) // 2 + offset
                    apply_text_effect(draw, (line_x, current_y), line, font_wish, effect_settings, img)
                    occupied_boxes.append((line_x, current_y, line_widths[i], line_heights[i]))
                    if i < len(lines) - 1:
                        current_y += line_heights[i] + wish_gap
        
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
            
            # Avoid overlap
            for ox, oy, ow, oh in occupied_boxes:
                if abs(date_y - oy) < oh + date_height:
                    date_x = (date_x + img.width // 2) % img.width  # shift
                    
            if settings['show_day'] and "(" in date_text:
                day_part = date_text[date_text.index("("):]
                day_width, _ = get_text_size(draw, day_part, font_date)
                if date_x + day_width > img.width - 20:
                    date_x = img.width - day_width - 25
            
            apply_text_effect(draw, (date_x, date_y), date_text, font_date, effect_settings, img)
            occupied_boxes.append((date_x, date_y, date_width, date_height))
        
        if settings['show_quote']:
            font_quote = font.font_variant(size=settings['quote_size'])
            quote_text = settings['quote_text']
            
            lines = [line.strip() for line in quote_text.split('\n') if line.strip()]
            
            total_height = 0
            line_heights = []
            line_widths = []
            
            for line in lines:
                w, h = get_text_size(draw, line, font_quote)
                line_heights.append(h)
                line_widths.append(w)
                total_height += h + 10
            
            quote_y = (img.height - total_height) // 2
            
            # Avoid overlap
            for ox, oy, ow, oh in occupied_boxes:
                if abs(quote_y - oy) < total_height + oh:
                    quote_y += oh + 20
            
            for i, line in enumerate(lines):
                line_x = (img.width - line_widths[i]) // 2
                apply_text_effect(draw, (line_x, quote_y), line, font_quote, effect_settings, img)
                occupied_boxes.append((line_x, quote_y, line_widths[i], line_heights[i]))
                quote_y += line_heights[i] + 10
        
        if settings['use_watermark'] and settings['watermark_image']:
            watermark = settings['watermark_image'].copy()
            
            if settings['watermark_opacity'] < 1.0:
                alpha = watermark.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(settings['watermark_opacity'])
                watermark.putalpha(alpha)
            
            watermark.thumbnail((img.width//4, img.height//4))
            pos = get_watermark_position(img, watermark, occupied_boxes)
            img.paste(watermark, pos, watermark)
            occupied_boxes.append((pos[0], pos[1], watermark.width, watermark.height))
        
        if settings['use_coffee_pet'] and settings['pet_choice']:
            pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
            if settings['pet_choice'] == "Random":
                selected_pet = random.choice(pet_files)
            else:
                selected_pet = settings['pet_choice']
            pet_path = os.path.join("assets/pets", selected_pet)
            if os.path.exists(pet_path):
                pet_img = Image.open(pet_path).convert("RGBA")
                pet_img = pet_img.resize(
                    (int(img.width * settings['pet_size']), 
                     int((img.width * settings['pet_size']) * (pet_img.height / pet_img.width))),
                    Image.LANCZOS
                )
                pet_pos = get_pet_position(img, pet_img)
                # Avoid overlap with watermark if present
                for ox, oy, ow, oh in occupied_boxes:
                    if abs(pet_pos[0] - ox) < ow + pet_img.width and abs(pet_pos[1] - oy) < oh + pet_img.height:
                        pet_pos = ((img.width - pet_pos[0] - pet_img.width, pet_pos[1]) if pet_pos[0] == 20 else (20, pet_pos[1]))
                img.paste(pet_img, pet_pos, pet_img)
                occupied_boxes.append((pet_pos[0], pet_pos[1], pet_img.width, pet_img.height))
        
        if settings.get('apply_emoji', False) and settings.get('emojis'):
            img = apply_emoji_stickers(img, settings['emojis'], settings.get('num_emojis', 5))
        
        # Apply advanced image enhancements
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

# Check user access level
user_type = CURRENT_RECORD.get("user_type", "Member") if "_auth_user" in st.session_state else "Guest"
visible_tools = _settings.get("visible_tools", ["V1.0"])

if user_type == "Member":
    # Only show basic tools to members
    available_tools = ["V1.0"]
elif user_type == "Pro Member":
    # Show all tools except admin features
    available_tools = [t for t in visible_tools if t != "Admin Panel"]
elif user_type == "Admin":
    # Show all tools
    available_tools = visible_tools
else:  # Guest
    # Show only basic tools if login is not required
    available_tools = ["V1.0"] if not login_required else []

# Show tool access message based on user type
if user_type == "Member":
    st.warning("🔒 You are Member. Upgrade to Pro for more features!")
elif user_type == "Pro Member":
    st.success("⭐ You have Pro Member access with premium features!")
elif user_type == "Admin":
    st.success("👑 You have Admin access with all feature!")
elif user_type == "Guest":
    st.info("👋 You are using the tool as a guest. Some features may be limited.")

# Check if Hue Color Tool is available
hue_tool_available = "Hue Color Tool" in available_tools

# Get tool visibility settings
tool_visibility = _settings.get("tool_visibility", {})

# Show image uploader if enabled
if tool_visibility.get("upload_images", True):
    uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
else:
    uploaded_images = []

with st.sidebar:
    st.markdown("### ⚙️  SETTINGS")
    
    if tool_visibility.get("greeting_type", True):
        greeting_type = st.selectbox("Greeting Type", 
                                     ["Good Morning", "Good Afternoon", "Good Evening", "Good Night", 
                                      "Happy Birthday", "Merry Christmas", "Custom Greeting"])
        if greeting_type == "Custom Greeting":
            custom_greeting = st.text_input("Enter Custom Greeting", "Awesome Day!")
        else:
            custom_greeting = None
    
    if tool_visibility.get("generate_variants", True):
        generate_variants = st.checkbox("Generate Multiple Variants", value=False)
        if generate_variants:
            num_variants = st.slider("Variants per Image", 1, 5, 3)
    
    if tool_visibility.get("style_mode", True):
        style_mode = st.selectbox("Style Mode", ["Text", "PNG Overlay"], index=0)
    
    overlay_year = "2025"
    if style_mode == 'PNG Overlay' and tool_visibility.get("style_mode", True):
        overlay_year = st.selectbox("Overlay Year", ["2024", "2025", "ALL"], index=1)
        png_size = st.slider("PNG Overlay Size", 0.1, 1.0, 0.5)
        
        # Hue color tool (only show if available)
        if hue_tool_available and tool_visibility.get("hue_tool", True):
            st.markdown("### 🎨 HUE COLOR TOOL")
            hue_options = ["Original", "Random", "Custom"]
            hue_option = st.selectbox("Hue Option", hue_options)
            
            if hue_option == "Custom":
                hue_shift = st.slider("Hue Shift", 0.0, 1.0, 0.0, 0.01, 
                                     help="Change the color of PNG overlays. 0 = original, 1.0 = full color cycle")
            elif hue_option == "Random":
                hue_shift = "random"
            else:
                hue_shift = 0.0
        else:
            hue_shift = 0.0
    
    if tool_visibility.get("text_effect", True):
        text_effect = st.selectbox(
            "Text Style",
            ["White Only", "White + Black Outline + Shadow", "Gradient", "NEON", "Rainbow", "RANDOM", "Country Flag", "3D"],
            index=2
        )
    
    if tool_visibility.get("text_position", True):
        text_position = st.radio("Main Text Position", ["Top Center", "Bottom Center", "Random"], index=1)
        text_position = text_position.lower().replace(" ", "_")
    
    if tool_visibility.get("custom_position", True):
        st.markdown("### 🎨 MANUAL TEXT POSITIONING")
        custom_position = st.checkbox("Enable Manual Positioning", value=False)
        if custom_position:
            text_x = st.slider("Text X Position", 0, 1000, 100)
            text_y = st.slider("Text Y Position", 0, 1000, 100)
    
    if tool_visibility.get("show_text", True):
        show_text = st.checkbox("Show Greeting", value=True)
        if show_text:
            main_size = st.slider("Main Text Size", 10, 200, 90)
    
    if tool_visibility.get("show_wish", True):
        show_wish = st.checkbox("Show Wish", value=True)
        if show_wish:
            wish_size = st.slider("Wish Text Size", 10, 200, 60)
            custom_wish = st.checkbox("Custom Wish", value=False)
            if custom_wish:
                wish_text = st.text_area("Enter Custom Wish", "Have a wonderful day!")
            else:
                wish_text = None
    
    if tool_visibility.get("overlap_percent", True):
        st.markdown("### Overlap Settings")
        overlap_percent = st.slider("Main Text Overlap (%)", 0, 50, 14)
    
    if tool_visibility.get("show_date", True):
        show_date = st.checkbox("Show Date", value=False)
        if show_date:
            date_size = st.slider("Date Text Size", 10, 200, 30)
            date_format = st.selectbox("Date Format", 
                                       ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                       index=0)
            show_day = st.checkbox("Show Day", value=False)
    
    if tool_visibility.get("show_quote", True):
        show_quote = st.checkbox("Add Quote", value=False)
        if show_quote:
            quote_size = st.slider("Quote Text Size", 10, 100, 40)
            st.markdown("### ✨ QUOTE DATABASE")
            st.markdown("<div class='quote-display'>" + get_random_quote() + "</div>", unsafe_allow_html=True)
            if st.button("Refresh Quote"):
                st.rerun()
    
    if tool_visibility.get("use_watermark", True):
        use_watermark = st.checkbox("Add Watermark", value=True)
        watermark_images = []
        
        if use_watermark:
            watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
            
            if watermark_option == "Pre-made":
                watermark_files = list_files("assets/logos", [".png", ".jpg", ".jpeg"])
                if watermark_files:
                    default_wm = ["Creative Canvas.png", "Nature Vibes.png", "TM SHIVAM.png"]
                    default = [f for f in default_wm if f in watermark_files]
                    if not default and len(watermark_files) >= 3:
                        default = watermark_files[:3]
                    selected_watermarks = st.multiselect("Select Watermark(s)", watermark_files, default=default)
                    for watermark_file in selected_watermarks:
                        watermark_path = os.path.join("assets/logos", watermark_file)
                        if os.path.exists(watermark_path):
                            watermark_images.append(Image.open(watermark_path).convert("RGBA"))
            else:
                uploaded_watermark = st.file_uploader("Upload Watermark", type=["png"], accept_multiple_files=True)
                if uploaded_watermark:
                    for watermark in uploaded_watermark:
                        watermark_images.append(Image.open(watermark).convert("RGBA"))
            
            watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 1.0)
    
    st.markdown("---")
    
    # Show premium features only to Pro Members and Admins
    if user_type in ["Pro Member", "Admin"] and tool_visibility.get("use_coffee_pet", True):
        st.markdown("###☕🐾 PRO OVERLAYS")
        use_coffee_pet = st.checkbox("Enable Coffee & Pet PNG", value=False)
        if use_coffee_pet:
            pet_size = st.slider("PNG Size", 0.1, 1.0, 0.3)
            pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
            if pet_files:
                pet_choice = st.selectbox("Select Pet PNG", ["Random"] + pet_files)
            else:
                pet_choice = None
                st.warning("No pet PNGs found in assets/pets")
        else:
            pet_choice = None
                
    if user_type in ["Pro Member", "Admin"] and tool_visibility.get("apply_emoji", True):
        st.markdown("### 😊 EMOJI STICKERS")
        apply_emoji = st.checkbox("Add Emoji Stickers", value=False)
        if apply_emoji:
            emojis = st.multiselect("Select Emojis", ["😊", "👍", "❤️", "🌟", "🎉", "🔥", "🌈", "✨", "💯"], default=["😊", "❤️", "🌟"])
            num_emojis = st.slider("Number of Emojis", 1, 10, 5)
        else:
            emojis = []
            num_emojis = 5
    else:
        if user_type not in ["Pro Member", "Admin"]:
            st.markdown("### 🔒 PRO FEATURES")
            st.info("Upgrade to Pro Member to access Coffee & Pet PNG overlays and Emoji Stickers!")
        use_coffee_pet = False
        pet_choice = None
        apply_emoji = False
        emojis = []
        num_emojis = 5
    
    if tool_visibility.get("bulk_quality", True):
        st.markdown("### ⚡ BULK PROCESSING")
        bulk_quality = st.selectbox("Output Quality", ["High (90%)", "Medium (80%)", "Low (70%)"], index=0)
    
    # Show advanced features only to Pro Members and Admins
    if user_type in ["Pro Member", "Admin"] and tool_visibility.get("advanced_features", True):
        with st.expander("🔥 Advanced Features (Compact Form)"):
            # Add 20+ new features here
            st.markdown("### Image Adjustments")
            brightness = st.slider("Brightness", 0.5, 1.5, 1.0)
            contrast = st.slider("Contrast", 0.5, 1.5, 1.0)
            sharpness = st.slider("Sharpness", 0.5, 2.0, 1.2)
            saturation = st.slider("Saturation", 0.5, 2.0, 1.1)
            
            st.markdown("### Filters")
            apply_sepia = st.checkbox("Apply Sepia Filter", value=False)
            apply_bw = st.checkbox("Apply Black & White Filter", value=False)
            apply_vintage = st.checkbox("Apply Vintage Filter", value=False)
            apply_vignette = st.checkbox("Apply Vignette Effect", value=False)
            if apply_vignette:
                vignette_intensity = st.slider("Vignette Intensity", 0.1, 1.0, 0.8)
            apply_sketch = st.checkbox("Apply Sketch Effect", value=False)
            apply_cartoon = st.checkbox("Apply Cartoon Effect", value=False)
            apply_anime = st.checkbox("Apply Anime Effect", value=False)
            
            st.markdown("### Text Customizations")
            font_folder = st.text_input("Font Folder Path", "assets/fonts")
            upscale_factor = st.slider("Text Upscale Factor", 1, 8, 4)
            
            st.markdown("### Additional Overlays")
            use_frame = st.checkbox("Add Frame Overlay", value=False)
            if use_frame:
                frame_files = list_files("assets/frames", [".png", ".jpg"])
                if frame_files:
                    frame_choice = st.selectbox("Select Frame", frame_files)
                    frame_path = os.path.join("assets/frames", frame_choice)
                    frame_size = st.slider("Frame Size", 0.1, 1.0, 1.0)
            
            st.markdown("### Export Options")
            export_format = st.selectbox("Export Format", ["JPEG", "PNG"], index=0)
            compression_level = st.slider("Compression Level (for JPEG)", 50, 100, 95)
    else:
        if user_type not in ["Pro Member", "Admin"]:
            st.markdown("### 🔒 ADVANCED FEATURES")
            st.info("Upgrade to Pro Member to access advanced image editing features!")
        brightness = 1.0
        contrast = 1.0
        sharpness = 1.2
        saturation = 1.1
        apply_sepia = False
        apply_bw = False
        apply_vintage = False
        apply_vignette = False
        vignette_intensity = 0.8
        apply_sketch = False
        apply_cartoon = False
        apply_anime = False
        font_folder = "assets/fonts"
        upscale_factor = 4
        use_frame = False
        export_format = "JPEG"
        compression_level = 95

if st.button("✨ GENERATE", key="generate", use_container_width=True):
    if uploaded_images:
        with st.spinner("Processing images with ULTRA PRO quality..."):
            processed_images = []
            variant_images = []
            progress_bar = st.progress(0)
            total_images = len(uploaded_images)
            
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
            selected_effect = effect_mapping[text_effect]
            
            watermark_groups = {}
            if watermark_images:
                if len(watermark_images) > 1:
                    group_size = len(uploaded_images) // len(watermark_images)
                    for i, watermark in enumerate(watermark_images):
                        start_idx = i * group_size
                        end_idx = (i + 1) * group_size if i < len(watermark_images) - 1 else len(uploaded_images)
                        watermark_groups[f"Group {i+1}"] = {
                            'watermark': watermark,
                            'images': uploaded_images[start_idx:end_idx]
                        }
                else:
                    watermark_groups["All Images"] = {
                        'watermark': watermark_images[0],
                        'images': uploaded_images
                    }
            else:
                watermark_groups["All Images"] = {
                    'watermark': None,
                    'images': uploaded_images
                }
            
            st.session_state.watermark_groups = watermark_groups
            
            for idx, (group_name, group_data) in enumerate(watermark_groups.items()):
                watermark = group_data['watermark']
                group_images = group_data['images']
                
                for img_idx, uploaded_file in enumerate(group_images):
                    try:
                        if uploaded_file is None:
                            continue
                            
                        img = Image.open(uploaded_file)
                        if img is None:
                            raise ValueError("Could not open image")
                            
                        img = img.convert("RGBA")
                        img = smart_crop(img)
                        
                        if generate_variants:
                            variants = []
                            for i in range(num_variants):
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
                                    'overlay_year': overlay_year,
                                    'png_size': png_size if style_mode == 'PNG Overlay' else 0.5,
                                    'brightness': brightness,
                                    'contrast': contrast,
                                    'sharpness': sharpness,
                                    'saturation': saturation,
                                    'apply_sepia': apply_sepia,
                                    'apply_bw': apply_bw,
                                    'apply_vintage': apply_vintage,
                                    'apply_vignette': apply_vignette,
                                    'vignette_intensity': vignette_intensity if 'vignette_intensity' in locals() else 0.8,
                                    'apply_sketch': apply_sketch,
                                    'apply_cartoon': apply_cartoon,
                                    'apply_anime': apply_anime,
                                    'font_folder': font_folder,
                                    'upscale_factor': upscale_factor,
                                    'hue_shift': hue_shift if hue_tool_available and style_mode == 'PNG Overlay' else 0.0
                                }
                                
                                variant = create_variant(img, settings)
                                if variant is not None:
                                    variants.append((generate_filename(), variant))
                            variant_images.extend(variants)
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
                                'overlay_year': overlay_year,
                                'png_size': png_size if style_mode == 'PNG Overlay' else 0.5,
                                'brightness': brightness,
                                'contrast': contrast,
                                'sharpness': sharpness,
                                'saturation': saturation,
                                'apply_sepia': apply_sepia,
                                'apply_bw': apply_bw,
                                'apply_vintage': apply_vintage,
                                'apply_vignette': apply_vignette,
                                'vignette_intensity': vignette_intensity if 'vignette_intensity' in locals() else 0.8,
                                'apply_sketch': apply_sketch,
                                'apply_cartoon': apply_cartoon,
                                'apply_anime': apply_anime,
                                'font_folder': font_folder,
                                'upscale_factor': upscale_factor,
                                'hue_shift': hue_shift if hue_tool_available and style_mode == 'PNG Overlay' else 0.0
                            }
                            
                            processed_img = create_variant(img, settings)
                            if processed_img is not None:
                                processed_images.append((generate_filename(), processed_img))
                    
                        progress = (idx * len(group_images) + img_idx + 1) / total_images
                        progress_bar.progress(min(progress, 1.0))
                    
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        st.error(traceback.format_exc())
                        continue

            st.session_state.generated_images = processed_images + variant_images
            
            if st.session_state.generated_images:
                st.success(f"✅ Successfully processed {len(st.session_state.generated_images)} images with ULTRA PRO quality!")
            else:
                st.warning("No images were processed.")
    else:
        st.warning("Please upload at least one image")

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
                        st.image(img_bytes, use_column_width=True)
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



