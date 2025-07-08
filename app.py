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
    <h1 style='text-align: center; color: white; background-color: black; padding: 12px; border-radius: 8px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h5 style='text-align: center; color: grey;'>Apply Greetings, Watermarks, Fonts, Wishes & More</h5>
""", unsafe_allow_html=True)

# ========== UTILS ==========
def list_files(folder, exts):
    if not os.path.exists(folder): return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def list_theme_folders(folder):
    if not os.path.exists(folder): return []
    return sorted([f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))], reverse=True)

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

def overlay_text(draw, position, text, font, fill, shadow=False):
    x, y = position
    if shadow:
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
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

def overlay_theme_images(img, theme_folder):
    base_folder = os.path.join("assets/overlays", theme_folder)
    for num in [1, 2, 3, 4, 5]:
        path = os.path.join(base_folder, f"{num}.png")
        if os.path.exists(path):
            try:
                overlay = Image.open(path).convert("RGBA")
                ow, oh = overlay.size
                scale = random.uniform(0.2, 0.4)
                iw, ih = img.size
                new_size = (int(iw * scale), int(oh * scale * (ow/oh)))
                overlay = overlay.resize(new_size, Image.LANCZOS)
                x = safe_randint(20, iw - overlay.width - 20)
                y = safe_randint(20, ih - overlay.height - 20)
                img.paste(overlay, (x, y), overlay)
            except Exception as e:
                print(f"Overlay error: {e}")
    return img

# ========== CONSTANTS ==========
MORNING_WISHES = ["Have a great day!", "Start your day with a smile", "Enjoy your coffee!", "Fresh start today!", "Make today beautiful", "Positive vibes only"]
NIGHT_WISHES = ["Sweet dreams", "Good night, sleep tight", "Peaceful rest ahead", "Relax and unwind", "Nighty night!", "Sleep peacefully"]
COLORS = [(255, 255, 0), (255, 0, 0), (255, 255, 255), (255, 192, 203), (0, 255, 0), (255, 165, 0), (173, 216, 230), (128, 0, 128), (255, 105, 180)]

# ========== SIDEBAR ==========
st.sidebar.header("🛠️ Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
def_wish = random.choice(MORNING_WISHES if greeting_type == "Good Morning" else NIGHT_WISHES)
custom_wish = st.sidebar.text_input("Wishes Text", value="")

show_wish_text = st.sidebar.checkbox("Show Wishes", value=True)
coverage_percent_user = st.sidebar.slider("Main Text Coverage (%)", 1, 100, 25)
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
date_size_factor = st.sidebar.slider("Date Size (%)", 30, 120, 70)

available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
use_own_font = st.sidebar.checkbox("Use Own Font")
if use_own_font:
    uploaded_font = st.sidebar.file_uploader("Upload Your Font", type=["ttf", "otf"])
else:
    font_file = st.sidebar.selectbox("Choose Font", available_fonts)

available_logos = list_files("assets/logos", [".png"])
use_own_logo = st.sidebar.checkbox("Use Own Watermark")
if use_own_logo:
    uploaded_logo = st.sidebar.file_uploader("Upload Your Watermark", type=["png"])
else:
    logo_file = st.sidebar.selectbox("Choose Watermark", available_logos)

# Overlay theme
themes_list = list_theme_folders("assets/overlays")
theme_options = ["Auto Select"] + themes_list
selected_theme = st.sidebar.selectbox("Overlay Theme", theme_options)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ========== MAIN ==========
results = []
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Processing images... Please wait."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            total = len(uploaded_images)
            for idx, image_file in enumerate(uploaded_images, start=1):
                try:
                    status_text.markdown(f"Processing **{image_file.name}** ({idx}/{total})")
                    time.sleep(0.2)

                    img = Image.open(image_file).convert("RGBA")
                    img = crop_to_3_4(img)
                    w, h = img.size

                    # --- Coverage scaling
                    normalized = (coverage_percent_user / 100) * 0.2
                    scale_factor = (normalized ** 2.5) * 2.8
                    area = scale_factor * w * h
                    main_font_size = max(30, int(area ** 0.5))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    # --- Font
                    if use_own_font and uploaded_font:
                        font_bytes = io.BytesIO(uploaded_font.read())
                        main_font = ImageFont.truetype(font_bytes, main_font_size)
                        sub_font = ImageFont.truetype(font_bytes, sub_font_size)
                        date_font = ImageFont.truetype(font_bytes, date_font_size)
                    else:
                        font_path = os.path.join("assets/fonts", font_file)
                        main_font = ImageFont.truetype(font_path, main_font_size)
                        sub_font = ImageFont.truetype(font_path, sub_font_size)
                        date_font = ImageFont.truetype(font_path, date_font_size)

                    # --- Draw text
                    draw = ImageDraw.Draw(img)
                    color = random.choice(COLORS)
                    wish_text = custom_wish.strip() or def_wish
                    x = safe_randint(30, w - main_font_size * len(greeting_type) // 2 - 30)
                    y = safe_randint(30, h - main_font_size - 30)
                    overlay_text(draw, (x, y), greeting_type, main_font, color, shadow=True)
                    if show_wish_text:
                        overlay_text(draw, (x + 10, y + main_font_size + 10), wish_text, sub_font, color, shadow=True)
                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        dx = safe_randint(30, w - 200)
                        dy = safe_randint(30, h - 50)
                        overlay_text(draw, (dx, dy), today, date_font, random.choice(COLORS), shadow=True)

                    # --- Overlay theme
                    if selected_theme != "Auto Select":
                        img = overlay_theme_images(img, selected_theme)

                    # --- Logo
                    if use_own_logo and uploaded_logo:
                        watermark = Image.open(uploaded_logo).convert("RGBA")
                    else:
                        logo_path = os.path.join("assets/logos", logo_file)
                        watermark = Image.open(logo_path).convert("RGBA")
                    watermark.thumbnail((int(w * 0.25), int(h * 0.25)))
                    img = place_logo_random(img, watermark)

                    final = img.convert("RGB")
                    results.append((image_file.name, final))
                    progress_bar.progress(idx / total)

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            progress_bar.empty()
            status_text.success("✅ All images processed successfully!")

        for name, img in results:
            st.image(img, caption=name, use_container_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=100, optimize=True)
            renamed = f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg"
            st.download_button(
                label=f"⬇️ Download {renamed}",
                data=img_bytes.getvalue(),
                file_name=renamed,
                mime="image/jpeg"
            )

# ========== ZIP DOWNLOAD ==========
if results:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for _, img in results:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=100, optimize=True)
            zipf.writestr(f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg", img_bytes.getvalue())
    zip_buffer.seek(0)
    st.download_button("📦 Download All as ZIP", data=zip_buffer, file_name="Shivam_Images.zip", mime="application/zip")
else:
    st.info("📂 Upload and generate images first to enable ZIP download.")
