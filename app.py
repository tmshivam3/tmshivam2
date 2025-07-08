import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import os
import io
import datetime
import zipfile

# CONFIG
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
<h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
""", unsafe_allow_html=True)

# Utils
def list_files(folder, exts):
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)] if os.path.exists(folder) else []

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def apply_opacity(image, opacity):
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    image.putalpha(alpha)
    return image

# Data
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# Sidebar
st.sidebar.header("🎨 Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
show_date = st.sidebar.checkbox("Add Today's Date", True)
show_wishes = st.sidebar.checkbox("Show Wishes", True)

coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 5, 20, 10)
date_size_factor = st.sidebar.slider("Date Font Size %", 30, 120, 70)

logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Upload Custom"])
logo_path = os.path.join("assets/logos", logo_choice) if logo_choice != "Upload Custom" else None

if logo_choice == "Upload Custom":
    logo_path = st.sidebar.file_uploader("Upload PNG Logo", type=["png"])

font_source = st.sidebar.radio("Font Source", ["Choose", "Upload"])
if font_source == "Choose":
    selected_font = st.sidebar.selectbox("Available Fonts", available_fonts)
    uploaded_font = None
else:
    uploaded_font = st.sidebar.file_uploader("Upload Font (.ttf or .otf)", type=["ttf", "otf"])
    selected_font = None

generate_variations = st.sidebar.checkbox("Generate 4 Variants", value=False)

# Upload
uploaded_images = st.file_uploader("📷 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
output_images = []

# Wishes data
wishes_dict = {
    "Good Morning": [
        "Have a beautiful day",
        "Rise and shine!",
        "Start your day with a smile",
        "Enjoy every moment",
        "Stay blessed!",
        "Seize the day!",
        "Wake up and shine!",
        "New day, new blessings",
        "Make today count",
        "Sunshine is here for you"
    ],
    "Good Night": [
        "Sweet dreams",
        "Sleep peacefully",
        "Rest well",
        "Recharge for tomorrow",
        "Good night and take care",
        "May your dreams be sweet",
        "Sleep tight!",
        "Peaceful night ahead",
        "Dream big tonight",
        "Nighty night!"
    ]
}

# Text rendering utility
def draw_text(draw, text, pos, font, fill, shadow=True, outline=False):
    x, y = pos
    if shadow:
        for dx, dy in [(-2, -2), (2, 2), (-2, 2), (2, -2)]:
            draw.text((x + dx, y + dy), text, font=font, fill="black")
    if outline:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                draw.text((x + dx, y + dy), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill=fill)

# Position utility
def get_non_center_position(img_w, img_h, text_w, text_h):
    margin = 30
    max_attempts = 10
    for _ in range(max_attempts):
        x = random.randint(margin, img_w - text_w - margin)
        y = random.randint(margin, img_h - text_h - margin)
        if not (img_w * 0.35 < x < img_w * 0.65 and img_h * 0.35 < y < img_h * 0.65):
            return x, y
    return x, y  # fallback

# ZIP
def create_zip(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for name, variants in images:
            for i, img in enumerate(variants):
                b = io.BytesIO()
                img.save(b, format="JPEG")
                t = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S-%f")
                fname = f"Picsart_{t}.jpg"
                z.writestr(fname, b.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# Main Generation
if st.button("✨ Generate Images"):
    if uploaded_images:
        try:
            with st.spinner("Processing..."):
                logo_img = None
                if logo_path:
                    logo_img = Image.open(logo_path).convert("RGBA")

                font_path = os.path.join("assets/fonts", selected_font) if selected_font else None
                font_bytes = io.BytesIO(uploaded_font.read()) if uploaded_font else None

                all_results = []

                for img_file in uploaded_images:
                    img = Image.open(img_file).convert("RGB")
                    img = crop_to_3_4(img)
                    img_w, img_h = img.size

                    variants = []

                    def render(img_copy):
                        draw = ImageDraw.Draw(img_copy)
                        main_area = (coverage_percent / 100) * img_w * img_h
                        main_font_size = int((main_area) ** 0.5 * 0.7)
                        sub_font_size = int(main_font_size * 0.45)
                        date_font_size = int(main_font_size * date_size_factor / 100)

                        font_to_use = ImageFont.truetype(font_path if font_path else font_bytes, size=main_font_size)
                        sub_font = ImageFont.truetype(font_path if font_path else font_bytes, size=sub_font_size)
                        date_font = ImageFont.truetype(font_path if font_path else font_bytes, size=date_font_size)

                        text_color = random.choice([
                            (255, 255, 255), (255, 215, 0), (255, 0, 0), (0, 255, 255),
                            (255, 105, 180), (173, 216, 230)
                        ])

                        # MAIN TEXT
                        main_text = greeting_type
                        text_w, text_h = draw.textbbox((0, 0), main_text, font=font_to_use)[2:]
                        x, y = get_non_center_position(img_w, img_h, text_w, text_h)
                        draw_text(draw, main_text, (x, y), font_to_use, fill=text_color, shadow=random.choice([True, False]))

                        # WISHES
                        if show_wishes:
                            wish = random.choice(wishes_dict[greeting_type])
                            wx, wy = get_non_center_position(img_w, img_h, text_w, sub_font_size)
                            draw_text(draw, wish, (wx, y + text_h + 5), sub_font, fill=text_color, shadow=True)

                        # DATE
                        if show_date:
                            date_str = datetime.datetime.now().strftime("%d %B %Y")
                            dx, dy = get_non_center_position(img_w, img_h, date_font_size * 10, date_font_size)
                            draw_text(draw, date_str, (dx, dy), date_font, fill=text_color, shadow=True)

                        # LOGO
                        if logo_img:
                            logo = logo_img.copy()
                            scale = random.uniform(0.15, 0.25)
                            size = int(img_w * scale)
                            logo.thumbnail((size, size))
                            logo = apply_opacity(logo, random.uniform(0.45, 1.0))
                            for _ in range(10):
                                lx = random.randint(30, img_w - logo.width - 30)
                                ly = random.randint(30, img_h - logo.height - 30)
                                if not (lx < x + text_w and lx + logo.width > x and
                                        ly < y + text_h and ly + logo.height > y):
                                    break
                            img_copy.paste(logo, (lx, ly), mask=logo)

                        return img_copy

                    if generate_variations:
                        for _ in range(4):
                            variants.append(render(img.copy()))
                    else:
                        variants.append(render(img))

                    all_results.append((img_file.name, variants))

            st.success("✅ All images ready!")

            for name, variants in all_results:
                st.write(f"📸 {name}")
                for img in variants:
                    st.image(img, use_container_width=True)
                    b = io.BytesIO()
                    img.save(b, format="JPEG")
                    fname = f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg"
                    st.download_button("⬇️ Download", data=b.getvalue(), file_name=fname, mime="image/jpeg")

            if st.button("⬇️ Download All as ZIP"):
                zip_buffer = create_zip(all_results)
                st.download_button("Download ZIP", data=zip_buffer, file_name="All_Edited.zip", mime="application/zip")

        except Exception as e:
            st.error(f"❌ Error Occurred: {e}")
    else:
        st.warning("⚠️ Upload at least one image to start.")
