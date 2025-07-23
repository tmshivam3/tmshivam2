from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import streamlit as st
import os
import io
import random
import datetime
import zipfile
import numpy as np
import math
import colorsys

# =================== UTILITY FUNCTIONS ===================
def get_dominant_color(image):
    """Get dominant color from image"""
    small_img = image.resize((1, 1))
    return small_img.getpixel((0, 0))

def random_bright_color():
    """Generate random bright color (avoiding black/dark colors)"""
    h = random.random()
    s = 0.8 + random.random() * 0.2
    v = 0.8 + random.random() * 0.2
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def create_gradient_mask(width, height, colors):
    """Create gradient mask with black stroke"""
    # Create gradient base
    base = Image.new('RGB', (width, height))
    half = width // 2
    for x in range(width):
        if x < half:
            r, g, b = colors[0]
        else:
            ratio = (x - half) / (width - half - 1)
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        for y in range(height):
            base.putpixel((x, y), (r, g, b))
    
    return base

def get_gradient_colors(dominant_color=None):
    """Return white + one bright color (random or from dominant)"""
    if dominant_color:
        # Use dominant color from image
        return [(255, 255, 255), dominant_color]
    else:
        # Use random bright color
        return [(255, 255, 255), random_bright_color()]

def get_text_size(draw, text, font):
    """Get text dimensions"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def random_text_style():
    """Select a random text style"""
    return random.choice([
        'gradient', 'neon', 'shadow', 'gold', 'silver', 
        'fire', 'ice', 'bubble', 'space', 'neon_pink'
    ])

# =================== MAIN APP ===================
st.set_page_config(page_title="Image Text Styler", layout="wide")

# Custom CSS for clean UI
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        color: #333333;
    }
    .header-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #4a86e8;
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 5px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #3a76d8;
    }
    .stImage>img {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .variant-container {
        display: flex;
        overflow-x: auto;
        gap: 15px;
        padding: 15px 0;
    }
    .variant-item {
        flex: 0 0 auto;
    }
    .download-btn {
        display: block;
        margin-top: 10px;
        text-align: center;
    }
    .section-title {
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
        margin-top: 25px;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# App header
st.markdown("""
    <div class='header-container'>
        <h1 style='text-align: center; color: #333333; margin: 0;'>
            Image Text Styler
        </h1>
        <p style='text-align: center; color: #666666;'>Add automatic stylized text to your images</p>
    </div>
""", unsafe_allow_html=True)

# Image upload
uploaded_images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings
with st.sidebar:
    st.markdown("### Text Settings")
    
    text_style = st.selectbox("Text Style", ["Gradient", "Smart Gradient", "Random Style"])
    
    if text_style == "Random Style":
        st.info("Each image will get a different random text style")
    
    text_content = st.text_input("Text Content", "Awesome Content")
    text_size = st.slider("Text Size", 20, 200, 80)
    num_variants = st.slider("Variants per Image", 1, 5, 3)
    
    st.markdown("### Output Settings")
    output_quality = st.selectbox("Output Quality", ["High", "Medium", "Low"], index=0)

# Processing function
def process_image(image, text, style, size, variant_idx):
    """Process image with stylized text"""
    img = image.copy().convert("RGBA")
    width, height = img.size
    
    # Create drawing context
    base = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(base)
    
    # Select font
    try:
        font = ImageFont.truetype("arialbd.ttf", size)
    except:
        font = ImageFont.load_default()
    
    # Get text dimensions
    text_width, text_height = get_text_size(draw, text, font)
    
    # Position text in center
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Determine style for this variant
    if style == "Random Style":
        current_style = random_text_style()
    else:
        current_style = "gradient" if style == "Gradient" else "smart_gradient"
    
    # Get colors based on style
    if current_style == "smart_gradient":
        dominant_color = get_dominant_color(img)
        colors = get_gradient_colors(dominant_color)
    else:
        colors = get_gradient_colors()
    
    # Create gradient text with black stroke
    gradient = create_gradient_mask(text_width, text_height, colors)
    gradient_text = Image.new('RGBA', (text_width, text_height))
    temp_img = Image.new('RGBA', (text_width, text_height))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
    gradient_text.paste(gradient, (0, 0), temp_img)
    
    # Apply black stroke
    stroke_size = 3
    for ox in range(-stroke_size, stroke_size+1):
        for oy in range(-stroke_size, stroke_size+1):
            if ox != 0 or oy != 0:
                base.paste((0, 0, 0), (x+ox, y+oy), temp_img)
    
    # Apply text
    base.paste(gradient_text, (x, y), gradient_text)
    
    # Combine with original image
    result = Image.alpha_composite(img, base)
    
    return result.convert("RGB")

# Process images when button clicked
if st.button("Process Images", use_container_width=True):
    if uploaded_images:
        processed_images = []
        
        with st.spinner("Processing images..."):
            for img_idx, uploaded_file in enumerate(uploaded_images):
                try:
                    img = Image.open(uploaded_file)
                    filename = os.path.splitext(uploaded_file.name)[0]
                    
                    # Create variants
                    for variant in range(num_variants):
                        processed_img = process_image(
                            img, 
                            text_content, 
                            text_style, 
                            text_size,
                            variant
                        )
                        
                        # Generate filename
                        variant_name = f"{filename}_v{variant+1}.jpg"
                        processed_images.append((variant_name, processed_img))
                        
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        st.session_state.processed_images = processed_images
        st.success(f"Successfully processed {len(processed_images)} images!")
    else:
        st.warning("Please upload at least one image")

# Display and download results
if 'processed_images' in st.session_state and st.session_state.processed_images:
    st.markdown("## Processed Results")
    
    # Create zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, img in st.session_state.processed_images:
            img_bytes = io.BytesIO()
            quality = 95 if output_quality == "High" else 80 if output_quality == "Medium" else 70
            img.save(img_bytes, format='JPEG', quality=quality)
            zip_file.writestr(filename, img_bytes.getvalue())
    
    # Download button
    st.download_button(
        label="Download All Images",
        data=zip_buffer.getvalue(),
        file_name="styled_images.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    # Display images
    cols_per_row = 3
    processed = st.session_state.processed_images
    
    for i in range(0, len(processed), cols_per_row):
        cols = st.columns(cols_per_row)
        row_images = processed[i:i+cols_per_row]
        
        for col_idx, (filename, img) in enumerate(row_images):
            with cols[col_idx]:
                st.image(img, use_container_width=True, caption=filename)
                
                # Individual download
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                st.download_button(
                    label="Download",
                    data=img_bytes.getvalue(),
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"dl_{filename}"
                        )
