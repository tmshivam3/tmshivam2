import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime

# PAGE CONFIG
st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🔆 EDIT PHOTO IN ONE CLICK 🔆</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
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

# SIDEBAR
st.sidebar.header("🎨 Tool Settings")

greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])

default_subtext = "Sweet Dreams" if greeting_type == "Good Night" else "Have a Nice Day"
user_subtext = st.sidebar.text_input("Wishes Text", default_subtext)

coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 2, 20, 8)

show_date = st.sidebar.checkbox("Add Today's Date on Image", value=True)
date_size_factor = st.sidebar.slider("Date Text Size (relative)", 30, 120, 70)

logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos if available_logos else ["None"])
logo_path = os.path.join("assets/logos", logo_choice) if available_logos and logo_choice != "None" else None

# SIDEBAR - Font Selection
font_option = st.sidebar.radio("Font Option", ["Manual", "Random"])

# Manual Font Selection
if font_option == "Manual":
    font_source = st.sidebar.radio("Select:", ["Available Fonts", "Upload Your Own"])

    if font_source == "Available Fonts":
        selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
        uploaded_font = None
    else:
        uploaded_font = st.sidebar.file_uploader("Upload .ttf or .otf Font", type=["ttf", "otf"])
        selected_font = None

else:
    uploaded_font = None
    selected_font = None

# MAIN UPLOAD
uploaded_images = st.file_uploader("🖼️ Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

output_images = []

# BUTTON
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("Processing..."):
            logo = None
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            def generate_single_variant(img, seed=None, selected_font=None):
                random.seed(seed)
                img = crop_to_3_4(img)
                img_w, img_h = img.size
                main_text_area = (coverage_percent / 100) * img_w * img_h
                main_font_size = max(30, int((main_text_area) ** 0.5 * 0.6))
                sub_font_size = int(main_font_size * 0.5)
                date_font_size = int(main_font_size * date_size_factor / 100)

                # Font Selection Logic
                try:
                    if font_option == "Manual":
                        if uploaded_font:
                            font_bytes = io.BytesIO(uploaded_font.read())
                            main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                            sub_font = ImageFont.truetype(font_bytes, size=sub_font_size)
                            date_font = ImageFont.truetype(font_bytes, size=date_font_size)
                        elif selected_font:
                            main_font = ImageFont.truetype(os.path.join("assets/fonts", selected_font), size=main_font_size)
                            sub_font = ImageFont.truetype(os.path.join("assets/fonts", selected_font), size=sub_font_size)
                            date_font = ImageFont.truetype(os.path.join("assets/fonts", selected_font), size=date_font_size)
                        else:
                            main_font = ImageFont.load_default()
                            sub_font = ImageFont.load_default()
                            date_font = ImageFont.load_default()

                    else:  # Random Font Selection
                        if available_fonts:
                            random_font_file = random.choice(available_fonts)
                            random_font_path = os.path.join("assets/fonts", random_font_file)  # Ensure correct path
                            main_font = ImageFont.truetype(random_font_path, size=main_font_size)
                            sub_font = ImageFont.truetype(random_font_path, size=sub_font_size)
                            date_font = ImageFont.truetype(random_font_path, size=date_font_size)
                        else:
                            st.error("No fonts found in assets/fonts directory.")
                            main_font = ImageFont.load_default()
                            sub_font = ImageFont.load_default()
                            date_font = ImageFont.load_default()
                
                except OSError as e:
                    st.error(f"Error loading font: {e}")
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()
                    date_font = ImageFont.load_default()

                draw = ImageDraw.Draw(img)
                safe_margin = 30

                # Colors
                strong_colors = [(255, 255, 0), (255, 0, 0), (255, 255, 255), (255, 192, 203), (0, 255, 0)]
                text_color = random.choice(strong_colors + [tuple(random.randint(100, 255) for _ in range(3))])

                # Main Text (Good Morning / Good Night)
                x = random.randint(safe_margin, max(safe_margin, img_w - main_font_size * len(greeting_type)//2 - safe_margin))
                y = random.randint(safe_margin, max(safe_margin, img_h - main_font_size - safe_margin))
                shadow_color = "black"
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # Subtext (Wishes)
                sub_x = x + random.randint(-20, 20)
                sub_y = y + main_font_size + 10
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # Date (Today's Date)
                if show_date:
                    today_str = datetime.datetime.now().strftime("%d %B %Y")
                    date_x = safe_margin
                    date_y = img_h - date_font_size - safe_margin  # Fixed position at the bottom
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((date_x + dx, date_y + dy), today_str, font=date_font, fill=shadow_color)
                    draw.text((date_x, date_y), today_str, font=date_font, fill=text_color)

                # Logo
                if logo:
                    img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                return img

            all_results = []
            for img_file in uploaded_images:
                image = Image.open(img_file).convert("RGB")
                variants = []
                variant = generate_single_variant(image.copy(), seed=random.randint(0, 99999), selected_font=selected_font)
                variants.append(variant)

                all_results.append((img_file.name, variants))

        st.success("✅ All images processed successfully!")

        # Preview and Download
        for name, variants in all_results:
            st.write(f"**{name}**")  # Fixed f-string error
            st.image(variants[0], caption=name, use_column_width=True)

            for i, img in enumerate(variants):
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=95)
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")  # Fixed the timestamp string error
                file_name = f"Picsart_{timestamp}.jpg"
                st.download_button(f"⬇️ Download {file_name}", data=img_bytes.getvalue(), file_name=file_name, mime="image/jpeg")

    else:
        st.warning("⚠️ Please upload images before clicking
