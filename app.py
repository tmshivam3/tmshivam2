import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="✨ Ultra Image Generator", layout="wide", page_icon="✨")

# Custom CSS for the cool theme
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #1a1a2e 100%);
        color: white;
    }
    .stImage>img {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .feature-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #6a11cb;
    }
    </style>
""", unsafe_allow_html=True)

# Main header with gradient
st.markdown("""
    <div style='background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%); padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
        <h1 style='text-align: center; color: white; margin: 0;'>✨ Ultra Image Generator</h1>
        <p style='text-align: center; color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>Professional Bulk Image Processing</p>
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

def get_random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def generate_filename():
    now = datetime.datetime.now()
    return f"Picsart_{now.strftime('%d-%m-%y_%H-%M-%S-%f')[:-3]}.jpg"

def apply_overlay(image, overlay_paths, size_factor=0.5):
    for path in overlay_paths:
        try:
            overlay = Image.open(path).convert("RGBA")
            new_width = int(image.width * size_factor)
            new_height = int(image.height * size_factor)
            overlay = overlay.resize((new_width, new_height))
            
            # Random position
            x = random.randint(20, image.width - overlay.width - 20)
            y = random.randint(20, image.height - overlay.height - 20)
            
            image.paste(overlay, (x, y), overlay)
        except Exception as e:
            st.error(f"Error applying overlay: {str(e)}")
    return image

# =================== MAIN APP ===================
col1, col2 = st.columns([3, 1])

# Image uploader
with col1:
    uploaded_images = st.file_uploader("📁 Upload Images (JPEG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Greeting type
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])
    
    # Watermark options
    st.markdown("#### Watermark Options")
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
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)
        
        # Load selected watermark
        watermark_path = os.path.join("assets/logos", selected_watermark)
        if os.path.exists(watermark_path):
            watermark_image = Image.open(watermark_path).convert("RGBA")
    
    # Overlay options
    st.markdown("#### Overlay Options")
    use_overlay = st.checkbox("Use Pre-made Overlays", value=False)
    
    if use_overlay:
        available_themes = [d for d in os.listdir("assets/overlays") if os.path.isdir(os.path.join("assets/overlays", d))]
        selected_theme = st.selectbox("Select Theme", available_themes)
        overlay_size = st.slider("Overlay Size", 0.1, 1.0, 0.5)
        
        # Determine which overlay files to use based on greeting type
        if greeting_type == "Good Morning":
            overlay_files = ["1.png", "2.png"]  # Good + Morning
        else:
            overlay_files = ["1.png", "3.png"]  # Good + Night
        
        overlay_paths = [os.path.join("assets/overlays", selected_theme, f) for f in overlay_files]

# Features panel
with col2:
    st.markdown("### ✨ Features")
    features = [
        "Smart Auto-Cropping",
        "Professional Watermarking",
        "Pre-made Overlays",
        "Bulk Processing",
        "High Quality Output",
        "Random Text Effects"
    ]
    for feature in features:
        st.markdown(f"""
            <div class="feature-card">
                <h4>{feature}</h4>
            </div>
        """, unsafe_allow_html=True)

# Process button
if st.button("✨ Generate Images", key="generate"):
    if uploaded_images:
        with st.spinner("⚡ Processing images..."):
            processed_images = []
            
            for uploaded_file in uploaded_images:
                try:
                    img = Image.open(uploaded_file).convert("RGBA")
                    img = center_crop(img)
                    
                    # Apply overlays if selected
                    if use_overlay:
                        img = apply_overlay(img, overlay_paths, overlay_size)
                    
                    # Add watermark if selected
                    if use_watermark and watermark_image:
                        watermark = watermark_image.copy()
                        if watermark_opacity < 1.0:
                            alpha = watermark.split()[3]
                            alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                            watermark.putalpha(alpha)
                        
                        watermark.thumbnail((img.width//4, img.height//4))
                        img.paste(watermark, (20, 20), watermark)
                    
                    processed_images.append((generate_filename(), img.convert("RGB")))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            st.session_state.processed_images = processed_images
            st.success(f"✅ Generated {len(processed_images)} images!")

# Display results
if 'processed_images' in st.session_state and st.session_state.processed_images:
    st.markdown("## Generated Images")
    
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
        mime="application/zip"
    )

# =================== FOOTER ===================
st.markdown("""
    <div style='text-align: center; color: grey; margin-top: 50px; font-size: 0.9em;'>
        <p>✨ Ultra Image Generator | © 2023</p>
    </div>
""", unsafe_allow_html=True)
