import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# --------------------------- CONFIG ---------------------------
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Create Beautiful Morning/Night Wishes with Fonts, Watermarks, and More</h4>
""", unsafe_allow_html=True)

# --------------------------- UTILITY FUNCTIONS ---------------------------
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

def safe_random_position(start, end):
    return start if end <= start else random.randint(start, end)

def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_name, variants in images:
            for i, variant in enumerate(variants):
                img_bytes = io.BytesIO()
                variant.save(img_bytes, format="PNG", quality=95)
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                file_name = f"Picsart_{timestamp}.png"
                zipf.writestr(file_name, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# --------------------------- ASSETS ---------------------------
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# --------------------------- SIDEBAR ---------------------------
st.sidebar.header("🔧 Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])

show_date = st.sidebar.checkbox("Add Date", value=True)
date_size_factor = st.sidebar.slider("Date Text Size %", 30, 150, 80)
coverage_percent = st.sidebar.slider("Main Text Coverage %", 2, 20, 8)

logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Own Logo"])
logo_path = os.path.join("assets/logos", logo_choice) if logo_choice != "Own Logo" else None
if logo_choice == "Own Logo":
    logo_path = st.sidebar.file_uploader("Upload Logo PNG", type="png")

font_source = st.sidebar.radio("Font Source", ["Available", "Upload Font"])
if font_source == "Available":
    selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
    uploaded_font = None
else:
    uploaded_font = st.sidebar.file_uploader("Upload Font", type=["ttf", "otf"])
    selected_font = None

variations = st.sidebar.checkbox("Generate 4 Variants per Image", value=False)

# --------------------------- TEXT POOLS ---------------------------
morning_wishes = ["Have a Great Day!", "Stay Positive!", "Rise and Shine", "Coffee Time ☕", "New Day, New Start", "Hello Sunshine!", "Be Awesome Today!", "Peaceful Morning 🌼"]
night_wishes = ["Sweet Dreams", "Good Night 🌙", "Sleep Tight", "Rest Well", "See You Tomorrow", "Silent Night", "Peaceful Sleep", "Starry Night 🌌"]

# --------------------------- MAIN APP ---------------------------
uploaded_images = st.file_uploader("📷 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("✨ Generate Images"):
    if not uploaded_images:
        st.warning("Please upload images first.")
    else:
        output_images = []
        try:
            logo = None
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA") if isinstance(logo_path, str) else Image.open(logo_path)
                logo.thumbnail((225, 225))

            font_path = os.path.join("assets/fonts", selected_font) if selected_font else uploaded_font
            if uploaded_font:
                font_bytes = io.BytesIO(uploaded_font.read())
            else:
                font_bytes = font_path

            def generate_variant(img, seed=None):
                random.seed(seed)
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)
                W, H = img.size
                area = (coverage_percent / 100) * W * H
                font_size = max(30, int((area)**0.5 * 0.6))
                sub_font_size = int(font_size * 0.5)
                date_font_size = int(font_size * date_size_factor / 100)

                if isinstance(font_bytes, str):
                    font = ImageFont.truetype(font_bytes, font_size)
                    sub_font = ImageFont.truetype(font_bytes, sub_font_size)
                    date_font = ImageFont.truetype(font_bytes, date_font_size)
                else:
                    font = ImageFont.truetype(font_bytes, font_size)
                    sub_font = ImageFont.truetype(font_bytes, sub_font_size)
                    date_font = ImageFont.truetype(font_bytes, date_font_size)

                main_text = greeting_type
                sub_text = random.choice(morning_wishes if "Morning" in greeting_type else night_wishes)

                x = safe_random_position(30, W - font_size * len(main_text) // 2 - 30)
                y = safe_random_position(30, H - font_size - 30)

                shadow = "black"
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), main_text, font=font, fill=shadow)
                draw.text((x, y), main_text, font=font, fill=random.choice([(255,255,255), (255,0,0), (255,255,0)]))

                draw.text((x+10, y + font_size + 10), sub_text, font=sub_font, fill="white")

                if show_date:
                    today = datetime.datetime.now().strftime("%d %B %Y")
                    dx = safe_random_position(10, W - 150)
                    dy = safe_random_position(10, H - 60)
                    draw.text((dx, dy), today, font=date_font, fill="white")

                if logo:
                    img.paste(logo, (W - logo.width - 10, H - logo.height - 10), logo)

                return img

            for file in uploaded_images:
                image = Image.open(file).convert("RGB")
                variants = []
                if variations:
                    for i in range(4):
                        variants.append(generate_variant(image.copy(), seed=random.randint(0,99999)))
                else:
                    variants = [generate_variant(image)]

                output_images.append((file.name, variants))

            st.success("✅ All images generated!")

            for name, variants in output_images:
                st.write(f"**{name}**")
                for i, v in enumerate(variants):
                    st.image(v, use_column_width=True)
                    img_io = io.BytesIO()
                    v.save(img_io, format="PNG")
                    st.download_button(f"⬇️ Download Variant {i+1}", img_io.getvalue(), file_name=f"Variant_{i+1}.png")

            zip_buffer = create_zip(output_images)
            st.download_button("⬇️ Download All as ZIP", zip_buffer, file_name="Generated_Wishes.zip", mime="application/zip")

        except Exception as e:
            st.error(f"❌ Error Occurred: {str(e)}")
