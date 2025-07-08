# FINAL PREMIUM app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import os
import io
import datetime
import zipfile

# PAGE CONFIG
st.set_page_config(page_title="Edit Photo in Bulk Tool ™ 📁", layout="centered")

# HEADER
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>📁 Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Quickly Generate Good Morning / Night Images with Watermarks, Fonts & Date</h4>
""", unsafe_allow_html=True)

# UTILS
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

# DATA
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

morning_wishes = ["Have a great day!", "Start fresh!", "Rise & Shine!", "Stay Positive!", "Good vibes only!"]
night_wishes = ["Sweet dreams!", "Sleep tight!", "Good Night dear!", "Rest well!", "Peaceful night ahead!"]

def get_random_position(w, h, text_w, text_h):
    regions = [
        (30, 30, w//2, h//3),  # Top-left
        (w//2, 30, w-30, h//3),  # Top-right
        (30, h//3*2, w//2, h-30),  # Bottom-left
        (w//2, h//3*2, w-30, h-30),  # Bottom-right
        ((w-text_w)//2, (h-text_h)//2, (w+text_w)//2, (h+text_h)//2)  # Center (rare)
    ]
    weights = [25, 25, 25, 25, 5]
    chosen = random.choices(regions, weights=weights)[0]
    x = random.randint(chosen[0], chosen[2]-text_w)
    y = random.randint(chosen[1], chosen[3]-text_h)
    return x, y

# SIDEBAR
st.sidebar.header(":art: Tool Settings")

greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])

user_subtext = st.sidebar.text_input("Add Wishes (leave blank for auto)", "")

coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 2, 20, 8)
show_date = st.sidebar.checkbox("Add Date", value=True)
date_size_factor = st.sidebar.slider("Date Text Size", 30, 120, 70)

logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Upload Custom"])
logo_path = os.path.join("assets/logos", logo_choice) if logo_choice != "Upload Custom" else None
if logo_choice == "Upload Custom":
    logo_path = st.sidebar.file_uploader("Upload Watermark", type=["png"])

font_source = st.sidebar.radio("Font Source", ["From List", "Upload Font"])
if font_source == "From List":
    selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
    uploaded_font = None
else:
    uploaded_font = st.sidebar.file_uploader("Upload Font", type=["ttf", "otf"])
    selected_font = None

# EXTRAS
generate_variations = st.sidebar.checkbox("Generate Variations", value=True)
color_mode = st.sidebar.radio("Color Effects", ["Original", "Enhance Contrast", "Black & White"])

uploaded_images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ZIP
def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for name, variants in images:
            for i, img in enumerate(variants):
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                fname = f"Picsart_{timestamp}.png"
                zipf.writestr(fname, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# GENERATOR
def generate_image_variant(img, greeting, wish_text, font_path):
    img = crop_to_3_4(img)

    # Filter
    if color_mode == "Enhance Contrast":
        img = ImageEnhance.Contrast(img).enhance(1.5)
    elif color_mode == "Black & White":
        img = img.convert("L").convert("RGB")

    draw = ImageDraw.Draw(img)
    img_w, img_h = img.size

    text_area = (coverage_percent / 100) * img_w * img_h
    font_size = max(30, int((text_area) ** 0.5 * 0.6))
    sub_font_size = int(font_size * 0.5)
    date_font_size = int(font_size * date_size_factor / 100)

    if isinstance(font_path, str):
        font = ImageFont.truetype(font_path, size=font_size)
        sub_font = ImageFont.truetype(font_path, size=sub_font_size)
        date_font = ImageFont.truetype(font_path, size=date_font_size)
    else:
        font = ImageFont.truetype(font_path, size=font_size)
        sub_font = ImageFont.truetype(font_path, size=sub_font_size)
        date_font = ImageFont.truetype(font_path, size=date_font_size)

    # Main Text
    text_w, text_h = draw.textbbox((0,0), greeting, font=font)[2:]
    x, y = get_random_position(img_w, img_h, text_w, text_h)
    shadow = random.choice([True, False])
    if shadow:
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x+dx, y+dy), greeting, font=font, fill="black")
    draw.text((x, y), greeting, font=font, fill=random.choice(["white", "yellow", "gold", "pink", "orange", "skyblue"]))

    # Subtext
    if wish_text:
        sub_w, sub_h = draw.textbbox((0,0), wish_text, font=sub_font)[2:]
        sub_x = x + 20
        sub_y = y + text_h + 10
        if random.random() > 0.5:
            draw.text((sub_x+1, sub_y+1), wish_text, font=sub_font, fill="black")
        draw.text((sub_x, sub_y), wish_text, font=sub_font, fill=random.choice(["white", "aqua", "yellow", "limegreen", "coral"]))

    # Date
    if show_date:
        today = datetime.datetime.now().strftime("%d %B %Y")
        dx = random.randint(30, img_w - 150)
        dy = random.randint(30, img_h - 100)
        draw.text((dx+1, dy+1), today, font=date_font, fill="black")
        draw.text((dx, dy), today, font=date_font, fill=random.choice(["white", "violet", "lightgreen", "orange"]))

    # Logo
    if logo_path:
        logo_img = Image.open(logo_path).convert("RGBA") if isinstance(logo_path, str) else Image.open(logo_path).convert("RGBA")
        logo_img.thumbnail((200, 200))
        img.paste(logo_img, (img_w - logo_img.width - 10, img_h - logo_img.height - 10), logo_img)

    return img

# MAIN ACTION
if st.button("✅ Generate Images"):
    if uploaded_images:
        try:
            results = []
            for image_file in uploaded_images:
                img = Image.open(image_file).convert("RGB")
                font_path = os.path.join("assets/fonts", selected_font) if font_source == "From List" else io.BytesIO(uploaded_font.read())
                wish = user_subtext.strip() or (random.choice(morning_wishes) if greeting_type == "Good Morning" else random.choice(night_wishes))

                variants = []
                count = 4 if generate_variations else 1
                for _ in range(count):
                    variant = generate_image_variant(img.copy(), greeting_type, wish, font_path)
                    variants.append(variant)

                results.append((image_file.name, variants))

            st.success("✅ All images processed!")

            for name, variants in results:
                for variant in variants:
                    st.image(variant, use_column_width=True)
                    img_bytes = io.BytesIO()
                    variant.save(img_bytes, format="PNG")
                    ts = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                    fname = f"Picsart_{ts}.png"
                    st.download_button(f"⬇️ Download {fname}", img_bytes.getvalue(), fname, mime="image/png")

            if st.button("⬇️ Download All as ZIP"):
                zip_data = create_zip(results)
                st.download_button("Download ZIP", zip_data, "Bulk_Images.zip", mime="application/zip")

        except Exception as e:
            st.error(f"Error Occurred: {e}")
    else:
        st.warning("⚠️ Please upload images first.")
