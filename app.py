import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import io
import random
import datetime
import zipfile

st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Apply Greetings, PNG Overlays, Watermarks & More</h4>
""", unsafe_allow_html=True)

# ========== CONSTANTS ==========
COLORS = [(255,255,0), (255,0,0), (255,255,255), (0,255,0), (255,165,0)]
POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "middle-left", "middle-right"]

def list_files(folder, exts):
    if not os.path.exists(folder): return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def crop_to_3_4(img):
    w, h = img.size
    ratio = 3 / 4
    if w / h > ratio:
        new_w = int(h * ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def overlay_text(draw, position, text, font, fill):
    x, y = position
    draw.text((x, y), text, font=font, fill=fill)

def place_logo(img, logo):
    w, h = img.size
    logo.thumbnail((int(w * 0.25), int(h * 0.25)))
    x = random.randint(20, w - logo.width - 20)
    y = random.randint(20, h - logo.height - 20)
    logo = ImageEnhance.Brightness(logo).enhance(random.uniform(0.5, 1.0))
    img.paste(logo, (x, y), logo)
    return img

def avoid_center(x, y, w, h):
    cx, cy = w // 3, h // 3
    if cx < x < cx * 2 and cy < y < cy * 2:
        return avoid_center(random.randint(0, w - 100), random.randint(0, h - 100), w, h)
    return x, y

def paste_overlay(img, overlay_path, resize_ratio=0.3):
    overlay = Image.open(overlay_path).convert("RGBA")
    w, h = img.size
    overlay.thumbnail((int(w * resize_ratio), int(h * resize_ratio)))
    x = random.randint(0, w - overlay.width)
    y = random.randint(0, h - overlay.height)
    x, y = avoid_center(x, y, w, h)
    img.paste(overlay, (x, y), overlay)
    return img

# ========== SIDEBAR ==========
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
use_overlay = st.sidebar.checkbox("📌 Use Pre-made PNG Overlays Instead of Font/Text")
show_date = st.sidebar.checkbox("Add Today's Date", value=False)

available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
font_file = st.sidebar.selectbox("Choose Font", available_fonts)

available_logos = list_files("assets/logos", [".png"])
logo_file = st.sidebar.selectbox("Choose Watermark Logo", available_logos)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ========== MAIN LOGIC ==========
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Processing images... Please wait..."):
            results = []
            font_path = os.path.join("assets/fonts", font_file)
            logo_path = os.path.join("assets/logos", logo_file)

            overlay_folder = "morning" if greeting_type == "Good Morning" else "night"
            overlay_path = os.path.join("assets/overlays", overlay_folder)
            overlay_files = list_files(overlay_path, [".png"])

            for image_file in uploaded_images:
                try:
                    img = Image.open(image_file).convert("RGBA")
                    img = crop_to_3_4(img)
                    w, h = img.size
                    draw = ImageDraw.Draw(img)

                    # ========== Overlay Logic ==========
                    if use_overlay:
                        if len(overlay_files) == 0:
                            st.warning("⚠️ PNG overlays coming soon! No overlays found.")
                        else:
                            selected_pngs = random.sample(overlay_files, min(2, len(overlay_files)))
                            for idx, overlay_name in enumerate(selected_pngs):
                                full_path = os.path.join(overlay_path, overlay_name)
                                resize_ratio = 0.25 if idx == 0 else 0.15
                                img = paste_overlay(img, full_path, resize_ratio)
                    else:
                        font = ImageFont.truetype(font_path, int(w * 0.08))
                        text_color = random.choice(COLORS)
                        x = random.randint(30, w - 200)
                        y = random.randint(30, h - 100)
                        overlay_text(draw, (x, y), greeting_type, font, text_color)

                    if show_date:
                        font = ImageFont.truetype(font_path, int(w * 0.045))
                        date = datetime.datetime.now().strftime("%d %b %Y")
                        dx, dy = random.randint(30, w - 150), random.randint(30, h - 50)
                        overlay_text(draw, (dx, dy), date, font, random.choice(COLORS))

                    logo = Image.open(logo_path).convert("RGBA")
                    img = place_logo(img, logo)

                    final_image = img.convert("RGB")
                    results.append((image_file.name, final_image))

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        # ========== Display & Download ==========
        for name, img in results:
            st.image(img, caption=name, use_container_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)
            renamed = f"Edited_{datetime.datetime.now().strftime('%H%M%S%f')}.jpg"
            st.download_button(f"⬇️ Download {renamed}", data=img_bytes.getvalue(), file_name=renamed, mime="image/jpeg")

        if st.button("📦 Download All as ZIP"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for name, img in results:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", quality=95)
                    fname = f"Edited_{datetime.datetime.now().strftime('%H%M%S%f')}.jpg"
                    zipf.writestr(fname, img_bytes.getvalue())
            zip_buffer.seek(0)
            st.download_button("📥 Download ZIP", data=zip_buffer, file_name="Bulk_Edited_Images.zip", mime="application/zip")
    else:
        st.warning("⚠️ Please upload at least one image.")
