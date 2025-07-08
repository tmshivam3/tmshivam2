import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# ========== CONFIGURATION ==========
st.set_page_config(page_title="SHIVAM TOOL", layout="centered")

# ========== STYLES AND HEADINGS ==========
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            color: white;
            background-color: #111;
            padding: 15px;
            border-radius: 10px;
            font-size: 32px;
        }
        .sub-title {
            text-align: center;
            color: grey;
            font-size: 18px;
        }
        .footer {
            margin-top: 20px;
            font-size: 14px;
            text-align: center;
            color: grey;
        }
    </style>
    <div class='main-title'>🔆 SHIVAM TOOL - PREMIUM IMAGE GENERATOR 🔆</div>
    <div class='sub-title'>Create Good Morning/Good Night Designs with Watermarks, Fonts, Dates, and more</div>
""", unsafe_allow_html=True)

# ========== UTILITY FUNCTIONS ==========
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

def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_name, variants in images:
            for i, variant in enumerate(variants):
                img_bytes = io.BytesIO()
                variant.save(img_bytes, format="JPEG", quality=95)
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                file_name = f"{img_name}_var_{i+1}_{timestamp}.jpg"
                zipf.writestr(file_name, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def display_error_with_trace(error):
    st.error(f"❌ Error: {str(error)}")
    st.markdown("""
        <div style='background-color: red; padding: 10px; border-radius: 10px; text-align: center; font-size: 18px; color: white;'>
            Contact Developer: <a href='https://wa.me/9140588751' style='color: white;'>+91 9140588751</a>
        </div>
    """, unsafe_allow_html=True)

# ========== LOAD ASSETS ==========
logo_dir = "assets/logos"
font_dir = "assets/fonts"
available_logos = list_files(logo_dir, [".png"])
available_fonts = list_files(font_dir, [".ttf", ".otf"])

# ========== SIDEBAR SETTINGS ==========
st.sidebar.header("🛠️ Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
default_subtext = "Have a Nice Day" if greeting_type == "Good Morning" else "Sweet Dreams"
user_subtext = st.sidebar.text_input("Subtext (Wishes)", default_subtext)

coverage_percent = st.sidebar.slider("Main Text Area %", 2, 20, 8)
show_date = st.sidebar.checkbox("Show Today's Date", value=True)
date_size_factor = st.sidebar.slider("Date Size Factor", 30, 120, 70)

logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Upload Custom"])
logo_path = None
if logo_choice == "Upload Custom":
    logo_path = st.sidebar.file_uploader("Upload PNG Watermark", type=["png"])
else:
    logo_path = os.path.join(logo_dir, logo_choice)

font_source = st.sidebar.radio("Font Source", ["Use Available Fonts", "Upload Font"])
if font_source == "Use Available Fonts":
    selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
    font_path = os.path.join(font_dir, selected_font)
else:
    uploaded_font = st.sidebar.file_uploader("Upload Font", type=["ttf", "otf"])
    font_path = io.BytesIO(uploaded_font.read()) if uploaded_font else None

variations_enabled = st.sidebar.checkbox("Generate 4 Variants Per Image", value=False)

# ========== MAIN UPLOAD AREA ==========
uploaded_images = st.file_uploader("📤 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ========== PROCESSING BUTTON ==========
if st.button("✅ Generate Images"):
    if not uploaded_images:
        st.warning("⚠️ Please upload images first.")
    else:
        try:
            logo = None
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((225, 225))

            results = []

            def create_variant(image, seed=None):
                random.seed(seed)
                img = crop_to_3_4(image)
                draw = ImageDraw.Draw(img)

                img_w, img_h = img.size
                area = (coverage_percent / 100) * img_w * img_h
                main_font_size = max(30, int((area) ** 0.5 * 0.6))
                sub_font_size = int(main_font_size * 0.5)
                date_font_size = int(main_font_size * date_size_factor / 100)

                try:
                    main_font = ImageFont.truetype(font_path, main_font_size)
                    sub_font = ImageFont.truetype(font_path, sub_font_size)
                    date_font = ImageFont.truetype(font_path, date_font_size)
                except Exception as e:
                    display_error_with_trace(e)
                    return img

                safe_margin = 30
                text_color = random.choice([(255,255,255),(255,0,0),(255,255,0),(0,255,0),(255,105,180)])
                shadow_color = "black"

                # --- Main Text ---
                x = random.randint(safe_margin, img_w - main_font_size * len(greeting_type) // 2 - safe_margin)
                y = random.randint(safe_margin, img_h - main_font_size - safe_margin)
                for dx in [-2, 2]:
                    for dy in [-2, 2]:
                        draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                # --- Sub Text ---
                draw.text((x+10, y + main_font_size + 10), user_subtext, font=sub_font, fill=text_color)

                # --- Date ---
                if show_date:
                    today = datetime.datetime.now().strftime("%d %B %Y")
                    dx = random.randint(safe_margin, img_w - date_font_size * 10)
                    dy = random.randint(safe_margin, img_h - date_font_size)
                    for sx in [-2, 2]:
                        for sy in [-2, 2]:
                            draw.text((dx+sx, dy+sy), today, font=date_font, fill=shadow_color)
                    draw.text((dx, dy), today, font=date_font, fill=text_color)

                # --- Logo ---
                if logo and random.random() < 0.6:
                    for _ in range(10):
                        lx = random.randint(safe_margin, img_w - logo.width - safe_margin)
                        ly = random.randint(safe_margin, img_h - logo.height - safe_margin)
                        if not (lx < x + main_font_size * len(greeting_type) and ly < y + main_font_size):
                            img.paste(logo, (lx, ly), mask=logo)
                            break

                return img

            # ========== LOOP IMAGES ==========
            for img_file in uploaded_images:
                image = Image.open(img_file).convert("RGB")
                variants = []
                if variations_enabled:
                    for i in range(4):
                        variant = create_variant(image.copy(), seed=random.randint(0, 99999))
                        variants.append(variant)
                else:
                    variants = [create_variant(image)]

                results.append((img_file.name, variants))

            st.success("✅ Processing Complete")

            # ========== DISPLAY AND DOWNLOAD ==========
            for name, variants in results:
                for i, img in enumerate(variants):
                    st.image(img, caption=f"{name} - Variant {i+1}", use_container_width=True)
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG")
                    timestamp = datetime.datetime.now().strftime("%H%M%S%f")
                    file_name = f"IMG_{timestamp}.jpg"
                    st.download_button("⬇️ Download Image", data=img_bytes.getvalue(), file_name=file_name, mime="image/jpeg")

            # Download All as ZIP
            zip_data = create_zip(results)
            st.download_button("⬇️ Download All as ZIP", data=zip_data, file_name="Shivam_Images.zip", mime="application/zip")

        except Exception as e:
            display_error_with_trace(e)

# ========== FOOTER ==========
st.markdown("""
    <div class='footer'>
        Made with ❤️ for daily greetings. Contact developer for custom versions.
    </div>
""", unsafe_allow_html=True)
