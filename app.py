import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="Bulk Image Processor", layout="wide")

# Custom CSS for clean look
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #000000;
        color: #ffffff;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def get_text_size(draw, text, font):
    # Helper function to replace deprecated textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_random_font(font_folder="assets/fonts"):
    fonts = list_files(font_folder, [".ttf", ".otf"])
    if not fonts:
        return None
    font_path = os.path.join(font_folder, random.choice(fonts))
    try:
        return ImageFont.truetype(font_path, 60)
    except:
        return None

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

def place_watermark(img, logo, opacity=1.0):
    w, h = img.size
    logo_w, logo_h = logo.size
    
    # Position watermark randomly but within bounds
    max_x = max(0, w - logo_w - 20)
    max_y = max(0, h - logo_h - 20)
    x = random.randint(20, max_x)
    y = random.randint(20, max_y)
    
    # Apply opacity
    watermark = logo.copy()
    if opacity < 1.0:
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
    
    img.paste(watermark, (x, y), watermark)
    return img

# =================== MAIN PAGE ===================
uploaded_images = st.file_uploader("📁 Upload Images (JPEG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# =================== SIDEBAR SETTINGS ===================
with st.sidebar:
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night", "Happy Birthday", "Thank You"])
    show_text = st.checkbox("Show Text", value=True)
    if show_text:
        text_size = st.slider("Text Size", 20, 100, 40)
    
    use_watermark = st.checkbox("Add Watermark", value=False)
    if use_watermark:
        watermark_file = st.file_uploader("Upload Watermark", type=["png"])
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)

# Process button at the top
if st.button("✨ Process Images", key="process_button"):
    if uploaded_images:
        results = []
        for image_file in uploaded_images:
            try:
                # Open image
                image = Image.open(image_file).convert("RGBA")
                
                # Apply cropping
                image = crop_to_3_4(image)
                w, h = image.size
                
                # Prepare for drawing
                draw = ImageDraw.Draw(image)
                
                # Get random font
                font = get_random_font()
                if font is None:
                    font = ImageFont.load_default()
                
                # Draw text if enabled
                if show_text:
                    font_main = font.font_variant(size=text_size)
                    text = greeting_type
                    
                    # Get text size using new method
                    text_width, text_height = get_text_size(draw, text, font_main)
                    
                    # Position text randomly but within bounds
                    text_x = random.randint(20, max(20, w - text_width - 20))
                    text_y = random.randint(20, max(20, h - text_height - 20))
                    
                    # Draw text with random color
                    draw.text((text_x, text_y), text, font=font_main, fill=get_random_color())
                
                # Add watermark if enabled
                if use_watermark and watermark_file:
                    watermark_image = Image.open(watermark_file).convert("RGBA")
                    watermark_size = min(w, h) // 4
                    watermark_image.thumbnail((watermark_size, watermark_size))
                    image = place_watermark(image, watermark_image, watermark_opacity)
                
                # Convert to RGB for JPEG
                final = image.convert("RGB")
                results.append((image_file.name, final))
            
            except Exception as e:
                st.error(f"Error processing {image_file.name}: {str(e)}")

        # Display download options
        if results:
            st.success(f"Processed {len(results)} images successfully!")
            
            # Individual downloads
            cols = st.columns(3)
            for idx, (name, img) in enumerate(results):
                with cols[idx % 3]:
                    st.image(img, caption=name, use_column_width=True)
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", quality=95)
                    st.download_button(
                        label=f"Download {name}",
                        data=img_bytes.getvalue(),
                        file_name=name,
                        mime="image/jpeg",
                        key=f"dl_{idx}"
                    )
            
            # ZIP download
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for name, img in results:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", quality=95)
                    zipf.writestr(name, img_bytes.getvalue())
            
            st.download_button(
                label="Download All as ZIP",
                data=zip_buffer.getvalue(),
                file_name="processed_images.zip",
                mime="application/zip",
                key="dl_all"
            )
    else:
        st.warning("Please upload at least one image to process.")
