import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import random
import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>EDIT PHOTO IN ONE CLICK</h1>
""", unsafe_allow_html=True)

# -----------------------------
# CONSTANTS / PATHS
# -----------------------------
DEFAULT_FONT_PATH = "roboto.ttf"
ASSETS_FONT_PATH = "assets/fonts"
ASSETS_LOGO_PATH = "assets/logos"
COLOR_PALETTE = [(255, 255, 0), (255, 0, 0), (255, 255, 255), (255, 192, 203), (0, 255, 0)]  # Yellow, Red, White, Pink, Green

os.makedirs(ASSETS_FONT_PATH, exist_ok=True)
os.makedirs(ASSETS_LOGO_PATH, exist_ok=True)

# -----------------------------
# UTILS
# -----------------------------
def list_files(folder, exts):
    return [f for f in os.listdir(folder) if f.lower().endswith(exts)]

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

def pick_random_color():
    return random.choice(COLOR_PALETTE)

# -----------------------------
# SIDEBAR OPTIONS
# -----------------------------
with st.sidebar:
    st.header("🔧 Customize Your Design")
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])

    default_subtext = random.choice(["Have a Nice Day", "Have a Great Day"]) if greeting_type == "Good Morning" else "Sweet Dreams"
    user_subtext = st.text_input("Wishes Text", default_subtext)

    coverage_percent = st.slider(
        "Main Text Coverage %", 5, 25, 20,
        help="How big the main greeting text should be."
    )

    add_date = st.checkbox("Add Today's Date", value=False)

    st.subheader("Font Options")
    font_mode = st.radio("Font Source", ["Default (Roboto)", "Own Font"], horizontal=True)

    selected_font = None
    if font_mode == "Own Font":
        available_fonts = list_files(ASSETS_FONT_PATH, (".ttf", ".otf"))
        selected_font = st.selectbox("Select Uploaded Font", available_fonts if available_fonts else ["None"])
        uploaded_font = st.file_uploader("Upload New Font (.ttf/.otf)", type=["ttf", "otf"])
        if uploaded_font:
            save_path = os.path.join(ASSETS_FONT_PATH, uploaded_font.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_font.getbuffer())
            st.success(f"✅ Uploaded: {uploaded_font.name}")

    st.subheader("Watermark Logo")
    logo_mode = st.radio("Logo Source", ["None", "Select Existing"], horizontal=True)

    selected_logo = None
    if logo_mode == "Select Existing":
        available_logos = list_files(ASSETS_LOGO_PATH, (".png",))
        selected_logo = st.selectbox("Choose Logo", available_logos if available_logos else ["None"])
        uploaded_logo = st.file_uploader("Upload New Logo (.png)", type=["png"])
        if uploaded_logo:
            save_path = os.path.join(ASSETS_LOGO_PATH, uploaded_logo.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            st.success(f"✅ Uploaded: {uploaded_logo.name}")

# -----------------------------
# MAIN IMAGE UPLOAD
# -----------------------------
uploaded_images = st.file_uploader(
    "🖼️ Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

output_images = []

# -----------------------------
# GENERATE BUTTON
# -----------------------------
if st.button("✅ Generate Edited Images"):
    if not uploaded_images:
        st.warning("⚠️ Please upload images before clicking Generate.")
    else:
        with st.spinner("Processing..."):
            logo = None
            if selected_logo and selected_logo != "None":
                logo_path = os.path.join(ASSETS_LOGO_PATH, selected_logo)
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            # Determine font path
            if font_mode == "Default (Roboto)":
                font_path = DEFAULT_FONT_PATH
            elif selected_font and selected_font != "None":
                font_path = os.path.join(ASSETS_FONT_PATH, selected_font)
            else:
                font_path = DEFAULT_FONT_PATH

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                img_w, img_h = img.size

                draw = ImageDraw.Draw(img)

                # Coverage scaling
                scale_factor = 0.3
                main_text_area = (coverage_percent / 100) * img_w * img_h * scale_factor
                main_font_size = max(20, int(main_text_area ** 0.5))
                sub_font_size = max(14, int(main_font_size * 0.6))
                date_font_size = sub_font_size  # Same as wishes

                try:
                    main_font = ImageFont.truetype(font_path, size=main_font_size)
                    sub_font = ImageFont.truetype(font_path, size=sub_font_size)
                    date_font = ImageFont.truetype(font_path, size=date_font_size)
                except Exception as e:
                    st.error(f"❌ Font load error: {e}")
                    continue

                # Safe random position
                x_max = max(30, img_w - main_font_size * len(greeting_type)//2 - 30)
                y_max = max(30, img_h - main_font_size - 30)
                x = random.randint(30, x_max)
                y = random.randint(30, y_max)

                text_color = pick_random_color()
                shadow_color = "black"

                # Draw shadow and main text
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x + dx, y + dy), greeting_type, font=main_font, fill=shadow_color)
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # Wishes below main
                sub_x = x + random.randint(-20, 20)
                sub_y = y + main_font_size + 10
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # Add Date separately (avoiding overlap)
                if add_date:
                    today = datetime.datetime.now().strftime("%d %B %Y")
                    date_x = random.randint(30, img_w - date_font_size * 8)
                    date_y = random.randint(sub_y + sub_font_size + 30, img_h - date_font_size - 30)
                    draw.text((date_x, date_y), today, font=date_font, fill=text_color)

                # Add Logo
                if logo:
                    img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                output_images.append((img_file.name, img))

        st.success("✅ Images processed successfully!")

        # Show and download
        for name, img in output_images:
            st.image(img, caption=name, use_column_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)
            st.download_button(f"⬇️ Download {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")
