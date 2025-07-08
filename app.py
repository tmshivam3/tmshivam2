import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np
from collections import Counter

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
    .feature-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def get_dominant_color(image):
    image = image.copy()
    image.thumbnail((100, 100))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    colors = image.getcolors(maxcolors=10000)
    if not colors:
        return (255, 255, 255)
    colors.sort(reverse=True)
    return colors[0][1]

def get_text_color(bg_color):
    r, g, b = bg_color
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

def smart_crop(img):
    # Simple smart crop (replace with actual object detection if needed)
    w, h = img.size
    if w > h:
        left = (w - h) // 2
        return img.crop((left, 0, left + h, h))
    else:
        top = (h - w) // 2
        return img.crop((0, top, w, top + w))

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
        "Good Morning": ["Have a great day!", "Rise and shine!", "Make today amazing!"],
        "Good Night": ["Sweet dreams!", "Sleep tight!", "Night night!"]
    }
    return random.choice(wishes.get(greeting_type, ["Have a nice day!"]))

def get_random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def get_gradient_color(color1, color2, factor):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

def add_text_effects(draw, position, text, font, image_width):
    # Random effects
    effect_type = random.choice(["outline", "shadow", "gradient", "plain"])
    color1 = get_random_color()
    color2 = get_random_color()
    
    if effect_type == "outline":
        outline_size = random.randint(1, 3)
        for x in range(-outline_size, outline_size+1):
            for y in range(-outline_size, outline_size+1):
                draw.text((position[0]+x, position[1]+y), text, font=font, fill=(0,0,0))
        draw.text(position, text, font=font, fill=color1)
    
    elif effect_type == "shadow":
        shadow_offset = random.randint(2, 5)
        draw.text((position[0]+shadow_offset, position[1]+shadow_offset), 
                 text, font=font, fill=(0,0,0,150))
        draw.text(position, text, font=font, fill=color1)
    
    elif effect_type == "gradient":
        for i, char in enumerate(text):
            factor = i / len(text)
            color = get_gradient_color(color1, color2, factor)
            char_width = get_text_size(draw, char, font)[0]
            draw.text((position[0], position[1]), char, font=font, fill=color)
            position = (position[0] + char_width, position[1])
    
    else:
        draw.text(position, text, font=font, fill=color1)

def place_watermark_smart(img, logo):
    w, h = img.size
    logo_w, logo_h = logo.size
    
    # Simple smart placement (top-right corner)
    x = w - logo_w - 20
    y = 20
    
    img.paste(logo, (x, y), logo)
    return img

def generate_filename():
    now = datetime.datetime.now()
    return f"Picsart_{now.strftime('%d-%m-%y_%H-%M-%S-%f')[:-3]}.jpg"

# =================== MAIN APP ===================
col1, col2 = st.columns([3, 1])

# Image uploader
with col1:
    uploaded_images = st.file_uploader("📷 Upload Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Main settings panel
with st.sidebar:
    st.markdown("### ⚙️ Basic Settings")
    
    greeting_type = st.selectbox("Greeting Type", ["Good Morning", "Good Night"])
    show_text = st.checkbox("Show Greeting", value=True)
    show_wish = st.checkbox("Show Wish", value=True)
    
    # Watermark options
    use_watermark = st.checkbox("Add Watermark", value=False)
    watermark_image = None
    
    if use_watermark:
        watermark_option = st.radio("Watermark Source", ["Select from Library", "Upload Your Own"])
        
        if watermark_option == "Select from Library":
            available_watermarks = list_files("assets/logos", [".png"])
            if available_watermarks:
                selected_watermark = st.selectbox("Select Watermark", available_watermarks)
                watermark_image = Image.open(os.path.join("assets/logos", selected_watermark)).convert("RGBA")
            else:
                st.warning("No watermarks found in assets/logos folder")
        else:
            uploaded_watermark = st.file_uploader("Upload Watermark PNG", type=["png"])
            if uploaded_watermark:
                watermark_image = Image.open(uploaded_watermark).convert("RGBA")

# Advanced settings panel (floating on right)
with col2:
    st.markdown("### ✨ Advanced Tools")
    
    with st.expander("Text Effects"):
        auto_text_size = st.checkbox("Auto Adjust Text Size", value=True)
        random_effects = st.checkbox("Random Text Effects", value=True)
        multi_line = st.checkbox("Multi-line Greeting", value=False)
    
    with st.expander("Image Enhancements"):
        auto_contrast = st.checkbox("Auto Contrast", value=True)
        enhance_sharpness = st.checkbox("Enhance Sharpness", value=True)
    
    with st.expander("Layout Options"):
        text_position = st.selectbox("Text Position", ["Auto", "Top", "Center", "Bottom"])
        watermark_opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.7)

# Process button
if st.button("✨ Generate Photos", key="generate"):
    if uploaded_images:
        with st.spinner("Processing images..."):
            processed_images = []
            
            for uploaded_file in uploaded_images:
                try:
                    img = Image.open(uploaded_file).convert("RGBA")
                    img = smart_crop(img)
                    w, h = img.size
                    
                    # Auto enhancements
                    if auto_contrast:
                        img = ImageEnhance.Contrast(img).enhance(1.2)
                    if enhance_sharpness:
                        img = img.filter(ImageFilter.SHARPEN)
                    
                    draw = ImageDraw.Draw(img)
                    font = get_random_font()
                    
                    # Smart text placement
                    if show_text:
                        greeting = greeting_type
                        if multi_line and random.choice([True, False]):
                            greeting = greeting_type.replace(" ", "\n")
                        
                        # Auto font size based on image width
                        font_size = min(w//5, h//3) if auto_text_size else w//6
                        font = font.font_variant(size=font_size)
                        
                        text_width, text_height = get_text_size(draw, greeting, font)
                        
                        # Position text
                        if text_position == "Auto":
                            text_x = random.randint(20, max(20, w - text_width - 20))
                            text_y = random.randint(20, max(20, h - text_height - 50))
                        elif text_position == "Top":
                            text_x = (w - text_width) // 2
                            text_y = 20
                        elif text_position == "Center":
                            text_x = (w - text_width) // 2
                            text_y = (h - text_height) // 2
                        else: # Bottom
                            text_x = (w - text_width) // 2
                            text_y = h - text_height - 20
                        
                        # Add text with effects
                        if random_effects:
                            add_text_effects(draw, (text_x, text_y), greeting, font, w)
                        else:
                            draw.text((text_x, text_y), greeting, font=font, fill=get_random_color())
                    
                    # Add wish
                    if show_wish:
                        wish_text = get_random_wish(greeting_type)
                        wish_font_size = font_size // 2
                        wish_font = font.font_variant(size=wish_font_size)
                        wish_width, wish_height = get_text_size(draw, wish_text, wish_font)
                        
                        wish_x = (w - wish_width) // 2
                        wish_y = text_y + text_height + 10
                        
                        draw.text((wish_x, wish_y), wish_text, font=wish_font, fill=get_random_color())
                    
                    # Add watermark
                    if use_watermark and watermark_image:
                        watermark = watermark_image.copy()
                        if watermark_opacity < 1.0:
                            alpha = watermark.split()[3]
                            alpha = ImageEnhance.Brightness(alpha).enhance(watermark_opacity)
                            watermark.putalpha(alpha)
                        
                        watermark.thumbnail((w//4, h//4))
                        img = place_watermark_smart(img, watermark)
                    
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
