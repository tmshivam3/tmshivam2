import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import io
import random
import datetime
import zipfile
import time

# =================== PAGE CONFIG ===================
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Apply Greetings, Watermarks, Fonts, Wishes & More</h4>
""", unsafe_allow_html=True)

# =================== CONSTANTS ===================
COLORS = [
    (255, 255, 0), (255, 0, 0), (255, 255, 255),
    (255, 192, 203), (0, 255, 0), (255, 165, 0),
    (173, 216, 230), (128, 0, 128), (255, 105, 180)
]

# =================== UTILS ===================
def list_dirs(path):
    if not os.path.exists(path):
        return []
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def list_files(path, exts):
    if not os.path.exists(path):
        return []
    return [f for f in os.listdir(path) if any(f.lower().endswith(ext) for ext in exts)]

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

def paste_overlay_fixed(img, overlay, position):
    overlay_ratio = overlay.width / overlay.height
    target_w = int(img.width * 0.45)
    target_h = int(target_w / overlay_ratio)
    overlay_resized = overlay.resize((target_w, target_h), Image.LANCZOS)
    x, y = position
    img.paste(overlay_resized, (x, y), overlay_resized)
    return img

def sorted_theme_list():
    themes = list_dirs("assets/overlays")
    themes.sort(reverse=True)
    return themes

# =================== SIDEBAR ===================
st.sidebar.header("🛠️ Tool Settings")

# Overlay enable/disable
use_overlay = st.sidebar.checkbox("🖼️ Enable Overlay Wishes", value=False)

# If overlay is enabled show its options
overlay_theme = None
overlay_mode = None
overlay_good_size = 100
overlay_wish_size = 60

if use_overlay:
    theme_options = ["Auto", "Random"] + sorted_theme_list()
    overlay_theme = st.sidebar.selectbox("🎨 Select Overlay Theme", theme_options)

    with st.sidebar.expander("Overlay Text Settings"):
        overlay_good_size = st.slider("Good / Morning / Night Text Size %", 40, 160, 100, step=5)
        overlay_wish_size = st.slider("Wishes Text Size %", 30, 120, 60, step=5)

# Greeting type
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])

# Wishes text
custom_wish = st.sidebar.text_input("Wishes Text (optional)", value="")
show_wish_text = st.sidebar.checkbox("Show Wishes Text", value=True)

# Main text coverage
coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 1, 100, 20)

# Date
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
date_size_factor = None
if show_date:
    date_size_factor = st.sidebar.slider("Date Text Size (%)", 30, 120, 70)

# Font selection
own_font = st.sidebar.checkbox("Use Own Font")
font_file = None
if own_font:
    uploaded_font = st.sidebar.file_uploader("Upload Font (.ttf, .otf)", type=["ttf", "otf"])
    if uploaded_font:
        font_file = io.BytesIO(uploaded_font.read())
    else:
        available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
        font_file = st.sidebar.selectbox("Choose Font", available_fonts)
        if font_file:
            font_file = os.path.join("assets/fonts", font_file)

# Logo selection
own_logo = st.sidebar.checkbox("Use Own Watermark Logo")
logo_file = None
if own_logo:
    uploaded_logo = st.sidebar.file_uploader("Upload Logo (.png)", type=["png"])
    if uploaded_logo:
        logo_file = io.BytesIO(uploaded_logo.read())
    else:
        available_logos = list_files("assets/logos", [".png"])
        logo_file = st.sidebar.selectbox("Choose Watermark Logo", available_logos)
        if logo_file:
            logo_file = os.path.join("assets/logos", logo_file)

# Upload images
uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# =================== MAIN ===================
results = []

if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Generating images, please wait..."):
            time.sleep(0.5)

            for idx, image_file in enumerate(uploaded_images):
                try:
                    image = Image.open(image_file).convert("RGBA")
                    image = crop_to_3_4(image)
                    w, h = image.size

                    # ================= Overlay Wishes =================
                    if use_overlay and overlay_theme:
                        if overlay_theme == "Auto":
                            theme_folders = sorted_theme_list()
                            theme_path = os.path.join("assets/overlays", random.choice(theme_folders))
                        elif overlay_theme == "Random":
                            theme_folders = sorted_theme_list()
                            theme_path = os.path.join("assets/overlays", random.choice(theme_folders))
                        else:
                            theme_path = os.path.join("assets/overlays", overlay_theme)

                        if greeting_type == "Good Morning":
                            overlay_files = ["1.png", "2.png"]
                        elif greeting_type == "Good Night":
                            overlay_files = ["1.png", "3.png"]
                        else:
                            overlay_files = ["1.png"]

                        for i, num in enumerate(overlay_files):
                            overlay_file = os.path.join(theme_path, num)
                            if os.path.exists(overlay_file):
                                overlay_img = Image.open(overlay_file).convert("RGBA")
                                if i == 0:
                                    pos = (int(w*0.05), int(h*0.05))
                                else:
                                    pos = (int(w*0.05), int(h*0.75))
                                image = paste_overlay_fixed(image, overlay_img, pos)

                    # ================= Text Wishes =================
                    text_area_scale = coverage_percent / 500
                    main_font_size = max(20, int((w * h * text_area_scale) ** 0.5 * 0.6))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100) if show_date and date_size_factor else None

                    if font_file:
                        if isinstance(font_file, str):
                            main_font = ImageFont.truetype(font_file, main_font_size)
                            sub_font = ImageFont.truetype(font_file, sub_font_size)
                            if date_font_size:
                                date_font = ImageFont.truetype(font_file, date_font_size)
                        else:
                            main_font = ImageFont.truetype(font_file, main_font_size)
                            sub_font = ImageFont.truetype(font_file, sub_font_size)
                            if date_font_size:
                                date_font = ImageFont.truetype(font_file, date_font_size)
                    else:
                        main_font = ImageFont.load_default()
                        sub_font = ImageFont.load_default()
                        date_font = ImageFont.load_default()

                    draw = ImageDraw.Draw(image)
                    text_color = random.choice(COLORS)

                    x_range = max(30, w - main_font_size * len(greeting_type) // 2 - 30)
                    y_range = max(30, h - main_font_size - 30)
                    x = safe_randint(30, x_range)
                    y = safe_randint(30, y_range)

                    overlay_text(draw, (x, y), greeting_type, main_font, text_color, shadow=True, outline=True)

                    if show_wish_text:
                        wish_text = custom_wish if custom_wish.strip() else "Have a Nice Day!"
                        wish_x = x + random.randint(-15, 15)
                        wish_y = y + main_font_size + 10
                        overlay_text(draw, (wish_x, wish_y), wish_text, sub_font, text_color, shadow=True)

                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        dx = safe_randint(30, max(30, w - 200))
                        dy = safe_randint(30, max(30, h - 50))
                        overlay_text(draw, (dx, dy), today, date_font, random.choice(COLORS), shadow=True)

                    # ================= Watermark =================
                    if logo_file:
                        if isinstance(logo_file, str):
                            logo = Image.open(logo_file).convert("RGBA")
                        else:
                            logo = Image.open(logo_file).convert("RGBA")
                        logo.thumbnail((int(w * 0.25), int(h * 0.25)))
                        image = place_logo_random(image, logo)

                    # ================= Save result =================
                    final_image = image.convert("RGB")
                    results.append((image_file.name, final_image))

                except Exception as e:
                    st.error(f"❌ Error Occurred: {str(e)}")

            st.success("✅ All images processed successfully!")

        for name, img in results:
            st.image(img, caption=name, use_container_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            renamed = f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg"
            st.download_button(
                label=f"⬇️ Download {renamed}",
                data=img_bytes.getvalue(),
                file_name=renamed,
                mime="image/jpeg"
            )

# =================== ZIP DOWNLOAD ===================
if results:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for _, img in results:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            zipf.writestr(f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg", img_bytes.getvalue())
    zip_buffer.seek(0)

    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer,
        file_name="Shivam_Images.zip",
        mime="application/zip"
    )
else:
    st.info("📂 Upload and generate images first to enable ZIP download.")
