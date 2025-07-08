import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# PAGE CONFIGURATION
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

# HEADER
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Professional Image Generator with Greetings, Watermark, Date & More</h4>
""", unsafe_allow_html=True)

# UTILITY FUNCTIONS
def list_files(folder, exts):
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)] if os.path.exists(folder) else []

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_random_position(img_size, text_size, exclude_center=True):
    img_w, img_h = img_size
    txt_w, txt_h = text_size
    margin = 30
    x_range = img_w - txt_w - 2 * margin
    y_range = img_h - txt_h - 2 * margin

    if x_range <= 0 or y_range <= 0:
        return (margin, margin)

    while True:
        x = random.randint(margin, x_range)
        y = random.randint(margin, y_range)
        if not exclude_center or not (img_w * 0.3 < x < img_w * 0.7 and img_h * 0.3 < y < img_h * 0.7):
            return x, y

def add_shadow(draw, position, text, font, shadow_color):
    x, y = position
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)

def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_name, variants in images:
            for variant in variants:
                img_bytes = io.BytesIO()
                variant.save(img_bytes, format="JPEG", quality=95)
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                file_name = f"Picsart_{timestamp}.jpg"
                zipf.writestr(file_name, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# DATA
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

morning_wishes = ["Have a great day!", "Start your day with a smile!", "Rise and shine!", "Wishing you a beautiful morning!", "Spread positivity today!", "New day, new hope."]
night_wishes = ["Sweet dreams!", "Good night & take care!", "Sleep peacefully!", "Dream big!", "Wishing you a restful night."]

# SIDEBAR
st.sidebar.header("🎨 Customize Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
def_wish = "" if greeting_type == "Good Morning" else ""
custom_wish = st.sidebar.text_input("Custom Wish (Optional)", def_wish)
coverage_percent = st.sidebar.slider("Text Coverage (%)", 2, 20, 8)
show_date = st.sidebar.checkbox("Show Today's Date", value=True)
date_size_factor = st.sidebar.slider("Date Text Size", 30, 120, 70)
logo_choice = st.sidebar.selectbox("Select Watermark Logo", available_logos + ["Upload Your Own"])

logo_path = None
if logo_choice == "Upload Your Own":
    logo_file = st.sidebar.file_uploader("Upload PNG Watermark", type=["png"])
    if logo_file:
        logo_path = Image.open(logo_file).convert("RGBA")
else:
    logo_path = Image.open(os.path.join("assets/logos", logo_choice)).convert("RGBA") if logo_choice else None

font_source = st.sidebar.radio("Font Source", ["Available Fonts", "Upload Font"])
selected_font = uploaded_font = None

if font_source == "Available Fonts":
    selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
else:
    uploaded_font = st.sidebar.file_uploader("Upload Font", type=["ttf", "otf"])

generate_variations = st.sidebar.checkbox("Generate 4 Variations", value=True)

# UPLOAD IMAGES
uploaded_images = st.file_uploader("📸 Upload Your Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# MAIN BUTTON
if st.button("✨ Generate Images"):
    if not uploaded_images:
        st.warning("Please upload images to continue.")
    else:
        output = []
        with st.spinner("Processing images..."):
            for file in uploaded_images:
                img = Image.open(file).convert("RGB")
                img = crop_to_3_4(img)
                img_w, img_h = img.size

                font_path = os.path.join("assets/fonts", selected_font) if selected_font else uploaded_font
                font_bytes = io.BytesIO(font_path.read()) if uploaded_font else font_path
                variations = []

                for i in range(4 if generate_variations else 1):
                    random.seed(datetime.datetime.now().timestamp() + i)
                    variant = img.copy()
                    draw = ImageDraw.Draw(variant)

                    wish_list = morning_wishes if greeting_type == "Good Morning" else night_wishes
                    subtext = custom_wish if custom_wish else random.choice(wish_list)

                    main_area = (coverage_percent / 100) * img_w * img_h
                    main_font_size = max(30, int((main_area) ** 0.5 * 0.6))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    font = ImageFont.truetype(font_bytes, size=main_font_size)
                    sub_font = ImageFont.truetype(font_bytes, size=sub_font_size)
                    date_font = ImageFont.truetype(font_bytes, size=date_font_size)

                    colors = [(255, 255, 255), (255, 215, 0), (255, 192, 203), (0, 255, 0), (135, 206, 250)]
                    text_color = random.choice(colors)
                    shadow = random.choice([True, False])

                    text_size = draw.textbbox((0, 0), greeting_type, font=font)
                    text_w = text_size[2] - text_size[0]
                    text_h = text_size[3] - text_size[1]
                    position = get_random_position((img_w, img_h), (text_w, text_h), exclude_center=random.random() > 0.05)

                    if shadow:
                        add_shadow(draw, position, greeting_type, font, "black")
                    draw.text(position, greeting_type, font=font, fill=text_color)

                    sub_x = position[0] + random.randint(-10, 10)
                    sub_y = position[1] + main_font_size + 5
                    if shadow:
                        add_shadow(draw, (sub_x, sub_y), subtext, sub_font, "black")
                    draw.text((sub_x, sub_y), subtext, font=sub_font, fill=text_color)

                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        date_pos = get_random_position((img_w, img_h), (150, date_font_size), exclude_center=True)
                        if shadow:
                            add_shadow(draw, date_pos, today, date_font, "black")
                        draw.text(date_pos, today, font=date_font, fill=random.choice(colors))

                    if logo_path:
                        logo = logo_path.copy()
                        base_width = int(min(img_w, img_h) * 0.25)
                        logo.thumbnail((base_width, base_width))
                        opacity = random.randint(115, 255)
                        logo.putalpha(opacity)

                        lw, lh = logo.size
                        max_x = img_w - lw - 10
                        max_y = img_h - lh - 10
                        logo_x = random.randint(10, max_x)
                        logo_y = random.randint(10, max_y)

                        variant.paste(logo, (logo_x, logo_y), logo)

                    variations.append(variant)

                output.append((file.name, variations))

        # DISPLAY OUTPUT
        for name, images in output:
            for img in images:
                st.image(img, caption=name, use_container_width=True)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG")
                img_bytes.seek(0)
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                fname = f"Picsart_{timestamp}.jpg"
                st.download_button("⬇️ Download", data=img_bytes, file_name=fname, mime="image/jpeg")

        # DOWNLOAD ALL
        if st.button("⬇️ Download All as ZIP"):
            zip_buffer = create_zip(output)
            st.download_button("📦 Download ZIP", data=zip_buffer, file_name="All_Images.zip", mime="application/zip")
