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

def random_contrasting_color(bg_color):
    return tuple(min(255, max(100, 255 - c + random.randint(-30,30))) for c in bg_color)

# -----------------------------
# SIDEBAR OPTIONS
# -----------------------------
st.sidebar.header("🔧 Customize Your Design")

# 1. GREETING TYPE
greeting_type = st.sidebar.selectbox("Select Greeting Type", ["Good Morning", "Good Night"])

# 2. Subtext
if greeting_type == "Good Morning":
    default_subtext = random.choice(["Have a Nice Day", "Have a Great Day"])
else:
    default_subtext = "Sweet Dreams"

user_subtext = st.sidebar.text_input("Subtext (optional)", default_subtext)

# 3. Coverage Slider
coverage_percent = st.sidebar.slider(
    "Main Text Coverage (area %)", 5, 25, 20,
    help="Adjust how big the main greeting text is."
)

# 4. Texture Option
texture_mode = st.sidebar.checkbox("Apply texture (text fill from image)", value=False)

# 5. Date Watermark
add_date = st.sidebar.checkbox("Add today's date", value=False)

# 6. Font Selection
st.sidebar.subheader("Font Options")
available_fonts = list_files(ASSETS_FONT_PATH, (".ttf", ".otf"))
selected_font = st.sidebar.selectbox("Select Existing Font", ["Default (Roboto)"] + available_fonts)

uploaded_font = st.sidebar.file_uploader("Or Upload New Font (.ttf/.otf)", type=["ttf", "otf"])
if uploaded_font:
    save_path = os.path.join(ASSETS_FONT_PATH, uploaded_font.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_font.getbuffer())
    st.sidebar.success(f"✅ Uploaded and saved: {uploaded_font.name}")

# 7. Logo Selection
st.sidebar.subheader("Watermark Logo")
available_logos = list_files(ASSETS_LOGO_PATH, (".png",))
selected_logo = st.sidebar.selectbox("Select Existing Logo", ["None"] + available_logos)

uploaded_logo = st.sidebar.file_uploader("Or Upload New Logo (.png)", type=["png"])
if uploaded_logo:
    save_path = os.path.join(ASSETS_LOGO_PATH, uploaded_logo.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_logo.getbuffer())
    st.sidebar.success(f"✅ Uploaded and saved: {uploaded_logo.name}")

# -----------------------------
# MAIN IMAGE UPLOAD
# -----------------------------
uploaded_images = st.file_uploader(
    "🖼️ Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
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
            # Load logo if any
            logo = None
            if selected_logo != "None":
                logo_path = os.path.join(ASSETS_LOGO_PATH, selected_logo)
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((150, 150))

            # Decide font path
            if selected_font == "Default (Roboto)":
                font_path = DEFAULT_FONT_PATH
            else:
                font_path = os.path.join(ASSETS_FONT_PATH, selected_font)

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                img_w, img_h = img.size

                draw = ImageDraw.Draw(img)

                # Dynamically scale text size from coverage
                scale_factor = 0.3   # Reduce so 5% is smaller
                main_text_area = (coverage_percent / 100) * img_w * img_h * scale_factor
                main_font_size = max(20, int(main_text_area ** 0.5))
                subtext_font_size = max(12, int(main_font_size * 0.4))
                date_font_size = max(12, int(main_font_size * 0.35))

                try:
                    main_font = ImageFont.truetype(font_path, size=main_font_size)
                    sub_font = ImageFont.truetype(font_path, size=subtext_font_size)
                    date_font = ImageFont.truetype(font_path, size=date_font_size)
                except Exception as e:
                    st.error(f"❌ Failed to load font: {e}")
                    continue

                # Random text position with safe range
                x_min = 30
                x_max = max(30, img_w - main_font_size * len(greeting_type)//2 - 30)
                x = x_min if x_max <= x_min else random.randint(x_min, x_max)

                y_min = 30
                y_max = max(30, img_h - main_font_size - 30)
                y = y_min if y_max <= y_min else random.randint(y_min, y_max)

                # Random high-contrast color
                avg_color = img.resize((1,1)).getpixel((0,0))
                text_color = random_contrasting_color(avg_color)
                shadow_color = "black"

                # Optional Texture
                if texture_mode:
                    mask = Image.new("L", img.size, 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.text((x,y), greeting_type, font=main_font, fill=255)
                    textured = img.copy()
                    img.paste(textured, mask=mask)
                else:
                    # Draw shadow
                    for dx in [-2,2]:
                        for dy in [-2,2]:
                            draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                    draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # Subtext
                sub_x = x + random.randint(-20, 20)
                sub_y = y + main_font_size + 10
                draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                # Add Date if enabled
                if add_date:
                    today = datetime.datetime.now().strftime("%d %B %Y")
                    date_x_min = 20
                    date_x_max = max(20, img_w - date_font_size * 8)
                    date_x = date_x_min if date_x_max <= date_x_min else random.randint(date_x_min, date_x_max)
                    date_y_min = 20
                    date_y_max = max(20, img_h - date_font_size - 20)
                    date_y = date_y_min if date_y_max <= date_y_min else random.randint(date_y_min, date_y_max)
                    draw.text((date_x, date_y), today, font=date_font, fill=text_color)

                # Add watermark logo
                if logo:
                    img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                output_images.append((img_file.name, img))

        st.success("✅ Images processed successfully!")

        # Show and download each
        for name, img in output_images:
            st.image(img, caption=name, use_column_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)
            st.download_button(f"⬇️ Download {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")
