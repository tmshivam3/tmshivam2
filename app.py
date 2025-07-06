import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import random
import os

DEFAULT_FONT_PATH = "default.ttf"

# =============== PAGE CONFIG ===================
st.set_page_config(
    page_title="🌟 SHIVAM TOOL™",
    page_icon="🧿",
    layout="centered"
)

# =============== HEADER ===================
st.markdown(
    """
    <div style='background: linear-gradient(to right, #2c3e50, #3498db); padding: 20px; border-radius: 12px; text-align: center;'>
        <h1 style='color: yellow; font-size: 60px; margin: 0;'>SHIVAM TOOL™</h1>
        <h4 style='color: white; margin-top: 10px;'>PREMIUM PHOTO GREETING & WATERMARK GENERATOR</h4>
        <p style='color: #eee;'>Designed with ❤️ by Shivam Bind</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# =============== UPLOAD ZONE ===================
st.subheader("📌 Upload Zone")
logo_file = st.file_uploader("✅ Watermark Logo (PNG recommended)", type=["png"])
font_files = st.file_uploader("🔠 Upload Custom Fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("🖼️ Images to Edit", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.markdown("---")

# =============== TEXT OPTIONS ===================
st.subheader("✏️ Greeting Text")
text_choice = st.selectbox("✅ Choose Greeting", ["Good Morning", "Good Night", "Custom"])
if text_choice == "Custom":
    main_text = st.text_input("🖋️ Enter Your Custom Greeting", "").strip() or "Your Greeting"
else:
    main_text = text_choice

extra_line = st.checkbox("✅ Add Extra Line (optional)")
extra_text_input = ""
if extra_line:
    default_extra = "Have a Nice Day" if text_choice == "Good Morning" else "Sweet Dreams"
    extra_text_input = st.text_input("✍️ Enter Extra Line", value=default_extra)

st.markdown("---")

# =============== STYLE OPTIONS ===================
st.subheader("🎨 Watermark Options")
opacity = st.slider("Logo Opacity (%)", 10, 100, 70)
position_choice = st.selectbox("Logo Position", ["Bottom Right", "Bottom Left", "Top Right", "Top Left"])

st.markdown("---")

# =============== HELPER FUNCTIONS ===================
def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_font(size, custom_fonts=None):
    choices = []
    if custom_fonts:
        choices.extend(custom_fonts)
    if os.path.exists(DEFAULT_FONT_PATH):
        with open(DEFAULT_FONT_PATH, "rb") as f:
            choices.append(io.BytesIO(f.read()))
    if not choices:
        return ImageFont.load_default()
    selected = random.choice(choices)
    selected.seek(0)
    try:
        return ImageFont.truetype(selected, size=size)
    except:
        return ImageFont.load_default()

def paste_logo(img, logo, pos_choice, opacity_pct):
    img_w, img_h = img.size
    logo = logo.copy()
    logo.thumbnail((200, 200))
    alpha = logo.split()[3]
    alpha = alpha.point(lambda p: int(p * (opacity_pct / 100)))
    logo.putalpha(alpha)
    positions = {
        "Bottom Right": (img_w - logo.width - 15, img_h - logo.height - 15),
        "Bottom Left": (15, img_h - logo.height - 15),
        "Top Right": (img_w - logo.width - 15, 15),
        "Top Left": (15, 15)
    }
    img.paste(logo, positions[pos_choice], logo)

def random_color():
    # pick bright/pastelish color
    return tuple(random.randint(100, 255) for _ in range(3))

def random_position(img_w, img_h, font_size):
    choices = ["top", "middle", "bottom"]
    pick = random.choice(choices)
    if pick == "top":
        return 30
    elif pick == "middle":
        return img_h // 2 - font_size // 2
    else:
        return img_h - font_size - 100

# =============== MAIN PROCESS ===================
if st.button("✅ Generate Edited Images"):
    if not uploaded_images or not logo_file:
        st.warning("⚠️ Please upload images and a logo!")
    else:
        with st.spinner("🔄 Processing Images..."):
            # Load logo
            logo = Image.open(logo_file).convert("RGBA")

            # Load custom fonts
            custom_fonts_streams = []
            if font_files:
                for f in font_files:
                    custom_fonts_streams.append(io.BytesIO(f.read()))

            output_images = []
            for img_file in uploaded_images:
                try:
                    img = Image.open(img_file).convert("RGB")
                    img = crop_to_3_4(img)
                    draw = ImageDraw.Draw(img)
                    img_w, img_h = img.size

                    # Random font & color
                    main_font_size = random.randint(60, 100)
                    font_main = get_font(main_font_size, custom_fonts_streams)
                    color_main = random_color()

                    # Random position Y
                    y_pos = random_position(img_w, img_h, main_font_size)

                    # Draw main text
                    draw.text((30, y_pos), main_text, font=font_main, fill=color_main)

                    # Draw extra line if any
                    if extra_line and extra_text_input.strip():
                        font_extra = get_font(int(main_font_size * 0.6), custom_fonts_streams)
                        color_extra = random_color()
                        draw.text((35, y_pos + main_font_size + 10), extra_text_input.strip(), font=font_extra, fill=color_extra)

                    # Paste watermark
                    paste_logo(img, logo, position_choice, opacity)

                    output_images.append((img_file.name, img))
                except Exception as e:
                    st.error(f"❌ Error processing {img_file.name}: {e}")

            if output_images:
                # Create zip
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for name, image in output_images:
                        img_bytes = io.BytesIO()
                        image.save(img_bytes, format="JPEG", quality=95)
                        zipf.writestr(name, img_bytes.getvalue())

                st.success("✅ All images processed successfully!")
                st.download_button("📦 Download All Images as ZIP", data=zip_buffer.getvalue(), file_name="Shivam_Greetings.zip", mime="application/zip")

                # Individual download
                st.subheader("✅ Preview & Download Individually")
                for name, image in output_images:
                    st.image(image, caption=name, use_column_width=True)
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format="JPEG", quality=95)
                    st.download_button(f"⬇️ Download {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")
            else:
                st.warning("⚠️ No images were processed!")

