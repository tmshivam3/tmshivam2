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

    # Main Overlays Side by Side
    target_main_h = int(ih * main_scale)
    main_resized = []
    for overlay, role, num in main_overlays:
        ow, oh = overlay.size
        new_h = target_main_h
        new_w = int(ow * new_h / oh)
        main_resized.append((overlay.resize((new_w, new_h), Image.LANCZOS), new_w, new_h))

    total_main_width = sum(w for _, w, _ in main_resized) + (len(main_resized) - 1) * 20
    start_x = (iw - total_main_width) // 2

    # Choose Top or Bottom
    if random.choice([True, False]):
        current_y = y_padding
    else:
        current_y = ih - target_main_h - len(wish_overlays) * int(ih * wish_scale) - 2 * y_padding

    # Paste main overlays side by side
    x_pos = start_x
    for overlay_img, ow, oh in main_resized:
        img.paste(overlay_img, (x_pos, current_y), overlay_img)
        x_pos += ow + 20
    current_y += target_main_h + y_padding

    # Wishes Overlays
    for overlay, role, num in wish_overlays:
        ow, oh = overlay.size
        new_h = int(ih * wish_scale)
        new_w = int(ow * new_h / oh)
        overlay_resized = overlay.resize((new_w, new_h), Image.LANCZOS)

        px = (iw - new_w) // 2
        img.paste(overlay_resized, (px, current_y), overlay_resized)
        current_y += new_h + y_padding

    return img

# ========== SIDEBAR ==========
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
def_wish = random.choice(MORNING_WISHES if greeting_type == "Good Morning" else NIGHT_WISHES)
custom_wish = st.sidebar.text_input("Wishes Text (optional)", value="")

use_png_overlay = st.sidebar.checkbox("🖼️ Use PNG Overlay Wishes Instead of Text")
if use_png_overlay:
    overlay_main_scale = st.sidebar.slider("Main Overlay Size (%)", 10, 100, 40)
    overlay_wish_scale = st.sidebar.slider("Wishes Overlay Size (%)", 10, 100, 30)

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

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

results = []

# ========== MAIN ==========
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Processing images... Please wait."):
            status_text = st.empty()

            # Handle font selection
            if uploaded_font is not None:
                font_bytes = io.BytesIO(uploaded_font.read())
                font_path = font_bytes
            else:
                font_path = os.path.join("assets/fonts", font_file)

            # Handle logo selection
            if uploaded_logo is not None:
                logo = Image.open(uploaded_logo).convert("RGBA")
            else:
                logo_path = os.path.join("assets/logos", logo_file)
                logo = Image.open(logo_path).convert("RGBA")

            for idx, image_file in enumerate(uploaded_images, start=1):
                try:
                    status_text.markdown(f"🔧 Processing **{image_file.name}** ({idx}/{len(uploaded_images)})...")
                    time.sleep(0.2)

                    image = Image.open(image_file).convert("RGBA")
                    image = crop_to_3_4(image)
                    w, h = image.size

                    if use_png_overlay:
                        processed = overlay_png_random(image.copy(), greeting_type, overlay_main_scale, overlay_wish_scale)
                        if processed is None:
                            st.markdown("<h4 style='color: yellow;'>⚠ PNG Wishes Coming Soon!</h4>", unsafe_allow_html=True)
                            continue
                        image = processed
                    else:
                        normalized = coverage_percent / 100
                        scale_factor = (normalized ** 2.5) * 2.8
                        area = scale_factor * w * h
                        main_font_size = max(30, int(area ** 0.5))
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

                    logo.thumbnail((int(w * 0.25), int(h * 0.25)))
                    image = place_logo_random(image, logo)

                    final = image.convert("RGB")
                    results.append((image_file.name, final))

                except Exception as e:
                    st.error(f"❌ Error Occurred: {str(e)}")

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

    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer,
        file_name="Shivam_Images.zip",
        mime="application/zip"
    )
else:
    st.info("📂 Upload and generate images first to enable ZIP download.")
