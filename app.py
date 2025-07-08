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

    # ✅ Fixed watermark opacity to 100%
    watermark = logo.copy()
    watermark = ImageEnhance.Brightness(watermark).enhance(1.0)
    img.paste(watermark, (x, y), watermark)
    return img

def overlay_png_random(img, greeting_type):
    base_folder = f"assets/overlays/{greeting_type.lower().replace(' ', '')}"
    if not os.path.exists(base_folder): return None
    png_files = list_files(base_folder, ['.png'])
    if not png_files: return None

    for png_name in random.sample(png_files, min(3, len(png_files))):
        try:
            overlay = Image.open(os.path.join(base_folder, png_name)).convert("RGBA")
            ow, oh = overlay.size
            iw, ih = img.size
            scale = random.uniform(0.2, 0.4)
            overlay = overlay.resize((int(iw * scale), int(oh * scale)))
            px = safe_randint(30, iw - overlay.width - 30)
            py = safe_randint(30, ih - overlay.height - 30)
            img.paste(overlay, (px, py), overlay)
        except:
            continue
    return img

# ========== SIDEBAR ==========
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
def_wish = random.choice(MORNING_WISHES if greeting_type == "Good Morning" else NIGHT_WISHES)
custom_wish = st.sidebar.text_input("Wishes Text (optional)", value="")
use_png_overlay = st.sidebar.checkbox("🖼️ Use PNG Overlay Wishes Instead of Text")
show_wish_text = st.sidebar.checkbox("Show Wishes Text", value=True)
coverage_slider = st.sidebar.slider("Main Text Coverage (%)", 1, 100, 30)
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
date_size_factor = st.sidebar.slider("Date Text Size (%)", 30, 120, 70)

available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
font_file = st.sidebar.selectbox("Choose Font", available_fonts)

available_logos = list_files("assets/logos", [".png"])
logo_file = st.sidebar.selectbox("Choose Watermark Logo", available_logos)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

results = []

# ========== MAIN ==========
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Processing images... Please wait."):
            status_text = st.empty()
            logo_path = os.path.join("assets/logos", logo_file)
            font_path = os.path.join("assets/fonts", font_file)

            for idx, image_file in enumerate(uploaded_images, start=1):
                try:
                    status_text.markdown(f"🔧 Processing **{image_file.name}** ({idx}/{len(uploaded_images)})...")
                    time.sleep(0.2)

                    image = Image.open(image_file).convert("RGBA")
                    image = crop_to_3_4(image)
                    w, h = image.size

                    if use_png_overlay:
                        processed = overlay_png_random(image.copy(), greeting_type)
                        if processed is None:
                            st.markdown("<h4 style='color: yellow;'>⚠ PNG Wishes Coming Soon!</h4>", unsafe_allow_html=True)
                            continue
                        image = processed
                    else:
                        scaled_coverage = coverage_slider * 0.00167
                        area = (scaled_coverage) * w * h
                        main_font_size = max(30, int(area ** 0.5 * 0.6))
                        sub_font_size = int(main_font_size * 0.5)
                        date_font_size = int(main_font_size * date_size_factor / 100)

                        main_font = ImageFont.truetype(font_path, main_font_size)
                        sub_font = ImageFont.truetype(font_path, sub_font_size)
                        date_font = ImageFont.truetype(font_path, date_font_size)

                        draw = ImageDraw.Draw(image)
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

                    logo = Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((int(w * 0.25), int(h * 0.25)))
                    image = place_logo_random(image, logo)

                    final = image.convert("RGB")
                    renamed = f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')[:-3]}.jpg"
                    img_bytes = io.BytesIO()
                    final.save(img_bytes, format="JPEG", quality=95, dpi=(300, 300), optimize=True)
                    results.append((renamed, img_bytes.getvalue()))

                except Exception as e:
                    st.error(f"❌ Error Occurred: {str(e)}")

            status_text.success("✅ All images processed successfully!")

        for name, img_data in results:
            st.image(Image.open(io.BytesIO(img_data)), caption=name, use_container_width=True)
            st.download_button(
                label=f"⬇️ Download {name}",
                data=img_data,
                file_name=name,
                mime="image/jpeg"
            )

# ========== ZIP DOWNLOAD ==========
if results:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for name, img_data in results:
            zipf.writestr(name, img_data)
    zip_buffer.seek(0)

    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer,
        file_name="Shivam_Images.zip",
        mime="application/zip"
    )
else:
    st.info("📂 Upload and generate images first to enable ZIP download.")
