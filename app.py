import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Instant Photo Generator", layout="wide")

# Custom CSS to clean up the interface
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #000000;
        color: #ffff00;
        border: 2px solid #ffff00;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #000000;
        color: white;
    }
    .stImage>img {
        border-radius: 8px;
    }
    .feature-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Instant Photo Generator</h1>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def center_crop(img):
    w, h = img.size
    if w > h:
        left = (w - h) // 2
        return img.crop((left, 0, left + h, h))
    else:
        top = (h - w) // 2
        return img.crop((0, top, w, top + w))

def get_random_font():
    fonts = list_files("assets/fonts", [".ttf", ".otf"])
    if not fonts:
        return ImageFont.load_default()
    font_path = os.path.join("assets/fonts", random.choice(fonts))
    try:
        return ImageFont.truetype(font_path, 60)
    except:
        return ImageFont.load_default()

def get_random_wish(greeting_type):
    wishes = {
        "Good Morning": ["Have a great day!", "Rise and shine!", "Make today amazing!"],
        "Good Night": ["Sweet dreams!", "Sleep tight!", "Night night!"]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def generate_filename():
    now = datetime.datetime.now()
    return f"Picsart_{now.strftime('%d-%m-%y_%H-%M-%S-%f')[:-3]}.jpg"

def process_image(img, settings):
    try:
        img = center_crop(img)
        w, h = img.size
        
        draw = ImageDraw.Draw(img)
        font = get_random_font()
        
        # Main text (70% size)
        if settings["show_text"]:
            font_main = font.font_variant(size=settings["main_size"])
            text = settings["greeting_type"]
            text_width, text_height = get_text_size(draw, text, font_main)
            text_x = random.randint(20, max(20, w - text_width - 20))
            text_y = random.randint(20, max(20, h - text_height - 50))
            draw.text((text_x, text_y), text, font=font_main, fill=get_random_color())
        
        # Wish text (30% size)
        if settings["show_wish"]:
            font_wish = font.font_variant(size=settings["wish_size"])
            wish_text = get_random_wish(settings["greeting_type"])
            wish_x = random.randint(20, max(20, w - text_width - 20))
            wish_y = text_y + settings["main_size"] + 10
            draw.text((wish_x, wish_y), wish_text, font=font_wish, fill=get_random_color())
        
        # Watermark
        if settings["use_watermark"] and settings["watermark_image"]:
            watermark = settings["watermark_image"].copy()
            watermark.thumbnail((w//4, h//4))
            img.paste(watermark, (20, 20), watermark)
        
        return img.convert("RGB")
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        return None

# =================== MAIN APP ===================
col1, col2 = st.columns([3, 1])

# Image uploader
with col1:
    uploaded_images = st.file_uploader("📁 Upload Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Text settings
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])
    show_text = st.checkbox("Show Main Text", value=True)
    if show_text:
        main_size = st.slider("Main Text Size", 20, 100, 60)
    show_wish = st.checkbox("Show Wish Text", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 60, 30)
    
    # Watermark settings
    use_watermark = st.checkbox("Add Watermark", value=False)
    watermark_image = None
    
    if use_watermark:
        # First show upload option
        uploaded_watermark = st.file_uploader("Upload Your Watermark", type=["png"])
        
        # Then show available watermarks
        available_watermarks = list_files("assets/watermarks", [".png"])
        if available_watermarks:
            selected_watermark = st.selectbox("Or Select Watermark", [""] + available_watermarks)
            if selected_watermark:
                watermark_image = Image.open(os.path.join("assets/watermarks", selected_watermark)).convert("RGBA")
        if uploaded_watermark:
            watermark_image = Image.open(uploaded_watermark).convert("RGBA")

# Features panel
with col2:
    st.markdown("### ✨ Features")
    features = [
        "One-Click Generation",
        "Smart Text Placement",
        "Random Styles",
        "Bulk Processing",
        "Watermark Support",
        "High Quality Output"
    ]
    for feature in features:
        st.markdown(f"✔️ {feature}")

# Process button
if col1.button("✨ Generate Photos", key="generate"):
    if uploaded_images:
        settings = {
            "greeting_type": greeting_type,
            "show_text": show_text,
            "main_size": main_size if show_text else 0,
            "show_wish": show_wish,
            "wish_size": wish_size if show_wish else 0,
            "use_watermark": use_watermark,
            "watermark_image": watermark_image
        }
        
        progress_bar = col1.progress(0)
        processed_images = []
        
        for idx, uploaded_file in enumerate(uploaded_images):
            img = Image.open(uploaded_file).convert("RGBA")
            processed_img = process_image(img, settings)
            if processed_img:
                processed_images.append((generate_filename(), processed_img))
            progress_bar.progress((idx + 1) / len(uploaded_images))
        
        progress_bar.empty()
        
        if processed_images:
            st.session_state.processed_images = processed_images
            col1.success(f"✅ Generated {len(processed_images)} photos!")

# Display results
if 'processed_images' in st.session_state:
    cols = col1.columns(3)
    for idx, (name, img) in enumerate(st.session_state.processed_images):
        with cols[idx % 3]:
            st.image(img)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)
            st.download_button(
                label=f"⬇️ {name}",
                data=img_bytes.getvalue(),
                file_name=name,
                mime="image/jpeg",
                key=f"dl_{idx}"
            )
    
    # ZIP download
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for name, img in st.session_state.processed_images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=95)
            zipf.writestr(name, img_bytes.getvalue())
    
    col1.download_button(
        label="📦 Download All",
        data=zip_buffer.getvalue(),
        file_name="Generated_Photos.zip",
        mime="application/zip"
                )
