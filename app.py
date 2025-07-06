import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

DEFAULT_FONT_PATH = "default.ttf"

st.set_page_config(
    page_title="🌟 GOOD VIBES",
    layout="centered",
    page_icon="✨"
)

st.markdown(
    """
    <div style='background: linear-gradient(to right, #ff7e5f, #feb47b); padding: 20px; border-radius: 12px; text-align: center;'>
        <h1 style='color: #fff700; font-size: 58px; margin: 0;'>GOOD VIBES</h1>
        <h4 style='color: white; margin-top: 10px;'>EDIT PHOTO IN ONE CLICK – Premium Free Tool</h4>
        <p style='color: #f0f0f0;'>Designed with ❤️ for Creators</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -- Upload Zone
st.subheader("📌 Upload Your Assets")
logo_file = st.file_uploader("✅ Watermark/Logo (PNG preferred)", type=["png"])
font_files = st.file_uploader("🔠 Custom Fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("🖼️ Images to Edit", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.markdown("---")

st.subheader("✏️ Text Options")
text_choice = st.selectbox("✅ Choose greeting text:", ["Good Morning", "Good Night"])
extra_line_checkbox = st.checkbox("✅ Add optional line (e.g. Have a Nice Day / Sweet Dreams)")

if text_choice == "Good Morning":
    extra_default = "Have a Nice Day"
else:
    extra_default = "Sweet Dreams"

extra_text_input = ""
if extra_line_checkbox:
    extra_text_input = st.text_input("✍️ Enter extra line text:", value=extra_default)

# -- Load Fonts
available_fonts = []
font_names = []

try:
    with open(DEFAULT_FONT_PATH, "rb") as f:
        default_font_bytes = io.BytesIO(f.read())
        available_fonts.append(("Default Font", default_font_bytes))
        font_names.append("Default Font")
except FileNotFoundError:
    st.warning("⚠️ default.ttf not found. System fallback will be used.")

for uploaded_font in font_files or []:
    font_bytes = io.BytesIO(uploaded_font.read())
    font_label = os.path.splitext(uploaded_font.name)[0]
    available_fonts.append((font_label, font_bytes))
    font_names.append(font_label)

if available_fonts:
    selected_font_label = st.selectbox("🔠 Choose font for text:", font_names)
    selected_font_bytes = dict(available_fonts)[selected_font_label]
else:
    selected_font_bytes = None

# -- Helper to crop
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

# -- High-contrast / premium colors
PREMIUM_COLORS = [
    "#ffffff", "#f1c40f", "#e74c3c", "#9b59b6",
    "#3498db", "#1abc9c", "#2ecc71", "#e67e22",
    "#ecf0f1", "#fd79a8", "#ffeaa7", "#fab1a0"
]

def get_random_premium_color():
    return random.choice(PREMIUM_COLORS)

output_images = []

# -- Main button
if st.button("✅ Generate Edited Images"):
    if uploaded_images and logo_file:
        with st.spinner("🔄 Processing... Please wait."):

            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((200, 200))
            logo.putalpha(60)  # subtle

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # Load selected font
                font_size = random.randint(60, 85)
                if selected_font_bytes:
                    try:
                        selected_font_bytes.seek(0)
                        main_font = ImageFont.truetype(selected_font_bytes, size=font_size)
                    except:
                        main_font = ImageFont.load_default()
                else:
                    main_font = ImageFont.load_default()

                # Text color (premium random)
                text_color = get_random_premium_color()

                # Shadow
                if random.random() < 0.7:
                    shadow_color = "black"
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((30+dx, 50+dy), text_choice, font=main_font, fill=shadow_color)

                draw.text((30, 50), text_choice, font=main_font, fill=text_color)

                # Extra line
                if extra_line_checkbox and extra_text_input.strip():
                    small_font_size = int(font_size * 0.5)
                    if selected_font_bytes:
                        try:
                            selected_font_bytes.seek(0)
                            extra_font = ImageFont.truetype(selected_font_bytes, size=small_font_size)
                        except:
                            extra_font = ImageFont.load_default()
                    else:
                        extra_font = ImageFont.load_default()

                    extra_color = get_random_premium_color()
                    if random.random() < 0.6:
                        for dx in [-1, 1]:
                            for dy in [-1, 1]:
                                draw.text((35+dx, 50+font_size+10+dy), extra_text_input, font=extra_font, fill="black")
                    draw.text((35, 50+font_size+10), extra_text_input, font=extra_font, fill=extra_color)

                # Paste watermark
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
        st.download_button("📦 Download All as ZIP", data=zip_buffer.getvalue(), file_name="GoodVibes_Greetings.zip", mime="application/zip")

        # -- Direct previews
        st.subheader("✅ Preview & Download Individually")
        for name, image in output_images:
            st.image(image, caption=name, use_column_width=True)
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="JPEG", quality=95)
            st.download_button(f"⬇️ Download {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")

    else:
        st.warning("⚠️ Please upload logo and images first!")

