import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import zipfile
import os
import random
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="🔆 SHIVAM TOOL ™", layout="centered")

# --- PREMIUM HEADER ---
st.markdown("""
    <div style='background-color: black; padding: 20px; border-radius: 12px; text-align: center;'>
        <h1 style='color: gold;'>🔆 SHIVAM TOOL ™</h1>
        <h4 style='color: silver;'>Premium Greeting Watermark Designer</h4>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR UPLOADS ---
st.sidebar.header("🛠️ Settings")
logo_file = st.sidebar.file_uploader("📌 Upload your watermark/logo (PNG recommended)", type=["png"])
font_files = st.sidebar.file_uploader("🔠 Upload custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.sidebar.file_uploader("🖼️ Upload images to process", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
texture_images = st.sidebar.file_uploader("🌈 Upload images for text texture (Optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# --- GREETING OPTIONS ---
greeting_choice = st.sidebar.radio("🌅 Choose Greeting:", ["Good Morning", "Good Night"])
add_subtext = st.sidebar.checkbox("✨ Add Subtext (e.g. Have a Nice Day / Sweet Dream)")
selected_subtext = None
if add_subtext:
    if greeting_choice == "Good Morning":
        selected_subtext = st.sidebar.selectbox("Choose subtext", ["Have a Nice Day", "Have a Great Day"])
    else:
        selected_subtext = st.sidebar.selectbox("Choose subtext", ["Sweet Dream"])

# --- DEFAULT FONT ---
DEFAULT_FONT_PATH = "default.ttf"

# --- HELPER FUNCTIONS ---
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

def get_random_color():
    return tuple(random.randint(80, 255) for _ in range(3))

def draw_text_with_effects(draw, position, text, font, base_color, use_shadow, multi_color, texture_img=None):
    x, y = position
    if use_shadow:
        for dx in [-3, 3]:
            for dy in [-3, 3]:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
    if texture_img:
        mask = Image.new("L", draw.im.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text(position, text, font=font, fill=255)
        texture_resized = texture_img.resize(draw.im.size).crop((0, 0, draw.im.size[0], draw.im.size[1]))
        draw.im.paste(texture_resized, mask=mask)
    elif multi_color:
        offset_x = 0
        for letter in text:
            color = get_random_color()
            draw.text((x + offset_x, y), letter, font=font, fill=color)
            offset_x += font.getlength(letter)
    else:
        draw.text((x, y), text, font=font, fill=base_color)

# --- GENERATE BUTTON ---
output_images = []
if st.sidebar.button("✅ Generate Images"):
    if uploaded_images and logo_file:
        with st.spinner("🧪 Generating Premium Images..."):
            # --- Load logo ---
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((250, 250))
            logo.putalpha(100)

            # --- Load fonts ---
            fonts = []
            if font_files:
                for f in font_files:
                    fonts.append(io.BytesIO(f.read()))
            else:
                with open(DEFAULT_FONT_PATH, "rb") as f:
                    fonts.append(io.BytesIO(f.read()))

            # --- Load textures ---
            textures = []
            if texture_images:
                for t in texture_images:
                    textures.append(Image.open(t).convert("RGB"))

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # --- Font and size ---
                font_stream = random.choice(fonts)
                font_stream.seek(0)
                size = random.randint(90, 140)
                font = ImageFont.truetype(font_stream, size=size)

                # --- Colors & Position ---
                base_color = get_random_color()
                positions = [
                    (30, 30),
                    (img.width // 2 - size * 2, img.height // 2 - size // 2)
                ]
                pos = random.choice(positions)

                # --- Style choices ---
                use_shadow = random.random() > 0.3
                multi_color = random.random() > 0.4
                use_texture = (random.random() > 0.6) and textures
                texture_img = random.choice(textures) if use_texture else None

                # --- Main Greeting ---
                draw_text_with_effects(draw, pos, greeting_choice, font, base_color, use_shadow, multi_color, texture_img)

                # --- Subtext ---
                if selected_subtext:
                    sub_font = ImageFont.truetype(font_stream, size=40)
                    sub_pos = (pos[0], pos[1] + size + 10)
                    draw.text(sub_pos, selected_subtext, font=sub_font, fill=(200, 200, 200))

                # --- Paste logo watermark ---
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                img.paste(logo, (img_w - logo_w - 20, img_h - logo_h - 20), mask=logo)

                # --- TM SHIVAM Signature ---
                sign_font = ImageFont.truetype(font_stream, size=30)
                sign_pos = (10, img_h - 40)
                draw.text(sign_pos, "™ SHIVAM", font=sign_font, fill=(180, 180, 180))

                output_images.append((img_file.name, img))

            # --- Create ZIP ---
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for name, image in output_images:
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format="JPEG", quality=95)
                    zipf.writestr(name, img_bytes.getvalue())

        st.success("✅ All images processed successfully!")

        # --- Show PREVIEW & Individual Downloads ---
        st.subheader("🔎 Preview & Download Images")

        for idx, (name, image) in enumerate(output_images):
            st.image(image, caption=f"Preview: {name}", use_column_width=True)
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="JPEG", quality=95)
            img_bytes.seek(0)
            st.download_button(
                label=f"📥 Download {name}",
                data=img_bytes,
                file_name=name,
                mime="image/jpeg",
                key=f"download_{idx}"
            )

        # --- ZIP Download Button ---
        st.download_button(
            "📦 Download All Images (ZIP)", 
            data=zip_buffer.getvalue(), 
            file_name="SHIVAM_TOOL_Images.zip", 
            mime="application/zip"
        )

        # --- Footer ---
        st.markdown("<p style='text-align: center; color: grey; font-size: 12px;'>© 2025 SHIVAM TOOL™ - All Rights Reserved</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please upload at least images and logo to start.")
