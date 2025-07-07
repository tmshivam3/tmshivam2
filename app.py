import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import random

st.set_page_config(page_title="🔆 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🔆 SHIVAM TOOL 🔆</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# === Upload sections ===
logo_file = st.file_uploader("📌 Upload your watermark/logo (PNG recommended)", type=["png"])
font_files = st.file_uploader("🔠 Upload custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("🖼️ Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# === Custom text options ===
greeting_choice = st.selectbox("🌅 Choose Greeting Type", ["Good Morning", "Good Night"])
if greeting_choice == "Good Morning":
    default_subtexts = ["Have a Nice Day", "Have a Great Day"]
else:
    default_subtexts = ["Sweet Dreams", "Sleep Well"]

subtext_choice = st.selectbox("✨ Choose Subtext", default_subtexts)

branding_options = ["None", "Traveller Bharat", "Good Vibes", "Happy happy", "Bharattak"]
branding_choice = st.selectbox("📢 Choose Facebook Page Branding", branding_options)

font_size = st.slider("🔠 Main Text Font Size", min_value=60, max_value=150, value=100, step=5)
subtext_size = int(font_size * 0.5)

add_shadow = st.checkbox("🌟 Add Shadow Effect Randomly", value=True)

download_mode = st.radio("📥 Choose Download Mode", ["Individual Images", "ZIP of All Images"])

# === Helper functions ===
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
    """Safe text sizing for PIL versions"""
    try:
        return font.getsize(text)
    except AttributeError:
        # Newer PIL uses textbbox
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

# === Generate button ===
if st.button("✅ Generate Edited Images"):
    if not (uploaded_images and logo_file):
        st.warning("⚠️ Please upload logo and images before clicking Generate.")
    else:
        with st.spinner("Processing images..."):
            # Prepare logo
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((150, 150))

            # Load fonts
            fonts = []
            if font_files:
                for f in font_files:
                    fonts.append(io.BytesIO(f.read()))

            output_images = []

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # === Safe font selection
                if fonts:
                    try:
                        font_stream = random.choice(fonts)
                        font_stream.seek(0)
                        main_font = ImageFont.truetype(font_stream, size=font_size)
                        sub_font = ImageFont.truetype(font_stream, size=subtext_size)
                    except Exception:
                        main_font = ImageFont.load_default()
                        sub_font = ImageFont.load_default()
                else:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()

                # Main text: Greeting + Branding
                main_text = greeting_choice
                if branding_choice != "None":
                    main_text += f" - {branding_choice}"

                # Random color
                text_color = tuple(random.randint(100, 255) for _ in range(3))

                # Decide shadow on/off randomly if enabled
                shadow_enabled = add_shadow and random.choice([True, False])

                # Random position for main text
                main_text_size = get_text_size(draw, main_text, main_font)
                x, y = get_random_position(img.size, main_text_size)

                # Draw shadow if enabled
                if shadow_enabled:
                    for dx in [-2, -1, 0, 1, 2]:
                        for dy in [-2, -1, 0, 1, 2]:
                            if dx != 0 or dy != 0:
                                draw.text((x+dx, y+dy), main_text, font=main_font, fill="black")

                # Draw main text
                draw.text((x, y), main_text, font=main_font, fill=text_color)

                # Subtext position: below main text
                sub_x = x + 10
                sub_y = y + main_text_size[1] + 10
                sub_color = tuple(random.randint(100, 255) for _ in range(3))
                draw.text((sub_x, sub_y), subtext_choice, font=sub_font, fill=sub_color)

                # Paste logo at bottom-right
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                img.paste(logo, (img_w - logo_w - 10, img_h - logo_h - 10), mask=logo)

                output_images.append((img_file.name, img))

        st.success("✅ All images processed successfully!")

        # === Show previews and download buttons ===
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
            # Create ZIP
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
