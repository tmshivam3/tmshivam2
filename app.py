import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# Set page configuration
st.set_page_config(page_title="🔆 Shivam Tool", layout="centered")

# Title
st.markdown("""
    <h1 style='text-align: center; background-color: black; color: white; padding: 10px; border-radius: 8px;'>🔆 EDIT PHOTO IN ONE CLICK 🔆</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# Load logo and font
logo_path = "assets/logos/logo.png"
font_path = "assets/fonts/roboto.ttf"

if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
else:
    logo = None

# Sidebar inputs
greeting = st.sidebar.selectbox("Greeting", ["Good Morning", "Good Night"])
subtext = st.sidebar.text_input("Sub Text", "Have a nice day" if greeting == "Good Morning" else "Sweet Dreams")
show_date = st.sidebar.checkbox("Add today's date", True)
generate_variants = st.sidebar.checkbox("Generate 4 Variants", True)

# File uploader
uploaded_images = st.file_uploader("📤 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Session state to retain images and ZIP
if "results" not in st.session_state:
    st.session_state.results = []
if "zip_data" not in st.session_state:
    st.session_state.zip_data = None

# Crop image to 3:4 ratio
def crop_image_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_width = int(h * target_ratio)
        left = (w - new_width) // 2
        return img.crop((left, 0, left + new_width, h))
    else:
        new_height = int(w / target_ratio)
        top = (h - new_height) // 2
        return img.crop((0, top, w, top + new_height))

# Generate image variant
def generate_variant(img, greeting, subtext, font_path, logo=None, show_date=False, seed=None):
    random.seed(seed)
    img = crop_image_to_3_4(img.copy())
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Dynamic font sizes
    main_size = int((w * h * 0.08) ** 0.5)
    sub_size = int(main_size * 0.5)
    date_size = int(main_size * 0.6)

    font_main = ImageFont.truetype(font_path, main_size)
    font_sub = ImageFont.truetype(font_path, sub_size)
    font_date = ImageFont.truetype(font_path, date_size)

    # Position text randomly
    x = random.randint(30, w - main_size * len(greeting) // 2 - 30)
    y = random.randint(30, h - main_size - 30)

    text_color = random.choice([(255, 255, 255), (255, 255, 0), (255, 0, 0)])

    draw.text((x, y), greeting, font=font_main, fill=text_color)
    draw.text((x, y + main_size + 5), subtext, font=font_sub, fill=text_color)

    if show_date:
        today = datetime.datetime.now().strftime("%d %B %Y")
        draw.text((30, h - date_size - 10), today, font=font_date, fill=text_color)

    if logo:
        logo_copy = logo.copy()
        logo_copy.thumbnail((200, 200))
        img.paste(logo_copy, (w - logo_copy.width - 10, h - logo_copy.height - 10), logo_copy)

    return img

# Generate button
if st.button("✅ Generate"):
    results = []

    for img_file in uploaded_images:
        img = Image.open(img_file).convert("RGB")
        name = os.path.splitext(img_file.name)[0]
        variants = []

        for i in range(4 if generate_variants else 1):
            variant = generate_variant(
                img,
                greeting,
                subtext,
                font_path,
                logo=logo,
                show_date=show_date,
                seed=random.randint(0, 100000)
            )
            variants.append((f"{name}_v{i+1}.jpg", variant))

        results.append((name, variants))

    st.session_state.results = results

    # Generate ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for name, variants in results:
            for filename, image in variants:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG")
                img_bytes.seek(0)
                zipf.writestr(filename, img_bytes.getvalue())
    zip_buffer.seek(0)
    st.session_state.zip_data = zip_buffer

# Display results
if st.session_state.results:
    st.subheader("🖼️ Generated Images:")

    for name, variants in st.session_state.results:
        st.write(f"**{name}**")
        for filename, img in variants:
            st.image(img, caption=filename, use_column_width=True)

            # Individual download
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            st.download_button(
                label=f"⬇️ Download {filename}",
                data=img_bytes.getvalue(),
                file_name=filename,
                mime="image/jpeg"
            )

    # ZIP download
    if st.session_state.zip_data:
        st.download_button(
            "⬇️ Download All as ZIP",
            data=st.session_state.zip_data,
            file_name="All_Images.zip",
            mime="application/zip"
        )
