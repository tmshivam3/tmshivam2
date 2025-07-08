import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# PAGE CONFIG
st.set_page_config(page_title="\ud83d\udd06 SHIVAM TOOL", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>\ud83d\udd06 EDIT PHOTO IN ONE CLICK \ud83d\udd06</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# UTILS
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

def display_error_message(err):
    st.markdown(f"""
        <div style="background-color: red; padding: 10px; border-radius: 10px; text-align: center; font-size: 20px; color: white; font-weight: bold;">
            \u26a0\ufe0f <strong>Contact Developer via WhatsApp:</strong> <a href="https://wa.me/9140588751" style="color: white; text-decoration: underline;">9140588751</a><br>
            <small>Error: {err}</small>
        </div>
    """, unsafe_allow_html=True)

# SIDEBAR SETTINGS
st.sidebar.header("\ud83c\udfa8 Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
default_subtext = "Sweet Dreams" if greeting_type == "Good Night" else "Have a Nice Day"
user_subtext = st.sidebar.text_input("Wishes Text", default_subtext)
coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 2, 20, 8)
show_date = st.sidebar.checkbox("Add Today's Date on Image", value=False)
date_size_factor = st.sidebar.slider("Date Text Size (relative)", 30, 120, 70)

available_logos = list_files("assets/logos", [".png"])
logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Own Watermark"])
logo_path = os.path.join("assets/logos", logo_choice) if logo_choice != "Own Watermark" else None
if logo_choice == "Own Watermark":
    logo_path = st.sidebar.file_uploader("Upload Custom Watermark PNG", type=["png"])

st.sidebar.subheader("Font Source")
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
font_source = st.sidebar.radio("Select:", ["Available Fonts", "Upload Your Own"])
if font_source == "Available Fonts":
    selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
    uploaded_font = None
else:
    uploaded_font = st.sidebar.file_uploader("Upload .ttf or .otf Font", type=["ttf", "otf"])
    selected_font = None

generate_variations = st.sidebar.checkbox("Generate 4 Variations per Photo (Slideshow)", value=False)

# MAIN IMAGE UPLOAD
uploaded_images = st.file_uploader("\ud83d\uddbc\ufe0f Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ZIP Creation
def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_name, variants in images:
            for i, variant in enumerate(variants):
                img_bytes = io.BytesIO()
                variant.save(img_bytes, format="JPEG", quality=95)
                timestamp = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                file_name = f"{img_name}_variant_{i+1}_{timestamp}.jpg"
                zipf.writestr(file_name, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

if st.button("\u2705 Generate Edited Images"):
    if uploaded_images:
        try:
            with st.spinner("Processing..."):
                logo = None
                if logo_path:
                    logo = Image.open(logo_path).convert("RGBA") if not isinstance(logo_path, str) else Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((225, 225))

                font_bytes = io.BytesIO(uploaded_font.read()) if uploaded_font else os.path.join("assets/fonts", selected_font or "roboto.ttf")

                def safe_random(min_val, max_val):
                    return random.randint(min_val, max_val) if max_val > min_val else min_val

                def generate_variant(img, seed=None):
                    random.seed(seed)
                    img = crop_to_3_4(img)
                    img_w, img_h = img.size
                    main_text_area = (coverage_percent / 100) * img_w * img_h
                    main_font_size = max(30, int((main_text_area) ** 0.5 * 0.6))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    if isinstance(font_bytes, str):
                        main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                        sub_font = ImageFont.truetype(font_bytes, size=sub_font_size)
                        date_font = ImageFont.truetype(font_bytes, size=date_font_size)
                    else:
                        main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                        sub_font = ImageFont.truetype(font_bytes, size=sub_font_size)
                        date_font = ImageFont.truetype(font_bytes, size=date_font_size)

                    draw = ImageDraw.Draw(img)
                    safe_margin = 30
                    strong_colors = [(255,255,0), (255,0,0), (255,255,255), (255,192,203), (0,255,0)]
                    text_color = random.choice(strong_colors + [tuple(random.randint(100, 255) for _ in range(3))])

                    x = safe_random(safe_margin, img_w - main_font_size * len(greeting_type)//2 - safe_margin)
                    y = safe_random(safe_margin, img_h - main_font_size - safe_margin)

                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((x+dx, y+dy), greeting_type, font=main_font, fill="black")
                    draw.text((x, y), greeting_type, font=main_font, fill=text_color)

                    sub_x = safe_random(safe_margin, img_w - sub_font_size * len(user_subtext)//2 - safe_margin)
                    sub_y = y + main_font_size + 10
                    draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=text_color)

                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        date_x = safe_random(safe_margin, img_w - date_font_size * 10 - safe_margin)
                        date_y = safe_random(safe_margin, img_h - date_font_size - safe_margin)
                        for dx in [-2, 2]:
                            for dy in [-2, 2]:
                                draw.text((date_x+dx, date_y+dy), today, font=date_font, fill="black")
                        draw.text((date_x, date_y), today, font=date_font, fill=text_color)

                    if logo:
                        img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                    return img

                results = []
                for img_file in uploaded_images:
                    image = Image.open(img_file).convert("RGB")
                    font_bytes = io.BytesIO(uploaded_font.read()) if uploaded_font else os.path.join("assets/fonts", selected_font or "roboto.ttf")
                    variants = [generate_variant(image.copy(), seed=random.randint(0, 99999)) for _ in range(4)] if generate_variations else [generate_variant(image)]
                    results.append((img_file.name, variants))

            st.success("\u2705 All images processed successfully!")

            for name, variants in results:
                for i, variant in enumerate(variants):
                    st.image(variant, use_column_width=True)
                    img_bytes = io.BytesIO()
                    variant.save(img_bytes, format="JPEG")
                    file_name = f"{name}_var{i+1}.jpg"
                    st.download_button(f"\u2b07\ufe0f Download {file_name}", img_bytes.getvalue(), file_name, mime="image/jpeg")

            if st.button("\u2b07\ufe0f Download All as ZIP"):
                zip_file = create_zip(results)
                st.download_button("Download ZIP", data=zip_file, file_name="Shivam_Greetings.zip", mime="application/zip")

        except Exception as e:
            display_error_message(str(e))
    else:
        st.warning("\u26a0\ufe0f Please upload images first.")
