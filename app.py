import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random
import io
import datetime

# PAGE SETTINGS
st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🔆 EDIT PHOTO IN ONE CLICK 🔆</h1>
""", unsafe_allow_html=True)

# SAFELY LIST FILES
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

# PERMANENT ASSETS
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# SIDEBAR
st.sidebar.header("🛠️ Customization Panel")

# Greeting Type
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])

# Subtext
default_subtext = "Sweet Dreams" if greeting_type == "Good Night" else random.choice(["Have a Nice Day", "Have a Great Day"])
user_subtext = st.sidebar.text_input("Wishes Text", default_subtext)

# Coverage Slider
coverage_percent = st.sidebar.slider("Main Text Coverage %", 5, 100, 20)

# Font Choice
if available_fonts:
    st.sidebar.markdown("### Font Selection")
    font_choice_mode = st.sidebar.radio("Font Source", ["Available Fonts", "Upload Your Own"], horizontal=True)

    if font_choice_mode == "Available Fonts":
        font_choice = st.sidebar.selectbox("Select Available Font", available_fonts)
        uploaded_font_file = None
    else:
        uploaded_font_file = st.sidebar.file_uploader("Upload Font (.ttf/.otf)", type=["ttf", "otf"])
        font_choice = None
else:
    st.sidebar.warning("⚠️ No fonts found in assets/fonts")
    font_choice = None
    uploaded_font_file = None

# Logo Choice
if available_logos:
    st.sidebar.markdown("### Watermark Logo")
    logo_choice_mode = st.sidebar.radio("Logo Source", ["Available Logos", "Upload Your Own"], horizontal=True)

    if logo_choice_mode == "Available Logos":
        logo_choice = st.sidebar.selectbox("Select Logo", available_logos)
        uploaded_logo_file = None
    else:
        uploaded_logo_file = st.sidebar.file_uploader("Upload Logo (.png)", type=["png"])
        logo_choice = None
else:
    st.sidebar.warning("⚠️ No logos found in assets/logos")
    logo_choice = None
    uploaded_logo_file = None

# Add Date Toggle
add_date_option = st.sidebar.checkbox("Add Today's Date", value=False)

# Image Upload
uploaded_images = st.file_uploader("🖼️ Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

output_images = []

# Helper Crop
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

# GENERATE BUTTON
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("Processing..."):
            # Load Logo
            logo = None
            if uploaded_logo_file:
                logo = Image.open(uploaded_logo_file).convert("RGBA")
                logo.thumbnail((150, 150))
            elif logo_choice:
                logo_path = os.path.join("assets/logos", logo_choice)
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            # Load Font
            font_bytes = None
            if uploaded_font_file:
                font_bytes = io.BytesIO(uploaded_font_file.read())
            elif font_choice:
                font_path = os.path.join("assets/fonts", font_choice)
                font_bytes = open(font_path, "rb")

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)
                img_w, img_h = img.size

                # Slow scale mapping
                scale_factor = 0.02 + 0.18 * (coverage_percent / 100)
                main_text_area = scale_factor * img_w * img_h
                main_font_size = max(12, int(main_text_area ** 0.5))
                sub_font_size = max(10, int(main_font_size * 0.6))
                date_font_size = max(10, int(main_font_size * 0.8))

                # Load Fonts
                if font_bytes:
                    font_bytes.seek(0)
                    main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                    font_bytes.seek(0)
                    sub_font = ImageFont.truetype(font_bytes, size=sub_font_size)
                    font_bytes.seek(0)
                    date_font = ImageFont.truetype(font_bytes, size=date_font_size)
                else:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()
                    date_font = ImageFont.load_default()

                # Randomized Positioning
                try:
                    x = random.randint(30, max(30, img_w - main_font_size * len(greeting_type) // 2 - 30))
                    y = random.randint(30, max(30, img_h - main_font_size - 30))
                except ValueError:
                    x, y = 30, 30

                # Colors Focus
                preferred_colors = [(255,255,0), (255,0,0), (255,255,255), (255,192,203), (0,255,0)]
                if random.random() < 0.8:
                    text_color = random.choice(preferred_colors)
                else:
                    text_color = tuple(random.randint(150, 255) for _ in range(3))
                shadow_color = "black"

                # Draw Main Text with Shadow
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # Draw Subtext
                sub_x = x + random.randint(-20, 20)
                sub_y = y + main_font_size + 10
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # Add Date
                if add_date_option:
                    date_text = datetime.datetime.now().strftime("%d %B %Y")
                    try:
                        date_x = random.randint(30, max(30, img_w - date_font_size * len(date_text) // 2 - 30))
                        date_y = random.randint(30, max(30, img_h - date_font_size - 30))
                    except ValueError:
                        date_x, date_y = 30, 30
                    draw.text((date_x, date_y), date_text, font=date_font, fill=text_color)

                # Paste Logo
                if logo:
                    img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                output_images.append((img_file.name, img))

        st.success("✅ Images processed successfully!")
        for name, img in output_images:
            st.image(img, caption=name, use_column_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)
            st.download_button(f"⬇️ Download {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")
    else:
        st.warning("⚠️ Please upload images before clicking Generate.")
