import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

# ------------ Settings ------------
DEFAULT_FONT_PATH = "default/default.ttf"
WATERMARK_OPACITY = 40
WATERMARK_SIZE_FACTOR = 0.15  # Smaller watermark

st.set_page_config(
    page_title="🌟 GOOD VIBES - Edit Photo in One Click",
    layout="wide",
    page_icon="✨"
)

# ------------ CSS Styling ------------
st.markdown("""
    <style>
    body {
        background-color: #f6f6f6;
    }
    .big-header {
        background: linear-gradient(90deg, #f9d423, #ff4e50);
        color: white;
        text-align: center;
        padding: 20px;
        font-size: 36px;
        border-radius: 10px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 18px;
        margin-bottom: 20px;
    }
    .footer-note {
        text-align: center;
        color: #999;
        font-size: 14px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------ Header ------------
st.markdown("<div class='big-header'>🌟 GOOD VIBES PHOTO EDITOR 🌟</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Edit photo in ONE click - Premium, Stylish, Personalized</div>", unsafe_allow_html=True)

# ------------ Uploaders ------------
col1, col2 = st.columns(2)

with col1:
    logo_file = st.file_uploader("📌 Upload your watermark/logo (PNG recommended)", type=["png"])
    uploaded_images = st.file_uploader("🖼️ Upload photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

with col2:
    font_files = st.file_uploader("🔠 Upload custom fonts (.ttf/.otf) (Optional)", type=["ttf", "otf"], accept_multiple_files=True)

# ------------ Text Options ------------
st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    main_text_choice = st.selectbox("🎯 Choose Main Greeting:", ["Good Morning", "Good Night"])
    add_extra_line = st.checkbox("✨ Add extra message (Have a Nice Day / Sweet Dreams)")

with col4:
    if main_text_choice == "Good Morning":
        extra_options = ["Have a Nice Day", "Have a Great Day"]
    else:
        extra_options = ["Sweet Dreams", "Sleep Well"]
    extra_text = st.selectbox("✅ Choose extra line:", extra_options) if add_extra_line else ""

# ------------ Helper Functions ------------
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

def apply_watermark(base_img, watermark):
    base_img = base_img.convert("RGBA")
    watermark = watermark.convert("RGBA")
    watermark.putalpha(WATERMARK_OPACITY)
    wm_w, wm_h = watermark.size
    new_size = (int(wm_w * WATERMARK_SIZE_FACTOR), int(wm_h * WATERMARK_SIZE_FACTOR))
    watermark = watermark.resize(new_size, Image.ANTIALIAS)
    pos = (base_img.width - watermark.width - 10, base_img.height - watermark.height - 10)
    base_img.alpha_composite(watermark, dest=pos)
    return base_img.convert("RGB")

def random_color():
    return tuple(random.randint(100, 255) for _ in range(3))

def random_multicolor():
    return [random_color() for _ in range(random.randint(2, 5))]

def get_font_from_file(font_file, size):
    try:
        return ImageFont.truetype(font_file, size)
    except Exception:
        return None

# ------------ Font Handling ------------
available_fonts = []
font_names = []

if font_files:
    for f in font_files:
        font_bytes = io.BytesIO(f.read())
        available_fonts.append(font_bytes)
        font_names.append(f.name)
else:
    # Default font
    try:
        with open(DEFAULT_FONT_PATH, "rb") as f:
            default_font_bytes = io.BytesIO(f.read())
            available_fonts.append(default_font_bytes)
            font_names.append("Default Font")
    except FileNotFoundError:
        st.warning("⚠️ Default font not found. Please upload at least one font.")

# ------------ Generate Images Button ------------
st.markdown("---")
if st.button("✅ Generate Edited Images"):

    if not uploaded_images or not logo_file or not available_fonts:
        st.warning("⚠️ Please upload images, watermark, and at least one font (or add default.ttf).")
    else:
        with st.spinner("Processing your images..."):

            logo_image = Image.open(logo_file).convert("RGBA")

            result_images = []
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as zipf:

                for img_file in uploaded_images:
                    img = Image.open(img_file).convert("RGB")
                    img = crop_to_3_4(img)
                    img_w, img_h = img.size

                    # Watermark
                    final_img = apply_watermark(img, logo_image)

                    # Draw text
                    draw = ImageDraw.Draw(final_img)
                    font_stream = random.choice(available_fonts)
                    font_stream.seek(0)
                    main_font = get_font_from_file(font_stream, size=70)
                    if not main_font:
                        continue

                    # Random position
                    y_positions = [int(img_h * 0.1), int(img_h * 0.3), int(img_h * 0.6)]
                    text_y = random.choice(y_positions)

                    # Colors
                    if random.random() < 0.5:
                        text_color = random_color()
                    else:
                        text_color = tuple(map(lambda x: int(x), img.resize((1, 1)).getpixel((0, 0))))
                    
                    # Outline / Shadow
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((30+dx, text_y+dy), main_text_choice, font=main_font, fill="black")

                    draw.text((30, text_y), main_text_choice, font=main_font, fill=text_color)

                    # Optional extra line
                    if add_extra_line and extra_text:
                        extra_font = get_font_from_file(font_stream, size=35)
                        if extra_font:
                            extra_y = text_y + 80
                            draw.text((35, extra_y), extra_text, font=extra_font, fill=(random_color()))

                    # Save
                    img_bytes = io.BytesIO()
                    final_img.save(img_bytes, format="JPEG", quality=95)
                    zipf.writestr(img_file.name, img_bytes.getvalue())

                    result_images.append((img_file.name, final_img))

            # Download
            st.success("✅ Images processed successfully!")
            st.download_button("📦 Download All as ZIP", data=zip_buffer.getvalue(), file_name="GoodVibes_Images.zip", mime="application/zip")

            st.markdown("---")
            st.subheader("📸 Preview Edited Images")
            for name, img in result_images:
                st.image(img, caption=name, use_column_width=True)

# ------------ Footer ------------
st.markdown("<div class='footer-note'>Made with ❤️ by GOOD VIBES</div>", unsafe_allow_html=True)
