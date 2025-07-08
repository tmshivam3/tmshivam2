import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# PAGE CONFIG
st.set_page_config(page_title="Edit Photo in Bulk Tool ™", layout="centered")

# HEADER
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Add Good Morning / Good Night greetings with stylish fonts, watermark, and more</h4>
""", unsafe_allow_html=True)

# FUNCTIONS
def list_files(folder, exts):
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_random_position(img_w, img_h, text_w, text_h):
    margin = 30
    areas = ['center'] * 5 + ['top_left'] * 10 + ['top_right'] * 10 + ['bottom_left'] * 10 + ['bottom_right'] * 10
    choice = random.choice(areas)
    if choice == 'center':
        return (img_w - text_w) // 2, (img_h - text_h) // 2
    elif choice == 'top_left':
        return margin, margin
    elif choice == 'top_right':
        return img_w - text_w - margin, margin
    elif choice == 'bottom_left':
        return margin, img_h - text_h - margin
    else:
        return img_w - text_w - margin, img_h - text_h - margin

def apply_shadow(draw, pos, text, font, color):
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((pos[0]+dx, pos[1]+dy), text, font=font, fill="black")
    draw.text(pos, text, font=font, fill=color)

def get_random_color():
    return tuple(random.randint(100, 255) for _ in range(3))

# MORNING/NIGHT WISHES
morning_wishes = ["Have a great day", "Rise and Shine!", "Wishing you success today!", "Stay positive!", "Fresh start ahead", "Smile & Shine!", "Bright morning to you"]
night_wishes = ["Sweet dreams", "Sleep tight", "Good Night & Take care", "Dream big", "Peaceful sleep", "Relax & Unwind", "Moonlight blessings"]

# LOAD FILES
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# SIDEBAR OPTIONS
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
default_subtext = "Sweet dreams" if greeting_type == "Good Night" else "Have a great day"

user_subtext = st.sidebar.text_input("Optional Wish Text", "")
coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 4, 15, 8)
add_date = st.sidebar.checkbox("Add Today's Date")
date_scale = st.sidebar.slider("Date Size Factor", 50, 150, 80)

selected_logo = st.sidebar.selectbox("Watermark Logo", available_logos + ["Upload Custom"])
logo_path = st.sidebar.file_uploader("Upload PNG Logo", type="png") if selected_logo == "Upload Custom" else os.path.join("assets/logos", selected_logo)

font_source = st.sidebar.radio("Font Source", ["Available Fonts", "Upload Font"])
selected_font = st.sidebar.selectbox("Choose Font", available_fonts) if font_source == "Available Fonts" else None
uploaded_font = st.sidebar.file_uploader("Upload Font", type=["ttf", "otf"]) if font_source == "Upload Font" else None

multi_variation = st.sidebar.checkbox("Generate 4 Variations per Photo", True)

# MAIN UPLOAD
uploaded_images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# IMAGE GENERATOR FUNCTION
def generate_variant(img, seed):
    random.seed(seed)
    img = crop_to_3_4(img.convert("RGBA"))
    draw = ImageDraw.Draw(img)

    img_w, img_h = img.size
    area = (coverage_percent / 100) * img_w * img_h
    main_font_size = max(30, int((area) ** 0.5 * 0.6))
    sub_font_size = int(main_font_size * 0.5)
    date_font_size = int(main_font_size * date_scale / 100)

    font_path = io.BytesIO(uploaded_font.read()) if uploaded_font else os.path.join("assets/fonts", selected_font)
    main_font = ImageFont.truetype(font_path, main_font_size)
    sub_font = ImageFont.truetype(font_path, sub_font_size)
    date_font = ImageFont.truetype(font_path, date_font_size)

    main_text = greeting_type
    wish_text = user_subtext if user_subtext else random.choice(morning_wishes if greeting_type == "Good Morning" else night_wishes)
    color = get_random_color()

    # MAIN TEXT
    text_w, text_h = draw.textbbox((0,0), main_text, font=main_font)[2:]
    x, y = get_random_position(img_w, img_h, text_w, text_h)
    apply_shadow(draw, (x, y), main_text, main_font, color)

    # SUB TEXT
    sub_w, sub_h = draw.textbbox((0,0), wish_text, font=sub_font)[2:]
    sub_x, sub_y = x + 10, y + text_h + 10
    apply_shadow(draw, (sub_x, sub_y), wish_text, sub_font, color)

    # DATE
    if add_date:
        date_text = datetime.datetime.now().strftime("%d %B %Y")
        date_w, date_h = draw.textbbox((0,0), date_text, font=date_font)[2:]
        dx, dy = get_random_position(img_w, img_h, date_w, date_h)
        draw.text((dx, dy), date_text, font=date_font, fill=random.choice([(255,215,0), color]))

    # WATERMARK
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((int(logo.width * 1.25), int(logo.height * 1.25)))
        lw, lh = logo.size
        pos_choices = [(10,10), (img_w - lw - 10,10), (10, img_h - lh - 10), (img_w - lw - 10, img_h - lh - 10)]
        px, py = random.choice(pos_choices)
        opacity = random.choice([128, 192, 255])
        logo.putalpha(opacity)
        img.paste(logo, (px, py), logo)

    return img.convert("RGB")

# GENERATE
if st.button("Generate Images"):
    if uploaded_images:
        results = []
        with st.spinner("Processing..."):
            for file in uploaded_images:
                base = Image.open(file)
                name = file.name
                variants = [generate_variant(base.copy(), random.randint(0,9999)) for _ in range(4 if multi_variation else 1)]
                results.append((name, variants))

        st.success("Done!")

        for name, variants in results:
            for img in variants:
                st.image(img, use_column_width=True)
                buffer = io.BytesIO()
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                file_name = f"Picsart_{timestamp}.jpg"
                img.save(buffer, format="JPEG")
                st.download_button("Download Image", buffer.getvalue(), file_name=file_name, mime="image/jpeg")

        if st.button("Download All as ZIP"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                for name, variants in results:
                    for img in variants:
                        img_io = io.BytesIO()
                        timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                        fname = f"Picsart_{timestamp}.jpg"
                        img.save(img_io, format="JPEG")
                        zipf.writestr(fname, img_io.getvalue())
            zip_buffer.seek(0)
            st.download_button("Download ZIP", zip_buffer.getvalue(), file_name="Picsart_Images.zip", mime="application/zip")

    else:
        st.warning("Please upload images first.")
