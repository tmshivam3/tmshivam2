# app.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🔆 SHIVAM TOOL 🔆</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning Watermark Generator</h4>
""", unsafe_allow_html=True)

logo_file = st.file_uploader("📌 Upload your watermark/logo (PNG recommended)", type=["png"])
font_files = st.file_uploader("🔠 Upload custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("🖼️ Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

output_images = []

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

if st.button("✅ Generate Edited Images"):
    if uploaded_images and logo_file and font_files:
        with st.spinner("Processing..."):

            # Load logo
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((150, 150))

            # Load fonts
            fonts = []
            for f in font_files:
                font_bytes = io.BytesIO(f.read())
                fonts.append(font_bytes)

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)

                draw = ImageDraw.Draw(img)

                # Select random font and size
                font_stream = random.choice(fonts)
                font_stream.seek(0)
                font = ImageFont.truetype(font_stream, size=70)

                # Random color or texture color (average from image)
                avg_color = tuple(map(lambda x: int(x), img.resize((1,1)).getpixel((0,0))))
                text_color = tuple(random.randint(100, 255) for _ in range(3))

                # Text with outline + shadow
                text = "Good Morning"
                x, y = 30, 30
                shadow_color = "black"

                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), text, font=font, fill=shadow_color)

                draw.text((x, y), text, font=font, fill=text_color)

                # Paste logo at bottom-right
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                img.paste(logo, (img_w - logo_w - 10, img_h - logo_h - 10), mask=logo)

                output_images.append((img_file.name, img))

        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.success("✅ All images processed successfully!")
        st.download_button("📦 Download ZIP", data=zip_buffer.getvalue(), file_name="GoodMorning_Images.zip", mime="application/zip")
    else:
        st.warning("⚠️ Please upload logo, fonts, and images before clicking Generate.")
