import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import zipfile
import random
import os

DEFAULT_FONT_PATH = "default.ttf"

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="🌟 GOOD VIBES STUDIO™",
    page_icon="🧿",
    layout="centered"
)

# ==================== HEADER ====================
st.markdown(
    """
    <div style='background: linear-gradient(to right, #6a11cb, #2575fc); padding: 20px; border-radius: 12px; text-align: center;'>
        <h1 style='color: #fff; font-size: 50px; margin: 0;'>GOOD VIBES STUDIO™</h1>
        <h4 style='color: #ddd; margin-top: 10px;'>Your PicksArt-Style Bulk Photo Editor</h4>
        <p style='color: #ccc;'>Designed with ❤️ by Shivam Bind</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ==================== SIDEBAR UPLOAD ====================
st.sidebar.title("📌 Upload Your Assets")

uploaded_images = st.sidebar.file_uploader(
    "🖼️ Upload Multiple Photos", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

uploaded_fonts = st.sidebar.file_uploader(
    "🔤 Upload Custom Fonts (.ttf/.otf)", 
    type=["ttf", "otf"], 
    accept_multiple_files=True
)

logo_file = st.sidebar.file_uploader(
    "🌟 Upload Logo/Watermark (PNG)", 
    type=["png"]
)

st.sidebar.markdown("---")

# ==================== THEME SELECTION ====================
st.sidebar.header("🎨 Choose a Theme")
theme = st.sidebar.selectbox("Theme", ["Good Morning", "Good Night", "Love", "Custom"])

# Predefined color palettes
theme_colors = {
    "Good Morning": [(255, 223, 186), (255, 182, 193), (255, 255, 255)],
    "Good Night": [(255, 255, 255), (173, 216, 230), (192, 192, 192)],
    "Love": [(255, 105, 180), (255, 0, 0), (255, 182, 193)],
    "Custom": [(255, 255, 255)]
}

if theme == "Custom":
    custom_color = st.sidebar.color_picker("Pick Text Color", "#ffffff")
    user_color = tuple(int(custom_color.strip("#")[i:i+2], 16) for i in (0, 2 ,4))
else:
    user_color = None

st.sidebar.markdown("---")

# ==================== TEXT SETTINGS ====================
st.sidebar.header("🖊️ Text Options")

if theme in ["Good Morning", "Good Night"]:
    main_text_default = theme
else:
    main_text_default = "Your Greeting"

main_text = st.sidebar.text_input("Main Text", value=main_text_default)

extra_line_toggle = st.sidebar.checkbox("Add Extra Line")
extra_line_text = ""
if extra_line_toggle:
    extra_line_text = st.sidebar.text_input("Extra Line Text", value="Have a Nice Day")

# ==================== WATERMARK SETTINGS ====================
st.sidebar.header("💧 Watermark Settings")
logo_opacity = st.sidebar.slider("Logo Opacity (%)", 10, 100, 70)
logo_position = st.sidebar.selectbox("Logo Position", ["Bottom Right", "Bottom Left", "Top Right", "Top Left"])

st.sidebar.markdown("---")
st.sidebar.success("✅ All settings loaded!")

# ==================== HELPER FUNCTIONS ====================
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

def get_font(size, fonts):
    choices = []
    if fonts:
        choices.extend(fonts)
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

def random_position(img_w, img_h, font_size):
    y_choices = ["top", "middle", "bottom"]
    y_pick = random.choice(y_choices)
    if y_pick == "top":
        return 30
    elif y_pick == "middle":
        return img_h // 2 - font_size // 2
    else:
        return img_h - font_size - 100

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

def choose_color():
    if theme == "Custom":
        return user_color
    else:
        return random.choice(theme_colors[theme])

# ==================== MAIN BUTTON ====================
st.markdown("---")
if st.button("✅ Generate Edited Images in Bulk"):
    if not uploaded_images:
        st.warning("⚠️ Please upload at least one photo.")
    else:
        with st.spinner("🔄 Processing Images... Please wait."):
            output_images = []
            logo = None
            if logo_file:
                logo = Image.open(logo_file).convert("RGBA")
            
            custom_fonts = []
            if uploaded_fonts:
                for f in uploaded_fonts:
                    custom_fonts.append(io.BytesIO(f.read()))

            for img_file in uploaded_images:
                try:
                    img = Image.open(img_file).convert("RGB")
                    img = crop_to_3_4(img)
                    draw = ImageDraw.Draw(img)

                    img_w, img_h = img.size
                    font_size = random.randint(60, 100)
                    font = get_font(font_size, custom_fonts)

                    color_main = choose_color()
                    y_pos = random_position(img_w, img_h, font_size)
                    draw.text((30, y_pos), main_text, font=font, fill=color_main)

                    if extra_line_toggle and extra_line_text.strip():
                        extra_font = get_font(int(font_size * 0.6), custom_fonts)
                        extra_color = choose_color()
                        draw.text((35, y_pos + font_size + 10), extra_line_text.strip(), font=extra_font, fill=extra_color)

                    if logo:
                        paste_logo(img, logo, logo_position, logo_opacity)

                    output_images.append((img_file.name, img))

                except Exception as e:
                    st.error(f"❌ Error processing {img_file.name}: {e}")

        # ============= DOWNLOAD SECTION =============
        if output_images:
            st.success("✅ All images processed successfully!")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for name, image in output_images:
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format="JPEG", quality=95)
                    zipf.writestr(name, img_bytes.getvalue())

            st.download_button(
                "📦 Download All Images as ZIP",
                data=zip_buffer.getvalue(),
                file_name="Good_Vibes_Bulk.zip",
                mime="application/zip"
            )

            st.subheader("✅ Preview & Download Individually")
            for name, image in output_images:
                st.image(image, caption=name, use_column_width=True)
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                st.download_button(
                    f"⬇️ Download {name}",
                    data=img_bytes.getvalue(),
                    file_name=name,
                    mime="image/jpeg"
                )

