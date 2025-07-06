import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

# -- PAGE CONFIG --
st.set_page_config(page_title="🔆 SHIVAM TOOL ™", layout="wide")

# -- STYLES --
st.markdown("""
<style>
body {
    background-color: #1a1a1a;
}
header, .css-18e3th9, .css-h5rgaw {
    background: linear-gradient(90deg, #000000, #111111, #222222) !important;
}
section.main {
    background-color: #111;
    color: #EEE;
}
.block-container {
    padding: 2rem 2rem;
}
h1, h2, h3 {
    color: gold;
}
.stButton>button {
    background-color: gold;
    color: black;
    border-radius: 10px;
    font-weight: bold;
}
.stDownloadButton>button {
    background-color: #ff8800;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -- HEADER --
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(90deg, black, #111111, black); border-radius: 12px;'>
    <h1>🔆 SHIVAM TOOL ™</h1>
    <h4 style='color: silver;'>EDIT PHOTO IN ONE CLICK | Make premium greeting images instantly</h4>
</div>
""", unsafe_allow_html=True)


# -- FILE UPLOADS SECTION --
st.subheader("📌 Upload Your Files (All in One Place)")

col1, col2, col3 = st.columns(3)
with col1:
    logo_file = st.file_uploader("🔖 Upload Watermark/Logo (PNG)", type=["png"])
with col2:
    font_files = st.file_uploader("🔠 Upload Custom Fonts (Optional)", type=["ttf", "otf"], accept_multiple_files=True)
with col3:
    texture_images = st.file_uploader("🌈 Upload Texture Images (Optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

uploaded_images = st.file_uploader("🖼️ Upload Photos to Edit", type=["jpg", "jpeg", "png"], accept_multiple_files=True)


# -- OPTIONS SECTION --
st.markdown("---")
st.subheader("⚙️ Choose Your Greeting Options")

col4, col5 = st.columns(2)
with col4:
    greeting_choice = st.radio("🌅 Choose Greeting Text:", ["Good Morning", "Good Night"])
with col5:
    add_subtext = st.checkbox("✨ Add Subtext")

selected_subtext = None
if add_subtext:
    if greeting_choice == "Good Morning":
        selected_subtext = st.selectbox("Select Subtext", ["Have a Nice Day", "Have a Great Day"])
    else:
        selected_subtext = st.selectbox("Select Subtext", ["Sweet Dream"])

# -- DEFAULT FONT PATH --
DEFAULT_FONT_PATH = "default.ttf"

# -- CROP FUNCTION --
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

# -- MAIN BUTTON --
st.markdown("---")
st.subheader("✅ Ready to Make?")

output_images = []
if st.button("✨ EDIT IMAGES IN ONE CLICK"):
    if uploaded_images and logo_file:
        with st.spinner("🧪 Generating Premium Images..."):

            # Load logo
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((300, 300))
            logo.putalpha(80)

            # Load fonts
            fonts = []
            if font_files:
                for f in font_files:
                    fonts.append(io.BytesIO(f.read()))
            else:
                with open(DEFAULT_FONT_PATH, "rb") as f:
                    fonts.append(io.BytesIO(f.read()))

            # Load textures
            textures = []
            if texture_images:
                for t in texture_images:
                    textures.append(Image.open(t).convert("RGB"))

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # Font & size
                font_stream = random.choice(fonts)
                font_stream.seek(0)
                size = random.randint(90, 140)
                font = ImageFont.truetype(font_stream, size=size)

                # Color, position, style
                base_color = get_random_color()
                pos = (30, 30)
                use_shadow = random.random() > 0.3
                multi_color = random.random() > 0.4
                use_texture = (random.random() > 0.6) and textures
                texture_img = random.choice(textures) if use_texture else None

                # Main text
                draw_text_with_effects(draw, pos, greeting_choice, font, base_color, use_shadow, multi_color, texture_img)

                # Subtext
                if selected_subtext:
                    sub_font = ImageFont.truetype(font_stream, size=40)
                    sub_pos = (pos[0], pos[1] + size + 10)
                    draw.text(sub_pos, selected_subtext, font=sub_font, fill=(200, 200, 200))

                # Watermark
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                img.paste(logo, (img_w - logo_w - 20, img_h - logo_h - 20), mask=logo)

                # Signature
                sign_font = ImageFont.truetype(font_stream, size=30)
                sign_pos = (10, img_h - 40)
                draw.text(sign_pos, "™ SHIVAM", font=sign_font, fill=(180, 180, 180))

                output_images.append((img_file.name, img))

        st.success("✅ All Images Processed Successfully!")

        # -- PREVIEW SECTION --
        st.markdown("---")
        st.subheader("🔎 Preview & Download")

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

        # -- ZIP DOWNLOAD --
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.download_button(
            "📦 Download All Images (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="SHIVAM_TOOL_Images.zip",
            mime="application/zip"
        )

        st.markdown("<p style='text-align: center; color: grey; font-size: 12px;'>© 2025 SHIVAM TOOL™ - All Rights Reserved</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please upload at least images and logo to start.")

