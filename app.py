import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np
import cv2

# =================== CONFIG ===================
st.set_page_config(page_title="✨ Smart Photo Editor", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #000000;
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

# =================== UTILS ===================
def find_empty_spaces(image_np, min_area=5000):
    """Find empty spaces in image using edge detection"""
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    kernel = np.ones((5,5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=3)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    empty_spaces = []
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        area = w * h
        if area > min_area:
            empty_spaces.append((x, y, w, h))
    
    return empty_spaces if empty_spaces else [(0, 0, image_np.shape[1], image_np.shape[0])]

def best_position_for_text(empty_spaces, text_size, image_size):
    """Find best position for text in empty spaces"""
    img_w, img_h = image_size
    text_w, text_h = text_size
    
    for space in empty_spaces:
        x, y, w, h = space
        if w >= text_w and h >= text_h:
            center_x = x + (w - text_w) // 2
            center_y = y + (h - text_h) // 2
            return (center_x, center_y)
    
    # Fallback to random position if no perfect space found
    return (random.randint(20, img_w - text_w - 20), 
            random.randint(20, img_h - text_h - 20))

def add_element_to_space(image, element, empty_spaces, element_size):
    """Add an element to the most suitable empty space"""
    img_w, img_h = image.size
    el_w, el_h = element_size
    
    for space in empty_spaces:
        x, y, w, h = space
        if w >= el_w and h >= el_h:
            pos_x = x + (w - el_w) // 2
            pos_y = y + (h - el_h) // 2
            image.paste(element, (pos_x, pos_y), element)
            return image
    
    # Fallback to random position
    pos_x = random.randint(20, img_w - el_w - 20)
    pos_y = random.randint(20, img_h - el_h - 20)
    image.paste(element, (pos_x, pos_y), element)
    return image

def process_image(image, settings):
    try:
        img = image.convert("RGBA")
        img_np = np.array(img)
        empty_spaces = find_empty_spaces(img_np)
        
        # Auto enhance
        img = ImageEnhance.Contrast(img).enhance(1.1)
        img = ImageEnhance.Sharpness(img).enhance(1.1)
        
        draw = ImageDraw.Draw(img)
        
        # Add text if enabled
        if settings["show_text"]:
            font = ImageFont.truetype("assets/fonts/arial.ttf", settings["text_size"])
            text = settings["greeting_type"]
            text_w, text_h = get_text_size(draw, text, font)
            
            # Find best position
            text_x, text_y = best_position_for_text(empty_spaces, (text_w, text_h), img.size)
            
            # Add text with effects
            draw.text((text_x, text_y), text, font=font, fill=settings["text_color"])
        
        # Add watermark if enabled
        if settings["use_watermark"] and settings["watermark_image"]:
            watermark = settings["watermark_image"].copy()
            watermark.thumbnail((img.width//4, img.height//4))
            
            if settings["watermark_opacity"] < 1.0:
                alpha = watermark.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(settings["watermark_opacity"])
                watermark.putalpha(alpha)
            
            img = add_element_to_space(img, watermark, empty_spaces, watermark.size)
        
        return img.convert("RGB")
    
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# =================== MAIN APP ===================
st.title("✨ Smart Photo Editor")

uploaded_images = st.file_uploader("📷 Upload Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings
with st.sidebar:
    st.header("Settings")
    
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])
    
    # Text settings
    show_text = st.checkbox("Add Text", True)
    if show_text:
        text_size = st.slider("Text Size", 20, 100, 50)
        text_color = st.color_picker("Text Color", "#FFFFFF")
    
    # Watermark settings
    use_watermark = st.checkbox("Add Watermark", False)
    if use_watermark:
        watermark_files = ["Think Tank TV.png", "Wishful Vibes.png", "Travellar Bharat.png", "Good Vibes.png"]
        watermark_file = st.selectbox("Select Watermark", watermark_files)
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)
        
        watermark_path = os.path.join("assets/logos", watermark_file)
        watermark_image = Image.open(watermark_path).convert("RGBA") if os.path.exists(watermark_path) else None

if st.button("✨ Process Images"):
    if uploaded_images:
        settings = {
            "greeting_type": greeting_type,
            "show_text": show_text,
            "text_size": text_size if show_text else 0,
            "text_color": text_color if show_text else "#FFFFFF",
            "use_watermark": use_watermark,
            "watermark_image": watermark_image if use_watermark else None,
            "watermark_opacity": watermark_opacity if use_watermark else 1.0
        }
        
        processed_images = []
        for uploaded_file in uploaded_images:
            img = Image.open(uploaded_file)
            processed_img = process_image(img, settings)
            if processed_img:
                filename = f"processed_{uploaded_file.name}"
                processed_images.append((filename, processed_img))
        
        if processed_images:
            st.success(f"Processed {len(processed_images)} images successfully!")
            
            # Display and download options
            cols = st.columns(3)
            for idx, (name, img) in enumerate(processed_images):
                with cols[idx % 3]:
                    st.image(img, caption=name)
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", quality=95)
                    st.download_button(
                        label=f"Download {name}",
                        data=img_bytes.getvalue(),
                        file_name=name,
                        mime="image/jpeg"
                    )
            
            # ZIP download
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for name, img in processed_images:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", quality=95)
                    zipf.writestr(name, img_bytes.getvalue())
            
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_buffer.getvalue(),
                file_name="processed_images.zip",
                mime="application/zip"
            )
