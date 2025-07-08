import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import io
import random
import datetime
import zipfile
import time

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Apply Greetings, Watermarks, Fonts, Wishes & More</h4>
""", unsafe_allow_html=True)

# ========== CONSTANTS ==========
MORNING_WISHES = [
    "Have a great day!", "Start your day with a smile", "Enjoy your coffee!",
    "Fresh start today!", "Make today beautiful", "Positive vibes only"
]

NIGHT_WISHES = [
    "Sweet dreams", "Good night, sleep tight", "Peaceful rest ahead",
    "Relax and unwind", "Nighty night!", "Sleep peacefully"
]

COLORS = [
    (255, 255, 0), (255, 0, 0), (255, 255, 255),
    (255, 192, 203), (0, 255, 0), (255, 165, 0),
    (173, 216, 230), (128, 0, 128), (255, 105, 180)
]

# ========== UTILS ==========
def list_files(folder, exts):
    if not os.path.exists(folder): return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def safe_randint(a, b):
    if a > b: a, b = b, a
    return random.randint(a, b)

def overlay_text(draw, position, text, font, fill, shadow=False, outline=False):
    x, y = position
    if shadow:
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
    if outline:
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                draw.text((x + dx, y + dy), text, font=font, fill="white")
    draw.text((x, y), text, font=font, fill=fill)

def place_logo_random(img, logo):
    w, h = img.size
    logo_w, logo_h = logo.size
    max_x = max(0, w - logo_w - 30)
    max_y = max(0, h - logo_h - 30)
    x = safe_randint(20, max_x)
    y = safe_randint(20, max_y)
    opacity = random.uniform(0.45, 1.0)
    watermark = logo.copy()
    watermark = ImageEnhance.Brightness(watermark).enhance(opacity)
    img.paste(watermark, (x, y), watermark)
    return img

def overlay_png_random(img, greeting_type, overlay_main_scale=40, overlay_wish_scale=30):
    base_folder = os.path.join("assets", "overlays")
    if not os.path.exists(base_folder):
        st.warning("⚠️ Overlays folder not found!")
        return None

    themes = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
    if not themes:
        st.warning("⚠️ No overlay themes found in overlays folder!")
        return None

    chosen_theme = random.choice(themes)
    theme_path = os.path.join(base_folder, chosen_theme)

    if greeting_type == "Good Morning":
        overlay_numbers = [1, 2, 4]
    elif greeting_type == "Good Night":
        overlay_numbers = [1, 3, 5]
    else:
        overlay_numbers = [1]

    iw, ih = img.size
    overlays = []
    for num in overlay_numbers:
        file_path = os.path.join(theme_path, f"{num}.png")
        if not os.path.exists(file_path):
            continue
        try:
            overlay = Image.open(file_path).convert("RGBA")
            role = "main" if num in [1, 2, 3] else "wish"
            overlays.append((overlay, role, num))
        except:
            continue

    if not overlays:
        return img

    main_scale = overlay_main_scale / 100.0
    wish_scale = overlay_wish_scale / 100.0
    y_padding = 20

    main_overlays = [ov for ov in overlays if ov[1] == "main"]
    wish_overlays = [ov for ov in overlays if ov[1] == "wish"]

    target_main_h = int(ih * main_scale)
    main_resized = []
    for overlay, role, num in main_overlays:
        ow, oh = overlay.size
        new_h = target_main_h
        new_w = int(ow * new_h / oh)
        main_resized.append((overlay.resize((new_w, new_h), Image.LANCZOS), new_w, new_h))

    total_main_width = sum(w for _, w, _ in main_resized) + (len(main_resized) - 1) * 20
    start_x = max(0, (iw - total_main_width) // 2)
    current_y = y_padding

    if current_y + target_main_h + len(wish_overlays)*int(ih*wish_scale) + 2*y_padding > ih:
        current_y = ih - (target_main_h + len(wish_overlays)*int(ih*wish_scale) + 2*y_padding)

    x_pos = start_x
    for overlay_img, ow, oh in main_resized:
        if x_pos + ow > iw: break
        img.paste(overlay_img, (x_pos, current_y), overlay_img)
        x_pos += ow + 20
    current_y += target_main_h + y_padding

    for overlay, role, num in wish_overlays:
        ow, oh = overlay.size
        new_h = int(ih * wish_scale)
        new_w = int(ow * new_h / oh)
        overlay_resized = overlay.resize((new_w, new_h), Image.LANCZOS)

        if current_y + new_h + y_padding > ih:
            current_y = ih - new_h - y_padding

        px = max(0, (iw - new_w) // 2)
        img.paste(overlay_resized, (px, current_y), overlay_resized)
        current_y += new_h + y_padding

    return img

# ========== SIDEBAR ==========
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
def_wish = random.choice(MORNING_WISHES if greeting_type == "Good Morning" else NIGHT_WISHES)
custom_wish = st.sidebar.text_input("Wishes Text (optional)", value="")
show_wish_text = st.sidebar.checkbox("Show Wishes Text", value=True)
coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 1, 100, 8)
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
date_size_factor = st.sidebar.slider("Date Text Size (%)", 30, 120, 70)

with st.sidebar.expander("🎨 Font & Watermark Selection", expanded=False):
    uploaded_font = st.file_uploader("Upload Font (.ttf/.otf)", type=["ttf", "otf"])
    available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
    font_file = st.selectbox("Choose Built-in Font", available_fonts)

    uploaded_logo = st.file_uploader("Upload Your Watermark (.png)", type=["png"])
    available_logos = list_files("assets/logos", [".png"])
    logo_file = st.selectbox("Choose Built-in Logo", available_logos)

with st.sidebar.expander("🖼️ PNG Overlays (Optional, Compact)", expanded=False):
    use_png_overlay = st.checkbox("Use PNG Overlay Wishes Instead of Text")
    overlay_main_scale = st.slider("Main Overlay Size (%)", 10, 100, 40)
    overlay_wish_scale = st.slider("Wishes Overlay Size (%)", 10, 100, 30)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

results = []
