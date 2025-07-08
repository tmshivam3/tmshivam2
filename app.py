import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import os
import io
import datetime
import zipfile

# PAGE CONFIG
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Apply greetings, watermarks, fonts & more in seconds!</h4>
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

def get_random_position(w, h, text_w, text_h):
    safe_margin = 30
    positions = [
        (random.randint(safe_margin, w//2 - text_w), random.randint(h//2, h - text_h - safe_margin)),  # bottom left
        (random.randint(w//2, w - text_w - safe_margin), random.randint(h//2, h - text_h - safe_margin)),  # bottom right
        (random.randint(safe_margin, w//2 - text_w), random.randint(safe_margin, h//2 - text_h)),  # top left
        (random.randint(w//2, w - text_w - safe_margin), random.randint(safe_margin, h//2 - text_h)),  # top right
    ]
    if random.random() < 0.05:
        # 5% chance for center
        x = (w - text_w) // 2
        y = (h - text_h) // 2
        return x, y
    return random.choice(positions)

# DATA
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# SIDEBAR
st.sidebar.header("🎨 Tool Settings")

greetings = [
    "Good Morning", "Good Night", "Rise & Shine", "Sweet Dreams", "Wishing You Well",
    "Peaceful Morning", "Starry Night", "Morning Bliss", "Cozy Night", "Bright Day Ahead"
]
greeting_type = st.sidebar.selectbox("Greeting Type", greetings)

default_subtext = "Stay Positive Always"
user_subtext = st.sidebar.text_input("Wishes Text", default_subtext)

coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 2, 20, 8)
show_date = st.sidebar.checkbox("Add Today's Date on Image", value=False)
date_size_factor = st.sidebar.slider("Date Text Size (relative)", 30, 120, 70)
logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Own Watermark"])
logo_path = os.path.join("assets/logos", logo_choice) if available_logos and logo_choice != "Own Watermark" else None

if logo_choice == "Own Watermark":
    logo_path = st.sidebar.file_uploader("Upload Custom Watermark PNG", type=["png"])

st.sidebar.subheader("Font Source")
font_source = st.sidebar.radio("Select:", ["Available Fonts", "Upload Your Own"])
if font_source == "Available Fonts":
    selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
    uploaded_font = None
else:
    uploaded_font = st.sidebar.file_uploader("Upload .ttf or .otf Font", type=["ttf", "otf"])
    selected_font = None

generate_variations = st.sidebar.checkbox("Generate 4 Variations per Photo (Slideshow)", value=False)
apply_brightness = st.sidebar.checkbox("Enhance Brightness")

uploaded_images = st.file_uploader("🖼️ Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_name, variants in images:
            for i, variant in enumerate(variants):
                img_bytes = io.BytesIO()
                variant.save(img_bytes, format="JPEG", quality=95)
                timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%f")
                file_name = f"{img_name}_v{i+1}_{timestamp}.jpg"
                zipf.writestr(file_name, img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def display_error_message(e=None):
    st.markdown(f"""
        <div style="background-color: red; padding: 10px; border-radius: 10px; text-align: center; font-size: 18px; color: white; font-weight: bold;">
            ⚠️ <strong>Contact Developer on WhatsApp:</strong> <a href="https://wa.me/9140588751" style="color: white; text-decoration: underline;">9140588751</a><br>
            <code>{str(e) if e else ''}</code>
        </div>
    """, unsafe_allow_html=True)

if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        try:
            with st.spinner("Processing images..."):
                logo = None
                if logo_path:
                    if isinstance(logo_path, str):
                        logo = Image.open(logo_path).convert("RGBA")
                    else:
                        logo = Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((225, 225))

                font_bytes = None
                if uploaded_font:
                    font_bytes = io.BytesIO(uploaded_font.read())
                elif selected_font:
                    font_bytes = os.path.join("assets/fonts", selected_font)
                else:
                    font_bytes = "assets/fonts/roboto.ttf"

                def generate_single_variant(img, seed=None):
                    random.seed(seed)
                    img = crop_to_3_4(img)
                    if apply_brightness:
                        img = ImageEnhance.Brightness(img).enhance(1.2)
                    img_w, img_h = img.size
                    main_area = (coverage_percent / 100) * img_w * img_h
                    main_font_size = max(30, int((main_area) ** 0.5 * 0.6))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    try:
                        if isinstance(font_bytes, str):
                            main_font = ImageFont.truetype(font_bytes, main_font_size)
                            sub_font = ImageFont.truetype(font_bytes, sub_font_size)
                            date_font = ImageFont.truetype(font_bytes, date_font_size)
                        else:
                            main_font = ImageFont.truetype(font_bytes, main_font_size)
                            sub_font = ImageFont.truetype(font_bytes, sub_font_size)
                            date_font = ImageFont.truetype(font_bytes, date_font_size)
                    except Exception as e:
                        display_error_message(e)
                        raise e

                    draw = ImageDraw.Draw(img)
                    strong_colors = [(255,255,0), (255,0,0), (255,255,255), (0,255,255), (255,192,203)]
                    color = random.choice(strong_colors)
                    shadow = "black"

                    text = greeting_type
                    text_w, text_h = draw.textsize(text, font=main_font)
                    x, y = get_random_position(img_w, img_h, text_w, text_h)
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((x+dx, y+dy), text, font=main_font, fill=shadow)
                    draw.text((x, y), text, font=main_font, fill=color)

                    sub_x = x + random.randint(-10, 10)
                    sub_y = y + main_font_size + 10
                    draw.text((sub_x, sub_y), user_subtext, font=sub_font, fill=color)

                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        dx, dy = random.randint(30, img_w - 200), random.randint(30, img_h - 100)
                        for dx_off in [-1, 1]:
                            for dy_off in [-1, 1]:
                                draw.text((dx+dx_off, dy+dy_off), today, font=date_font, fill=shadow)
                        draw.text((dx, dy), today, font=date_font, fill=color)

                    if logo:
                        img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), mask=logo)

                    return img

                all_results = []
                for img_file in uploaded_images:
                    image = Image.open(img_file).convert("RGB")
                    variants = []
                    if generate_variations:
                        for _ in range(4):
                            variants.append(generate_single_variant(image.copy(), seed=random.randint(0, 99999)))
                    else:
                        variants = [generate_single_variant(image)]
                    all_results.append((img_file.name, variants))

            st.success("✅ All images processed!")

            for name, variants in all_results:
                st.write(f"**{name} Variants**")
                for i, var in enumerate(variants):
                    st.image(var, use_column_width=True)
                    img_bytes = io.BytesIO()
                    var.save(img_bytes, format="JPEG", quality=95)
                    fname = f"Picsart_{datetime.datetime.now().strftime('%y%m%d_%H%M%S_%f')}.jpg"
                    st.download_button(f"⬇️ Download {fname}", img_bytes.getvalue(), fname, mime="image/jpeg")

            if st.button("⬇️ Download All as ZIP"):
                zip_buffer = create_zip(all_results)
                st.download_button(
                    label="Download All Images as ZIP",
                    data=zip_buffer,
                    file_name="Shivam_Greetings.zip",
                    mime="application/zip"
                )

        except Exception as e:
            display_error_message(e)
    else:
        st.warning("⚠️ Please upload images first.")
