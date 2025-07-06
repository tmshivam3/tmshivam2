import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import io
import random
import os

st.set_page_config(page_title="✨ GOOD VIBES TOOL", layout="centered")

# --- Style ---
st.markdown("""
    <style>
        body {
            background-color: #f8f3e6;
        }
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
            font-size: 54px;
            margin: 0;
            font-weight: bold;
            color: #fff700;
            text-shadow: 2px 2px #000;
        }
        .main-header p {
            font-size: 20px;
            margin-top: 8px;
            color: #ffe;
        }
        .section-title {
            color: #e67e22;
            font-weight: bold;
            font-size: 22px;
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #fa8231;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- Refresh Button ---
if st.button("🔄 Refresh / Reset"):
    st.experimental_rerun()

# --- Header ---
st.markdown("""
    <div class='main-header'>
        <h1>✨ GOOD VIBES ✨</h1>
        <p>Edit Your Photos in ONE Click – Premium & Stylish Watermark Generator</p>
    </div>
""", unsafe_allow_html=True)

# --- Upload Inputs ---
st.markdown("<div class='section-title'>📌 Upload your assets</div>", unsafe_allow_html=True)
logo_file = st.file_uploader("Upload your watermark/logo (PNG transparent recommended)", type=["png"])
font_files = st.file_uploader("Upload your custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("Upload your photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.markdown("<div class='section-title'>📝 Text Settings</div>", unsafe_allow_html=True)
mode = st.selectbox("Choose Greeting", ["Good Morning", "Good Night"])
extra_line_opt = st.checkbox("Add extra phrase below main text (e.g. Have a Nice Day / Sweet Dreams)")

# 👉 Main Text Size
text_size = st.slider("Main Text Size", min_value=80, max_value=200, value=130, step=5)
subtext_size = int(text_size * 0.4)

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

            # Load Logo
            logo = Image.open(logo_file).convert("RGBA")
            # Make logo smaller and subtler
            logo.thumbnail((80, 80))
            # Reduce opacity for subtle watermark
            alpha = logo.split()[3]
            alpha = alpha.point(lambda p: p * 0.4)
            logo.putalpha(alpha)

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # Font selection
                selected_font_stream = random.choice(available_fonts)
                if selected_font_stream:
                    selected_font_stream.seek(0)
                    try:
                        main_font = ImageFont.truetype(selected_font_stream, size=text_size)
                        sub_font = ImageFont.truetype(selected_font_stream, size=subtext_size)
                    except Exception:
                        main_font = ImageFont.load_default()
                        sub_font = ImageFont.load_default()
                else:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()

                # --- Texts
                main_text = mode
                sub_text = None
                if extra_line_opt:
                    if mode == "Good Morning":
                        sub_text = random.choice(["Have a Nice Day", "Have a Great Day"])
                    else:
                        sub_text = random.choice(["Sweet Dreams", "Sleep Well"])

                # --- Random Colors
                color_options = [
                    (255, random.randint(120,200), random.randint(50,150)),
                    (random.randint(120,255), 255, random.randint(50,150)),
                    (random.randint(100,255), random.randint(100,255), 255),
                    (255, 255, 255),
                    (random.randint(200,255), random.randint(150,200), random.randint(150,200))
                ]
                text_color = random.choice(color_options)
                shadow_color = "black"

                # --- Text Placement
                x = 30
                y_positions = [40, img.height // 2 - text_size//2, img.height - text_size - 80]
                y = random.choice(y_positions)

                # --- Draw Shadow
                for dx in [-3, 3]:
                    for dy in [-3, 3]:
                        draw.text((x + dx, y + dy), main_text, font=main_font, fill=shadow_color)

                # --- Draw Main Text
                draw.text((x, y), main_text, font=main_font, fill=text_color)

                # --- Subtext
                if sub_text:
                    sub_y = y + text_size + 10
                    draw.text((x + 10, sub_y), sub_text, font=sub_font, fill=(200, 200, 200))

                # --- Paste Logo
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                pos = (img_w - logo_w - 20, img_h - logo_h - 20)
                img.paste(logo, pos, mask=logo)

                output_images.append((img_file.name, img))

        # --- Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.success("✅ All photos ready!")

        # --- Previews
        st.markdown("<div class='section-title'>📸 Preview</div>", unsafe_allow_html=True)
        for name, image in output_images:
            st.image(image.resize((300, 400)), caption=name)

        # --- Download Options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📦 Download All (ZIP)", data=zip_buffer.getvalue(), file_name="GoodVibes_Images.zip", mime="application/zip")
        with col2:
            for name, img in output_images:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG")
                st.download_button(f"⬇️ {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")

        # --- Generate Again Button
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("✨ Generate Again"):
            st.experimental_rerun()

    else:
        st.warning("⚠️ Please upload your logo and at least one image to proceed.")
