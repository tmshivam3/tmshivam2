import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

# 🔹 Page Config
st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

# 🌟 Header Design
st.markdown("""
    <div style='background: linear-gradient(135deg, #ffcc00, #ff6600); padding: 20px; border-radius: 10px;'>
        <h1 style='text-align: center; color: white;'>✨ SHIVAM TOOL ✨</h1>
        <p style='text-align: center; color: white;'>EDIT PHOTO IN ONE CLICK</p>
    </div>
""", unsafe_allow_html=True)

# 🔹 Uploads
logo_file = st.file_uploader("📌 Upload your watermark/logo (PNG with transparent background preferred)", type=["png"])
font_files = st.file_uploader("🌐 Upload custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("🖼️ Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# 🔹 Text Options
mode = st.selectbox("🌄 What do you want to write on photos?", ["Good Morning", "Good Night"])
extra_line = st.checkbox("Include extra text (like 'Have a Nice Day' or 'Sweet Dreams')?")

output_images = []

# ✅ Function: Crop to 3:4 ratio
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

# ✅ Function: Load Default Font
DEFAULT_FONT_PATH = "default/default.ttf"
available_fonts = []
font_names = []

# Load custom fonts or fallback
if font_files:
    for f in font_files:
        font_bytes = io.BytesIO(f.read())
        available_fonts.append(font_bytes)
        font_names.append(f.name)
else:
    try:
        with open(DEFAULT_FONT_PATH, "rb") as f:
            default_font_bytes = io.BytesIO(f.read())
            available_fonts.append(default_font_bytes)
            font_names.append("Default Font")
    except:
        st.warning("Default font not found. Using PIL default.")
        available_fonts.append(None)
        font_names.append("System Default")

# ✅ Button: Generate Images
if st.button("✅ Generate Edited Images"):
    if uploaded_images and logo_file:
        with st.spinner("Processing images..."):

            # Load logo
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((100, 100))

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)

                draw = ImageDraw.Draw(img)

                # Choose font
                font_stream = random.choice(available_fonts)
                if font_stream is None:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()
                else:
                    font_stream.seek(0)
                    main_font = ImageFont.truetype(font_stream, size=70)
                    sub_font = ImageFont.truetype(font_stream, size=30)

                # Generate Text
                main_text = mode
                if extra_line:
                    if mode == "Good Morning":
                        sub_text = random.choice(["Have a Nice Day", "Have a Great Day"])
                    else:
                        sub_text = random.choice(["Sweet Dreams", "Sleep Well"])
                else:
                    sub_text = None

                # Text Colors & Shadow
                text_color = tuple(random.randint(100, 255) for _ in range(3))
                shadow_color = "black"
                x, y = 30, random.choice([20, img.height - 150])

                # Draw main text with shadow
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), main_text, font=main_font, fill=shadow_color)
                draw.text((x, y), main_text, font=main_font, fill=text_color)

                # Draw sub text
                if sub_text:
                    draw.text((x+10, y+75), sub_text, font=sub_font, fill=(180,180,180))

                # Add logo (bottom-right)
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                logo_pos = (img_w - logo_w - 15, img_h - logo_h - 15)
                img.paste(logo, logo_pos, mask=logo)

                output_images.append((img_file.name, img))

        # ✅ ZIP Download
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.success("✅ All images ready!")

        # Preview + Download Options
        for name, image in output_images:
            st.image(image.resize((300, 400)), caption=name)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📁 Download ZIP", data=zip_buffer.getvalue(), file_name="Edited_Images.zip", mime="application/zip")
        with col2:
            for name, img in output_images:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG")
                st.download_button(f"🔄 {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")

    else:
        st.warning("⚠️ Please upload logo and at least one image.")
