
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import random
import os

st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🔆 SHIVAM TOOL 🔆</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# === Helper to list files in assets folders ===
def list_files(folder, exts):
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

# === Load available logos & fonts ===
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# === Logo selection/upload ===
st.subheader("📌 Logo Selection")
logo_choice = st.radio("Choose Logo Source", ["Select from site", "Upload your own"])

if logo_choice == "Select from site":
    selected_logo_file = st.selectbox("🎨 Choose Built-in Logo", available_logos)
    logo_path = os.path.join("assets/logos", selected_logo_file)
    logo_image = Image.open(logo_path).convert("RGBA")
else:
    uploaded_logo_file = st.file_uploader("📌 Upload your watermark/logo (PNG recommended)", type=["png"])
    if uploaded_logo_file:
        logo_image = Image.open(uploaded_logo_file).convert("RGBA")
    else:
        logo_image = None

# === Font selection/upload ===
st.subheader("🔠 Font Selection")
font_choice = st.radio("Choose Font Source", ["Select from site", "Upload your own"])

if font_choice == "Select from site":
    selected_font_file = st.selectbox("🔤 Choose Built-in Font", available_fonts)
    with open(os.path.join("assets/fonts", selected_font_file), "rb") as f:
        font_bytes = f.read()
else:
    uploaded_fonts = st.file_uploader("🔠 Upload custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
    if uploaded_fonts:
        font_bytes = uploaded_fonts[0].read()
    else:
        font_bytes = None

# === Upload images ===
uploaded_images = st.file_uploader("🖼️ Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# === Custom text options ===
st.subheader("📝 Text Options")
greeting_choice = st.selectbox("🌅 Choose Greeting Type", ["Good Morning", "Good Night"])
if greeting_choice == "Good Morning":
    default_subtexts = ["Have a Nice Day", "Have a Great Day"]
else:
    default_subtexts = ["Sweet Dreams", "Sleep Well"]

subtext_choice = st.selectbox("✨ Choose Subtext", default_subtexts)

branding_options = ["None", "Traveller Bharat", "Good Vibes", "Happy happy", "Bharattak"]
branding_choice = st.selectbox("📢 Choose Facebook Page Branding", branding_options)

# === Slider for text coverage ===
text_area_percent = st.slider("🧠 Text Area Coverage (percentage of image)", 5, 25, 20, step=1)
text_area_ratio = text_area_percent / 100

# === Shadow and Download options ===
add_shadow = st.checkbox("🌟 Add Shadow Effect Randomly", value=True)
download_mode = st.radio("📥 Choose Download Mode", ["Individual Images", "ZIP of All Images"])

# === Utility functions ===
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

def get_random_position(img_size, text_size):
    w, h = img_size
    tw, th = text_size
    margin = 30
    x = random.randint(margin, max(margin, w - tw - margin))
    y = random.randint(margin, max(margin, h - th - margin))
    return x, y

def get_text_size(draw, text, font):
    try:
        return font.getsize(text)
    except AttributeError:
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

def find_best_font_size(draw, text, font_bytes, image_size, target_ratio=0.20):
    W, H = image_size
    target_area = W * H * target_ratio
    size = 20
    while size < 500:
        try:
            test_font = ImageFont.truetype(io.BytesIO(font_bytes), size=size)
            w, h = get_text_size(draw, text, test_font)
            if w * h > target_area:
                return max(10, size - 5)
        except Exception:
            break
        size += 5
    return size

# === Generate Button ===
if st.button("✅ Generate Edited Images"):
    if not (uploaded_images and logo_image and font_bytes):
        st.warning("⚠️ Please provide logo, font, and images before generating.")
    else:
        with st.spinner("Processing images..."):
            logo_image.thumbnail((150, 150))
            output_images = []

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # Determine dynamic font size
                best_main_size = find_best_font_size(draw, greeting_choice, font_bytes, img.size, target_ratio=text_area_ratio)
                main_font = ImageFont.truetype(io.BytesIO(font_bytes), size=best_main_size)
                sub_font = ImageFont.truetype(io.BytesIO(font_bytes), size=int(best_main_size * 0.5))

                # Compose main text
                main_text = greeting_choice
                if branding_choice != "None":
                    main_text += f" - {branding_choice}"

                # Colors
                text_color = tuple(random.randint(100, 255) for _ in range(3))
                shadow_enabled = add_shadow and random.choice([True, False])

                # Position
                main_text_size = get_text_size(draw, main_text, main_font)
                x, y = get_random_position(img.size, main_text_size)

                if shadow_enabled:
                    for dx in [-2, -1, 0, 1, 2]:
                        for dy in [-2, -1, 0, 1, 2]:
                            if dx != 0 or dy != 0:
                                draw.text((x+dx, y+dy), main_text, font=main_font, fill="black")

                draw.text((x, y), main_text, font=main_font, fill=text_color)

                # Subtext
                sub_x = x + 10
                sub_y = y + main_text_size[1] + 10
                sub_color = tuple(random.randint(100, 255) for _ in range(3))
                draw.text((sub_x, sub_y), subtext_choice, font=sub_font, fill=sub_color)

                # Logo
                img_w, img_h = img.size
                logo_w, logo_h = logo_image.size
                img.paste(logo_image, (img_w - logo_w - 10, img_h - logo_h - 10), mask=logo_image)

                output_images.append((img_file.name, img))

        st.success("✅ All images processed successfully!")

        if download_mode == "Individual Images":
            for i, (name, img) in enumerate(output_images):
                st.image(img, caption=f"Preview: {name}", use_column_width=True)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=95)
                st.download_button(
                    label=f"⬇️ Download {name}",
                    data=img_bytes.getvalue(),
                    file_name=f"edited_{name}",
                    mime="image/jpeg",
                    key=f"dl_{i}"
                )
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for name, image in output_images:
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format="JPEG", quality=95)
                    zipf.writestr(name, img_bytes.getvalue())
            zip_buffer.seek(0)
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_buffer,
                file_name="GoodImages.zip",
                mime="application/zip"
            )
