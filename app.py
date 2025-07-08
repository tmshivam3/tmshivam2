import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import zipfile
import datetime
import random

# Page configuration
st.set_page_config(page_title="🖼️ Bulk Image Editor", layout="centered")

# Header
st.markdown("""
    <h2 style='text-align: center;'>🖼️ Bulk Image Editor</h2>
    <h5 style='text-align: center; color: gray;'>Add greetings, watermark & more</h5>
""", unsafe_allow_html=True)

# Helper functions
def crop_to_3_4(image):
    w, h = image.size
    target_ratio = 3 / 4
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return image.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return image.crop((0, top, w, top + new_h))

def apply_text(draw, text, position, font, fill):
    draw.text(position, text, font=font, fill=fill)

def avoid_center(x, y, w, h):
    cx, cy = w // 3, h // 3
    if cx < x < cx * 2 and cy < y < cy * 2:
        return avoid_center(random.randint(0, w - 100), random.randint(0, h - 100), w, h)
    return x, y

def apply_png_overlay(img, overlay_folder):
    if not os.path.exists(overlay_folder):
        return img, False
    files = [f for f in os.listdir(overlay_folder) if f.endswith('.png')]
    if not files:
        return img, False

    selected = random.sample(files, min(2, len(files)))
    for i, file in enumerate(selected):
        overlay = Image.open(os.path.join(overlay_folder, file)).convert("RGBA")
        w, h = img.size
        resize = (int(w * 0.25), int(h * 0.1)) if i else (int(w * 0.3), int(h * 0.15))
        overlay.thumbnail(resize)
        ox, oy = avoid_center(random.randint(0, w - overlay.width), random.randint(0, h - overlay.height), w, h)
        img.paste(overlay, (ox, oy), overlay)

    return img, True

def place_logo(img, logo_path):
    if not os.path.exists(logo_path):
        return img
    logo = Image.open(logo_path).convert("RGBA")
    w, h = img.size
    logo.thumbnail((int(w * 0.25), int(h * 0.25)))
    x = random.randint(10, w - logo.width - 10)
    y = random.randint(10, h - logo.height - 10)
    img.paste(logo, (x, y), logo)
    return img

# Sidebar settings
st.sidebar.header("🔧 Settings")
greeting = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
use_overlay = st.sidebar.checkbox("Use PNG Overlays Instead of Text")

font_files = [f for f in os.listdir("assets/fonts") if f.endswith(".ttf")]
font_file = st.sidebar.selectbox("Select Font", font_files)
font_path = os.path.join("assets/fonts", font_file)

logo_files = [f for f in os.listdir("assets/logos") if f.endswith(".png")]
logo_file = st.sidebar.selectbox("Select Watermark Logo", logo_files)
logo_path = os.path.join("assets/logos", logo_file)

uploaded_files = st.file_uploader("📤 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Generate button
if st.button("🚀 Start Processing"):
    if not uploaded_files:
        st.warning("⚠️ Please upload images.")
    else:
        with st.spinner("🔄 Processing images... Please wait..."):
            results = []
            for file in uploaded_files:
                try:
                    img = Image.open(file).convert("RGBA")
                    img = crop_to_3_4(img)
                    w, h = img.size
                    draw = ImageDraw.Draw(img)
                    font = ImageFont.truetype(font_path, int(w * 0.08))
                    color = (255, 255, 255)

                    overlay_folder = "morning" if greeting == "Good Morning" else "night"
                    overlay_path = os.path.join("assets/overlays", overlay_folder)

                    if use_overlay:
                        img, success = apply_png_overlay(img, overlay_path)
                        if not success:
                            st.warning("⚠️ PNG overlays not found. Showing fallback text.")
                            apply_text(draw, greeting, (50, 50), font, color)
                    else:
                        apply_text(draw, greeting, (50, 50), font, color)

                    if show_date:
                        date_text = datetime.datetime.now().strftime("%d %b %Y")
                        small_font = ImageFont.truetype(font_path, int(w * 0.045))
                        apply_text(draw, date_text, (50, h - 80), small_font, color)

                    img = place_logo(img, logo_path)

                    rgb_img = img.convert("RGB")
                    results.append((file.name, rgb_img))

                except Exception as e:
                    st.error(f"❌ Error processing {file.name}: {str(e)}")

        # Show processed images
        for name, img in results:
            st.image(img, caption=name, use_column_width=True)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button(f"⬇️ Download {name}", buf.getvalue(), file_name=f"Edited_{name}", mime="image/jpeg")

        # ZIP download
        if st.button("📦 Download All as ZIP"):
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:
                for name, img in results:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", quality=95)
                    zipf.writestr(name, img_bytes.getvalue())
            zip_buf.seek(0)
            st.download_button("📥 Download ZIP", zip_buf.getvalue(), file_name="Edited_Images.zip", mime="application/zip")
