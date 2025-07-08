import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Ultra Image Processor", layout="wide")

# Custom CSS to hide deprecated warning
st.markdown("""
    <style>
    .stImage > img {
        width: 100% !important;
    }
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
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Ultra Image Processor</h1>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def center_crop(img, target_ratio=3/4):
    w, h = img.size
    if w/h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

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
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generate_filename():
    now = datetime.datetime.now()
    return f"Picsart_{now.strftime('%d-%m-%y_%H-%M-%S-%f')[:-3]}.jpg"

def process_image(image, settings):
    try:
        # Open and crop image
        img = Image.open(image).convert("RGBA")
        img = center_crop(img)
        w, h = img.size
        
        # Apply random enhancement
        enhancer = random.choice([
            ImageEnhance.Contrast(img),
            ImageEnhance.Brightness(img),
            ImageEnhance.Color(img)
        ])
        img = enhancer.enhance(random.uniform(0.9, 1.2))
        
        draw = ImageDraw.Draw(img)
        font = get_random_font()
        
        # Add main text (70% of image width)
        if settings["show_text"]:
            font_main = font.font_variant(size=int(w*0.7*0.1))  # 70% of width * 0.1 factor
            text = settings["greeting_type"]
            text_width, text_height = get_text_size(draw, text, font_main)
            text_x = random.randint(20, max(20, w - text_width - 20))
            text_y = random.randint(20, max(20, h - text_height - 50))
            draw.text((text_x, text_y), text, font=font_main, fill=get_random_color())
        
        # Add wish text (30% of image width)
        if settings["show_wish"]:
            font_wish = font.font_variant(size=int(w*0.3*0.1))  # 30% of width * 0.1 factor
            wish_text = get_random_wish(settings["greeting_type"])
            wish_x = random.randint(20, max(20, w - text_width - 20))
            wish_y = text_y + int(w*0.7*0.1) + 10
            draw.text((wish_x, wish_y), wish_text, font=font_wish, fill=get_random_color())
        
        # Add watermark if enabled
        if settings["use_watermark"] and settings["watermark_image"]:
            watermark = settings["watermark_image"].copy()
            watermark_size = min(w, h) // 4
            watermark.thumbnail((watermark_size, watermark_size))
            img = place_watermark(img, watermark, settings["watermark_opacity"])
        
        return img.convert("RGB")
    except Exception as e:
        st.error(f"Error processing {image.name}: {str(e)}")
        return None

def place_watermark(img, logo, opacity=1.0):
    w, h = img.size
    logo_w, logo_h = logo.size
    x = random.randint(20, w - logo_w - 20)
    y = random.randint(20, h - logo_h - 20)
    
    watermark = logo.copy()
    if opacity < 1.0:
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
    
    img.paste(watermark, (x, y), watermark)
    return img

# =================== MAIN APP ===================
# Initialize session state
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []

# File uploader
uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Greeting settings
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])
    show_text = st.checkbox("Show Main Text", value=True)
    show_wish = st.checkbox("Show Sub Wish", value=True)
    
    # Watermark settings
    use_watermark = st.checkbox("Add Watermark", value=False)
    watermark_image = None
    
    if use_watermark:
        # Check for watermarks in assets folder
        available_watermarks = list_files("assets/watermarks", [".png"])
        if available_watermarks:
            selected_watermark = st.selectbox("Select Watermark", available_watermarks)
            watermark_image = Image.open(os.path.join("assets/watermarks", selected_watermark)).convert("RGBA")
        else:
            uploaded_watermark = st.file_uploader("Upload Watermark", type=["png"])
            if uploaded_watermark:
                watermark_image = Image.open(uploaded_watermark).convert("RGBA")
        
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)

# Process button
if st.button("✨ Generate Images", key="generate_button"):
    if uploaded_images:
        settings = {
            "greeting_type": greeting_type,
            "show_text": show_text,
            "show_wish": show_wish,
            "use_watermark": use_watermark,
            "watermark_image": watermark_image,
            "watermark_opacity": watermark_opacity if use_watermark else 1.0
        }
        
        st.session_state.processed_images = []
        with st.spinner("Processing images..."):
            for img in uploaded_images:
                processed_img = process_image(img, settings)
                if processed_img:
                    st.session_state.processed_images.append((generate_filename(), processed_img))
        
        st.success(f"✅ Generated {len(st.session_state.processed_images)} images!")
    else:
        st.warning("Please upload at least one image")

# Display results
if st.session_state.processed_images:
    st.markdown("### Generated Images")
    cols = st.columns(3)
    for idx, (name, img) in enumerate(st.session_state.processed_images):
        with cols[idx % 3]:
            st.image(img, caption=name)
            
            # Download button for each image
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
    
    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer.getvalue(),
        file_name="Generated_Images.zip",
        mime="application/zip",
        key="dl_all"
    )
