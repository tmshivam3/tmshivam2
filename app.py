import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import io
import random
import os

st.set_page_config(page_title="✨ GOOD VIBES TOOL", layout="centered")

# --- Header / Branding ---
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #f5c71a, #fa8231);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            color: white;
            margin-bottom: 20px;
        }
        .main-header h1 {
            font-size: 48px;
            margin: 0;
            font-weight: bold;
        }
        .main-header p {
            font-size: 18px;
            margin-top: 8px;
        }
        .section-title {
            color: #f0932b;
            font-weight: bold;
            font-size: 20px;
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #f0932b;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
        }
    </style>
    <div class='main-header'>
        <h1>✨ GOOD VIBES ✨</h1>
        <p>Edit Photos in ONE Click. Premium & Stylish Watermark Creator</p>
    </div>
""", unsafe_allow_html=True)

# --- Upload Inputs ---
st.markdown("<div class='section-title'>📌 Upload your assets</div>", unsafe_allow_html=True)
logo_file = st.file_uploader("Watermark/logo (PNG transparent recommended)", type=["png"])
font_files = st.file_uploader("Custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("Photos to edit", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.markdown("<div class='section-title'>📝 Text Settings</div>", unsafe_allow_html=True)
mode = st.selectbox("Choose Main Greeting", ["Good Morning", "Good Night"])
extra_line_opt = st.checkbox("Add extra phrase below main text (e.g. Have a Nice Day / Sweet Dreams)")

# --- Crop Function ---
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

# --- Load Fonts ---
available_fonts = []
if font_files:
    for f in font_files:
        font_bytes = io.BytesIO(f.read())
        available_fonts.append(font_bytes)
else:
    try:
        with open("default/default.ttf", "rb") as f:
            default_font_bytes = io.BytesIO(f.read())
            available_fonts.append(default_font_bytes)
    except FileNotFoundError:
        available_fonts.append(None)

# --- Process Images ---
output_images = []

if st.button("✅ Generate Edited Images"):
    if uploaded_images and logo_file:
        with st.spinner("Processing your photos..."):

            # Prepare logo
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((70, 70))  # Smaller, subtler watermark

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # Randomly pick font
                selected_font_stream = random.choice(available_fonts)
                if selected_font_stream:
                    selected_font_stream.seek(0)
                    try:
                        main_font = ImageFont.truetype(selected_font_stream, size=80)   # Bolder main text
                        sub_font = ImageFont.truetype(selected_font_stream, size=30)    # Smaller sub text
                    except Exception:
                        main_font = ImageFont.load_default()
                        sub_font = ImageFont.load_default()
                else:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()

                # Decide main and sub text
                main_text = mode
                sub_text = None
                if extra_line_opt:
                    if mode == "Good Morning":
                        sub_text = random.choice(["Have a Nice Day", "Have a Great Day"])
                    else:
                        sub_text = random.choice(["Sweet Dreams", "Sleep Well"])

                # Random vibrant color for main text
                text_color = tuple(random.randint(120, 255) for _ in range(3))
                shadow_color = "black"

                x = 30
                y_positions = [30, img.height // 2 - 50, img.height - 200]
                y = random.choice(y_positions)

                # Shadow for main
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x + dx, y + dy), main_text, font=main_font, fill=shadow_color)

                draw.text((x, y), main_text, font=main_font, fill=text_color)

                # Subtext smaller and subtle
                if sub_text:
                    sub_y = y + 85
                    draw.text((x + 10, sub_y), sub_text, font=sub_font, fill=(180, 180, 180))

                # Watermark logo (bottom right)
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                pos = (img_w - logo_w - 15, img_h - logo_h - 15)
                img.paste(logo, pos, mask=logo)

                output_images.append((img_file.name, img))

        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.success("✅ All photos ready!")

        # Previews
        st.markdown("<div class='section-title'>📸 Preview</div>", unsafe_allow_html=True)
        for name, image in output_images:
            st.image(image.resize((300, 400)), caption=name)

        # Download Options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📦 Download All (ZIP)", data=zip_buffer.getvalue(), file_name="GoodVibes_Images.zip", mime="application/zip")
        with col2:
            for name, img in output_images:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG")
                st.download_button(f"⬇️ {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")
    else:
        st.warning("⚠️ Please upload your logo and at least one image to proceed.")

