import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import os
import io
import datetime
import zipfile

# Streamlit Page Config
st.set_page_config(page_title="🔆 Shivam Tool", layout="centered")

# Title
st.markdown("""
    <h1 style='text-align: center; background-color: black; color: white; padding: 10px; border-radius: 8px;'>🔆 EDIT PHOTO IN ONE CLICK 🔆</h1>
    <h4 style='text-align: center; color: grey;'>Premium Good Morning / Good Night Watermark Generator</h4>
""", unsafe_allow_html=True)

# Initialize session state
if "all_results" not in st.session_state:
    st.session_state.all_results = []
if "zip_buffer" not in st.session_state:
    st.session_state.zip_buffer = None

# Function: Crop Image to 3:4
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

# Function: Generate variant
def generate_variant(img, greeting, subtext, font_path, logo=None, show_date=False, seed=None):
    random.seed(seed)
    img = crop_to_3_4(img.copy())
    draw = ImageDraw.Draw(img)
    w, h = img.size

    main_size = int((w * h * 0.08) ** 0.5)
    sub_size = int(main_size * 0.5)
    date_size = int(main_size * 0.6)

    font_main = ImageFont.truetype(font_path, main_size)
    font_sub = ImageFont.truetype(font_path, sub_size)
    font_date = ImageFont.truetype(font_path, date_size)

    # Text positions
    x = random.randint(30, w - main_size * len(greeting) // 2 - 30)
    y = random.randint(30, h - main_size - 30)

    text_color = random.choice([(255, 255, 255), (255, 255, 0), (255, 0, 0)])

    draw.text((x, y), greeting, font=font_main, fill=text_color)
    draw.text((x, y + main_size + 5), subtext, font=font_sub, fill=text_color)

    if show_date:
        today = datetime.datetime.now().strftime("%d %B %Y")
        draw.text((30, h - date_size - 10), today, font=font_date, fill=text_color)

    if logo:
        logo = logo.copy()
        logo.thumbnail((200, 200))
        img.paste(logo, (w - logo.width - 10, h - logo.height - 10), logo)

    return img

# Sidebar settings
greeting = st.sidebar.selectbox("Greeting", ["Good Morning", "Good Night"])
subtext = st.sidebar.text_input("Sub Text", "Have a nice day" if greeting == "Good Morning" else "Sweet Dreams")
show_date = st.sidebar.checkbox("Add today's date", True)
generate_variants = st.sidebar.checkbox("Generate 4 Variants", True)

font_file = "assets/fonts/roboto.ttf"
logo_file = "assets/logos/logo.png"
if os.path.exists(logo_file):
    logo_img = Image.open(logo_file).convert("RGBA")
else:
    logo_img = None

# Upload images
uploaded_images = st.file_uploader("📤 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Generate Button
if st.button("✅ Generate"):
    st.session_state.all_results.clear()
    all_outputs = []
    for img_file in uploaded_images:
        img = Image.open(img_file).convert("RGB")
        variants = []
        for i in range(4 if generate_variants else 1):
            v = generate_variant(
                img,
                greeting,
                subtext,
                font_file,
                logo=logo_img,
                show_date=show_date,
                seed=random.randint(0, 99999)
            )
            variants.append(v)
        all_outputs.append((img_file.name, variants))
    st.session_state.all_results = all_outputs

    # Generate ZIP once
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for name, variants in all_outputs:
            for i, img in enumerate(variants):
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG")
                img_bytes.seek(0)
                zipf.writestr(f"{name}_v{i+1}.jpg", img_bytes.getvalue())
    zip_buffer.seek(0)
    st.session_state.zip_buffer = zip_buffer

# Display Images & Download
if st.session_state.all_results:
    st.subheader("🖼️ Generated Images:")
    for name, variants in st.session_state.all_results:
        st.write(f"**{name}**")
        for i, img in enumerate(variants):
            st.image(img, caption=f"{name} - Variant {i+1}", use_column_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)
            st.download_button(
                f"⬇️ Download {name} - v{i+1}",
                data=img_bytes.getvalue(),
                file_name=f"{name}_v{i+1}.jpg",
                mime="image/jpeg"
            )

    # ZIP download
    if st.session_state.zip_buffer:
        st.download_button(
            "⬇️ Download All as ZIP",
            data=st.session_state.zip_buffer,
            file_name="All_Images.zip",
            mime="application/zip"
        )
