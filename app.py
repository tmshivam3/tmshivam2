import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import random
import io

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")
st.markdown(
    """
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🔆 EDIT Photo in One Click 🔆</h1>
    """,
    unsafe_allow_html=True
)

# ------------------ UTILITY ------------------ #
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if abs((w / h) - target_ratio) < 0.01:
        return img
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_focus_color():
    focus_colors = [
        (255, 255, 0),   # Yellow
        (255, 0, 0),     # Red
        (255, 255, 255), # White
        (255, 105, 180), # Pink
        (0, 255, 0)      # Green
    ]
    return random.choice(focus_colors)

def generate_timestamp_filename():
    timestamp = datetime.datetime.now().strftime("%d-%m-%y_%H-%M-%S-%f")
    return f"Picsart_{timestamp}.jpg"

# ------------------ ASSET FOLDERS ------------------ #
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# ------------------ SIDEBAR ------------------ #
st.sidebar.header("🛠️ Customize Your Design")

# 1️⃣ Greeting Type
greeting_type = st.sidebar.selectbox(
    "Greeting Type",
    ["Good Morning", "Good Night"]
)

default_subtext = "Sweet Dreams" if greeting_type == "Good Night" else random.choice(["Have a Nice Day", "Have a Great Day"])
user_subtext = st.sidebar.text_input("Subtext (optional)", default_subtext)

# 2️⃣ Coverage
coverage_percent = st.sidebar.slider("Main Text Coverage % (smaller)", 2, 15, 8)

# 3️⃣ Date Option
add_date = st.sidebar.checkbox("Include Today's Date")

# 4️⃣ Advanced Positioning
advanced_positioning = st.sidebar.checkbox("Advanced Positioning", value=False)

if advanced_positioning:
    st.sidebar.markdown("**Main Text Position & Size**")
    main_x_pos = st.sidebar.slider("Main Text X (%)", 0, 100, 50)
    main_y_pos = st.sidebar.slider("Main Text Y (%)", 0, 100, 50)
    main_size_adjust = st.sidebar.slider("Main Text Size Scale", 50, 150, 100)

    st.sidebar.markdown("**Subtext Position & Size**")
    sub_x_pos = st.sidebar.slider("Subtext X (%)", 0, 100, 50)
    sub_y_pos = st.sidebar.slider("Subtext Y (%)", 0, 100, 60)
    sub_size_adjust = st.sidebar.slider("Subtext Size Scale", 50, 150, 100)

    if add_date:
        st.sidebar.markdown("**Date Position & Size**")
        date_x_pos = st.sidebar.slider("Date X (%)", 0, 100, 80)
        date_y_pos = st.sidebar.slider("Date Y (%)", 0, 100, 90)
        date_size_adjust = st.sidebar.slider("Date Size Scale", 50, 150, 100)

# 5️⃣ Logo Selection (Compact)
if available_logos:
    use_logo = st.sidebar.checkbox("Use Watermark Logo")
    if use_logo:
        logo_choice = st.sidebar.selectbox("Choose Logo", available_logos)
        logo_path = os.path.join("assets/logos", logo_choice)
    else:
        logo_path = None
else:
    logo_path = None

# 6️⃣ Font Section (Updated Compact)
st.sidebar.markdown("**Font Options**")
selected_font = None

if available_fonts:
    selected_font = st.sidebar.selectbox("Available Fonts", available_fonts)

uploaded_font = st.sidebar.file_uploader("Or Upload Your Own Font (.ttf or .otf)", type=["ttf", "otf"])

# ------------------ MAIN UPLOAD ------------------ #
uploaded_images = st.file_uploader("📸 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
output_images = []

# ------------------ PROCESSING ------------------ #
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("Processing..."):
            # Load logo
            logo = None
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            # Load font
            if uploaded_font is not None:
                font_bytes = io.BytesIO(uploaded_font.read())
                font_bytes.seek(0)
                selected_font_path = font_bytes
            elif selected_font is not None:
                selected_font_path = os.path.join("assets/fonts", selected_font)
            else:
                selected_font_path = "assets/fonts/roboto.ttf"

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)
                img_w, img_h = img.size

                # Base sizes from coverage %
                main_text_area = (coverage_percent / 1000) * img_w * img_h
                main_font_size = max(20, int((main_text_area) ** 0.5))
                subtext_font_size = max(16, int(main_font_size * 0.4))
                date_font_size = subtext_font_size

                # Advanced scaling overrides
                if advanced_positioning:
                    main_font_size = int(main_font_size * main_size_adjust / 100)
                    subtext_font_size = int(subtext_font_size * sub_size_adjust / 100)
                    if add_date:
                        date_font_size = int(date_font_size * date_size_adjust / 100)

                # Load fonts
                main_font = ImageFont.truetype(selected_font_path, size=main_font_size)
                sub_font = ImageFont.truetype(selected_font_path, size=subtext_font_size)
                date_font = ImageFont.truetype(selected_font_path, size=date_font_size)

                # Colors
                text_color = get_focus_color()

                # Positioning
                safe_margin = 20
                if advanced_positioning:
                    x = int(img_w * main_x_pos / 100)
                    y = int(img_h * main_y_pos / 100)
                    sub_x = int(img_w * sub_x_pos / 100)
                    sub_y = int(img_h * sub_y_pos / 100)
                else:
                    x = random.randint(safe_margin, img_w - main_font_size * len(greeting_type) // 2 - safe_margin)
                    y = random.randint(safe_margin, img_h - main_font_size - safe_margin)
                    sub_x = x + random.randint(-20, 20)
                    sub_y = y + main_font_size + 10

                # Draw main text
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), greeting_type, font=main_font, fill="black")
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # Draw date
                if add_date:
                    today_str = datetime.datetime.now().strftime("%d %B %Y")
                    if advanced_positioning:
                        date_x = int(img_w * date_x_pos / 100)
                        date_y = int(img_h * date_y_pos / 100)
                    else:
                        max_date_x = max(safe_margin, img_w - date_font_size * 12 - safe_margin)
                        max_date_y = max(safe_margin, img_h - date_font_size - safe_margin)
                        date_x = random.randint(safe_margin, max_date_x)
                        date_y = random.randint(safe_margin, max_date_y)
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((date_x+dx, date_y+dy), today_str, font=date_font, fill="black")
                    draw.text((date_x, date_y), today_str, font=date_font, fill=text_color)

                # Paste logo
                if logo:
                    img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                # Append
                output_images.append((generate_timestamp_filename(), img))

        st.success("✅ Images processed successfully!")
        for name, img in output_images:
            st.image(img, caption=name, use_column_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)
            st.download_button(f"⬇️ Download {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")
    else:
        st.warning("⚠️ Please upload images before clicking Generate.")
