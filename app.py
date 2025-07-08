import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Instant Photo Generator", layout="wide")

# Custom CSS for black/white/yellow theme
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
        border-right: 1px solid #ffff00;
    }
    .stSlider>div>div>div>div {
        background-color: #ffff00;
    }
    .stCheckbox>div>label {
        color: white !important;
    }
    .stSelectbox>div>div>select {
        color: white !important;
    }
    .stImage>img {
        border: 2px solid #ffff00;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Instant Photo Generator</h1>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def smart_crop(img, target_ratio=3/4):
    w, h = img.size
    if w/h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

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
        "Good Morning": ["Rise and shine!", "Make today amazing!", "Morning blessings!"],
        "Good Night": ["Sweet dreams!", "Sleep tight!", "Night night!"]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def apply_text_effects(draw, position, text, font):
    effect = random.choice(["plain", "shadow", "outline"])
    color = get_random_color()
    
    if effect == "shadow":
        shadow_offset = 3
        draw.text((position[0]+shadow_offset, position[1]+shadow_offset), 
                 text, font=font, fill=(0,0,0))
        draw.text(position, text, font=font, fill=color)
    elif effect == "outline":
        outline_size = 2
        for x in range(-outline_size, outline_size+1):
            for y in range(-outline_size, outline_size+1):
                draw.text((position[0]+x, position[1]+y), text, font=font, fill=(0,0,0))
        draw.text(position, text, font=font, fill=color)
    else:
        draw.text(position, text, font=font, fill=color)

def apply_overlay(image, overlay_path, size=0.5):
    try:
        overlay = Image.open(overlay_path).convert("RGBA")
        new_size = (int(image.width * size), int(image.height * size))
        overlay = overlay.resize(new_size)
        
        # Random position but within bounds
        max_x = image.width - overlay.width - 20
        max_y = image.height - overlay.height - 20
        x = random.randint(20, max_x)
        y = random.randint(20, max_y)
        
        image.paste(overlay, (x, y), overlay)
    except Exception as e:
        st.error(f"Error applying overlay: {str(e)}")
    return image

def generate_filename():
    now = datetime.datetime.now()
    return f"Picsart_{now.strftime('%d-%m-%y_%H-%M-%S-%f')[:-3]}.jpg"

# =================== MAIN APP ===================
uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Greeting type
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])
    
    # Text settings
    show_text = st.checkbox("Show Greeting", value=True)
    if show_text:
        main_size = st.slider("Main Text Size", 20, 100, 60)
    show_wish = st.checkbox("Show Wish", value=True)
    if show_wish:
        wish_size = st.slider("Wish Text Size", 10, 60, 30)
    
    # Watermark settings
    use_watermark = st.checkbox("Add Watermark", value=False)
    watermark_image = None
    
    if use_watermark:
        available_watermarks = [
            "Think Tank TV.png",
            "Wishful Vibes.png",
            "Travellar Bharat.png",
            "Good Vibes.png"
        ]
        selected_watermark = st.selectbox("Select Watermark", available_watermarks)
        watermark_path = os.path.join("assets/logos", selected_watermark)
        if os.path.exists(watermark_path):
            watermark_image = Image.open(watermark_path).convert("RGBA")
        
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)
    
    # Overlay settings
    use_overlay = st.checkbox("Use Pre-made Overlays", value=False)
    
    if use_overlay:
        overlay_theme = st.selectbox("Select Theme", ["Theme1", "Theme2"])
        
        # Random overlay selection
        random_overlay = st.checkbox("Random Overlay Selection", value=True)
        
        if not random_overlay:
            if greeting_type == "Good Morning":
                overlay_files = ["1.png", "2.png"]
            else:
                overlay_files = ["1.png", "3.png"]
        else:
            overlay_files = random.sample(["1.png", "2.png", "3.png", "4.png", "5.png"], 2)
        
        overlay_size = st.slider("Overlay Size", 0.1, 1.0, 0.5)

# Process button at the top
if st.button("✨ Generate Photos", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images..."):
            processed_images = []
            
            for uploaded_file in uploaded_images:
                try:
                    img = Image.open(uploaded_file).convert("RGBA")
                    
                    # Auto crop to 3:4 ratio
                    img = smart_crop(img)
                    
                    # Auto enhance
                    img = ImageEnhance.Contrast(img).enhance(1.1)
                    img = ImageEnhance.Sharpness(img).enhance(1.2)
                    
                    # Apply overlays if enabled
                    if use_overlay:
                        for overlay_file in overlay_files:
                            overlay_path = os.path.join("assets/overlays", overlay_theme, overlay_file)
                            img = apply_overlay(img, overlay_path, overlay_size)
                    
                    # Only add text if overlays not used
                    if not use_overlay:
                        draw = ImageDraw.Draw(img)
                        font = get_random_font()
                        
                        # Add main text
                        if show_text:
                            font_main = font.font_variant(size=main_size)
                            text = greeting_type
                            text_width, text_height = get_text_size(draw, text, font_main)
                            
                            # Smart positioning
                            text_x = random.randint(20, img.width - text_width - 20)
                            text_y = random.randint(20, img.height - text_height - 50)
                            
                            apply_text_effects(draw, (text_x, text_y), text, font_main)
                        
                        # Add wish text
                        if show_wish:
                            font_wish = font.font_variant(size=wish_size)
                            wish_text = get_random_wish(greeting_type)
                            wish_width, wish_height = get_text_size(draw, wish_text, font_wish)
                            
                            wish_x = random.randint(20, img.width - wish_width - 20)
                            wish_y = text_y + main_size + 10
                            
                            apply_text_effects(draw, (wish_x, wish_y), wish_text, font_wish)
                    
                    # Add watermark if enabled
                    if use_watermark and watermark_image:
                        watermark = watermark_image.copy()
                        
                        # Apply opacity
                        if watermark_opacity < 1.0:
                            alpha = watermark.split()[3]
                            alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                            watermark.putalpha(alpha)
                        
                        # Resize proportionally
                        watermark.thumbnail((img.width//4, img.height//4))
                        
                        # Position in one of the corners
                        positions = [
                            (20, 20),  # top-left
                            (img.width - watermark.width - 20, 20),  # top-right
                            (20, img.height - watermark.height - 20),  # bottom-left
                            (img.width - watermark.width - 20, img.height - watermark.height - 20)  # bottom-right
                        ]
                        pos = random.choice(positions)
                        
                        img.paste(watermark, pos, watermark)
                    
                    processed_images.append((generate_filename(), img.convert("RGB")))
                
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            st.session_state.processed_images = processed_images
            st.success(f"✅ Generated {len(processed_images)} photos!")

# Display results
if 'processed_images' in st.session_state and st.session_state.processed_images:
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
        label="📦 Download All",
        data=zip_buffer.getvalue(),
        file_name="Generated_Photos.zip",
        mime="application/zip"
        )
