# Final and Premium version of app.py (500+ lines compacted for clarity)

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# CONFIG
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

# HEADER
st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Watermark • Wishes • Fonts • Auto Slideshow • Zip Export</h4>
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

# MORNING/NIGHT WISHES
morning_wishes = [
    "Have a wonderful day!", "Rise and Shine!", "Spread kindness today!",
    "Start fresh with a smile!", "Make it a great one!", "New day, new chances!"
]
night_wishes = [
    "Sweet dreams ahead!", "Rest well tonight!", "Good night, sleep tight!",
    "Peaceful dreams!", "Recharge for tomorrow!", "Sleep in serenity."
]

# FILE DATA
available_logos = list_files("assets/logos", [".png"])
available_fonts = list_files("assets/fonts", [".ttf", ".otf"])

# SIDEBAR SETTINGS
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
coverage_percent = st.sidebar.slider("Main Text Coverage (%)", 2, 20, 8)
show_date = st.sidebar.checkbox("Add Today's Date", value=False)
date_size_factor = st.sidebar.slider("Date Text Size", 30, 120, 70)
logo_choice = st.sidebar.selectbox("Watermark Logo", available_logos + ["Own Watermark"])
logo_path = os.path.join("assets/logos", logo_choice) if logo_choice != "Own Watermark" else None
if logo_choice == "Own Watermark":
    logo_path = st.sidebar.file_uploader("Upload Custom Watermark PNG", type=["png"])

# Font
font_source = st.sidebar.radio("Font Source", ["Available Fonts", "Upload Your Own"])
if font_source == "Available Fonts":
    selected_font = st.sidebar.selectbox("Choose Font", available_fonts)
    uploaded_font = None
else:
    uploaded_font = st.sidebar.file_uploader("Upload Font (.ttf/.otf)", type=["ttf", "otf"])
    selected_font = None

# MULTI VARIATIONS
generate_variations = st.sidebar.checkbox("Generate 4 Variations per Image", value=False)

# MAIN FILE UPLOAD
uploaded_images = st.file_uploader("📁 Upload Your Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ZIP HANDLER

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

# ERROR UI

def display_error_message(msg="Contact developer: +91-9140588751"):
    st.markdown(f"""
        <div style="background-color: red; padding: 10px; border-radius: 10px; text-align: center; font-size: 20px; color: white; font-weight: bold;">
            ⚠️ <strong>{msg}</strong>
        </div>
    """, unsafe_allow_html=True)

# MAIN GENERATION
if st.button("🚀 Generate Images"):
    if uploaded_images:
        try:
            with st.spinner("Generating..."):
                logo = Image.open(logo_path).convert("RGBA") if logo_path else None
                if logo:
                    logo.thumbnail((225, 225))

                font_bytes = io.BytesIO(uploaded_font.read()) if uploaded_font else os.path.join("assets/fonts", selected_font or "roboto.ttf")
                def generate_variant(img, seed=None):
                    random.seed(seed)
                    img = crop_to_3_4(img)
                    img_w, img_h = img.size

                    # Font sizes
                    main_area = (coverage_percent / 100) * img_w * img_h
                    main_font_size = max(30, int((main_area) ** 0.5 * 0.6))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    # Fonts
                    try:
                        if isinstance(font_bytes, str):
                            main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                        else:
                            main_font = ImageFont.truetype(font_bytes, size=main_font_size)
                    except:
                        display_error_message("Font error. Use another font.")
                        return img

                    draw = ImageDraw.Draw(img)
                    safe_margin = 30
                    text_color = random.choice([(255,255,255), (255,0,0), (255,255,0), (255,192,203)])
                    shadow_color = "black"

                    wish = random.choice(morning_wishes if greeting_type == "Good Morning" else night_wishes)

                    # Random Position
                    x_range = img_w - main_font_size * len(greeting_type) // 2 - safe_margin
                    y_range = img_h - main_font_size - safe_margin
                    x = max(0, random.randint(safe_margin, max(safe_margin, x_range)))
                    y = max(0, random.randint(safe_margin, max(safe_margin, y_range)))
                    
                    # Shadow
                    for dx in [-2, 2]:
                        for dy in [-2, 2]:
                            draw.text((x+dx, y+dy), greeting_type, font=main_font, fill=shadow_color)
                    draw.text((x, y), greeting_type, font=main_font, fill=text_color)
                    draw.text((x+10, y + main_font_size + 10), wish, font=ImageFont.truetype(font_bytes, size=sub_font_size), fill=text_color)

                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        draw.text((safe_margin, img_h - 2*date_font_size), today, font=ImageFont.truetype(font_bytes, size=date_font_size), fill=text_color)

                    if logo:
                        img.paste(logo, (img_w - logo.width - 10, img_h - logo.height - 10), logo)

                    return img

                all_results = []
                for img_file in uploaded_images:
                    image = Image.open(img_file).convert("RGB")
                    variants = []
                    if generate_variations:
                        for i in range(4):
                            variants.append(generate_variant(image.copy(), seed=random.randint(0,99999)))
                    else:
                        variants = [generate_variant(image)]
                    all_results.append((img_file.name, variants))

            # DISPLAY
            for name, variants in all_results:
                st.write(f"### {name} Variants")
                for v in variants:
                    st.image(v, use_column_width=True)
                    img_bytes = io.BytesIO()
                    v.save(img_bytes, format="PNG")
                    file_name = f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.png"
                    st.download_button("⬇️ Download", data=img_bytes.getvalue(), file_name=file_name, mime="image/png")

            if st.button("📦 Download All as ZIP"):
                zip_buf = create_zip(all_results)
                st.download_button("⬇️ Download ZIP", data=zip_buf, file_name="Shivam_Generated_Images.zip", mime="application/zip")

            st.success("🎉 Done!")
        except Exception as e:
            display_error_message(str(e))
    else:
        st.warning("⚠️ Please upload at least one image.")
