import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# ----------------- Page Config -------------------
st.set_page_config(page_title="✨ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🌟 EDIT PHOTO IN BULK TOOL ™ 🌟</h1>
    <h4 style='text-align: center; color: grey;'>Create beautiful morning/night wishes in one click!</h4>
""", unsafe_allow_html=True)

# ----------------- Utility Functions -------------------
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img

def safe_randint(a, b):
    return a if a >= b else random.randint(a, b)

# ----------------- Load Resources -------------------
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

morning_wishes = [
    "Have a great day!",
    "Start fresh!",
    "Shine bright!",
    "Wishing you joy!",
    "Make it amazing!",
    "Rise & shine!",
    "Embrace the light!",
    "Spread positivity!"
]

goodnight_wishes = [
    "Sweet dreams!",
    "Good night dear!",
    "Sleep well!",
    "Rest your soul!",
    "Peaceful night!",
    "Dream big!",
    "Stars watching!",
    "Silent night!"
]

# ----------------- Sidebar -------------------
st.sidebar.header("🎨 Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])

use_custom_wish = st.sidebar.checkbox("Use Custom Wishes", value=False)

if use_custom_wish:
    user_subtext = st.sidebar.text_input("Custom Wish Text", "Stay Blessed!")
else:
    user_subtext = None

show_date = st.sidebar.checkbox("Add Date", value=True)
date_size_factor = st.sidebar.slider("Date Size %", 30, 120, 70)
coverage_percent = st.sidebar.slider("Text Coverage %", 3, 20, 8)

# Fonts
st.sidebar.subheader("Fonts")
font_source = st.sidebar.radio("Font Source", ["Available Fonts", "Upload Font"])
selected_font = None
uploaded_font = None
if font_source == "Available Fonts":
    selected_font = st.sidebar.selectbox("Select Font", available_fonts)
else:
    uploaded_font = st.sidebar.file_uploader("Upload Font", type=["ttf", "otf"])

# Watermark
logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Upload Custom Logo"])
logo_path = None
if logo_choice == "Upload Custom Logo":
    logo_path = st.sidebar.file_uploader("Upload PNG Logo", type=["png"])
else:
    logo_path = os.path.join("assets/logos", logo_choice)

# Variations
generate_variations = st.sidebar.checkbox("Generate 4 Variants Per Image", value=True)

# ----------------- Upload Images -------------------
uploaded_images = st.file_uploader("Upload Your Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for name, variants in images:
            for i, variant in enumerate(variants):
                img_bytes = io.BytesIO()
                variant.save(img_bytes, format="PNG")
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                zipf.writestr(f"Picsart_{timestamp}.png", img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# ----------------- Generation Button -------------------
if st.button("✅ Generate Images"):
    if uploaded_images:
        results = []
        for img_file in uploaded_images:
            try:
                image = Image.open(img_file).convert("RGB")
                base_img = crop_to_3_4(image)

                logo = None
                if logo_path:
                    logo = Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((200, 200))

                if uploaded_font:
                    font_bytes = io.BytesIO(uploaded_font.read())
                elif selected_font:
                    font_bytes = os.path.join("assets/fonts", selected_font)
                else:
                    font_bytes = "assets/fonts/roboto.ttf"

                def draw_variant(base_img, seed=None):
                    random.seed(seed)
                    img = base_img.copy()
                    draw = ImageDraw.Draw(img)

                    w, h = img.size
                    area = (coverage_percent / 100) * w * h
                    main_size = max(30, int(area**0.5 * 0.6))
                    sub_size = int(main_size * 0.5)
                    date_size = int(main_size * date_size_factor / 100)

                    font = ImageFont.truetype(font_bytes, size=main_size)
                    sub_font = ImageFont.truetype(font_bytes, size=sub_size)
                    date_font = ImageFont.truetype(font_bytes, size=date_size)

                    colors = [(255,255,255),(255,255,0),(255,192,203),(0,255,255),(0,255,0),(255,128,0)]
                    text_color = random.choice(colors)

                    pos_x = safe_randint(30, max(31, w - main_size * len(greeting_type)//2))
                    pos_y = safe_randint(int(h*0.35), int(h*0.85))

                    # Shadow
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((pos_x+dx, pos_y+dy), greeting_type, font=font, fill="black")
                    draw.text((pos_x, pos_y), greeting_type, font=font, fill=text_color)

                    # Subtext
                    wish = user_subtext or random.choice(morning_wishes if greeting_type == "Good Morning" else goodnight_wishes)
                    draw.text((pos_x+10, pos_y + main_size + 10), wish, font=sub_font, fill=text_color)

                    # Date
                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        dx = safe_randint(20, max(21, w - 200))
                        dy = safe_randint(20, max(21, h - 100))
                        draw.text((dx, dy), today, font=date_font, fill=random.choice(colors))

                    # Logo
                    if logo:
                        img.paste(logo, (w - logo.width - 10, h - logo.height - 10), logo)

                    return img

                variants = [draw_variant(base_img, seed=i) for i in range(4)] if generate_variations else [draw_variant(base_img)]
                results.append((img_file.name, variants))

            except Exception as e:
                st.error(f"Error Occurred: {e}")

        # ----------------- Show Results -------------------
        for name, variants in results:
            for i, var in enumerate(variants):
                st.image(var, caption=f"{name} - Variant {i+1}", use_column_width=True)
                buffer = io.BytesIO()
                var.save(buffer, format="PNG")
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                st.download_button("Download Image", buffer.getvalue(), file_name=f"Picsart_{timestamp}.png", mime="image/png")

        if st.button("⬇️ Download All As ZIP"):
            zip_file = create_zip(results)
            st.download_button("Download ZIP", zip_file, file_name="Bulk_Images.zip", mime="application/zip")

    else:
        st.warning("🚨 Please upload images first.")
