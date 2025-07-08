import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="✨ Smart Photo Generator", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #000000;
        color: #ffffff;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    .advanced-panel {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    </style>
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

def generate_filename():
    now = datetime.datetime.now()
    return f"Picsart_{now.strftime('%d-%m-%y_%H-%M-%S-%f')[:-3]}.jpg"

def apply_overlay(image, overlay_folder, greeting_type):
    overlay_files = {
        "Good Morning": ["1.png", "2.png"],
        "Good Night": ["1.png", "3.png"],
        "Have a nice day": ["4.png"],
        "Sweet dreams": ["5.png"]
    }
    
    overlay_paths = []
    for fname in overlay_files.get(greeting_type, []):
        path = os.path.join(overlay_folder, fname)
        if os.path.exists(path):
            overlay_paths.append(path)
    
    for path in overlay_paths:
        try:
            overlay = Image.open(path).convert("RGBA")
            overlay = overlay.resize(image.size)
            image = Image.alpha_composite(image.convert("RGBA"), overlay)
        except:
            pass
    
    return image

# =================== MAIN APP ===================
col1, col2 = st.columns([3, 1])

# Image uploader
with col1:
    uploaded_images = st.file_uploader("📷 Upload Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Greeting type
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])
    
    # Watermark options
    use_watermark = st.checkbox("Add Watermark", value=False)
    watermark_image = None
    
    if use_watermark:
        watermark_options = [
            "Think Tank TV.png",
            "Wishful Vibes.png",
            "Travellar Bharat.png",
            "Good Vibes.png"
        ]
        selected_watermark = st.selectbox("Select Watermark", watermark_options)
        watermark_image = Image.open(os.path.join("assets/logos", selected_watermark)).convert("RGBA")
    
    # Overlay options
    use_overlay = st.checkbox("Use Pre-made Overlays", value=False)
    overlay_size = 0.5
    
    if use_overlay:
        overlay_size = st.slider("Overlay Size", 0.1, 1.0, 0.5)
        available_themes = [d for d in os.listdir("assets/overlays") if os.path.isdir(os.path.join("assets/overlays", d))]
        selected_theme = st.selectbox("Select Theme", available_themes)

# Advanced panel
with col2:
    st.markdown("### ✨ Advanced Options")
    
    with st.expander("Text Settings"):
        show_text = st.checkbox("Show Custom Text", value=True)
        if show_text:
            text_size = st.slider("Text Size", 20, 100, 60)
            text_color = st.color_picker("Text Color", "#ffffff")
    
    with st.expander("Effects"):
        add_shadow = st.checkbox("Add Text Shadow", value=True)
        add_outline = st.checkbox("Add Text Outline", value=False)

# Process button
if st.button("✨ Generate Photos", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images..."):
            processed_images = []
            
            for uploaded_file in uploaded_images:
                try:
                    img = Image.open(uploaded_file).convert("RGBA")
                    img = center_crop(img)
                    w, h = img.size
                    draw = ImageDraw.Draw(img)
                    
                    # Apply overlay if selected
                    if use_overlay:
                        overlay_folder = os.path.join("assets/overlays", selected_theme)
                        img = apply_overlay(img, overlay_folder, greeting_type)
                    else:
                        # Add custom text if overlay not used
                        if show_text:
                            font = get_random_font().font_variant(size=text_size)
                            text = greeting_type
                            text_width, text_height = get_text_size(draw, text, font)
                            
                            # Position text
                            text_x = (w - text_width) // 2
                            text_y = (h - text_height) // 2
                            
                            # Add effects
                            if add_outline:
                                outline_size = 2
                                for x in range(-outline_size, outline_size+1):
                                    for y in range(-outline_size, outline_size+1):
                                        draw.text((text_x+x, text_y+y), text, font=font, fill="black")
                            
                            if add_shadow:
                                shadow_offset = 3
                                draw.text((text_x+shadow_offset, text_y+shadow_offset), 
                                         text, font=font, fill="black")
                            
                            draw.text((text_x, text_y), text, font=font, fill=text_color)
                    
                    # Add watermark
                    if use_watermark and watermark_image:
                        watermark = watermark_image.copy()
                        watermark.thumbnail((int(w*0.3), int(h*0.3)))
                        img.paste(watermark, (20, 20), watermark)
                    
                    processed_images.append((generate_filename(), img.convert("RGB")))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            st.session_state.processed_images = processed_images
            st.success(f"✅ Generated {len(processed_images)} photos!")

# Display results
if 'processed_images' in st.session_state and st.session_state.processed_images:
    st.markdown("## Generated Photos")
    
    cols = st.columns(3)
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
    
    st.download_button(
        label="📦 Download All Photos",
        data=zip_buffer.getvalue(),
        file_name="Generated_Photos.zip",
        mime="application/zip"
            )
