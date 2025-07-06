import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

DEFAULT_FONT_PATH = "default.ttf"

st.set_page_config(
    page_title="🌟 SHIVAM TOOL",
    layout="centered",
    page_icon="🧿"
)

st.markdown(
    """
    <div style='background: linear-gradient(to right, #2c3e50, #3498db); padding: 20px; border-radius: 12px; text-align: center;'>
        <h1 style='color: yellow; font-size: 60px; margin: 0;'>SHIVAM TOOL™</h1>
        <h4 style='color: white; margin-top: 10px;'>EDIT PHOTOS IN ONE CLICK – Premium Free Tool</h4>
        <p style='color: #eee;'>Designed with ❤️ by Shivam Bind</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -- Uploaders front & center
st.subheader("📌 Upload Zone")
logo_file = st.file_uploader("✅ Watermark/Logo (PNG recommended)", type=["png"])
font_files = st.file_uploader("🔠 Custom Fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("🖼️ Images to Edit", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.markdown("---")

st.subheader("✏️ Text Options")
text_choice = st.selectbox("✅ Choose greeting text:", ["Good Morning", "Good Night"])
extra_line = st.checkbox(
    "✅ Add optional line (e.g. Have a Nice Day / Sweet Dreams)"
)
if text_choice == "Good Morning":
    extra_default = "Have a Nice Day"
else:
    extra_default = "Sweet Dreams"

extra_text_input = ""
if extra_line:
    extra_text_input = st.text_input("✍️ Enter extra line text:", value=extra_default)

output_images = []

# -- Helper to crop 3:4
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

# -- Main button
if st.button("✅ Generate Edited Images"):
    if uploaded_images and logo_file:
        with st.spinner("🔄 Processing... Please wait."):

            # Load logo
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((200, 200))
            logo.putalpha(80)  # make it subtle

            # Load fonts
            fonts = []
            try:
                with open(DEFAULT_FONT_PATH, "rb") as f:
                    fonts.append(io.BytesIO(f.read()))
            except FileNotFoundError:
                st.warning("⚠️ Default.ttf not found – will use system font.")

            for f in font_files or []:
                fonts.append(io.BytesIO(f.read()))

            # -- Process all images
            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # Random font
                font_stream = random.choice(fonts) if fonts else None

                # Random size & style
                font_size = random.randint(60, 90)
                if font_stream:
                    font_stream.seek(0)
                    try:
                        font = ImageFont.truetype(font_stream, size=font_size)
                    except:
                        font = ImageFont.load_default()
                else:
                    font = ImageFont.load_default()

                # Random color / gradient
                if random.random() < 0.3:
                    # From image
                    avg_color = tuple(map(int, img.resize((1, 1)).getpixel((0, 0))))
                    text_color = avg_color
                else:
                    text_color = tuple(random.randint(50, 255) for _ in range(3))

                # Random shadow/outline
                if random.random() < 0.7:
                    shadow_color = "black"
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((30+dx, 50+dy), text_choice, font=font, fill=shadow_color)

                draw.text((30, 50), text_choice, font=font, fill=text_color)

                # Extra line
                if extra_line and extra_text_input.strip():
                    small_font_size = int(font_size * 0.5)
                    if font_stream:
                        font_stream.seek(0)
                        try:
                            small_font = ImageFont.truetype(font_stream, size=small_font_size)
                        except:
                            small_font = ImageFont.load_default()
                    else:
                        small_font = ImageFont.load_default()

                    if random.random() < 0.7:
                        for dx in [-1, 1]:
                            for dy in [-1, 1]:
                                draw.text((35+dx, 50+font_size+10+dy), extra_text_input, font=small_font, fill="black")
                    draw.text((35, 50+font_size+10), extra_text_input, font=small_font, fill=text_color)

                # Paste watermark bottom right
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                img.paste(logo, (img_w - logo_w - 15, img_h - logo_h - 15), mask=logo)

                output_images.append((img_file.name, img))

        # -- ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.success("✅ All images processed successfully!")
        st.download_button("📦 Download All Images as ZIP", data=zip_buffer.getvalue(), file_name="Shivam_Greetings.zip", mime="application/zip")

        # -- Direct individual download preview
        st.subheader("✅ Preview & Download Individually")
        for name, image in output_images:
            st.image(image, caption=name, use_column_width=True)
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="JPEG", quality=95)
            st.download_button(f"⬇️ Download {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")

    else:
        st.warning("⚠️ Please upload logo and images before generating!")

