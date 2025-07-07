import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

# PAGE SETTINGS
st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🔆 SHIVAM TOOL 🔆</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# SAFELY LIST FILES
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

# PERMANENT LOGO AND FONT SELECTION
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# SIDEBAR SETTINGS
st.sidebar.header("🔧 Customize Your Design")

# 1️⃣ Select Greeting Type
greeting_type = st.sidebar.selectbox(
    "Select Greeting Type",
    ["Good Morning", "Good Night"]
)

# 2️⃣ Add Subtext
if greeting_type == "Good Morning":
    default_subtext = random.choice(["Have a Nice Day", "Have a Great Day"])
else:
    default_subtext = "Sweet Dreams"

user_subtext = st.sidebar.text_input("Subtext (optional)", default_subtext)

# 3️⃣ Text Coverage Slider
coverage_percent = st.sidebar.slider("Main Text Coverage (area %)", 5, 25, 20)

# 4️⃣ Choose Permanent Logo
logo_choice = st.sidebar.selectbox("Select Your Watermark Logo", ["None"] + available_logos)
if logo_choice != "None":
    logo_path = os.path.join("assets/logos", logo_choice)
else:
    logo_path = None

# 5️⃣ Choose Permanent Font
font_choice = st.sidebar.selectbox("Select Font", ["Default"] + available_fonts)

# MAIN FILE UPLOADS
uploaded_images = st.file_uploader("🖼️ Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

output_images = []

# CROP IMAGE TO 3:4 RATIO
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
            # LOAD LOGO IF SELECTED
            logo = None
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            # LOAD FONT IF SELECTED
            fonts = []
            if font_choice != "Default":
                fonts = [os.path.join("assets/fonts", font_choice)]
            else:
                fonts = []

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)

                draw = ImageDraw.Draw(img)
                img_w, img_h = img.size

                # FONT SIZE BY COVERAGE
                main_text_area = (coverage_percent / 100) * img_w * img_h
                main_font_size = int((main_text_area) ** 0.5)
                subtext_font_size = int(main_font_size * 0.4)

                # Load Fonts
                if fonts:
                    main_font = ImageFont.truetype(fonts[0], size=main_font_size)
                    sub_font = ImageFont.truetype(fonts[0], size=subtext_font_size)
                else:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()

                # RANDOM TEXT POSITION
                max_x = img_w - main_font_size * len(greeting_type) // 2
                max_y = img_h - main_font_size
                x = random.randint(30, max(30, max_x))
                y = random.randint(30, max(30, max_y))

                # RANDOM COLOR / SHADOW
                text_color = tuple(random.randint(100, 255) for _ in range(3))
                shadow_color = "black"

                # DRAW MAIN TEXT WITH SHADOW
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # DRAW SUBTEXT NEAR MAIN TEXT
                sub_x = x + random.randint(-20, 20)
                sub_y = y + main_font_size + 10
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # PASTE LOGO IF PRESENT
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
