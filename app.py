import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io
import datetime

# PAGE SETTINGS
st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>EDIT Photo in One Click</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# SAFELY LIST FILES
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

# AVAILABLE LOGOS AND FONTS
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# SIDEBAR SETTINGS
with st.sidebar.expander("🛠️ Tool Settings", expanded=True):
    # 1️⃣ Greeting
    greeting_type = st.selectbox("Select Greeting Type", ["Good Morning", "Good Night"])
    if greeting_type == "Good Morning":
        default_subtext = random.choice(["Have a Nice Day", "Have a Great Day"])
    else:
        default_subtext = "Sweet Dreams"
    user_subtext = st.text_input("Subtext (optional)", default_subtext)

    # 2️⃣ Main Text Coverage
    coverage_percent = st.slider("Main Text Coverage (%)", 5, 100, 20)

    # 3️⃣ Add Today's Date
    add_date = st.checkbox("Add Today's Date")

    # 4️⃣ Watermark Logo Selection
    if available_logos:
        logo_choice = st.selectbox("Select Watermark Logo", available_logos)
        logo_path = os.path.join("assets/logos", logo_choice)
    else:
        logo_path = None

    # 5️⃣ Font Selection
    st.markdown("### Font Options")
    font_mode = st.radio("Font Source", ["Use Available Fonts", "Upload Your Font"])

    if font_mode == "Use Available Fonts":
        font_choice = st.selectbox("Available Fonts", available_fonts)
        font_path = os.path.join("assets/fonts", font_choice)
    else:
        uploaded_font_file = st.file_uploader("Upload .ttf/.otf Font", type=["ttf", "otf"])
        if uploaded_font_file:
            font_bytes = io.BytesIO(uploaded_font_file.read())
            font_path = font_bytes
        else:
            font_path = "assets/fonts/roboto.ttf"

# MAIN UPLOAD
uploaded_images = st.file_uploader("🖼️ Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

output_images = []

# CROP TO 3:4
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

# COLORS PRIORITY
priority_colors = [(255, 255, 0), (255, 0, 0), (255, 255, 255), (255, 105, 180), (0, 255, 0)]

# BUTTON
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("Processing..."):
            logo = None
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)
                img_w, img_h = img.size

                # FONT SIZING (further reduced scaling)
                main_text_area = (coverage_percent / 800) * img_w * img_h
                main_font_size = max(20, int(main_text_area ** 0.5))
                sub_font_size = int(main_font_size * 0.4)
                date_font_size = sub_font_size

                # Load Fonts
                try:
                    main_font = ImageFont.truetype(font_path, size=main_font_size)
                    sub_font = ImageFont.truetype(font_path, size=sub_font_size)
                    date_font = ImageFont.truetype(font_path, size=date_font_size)
                except:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()
                    date_font = ImageFont.load_default()

                # TEXT POSITION RANDOMNESS
                safe_margin = 40
                max_x = max(safe_margin, img_w - main_font_size * len(greeting_type)//2 - safe_margin)
                max_y = max(safe_margin, img_h - main_font_size - safe_margin)
                x = random.randint(safe_margin, max_x)
                y = random.randint(safe_margin, max_y)

                # COLOR RANDOM
                if random.random() < 0.7:
                    text_color = random.choice(priority_colors)
                else:
                    text_color = tuple(random.randint(100, 255) for _ in range(3))
                shadow_color = "black"

                # DRAW MAIN TEXT
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # SUBTEXT
                sub_x = x + random.randint(-30, 30)
                sub_y = y + main_font_size + random.randint(10, 30)
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # DATE
                if add_date:
                    today_str = datetime.datetime.now().strftime("%d %B %Y")
                    date_x = random.randint(safe_margin, max(img_w - date_font_size * 12, safe_margin))
                    date_y = random.randint(safe_margin, max(img_h - date_font_size - safe_margin))
                    draw.text((date_x, date_y), today_str, font=date_font, fill=text_color)

                # PASTE LOGO
                if logo:
                    img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                output_images.append((img_file.name, img))

        st.success("✅ Images processed successfully!")
        for _, img in output_images:
            st.image(img, use_column_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)

            timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")[:-3]
            filename = f"Picsart_{timestamp}.jpg"

            st.download_button(
                f"⬇️ Download {filename}",
                data=img_bytes.getvalue(),
                file_name=filename,
                mime="image/jpeg"
            )
    else:
        st.warning("⚠️ Please upload images before clicking Generate.")
