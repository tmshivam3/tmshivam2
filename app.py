import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# CONFIG
st.set_page_config(page_title="Edit Photo in Bulk Tool ™ 🌟", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🌟 Edit Photo in Bulk Tool ™ 🌟</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# UTILITY FUNCTIONS
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

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

def get_random_position(w, h, text_w, text_h):
    # Top-left, top-right, bottom-left, bottom-right, center
    zones = [
        (random.randint(10, w//4), random.randint(10, h//4)), # top-left
        (random.randint(3*w//4, w - text_w - 10), random.randint(10, h//4)), # top-right
        (random.randint(10, w//4), random.randint(3*h//4, h - text_h - 10)), # bottom-left
        (random.randint(3*w//4, w - text_w - 10), random.randint(3*h//4, h - text_h - 10)), # bottom-right
    ]
    if random.random() < 0.05:
        center_x = (w - text_w) // 2
        center_y = (h - text_h) // 2
        zones.append((center_x, center_y))
    return random.choice(zones)

# DATA
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

morning_wishes = [
    "Have a Great Day!", "Rise & Shine!", "Enjoy Your Morning!",
    "New Day, New Hopes", "Smile Today :)", "Embrace the Sunshine!"
]
night_wishes = [
    "Sweet Dreams", "Good Night, Sleep Tight", "Stars Watching Over You",
    "Peaceful Sleep Ahead", "Rest Well", "Moonlight Hugs"
]

# SIDEBAR
st.sidebar.header("🎨 Tool Settings")

greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
random_subtext = random.choice(morning_wishes if greeting_type == "Good Morning" else night_wishes)

user_subtext = st.sidebar.text_input("Wishes Text", random_subtext)
coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 2, 20, 8)
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
date_size_factor = st.sidebar.slider("Date Size", 30, 120, 70)

logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Own Watermark"])
logo_path = os.path.join("assets/logos", logo_choice) if logo_choice != "Own Watermark" else None
if logo_choice == "Own Watermark":
    logo_path = st.sidebar.file_uploader("Upload Custom Logo", type=["png"])

font_source = st.sidebar.radio("Font Source", ["Available Fonts", "Upload Font"])
selected_font = st.sidebar.selectbox("Choose Font", available_fonts) if font_source == "Available Fonts" else None
uploaded_font = st.sidebar.file_uploader("Upload .ttf/.otf Font", type=["ttf", "otf"]) if font_source != "Available Fonts" else None

multiple_variants = st.sidebar.checkbox("Generate 4 Variants per Image", value=False)

# IMAGE UPLOAD
uploaded_images = st.file_uploader("🖼️ Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ERROR DISPLAY
def display_error(e):
    st.error(f"⚠️ Error Occurred: {str(e)}")

# ZIP CREATION
def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_name, variants in images:
            for img in variants:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                file_name = f"Picsart_{timestamp}.png"
                zipf.writestr(file_name, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# MAIN FUNCTION
if st.button("✅ Generate Images"):
    if uploaded_images:
        try:
            with st.spinner("Processing Images..."):
                logo = Image.open(logo_path).convert("RGBA") if logo_path else None
                if logo:
                    logo.thumbnail((225, 225))

                font_path = os.path.join("assets/fonts", selected_font) if selected_font else uploaded_font
                if uploaded_font:
                    font_bytes = io.BytesIO(uploaded_font.read())
                else:
                    font_bytes = font_path

                def render_variant(img, seed=None):
                    random.seed(seed)
                    img = crop_to_3_4(img)
                    draw = ImageDraw.Draw(img)

                    img_w, img_h = img.size
                    main_area = (coverage_percent / 100) * img_w * img_h
                    main_font_size = max(30, int((main_area)**0.5 * 0.6))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    font = ImageFont.truetype(font_bytes, main_font_size) if isinstance(font_bytes, str) else ImageFont.truetype(font_bytes, main_font_size)
                    sub_font = ImageFont.truetype(font_bytes, sub_font_size) if isinstance(font_bytes, str) else ImageFont.truetype(font_bytes, sub_font_size)
                    date_font = ImageFont.truetype(font_bytes, date_font_size) if isinstance(font_bytes, str) else ImageFont.truetype(font_bytes, date_font_size)

                    # Text Width/Height
                    greeting_text = greeting_type
                    text_w, text_h = draw.textbbox((0, 0), greeting_text, font=font)[2:]
                    x, y = get_random_position(img_w, img_h, text_w, text_h)

                    shadow = "black"
                    color = random.choice([(255,255,0), (255,255,255), (255,0,0), (0,255,0), (255,192,203)])
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((x+dx, y+dy), greeting_text, font=font, fill=shadow)
                    draw.text((x, y), greeting_text, font=font, fill=color)

                    # Subtext
                    draw.text((x+10, y + text_h + 10), user_subtext, font=sub_font, fill=color)

                    # Date
                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        draw.text((10, img_h - date_font_size - 10), today, font=date_font, fill="white")

                    # Logo
                    if logo:
                        img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), logo)

                    return img

                all_outputs = []
                for file in uploaded_images:
                    image = Image.open(file).convert("RGB")
                    variants = [render_variant(image.copy(), seed=random.randint(0, 9999)) for _ in range(4)] if multiple_variants else [render_variant(image)]
                    all_outputs.append((file.name, variants))

                # Display + Download
                for name, vars in all_outputs:
                    for img in vars:
                        st.image(img, use_column_width=True)
                        buffer = io.BytesIO()
                        img.save(buffer, format="PNG")
                        timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                        filename = f"Picsart_{timestamp}.png"
                        st.download_button("⬇️ Download", data=buffer.getvalue(), file_name=filename, mime="image/png")

                if st.button("⬇️ Download All as ZIP"):
                    zip_file = create_zip(all_outputs)
                    st.download_button("Download ZIP", data=zip_file, file_name="Greetings.zip", mime="application/zip")

        except Exception as e:
            display_error(e)
    else:
        st.warning("⚠️ Please upload images first!")
