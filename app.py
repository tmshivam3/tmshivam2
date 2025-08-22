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
# ========== BEGIN AUTH / ADMIN BLOCK (PASTE ABOVE "MAIN APP" MARK) ==========
import json, uuid, hashlib
from datetime import datetime, timedelta

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def _auth_hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _auth_load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}

def _auth_save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _auth_load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"notice":"", "active_tool":"V1.0", "visible_tools":["V1.0"], "primary_color":"#ffcc00"}

def _auth_save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

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
            "expires_at": None
        }
        _auth_save_users(users)
    settings = _auth_load_settings()
    _auth_save_settings(settings)

_auth_ensure_files()
_users_db = _auth_load_users()
_settings = _auth_load_settings()

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
    if u.get("device_token") and token and u.get("device_token") != token:
        st.warning("You were logged in from another device. This session is logged out.")
        _auth_logout_and_rerun()

if "_auth_user" not in st.session_state:
    st.markdown("<h2 style='color:#ffcc00'>🔐 Login First</h2>", unsafe_allow_html=True)
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
                user["device_token"] = token
                user["last_login"] = now.isoformat()
                user["expires_at"] = (now + timedelta(days=7)).isoformat()
                _auth_save_users(db)
                st.session_state["_auth_user"] = login_id
                st.session_state["_auth_device"] = token
                st.session_state["_auth_login_time"] = now.isoformat()
                st.success(f"Welcome {login_id} — logged in!")
                st.rerun()
    st.stop()

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
    st.markdown("### Noticeboard")
    new_notice = st.text_area("Global notice (shows on main page)", value=_settings.get("notice",""))
    if st.button("Save Notice"):
        _settings["notice"] = new_notice
        _auth_save_settings(_settings)
        st.success("Notice saved.")
    st.markdown("---")
    st.markdown("### Create / Manage Users")
    c1,c2 = st.columns(2)
    with c1:
        new_id = st.text_input("New ID", key="__new_id")
        new_pw = st.text_input("New Password", type="password", key="__new_pw")
    with c2:
        new_admin = st.checkbox("Is Admin?", key="__new_admin")
        if st.button("Create User"):
            db = _auth_load_users()
            if new_id in db.get("users", {}):
                st.error("User already exists.")
            else:
                db.setdefault("users", {})[new_id] = {
                    "password_hash": _auth_hash(new_pw or "12345"),
                    "is_admin": bool(new_admin),
                    "device_token": None,
                    "last_login": None,
                    "expires_at": None
                }
                _auth_save_users(db)
                st.success(f"User {new_id} created.")
    st.markdown("#### Existing users")
    db = _auth_load_users()
    for uname, udata in list(db.get("users", {}).items()):
        cols = st.columns([3,1,1,1])
        cols[0].write(f"**{uname}** {'(admin)' if udata.get('is_admin') else ''}")
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
    st.markdown("---")
    st.write("Contact developer: +91 9140588751")
    st.stop()

if _settings.get("notice"):
    st.info(_settings.get("notice"))
# ========== END AUTH / ADMIN BLOCK ==========

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ 100+ EDIT IN 1 CLICK", layout="wide")

# Custom CSS for professional theme
st.markdown("""
    <style>
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    .header-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 2px solid #ffcc00;
        box-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
    }
    .image-preview-container {
        background-color: #121212;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #333333;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ffcc00 0%, #ff9900 100%);
        color: #000000;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 50px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(255, 204, 0, 0.5);
    }
    .sidebar .sidebar-content {
        background-color: #121212;
        color: #ffffff;
        border-right: 1px solid #333333;
    }
    .stSlider>div>div>div>div {
        background-color: #ffcc00;
    }
    .stCheckbox>div>label {
        color: #ffffff !important;
    }
    .stSelectbox>div>div>select {
        background-color: #1a1a1a;
        color: #ffffff !important;
        border: 1px solid #333333;
    }
    .stImage>img {
        border: 2px solid #ffcc00;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.3);
    }
    .variant-container {
        display: flex;
        overflow-x: auto;
        gap: 15px;
        padding: 15px 0;
    }
    .variant-item {
        flex: 0 0 auto;
    }
    .download-btn {
        display: block;
        margin-top: 10px;
        text-align: center;
    }
    .feature-card {
        border: 1px solid #ffcc00;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        color: #ffffff;
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.2);
    }
    .pro-badge {
        background-color: #ffcc00;
        color: #000;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: bold;
        margin-left: 8px;
    }
    .section-title {
        color: #ffcc00;
        border-bottom: 2px solid #ffcc00;
        padding-bottom: 8px;
        margin-top: 25px;
        font-size: 1.4rem;
    }
    .effect-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .tab-content {
        padding: 15px 0;
    }
    .manual-position {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
    }
    .quote-display {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        border-left: 4px solid #ffcc00;
    }
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #ffcc00, #ff9900);
    }
    .preview-container {
        position: relative;
        display: inline-block;
    }
    .text-overlay {
        position: absolute;
        cursor: move;
        border: 2px dashed #ffcc00;
        padding: 5px;
        background-color: rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder: str, exts: List[str]) -> List[str]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    files = os.listdir(folder)
    return [f for f in files 
           if any(f.lower().endswith(ext.lower()) for ext in exts)]

def list_subfolders(folder: str) -> List[str]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        return []
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

def smart_crop(img: Image.Image, target_ratio: float = 3/4) -> Image.Image:
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
    if text is None:
        return 0, 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def get_random_font() -> ImageFont.FreeTypeFont:
    try:
        fonts = list_files("assets/fonts", [".ttf", ".otf"])
        if not fonts:
            return ImageFont.truetype("arial.ttf", 80)
        
        for _ in range(3):
            try:
                font_path = os.path.join("assets/fonts", random.choice(fonts))
                return ImageFont.truetype(font_path, 80)
            except:
                continue
        
        return ImageFont.truetype("arial.ttf", 80)
    except:
        return ImageFont.load_default()

def get_random_wish(greeting_type: str) -> str:
    wishes = {
        "Good Morning": [
            "Rise and shine! A new day is a new opportunity!",
            "Good morning! Make today amazing!",
            "Morning blessings! Hope your day is filled with joy!",
            "New day, new blessings! Seize the day!",
            "Wake up with determination! Go to bed with satisfaction!",
            "Every sunrise is a new chapter! Write a beautiful story today!",
            "Morning is the perfect time to start something new!",
            "The early morning has gold in its mouth!",
            "A new day is a new chance to be better than yesterday!",
            "Morning is wonderful! Embrace the beauty of a fresh start!",
            "The sun is a daily reminder that we too can rise again!",
            "Today's morning brings new strength, new thoughts, and new possibilities!",
            "Morning is the time when the whole world starts anew!",
            "Every sunrise is an invitation for us to arise and brighten someone's day!",
            "Good morning! May your coffee be strong and your day be productive!",
            "Start your day with a smile! It sets the tone for the whole day!",
            "Morning is not just time, it's an opportunity! Make it count!",
            "Let the morning sunshine fill your heart with warmth and positivity!",
            "A beautiful morning begins with a beautiful mindset!",
            "Good morning! May your day be as bright as your smile!"
        ],
        "Good Afternoon": [
            "Enjoy your afternoon! Hope it's productive!",
            "Afternoon delights! Take a break and refresh!",
            "Sunshine and smiles! Hope your afternoon is great!",
            "Perfect day ahead! Make the most of your afternoon!",
            "Afternoon is the perfect time to accomplish great things!",
            "Hope your day is going well! Keep up the good work!",
            "Afternoon blessings! May your energy be renewed!",
            "Take a deep breath! You're doing great this afternoon!",
            "The afternoon is a bridge between morning and evening! Make it count!",
            "Good afternoon! Time to refuel and recharge!",
            "Hope your afternoon is filled with productivity and joy!",
            "Afternoon is the perfect time for a fresh start!",
            "Keep going! The day is still full of possibilities!",
            "Good afternoon! May your focus be sharp and your tasks be light!",
            "The afternoon sun brings warmth and energy! Use it wisely!",
            "Halfway through the day! Keep pushing forward!",
            "Afternoon is the perfect time to review and refocus!",
            "Hope your afternoon is as bright as the sun!",
            "Good afternoon! Time to conquer the rest of the day!",
            "May your afternoon be productive and peaceful!"
        ],
        "Good Evening": [
            "Beautiful sunset! Hope you had a great day!",
            "Evening serenity! Time to relax and unwind!",
            "Twilight magic! Hope your evening is peaceful!",
            "Peaceful evening! Reflect on the day's blessings!",
            "Evening is the time to slow down and appreciate life!",
            "Good evening! May your night be filled with peace!",
            "The evening sky is painting a masterpiece just for you!",
            "As the day ends, let go of stress and embrace calm!",
            "Evening blessings! May your heart be light!",
            "Good evening! Time to recharge for tomorrow!",
            "Hope your evening is as beautiful as the setting sun!",
            "Evening is the perfect time to count your blessings!",
            "Let the evening breeze wash away your worries!",
            "Good evening! May your night be restful and peaceful!",
            "As the stars come out, may your dreams take flight!",
            "Evening is nature's way of saying 'well done'!",
            "Unwind, relax, and enjoy the evening tranquility!",
            "Good evening! Time for family, friends, and relaxation!",
            "May your evening be filled with joy and contentment!",
            "The evening brings closure and peace! Embrace it!"
        ],
        "Good Night": [
            "Sweet dreams! Sleep tight!",
            "Night night! Rest well for tomorrow!",
            "Sleep well! Dream big!",
            "Good night! May your dreams be sweet!",
            "As you close your eyes, let peace fill your heart!",
            "Night blessings! May you wake up refreshed!",
            "Good night! Tomorrow is a new opportunity!",
            "Rest your mind, body, and soul! Good night!",
            "Wishing you a night of peaceful and deep sleep!",
            "May the night bring you comfort and restoration!",
            "Sleep is the best meditation! Have a good night!",
            "Good night! Let the stars watch over you!",
            "Tomorrow is another chance! Rest well tonight!",
            "End your day with gratitude! Good night!",
            "May your night be filled with sweet dreams!",
            "Sleep is the golden chain that ties health and our bodies together!",
            "Good night! Tomorrow's success starts with tonight's rest!",
            "Close your eyes, clear your heart, and sleep well!",
            "Wishing you a night as peaceful as a quiet forest!",
            "Good night! May angels watch over you while you sleep!"
        ],
        "Happy Birthday": [
            "Wishing you a fantastic birthday!",
            "Many happy returns! Enjoy your special day!",
            "Celebrate big! It's your day!",
            "Best wishes on your special day!",
            "Happy birthday! Make it memorable!",
            "Another year wiser! Happy birthday!",
            "May your birthday be filled with joy and laughter!",
            "Wishing you health, wealth and happiness!",
            "Happy birthday! May all your dreams come true!",
            "Celebrate yourself today! You deserve it!",
            "Happy birthday! Shine bright like a diamond!",
            "May your birthday be as special as you are!",
            "Happy birthday! Here's to another amazing year!",
            "Birthdays are nature's way of telling us to eat more cake!",
            "Wishing you 24 hours of pure happiness!",
            "Happy birthday! May your day be sprinkled with joy!",
            "Another adventure around the sun! Happy birthday!",
            "May your birthday be the start of your best year yet!",
            "Happy birthday! Time to make more wonderful memories!",
            "Wishing you a birthday that's as amazing as you are!"
        ],
        "Merry Christmas": [
            "Joy to the world! Merry Christmas!",
            "Season's greetings! Enjoy the holidays!",
            "Ho ho ho! Merry Christmas!",
            "Warmest wishes for a merry Christmas!",
            "May your Christmas be filled with love and joy!",
            "Merry Christmas! Hope Santa brings you everything you wished for!",
            "Wishing you peace, love and joy this Christmas!",
            "May the magic of Christmas fill your heart!",
            "Merry Christmas! Enjoy the festive season!",
            "Wishing you and your family a very merry Christmas!",
            "May your holidays sparkle with joy and laughter!",
            "Christmas is not a season, it's a feeling! Enjoy it!",
            "Warmest thoughts and best wishes for a wonderful Christmas!",
            "May the Christmas spirit bring you peace and happiness!",
            "Merry Christmas! May your heart be light and your days be bright!",
            "Sending you love and joy this Christmas season!",
            "May your home be filled with the joys of the season!",
            "Merry Christmas! Hope it's your best one yet!",
            "Wishing you a Christmas that's merry and bright!",
            "May the wonder of Christmas stay with you throughout the year!"
        ],
        "Custom Greeting": [
            "Have a wonderful day!",
            "Stay blessed! Keep smiling!",
            "Enjoy every moment!",
            "Make today amazing!",
            "You are awesome!",
            "Keep shining!",
            "Stay positive!",
            "Believe in yourself!",
            "Dream big! Work hard!",
            "You've got this!",
            "Make it happen!",
            "Create your own sunshine!",
            "Be the reason someone smiles today!",
            "Today is a gift!",
            "Spread kindness wherever you go!",
            "Your potential is endless!",
            "Radiate positivity!",
            "Embrace the journey!",
            "Make today count!",
            "You are capable of amazing things!"
        ]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_quote() -> str:
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Your time is limited, so don't waste it living someone else's life. - Steve Jobs",
        "Stay hungry, stay foolish. - Steve Jobs",
        "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "If life were predictable it would cease to be life, and be without flavor. - Eleanor Roosevelt",
        "Life is what happens when you're busy making other plans. - John Lennon",
        "Spread love everywhere you go. - Mother Teresa",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "Tell me and I forget. Teach me and I remember. Involve me and I learn. - Benjamin Franklin",
        "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart. - Helen Keller",
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "Whoever is happy will make others happy too. - Anne Frank",
        "Do not go where the path may lead, go instead where there is no path and leave a trail. - Ralph Waldo Emerson",
        "You will face many defeats in life, but never let yourself be defeated. - Maya Angelou",
        "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
        "In the end, it's not the years in your life that count. It's the life in your years. - Abraham Lincoln",
        "Never let the fear of striking out keep you from playing the game. - Babe Ruth",
        "Life is either a daring adventure or nothing at all. - Helen Keller"
    ]
    return random.choice(quotes)

def get_random_color() -> Tuple[int, int, int]:
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def get_vibrant_color() -> Tuple[int, int, int]:
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
    if random.random() < 0.8:
        return [(255, 255, 255), dominant_color]
    else:
        return [(255, 255, 255), random.choice(PURE_COLORS)]

def get_multi_gradient_colors() -> List[Tuple[int, int, int]]:
    num_colors = random.randint(2, 7)
    colors = []
    for _ in range(num_colors):
        colors.append(get_vibrant_color())
    return colors

def create_gradient_mask(width: int, height: int, colors: List[Tuple[int, int, int]], direction: str = 'horizontal') -> Image.Image:
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

def apply_overlay(image: Image.Image, overlay_path: str, size: float = 0.5) -> Image.Image:
    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        new_size = (int(image.width * size), int(image.height * size))
        overlay = overlay.resize(new_size, Image.LANCZOS)
        
        max_x = max(20, image.width - overlay.width - 20)
        max_y = max(20, image.height - overlay.height - 20)
        x = random.randint(20, max_x) if max_x > 20 else 20
        y = random.randint(20, max_y) if max_y > 20 else 20
        
        image.paste(overlay, (x, y), overlay)
    except Exception as e:
        st.error(f"Error applying overlay: {str(e)}")
    return image

def generate_filename() -> str:
    future_minutes = random.randint(1, 10)
    now = datetime.now()
    future_time = now + timedelta(minutes=future_minutes)
    return f"Picsart_{future_time.strftime('%y-%m-%d_%H-%M-%S')}.jpg"

def get_watermark_position(img: Image.Image, watermark: Image.Image) -> Tuple[int, int]:
    x = random.choice([20, img.width - watermark.width - 20])
    y = img.height - watermark.height - 20
    return (x, y)

def enhance_image_quality(img: Image.Image) -> Image.Image:
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.2)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)
    
    return img

def upscale_text_elements(img: Image.Image, scale_factor: int = 2) -> Image.Image:
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
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.5)
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = edges.convert('L')
    edges = edges.point(lambda x: 0 if x < 100 else 255)
    result = img.copy()
    result.paste((0, 0, 0), (0, 0), edges)
    return result

def apply_rain_effect(img: Image.Image) -> Image.Image:
    width, height = img.size
    rain = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rain)
    for _ in range(1000):
        x = random.randint(0, width)
        y = random.randint(0, height)
        length = random.randint(10, 30)
        draw.line([(x, y), (x, y+length)], fill=(200, 200, 255, 100), width=1)
    return Image.alpha_composite(img.convert('RGBA'), rain).convert('RGB')

def apply_snow_effect(img: Image.Image) -> Image.Image:
    width, height = img.size
    snow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(snow)
    for _ in range(500):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(2, 6)
        draw.ellipse([(x, y), (x+size, y+size)], fill=(255, 255, 255, 200))
    return Image.alpha_composite(img.convert('RGBA'), snow).convert('RGB')

def apply_emoji_stickers(img: Image.Image, emojis: List[str]) -> Image.Image:
    if not emojis:
        return img
        
    draw = ImageDraw.Draw(img)
    for _ in range(5):
        x = random.randint(20, img.width-40)
        y = random.randint(20, img.height-40)
        emoji = random.choice(emojis)
        font = ImageFont.truetype("arial.ttf", 40)
        draw.text((x, y), emoji, font=font, fill=(255, 255, 0))
    return img

def get_dominant_color(img: Image.Image) -> Tuple[int, int, int]:
    img_small = img.resize((100, 100))
    colors = Counter(img_small.getdata())
    dominant = colors.most_common(1)[0][0]
    h, l, s = colorsys.rgb_to_hls(*[c / 255 for c in dominant])
    if l < 0.5:
        l = 0.7
    return tuple(int(255 * c) for c in colorsys.hls_to_rgb(h, l, s))

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

def apply_text_effect(draw: ImageDraw.Draw, position: Tuple[int, int], text: str, font: ImageFont.FreeTypeFont, 
                     effect_settings: dict, base_img: Image.Image) -> dict:
    """Apply advanced text effects with separate layers for shadow, outline, and fill"""
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
    
    # Draw shadow on shadow_layer (offset 2,2, opacity 40)
    shadow_offset = (2, 2)
    shadow_draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 40))
    
    # Draw outline on outline_layer
    outline_range = 1 if effect_type == 'neon' else 2
    for ox in range(-outline_range, outline_range + 1):
        for oy in range(-outline_range, outline_range + 1):
            if ox != 0 or oy != 0:
                outline_draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 255))
    
    # Create white mask for text
    mask = Image.new("L", (text_width, text_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((0, 0), text, font=font, fill=255)
    
    # Apply fill based on effect type
    if effect_type in ['gradient', 'rainbow']:
        colors = effect_settings['colors']
        gradient = create_gradient_mask(text_width, text_height, colors)
        
        # Create fill layer with gradient applied through white mask
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
    
    else:  # white_only or white_black_outline_shadow
        fill_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # Merge layers using alpha compositing
    base_img_rgba = base_img.convert('RGBA') if base_img.mode != 'RGBA' else base_img
    base_img_rgba = Image.alpha_composite(base_img_rgba, shadow_layer)
    base_img_rgba = Image.alpha_composite(base_img_rgba, outline_layer)
    base_img_rgba = Image.alpha_composite(base_img_rgba, fill_layer)
    
    # Update base_img with the composited result
    base_img.paste(base_img_rgba, (0, 0))
    
    return effect_settings

def create_variant(original_img: Image.Image, settings: dict) -> Optional[Image.Image]:
    try:
        img = original_img.copy()
        draw = ImageDraw.Draw(img)
        
        font = get_random_font()
        if font is None:
            return None
        
        dominant_color = get_dominant_color(img)
        
        effect_settings = {
            'type': settings.get('text_effect', 'gradient'),
            'outline_size': 2,
            'colors': get_gradient_colors(dominant_color) if settings.get('text_effect', 'gradient') == 'gradient' else get_multi_gradient_colors()
        }
        
        style_mode = settings.get('style_mode', 'Text')
        
        if style_mode == 'PNG Overlay' and settings['greeting_type'] in ["Good Morning", "Good Night"]:
            themes = list_subfolders("assets/overlays")
            if not themes:
                st.warning("No overlay themes found.")
                return img
            theme = random.choice(themes)
            base_path = os.path.join("assets/overlays", theme)
            
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
                    pngs.append(Image.open(path).convert("RGBA"))
            
            if pngs:
                gap = 10
                total_h = sum(p.height for p in pngs) + (len(pngs) - 1) * gap
                max_w = max(p.width for p in pngs)
                
                scale = min(1.0, min((img.width * 0.8) / max_w, (img.height * 0.8) / total_h))
                pngs = [p.resize((int(p.width * scale), int(p.height * scale)), Image.LANCZOS) for p in pngs]
                
                total_h = sum(p.height for p in pngs) + (len(pngs) - 1) * gap
                max_w = max(p.width for p in pngs)
                
                prefer_top = settings['text_position'] == "top_center"
                start_x, start_y = find_text_position(img, max_w, total_h, prefer_top=prefer_top)
                
                if settings.get('custom_position', False):
                    start_x = settings.get('text_x', 100)
                    start_y = settings.get('text_y', 100)
                elif settings['text_position'] == "bottom_center":
                    start_y = img.height - total_h - 20
                
                current_y = start_y
                for p in pngs:
                    x = start_x + (max_w - p.width) // 2
                    img.paste(p, (x, current_y), p)
                    current_y += p.height + gap
                
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
                
                gap = 5
                total_h = sum(line_heights) + (len(main_texts) - 1) * gap
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
                    total_h = sum(line_heights) + (len(main_texts) - 1) * gap
                    max_w = max(line_widths)
                
                text_x, text_y = find_text_position(img, max_w, total_h, prefer_top=True)
                if settings.get('custom_position', False):
                    text_x = settings.get('text_x', 100)
                    text_y = settings.get('text_y', 100)
                elif settings['text_position'] == "top_center":
                    text_x = (img.width - max_w) // 2
                    text_y = 20
                elif settings['text_position'] == "bottom_center":
                    text_x = (img.width - max_w) // 2
                    text_y = img.height - total_h - 20
                
                current_y = text_y
                for i, t in enumerate(main_texts):
                    line_x = text_x + (max_w - line_widths[i]) // 2
                    apply_text_effect(draw, (line_x, current_y), t, font_main, effect_settings, img)
                    current_y += line_heights[i] + gap
                
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
                
                gap = 5
                total_h = sum(line_heights) + (len(lines) - 1) * gap
                max_w = max(line_widths)
                
                wish_x, wish_y = find_text_position(img, max_w, total_h, prefer_top=False)
                if settings['show_text']:
                    wish_y = max(wish_y, main_end_y + 20)
                
                current_y = wish_y
                for i, line in enumerate(lines):
                    line_x = wish_x + (max_w - line_widths[i]) // 2
                    apply_text_effect(draw, (line_x, current_y), line, font_wish, effect_settings, img)
                    current_y += line_heights[i] + gap
        
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
            
            max_date_x = max(20, img.width - date_width - 20)
            date_x = random.randint(20, max_date_x) if max_date_x > 20 else 20
            date_y = img.height - date_height - 20
            
            if settings['show_day'] and "(" in date_text:
                day_part = date_text[date_text.index("("):]
                day_width, _ = get_text_size(draw, day_part, font_date)
                if date_x + day_width > img.width - 20:
                    date_x = img.width - day_width - 25
            
            apply_text_effect(draw, (date_x, date_y), date_text, font_date, effect_settings, img)
        
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
            
            for i, line in enumerate(lines):
                line_x = (img.width - line_widths[i]) // 2
                apply_text_effect(draw, (line_x, quote_y), line, font_quote, effect_settings, img)
                quote_y += line_heights[i] + 10
        
        if settings['use_watermark'] and settings['watermark_image']:
            watermark = settings['watermark_image'].copy()
            
            if settings['watermark_opacity'] < 1.0:
                alpha = watermark.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(settings['watermark_opacity'])
                watermark.putalpha(alpha)
            
            watermark.thumbnail((img.width//4, img.height//4))
            pos = get_watermark_position(img, watermark)
            img.paste(watermark, pos, watermark)
        
        if settings['use_coffee_pet'] and settings['selected_pet']:
            pet_path = os.path.join("assets/pets", settings['selected_pet'])
            if os.path.exists(pet_path):
                pet_img = Image.open(pet_path).convert("RGBA")
                pet_img = pet_img.resize(
                    (int(img.width * settings['pet_size']), 
                    int(img.height * settings['pet_size'] * (pet_img.height/pet_img.width))),
                    Image.LANCZOS
                )
                x = img.width - pet_img.width - 20
                y = img.height - pet_img.height - 20
                img.paste(pet_img, (x, y), pet_img)
        
        if settings.get('apply_emoji', False) and settings.get('emojis'):
            img = apply_emoji_stickers(img, settings['emojis'])
        
        img = enhance_image_quality(img)
        img = upscale_text_elements(img, scale_factor=2)
        
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

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with st.sidebar:
    st.markdown("### ⚙️  SETTINGS")
    
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
    
    if style_mode == 'PNG Overlay':
        png_size = st.slider("PNG Overlay Size", 0.1, 1.0, 0.5)
    
    text_effect = st.selectbox(
        "Text Style",
        ["White Only", "White + Black Outline + Shadow", "Gradient", "NEON", "Rainbow", "RANDOM", "Country Flag", "3D"],
        index=2
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
    
    show_date = st.checkbox("Show Date", value=False)
    if show_date:
        date_size = st.slider("Date Text Size", 10, 200, 30)
        date_format = st.selectbox("Date Format", 
                                 ["8 July 2025", "28 January 2025", "07/08/2025", "2025-07-08"],
                                 index=0)
        show_day = st.checkbox("Show Day", value=False)
    
    show_quote = st.checkbox("Add Quote", value=False)
    if show_quote:
        quote_size = st.slider("Quote Text Size", 10, 100, 40)
        st.markdown("### ✨ QUOTE DATABASE")
        st.markdown("<div class='quote-display'>" + get_random_quote() + "</div>", unsafe_allow_html=True)
        if st.button("Refresh Quote"):
            st.rerun()
    
    use_watermark = st.checkbox("Add Watermark", value=True)
    watermark_images = []
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Pre-made", "Upload Your Own"])
        
        if watermark_option == "Pre-made":
            watermark_files = list_files("assets/logos", [".png", ".jpg", ".jpeg"])
            if watermark_files:
                default_wm = watermark_files[:3] if len(watermark_files) >= 3 else watermark_files
                selected_watermarks = st.multiselect("Select Watermark(s)", watermark_files, default=default_wm)
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
    st.markdown("### ☕🐾 PRO OVERLAYS")
    use_coffee_pet = st.checkbox("Enable Coffee & Pet PNG", value=False)
    if use_coffee_pet:
        pet_size = st.slider("PNG Size", 0.1, 1.0, 0.3)
        pet_files = list_files("assets/pets", [".png", ".jpg", ".jpeg"])
        if pet_files:
            selected_pet = st.selectbox("Select Pet PNG", ["Random"] + pet_files)
            if selected_pet == "Random":
                selected_pet = random.choice(pet_files)
            else:
                selected_pet = selected_pet
        else:
            selected_pet = None
            st.warning("No pet PNGs found in assets/pets")
    else:
        selected_pet = None
            
    st.markdown("### 😊 EMOJI STICKERS")
    apply_emoji = st.checkbox("Add Emoji Stickers", value=False)
    if apply_emoji:
        emojis = st.multiselect("Select Emojis", ["😊", "👍", "❤️", "🌟", "🎉", "🔥", "🌈", "✨", "💯"], default=["😊", "❤️", "🌟"])
    else:
        emojis = []
    
    st.markdown("### ⚡ BULK PROCESSING")
    bulk_quality = st.selectbox("Output Quality", ["High (90%)", "Medium (80%)", "Low (70%)"], index=0)

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
                        img = enhance_image_quality(img)
                        
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
                                    'selected_pet': selected_pet,
                                    'text_effect': selected_effect,
                                    'custom_position': custom_position,
                                    'text_x': text_x if custom_position else 100,
                                    'text_y': text_y if custom_position else 100,
                                    'apply_emoji': apply_emoji,
                                    'emojis': emojis,
                                    'style_mode': style_mode
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
                                'selected_pet': selected_pet,
                                'text_effect': selected_effect,
                                'custom_position': custom_position,
                                'text_x': text_x if custom_position else 100,
                                'text_y': text_y if custom_position else 100,
                                'apply_emoji': apply_emoji,
                                'emojis': emojis,
                                'style_mode': style_mode
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
    rows = (len(st.session_state.generated_images) // cols_per_row) + 1
    
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
